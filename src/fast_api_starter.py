import configparser, csv, glob, json, os, shutil, uvicorn
from pathlib import Path
from typing import List
from starlette.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Form, File, UploadFile, Request, HTTPException
from fastapi.templating import Jinja2Templates

import src.file_creating as fc
from src.consensus_maker import generate_consensus_fasta
from src.logging_config import setup_logging
from src.config import Config

import subprocess, logging

setup_logging()
logger = logging.getLogger("myapp")

logger.info("Application started at http://localhost:8000 (Press CTRL+C to quit)")

BASE_DIR = Path(__file__).resolve().parent.parent
os.environ["R_PROFILE_USER"] = str(BASE_DIR / ".Rprofile")
os.environ["LANG"] = "en_US.UTF-8"
from rpy2.robjects import r
from rpy2.rinterface_lib.embedded import RRuntimeError


# DEBUG MODE:
if not os.path.exists("/.dockerenv"):
    print('Program not in docker - debug mode')
    install_path = (BASE_DIR / "install_packages.R").resolve()
    install_path = str(install_path).replace("\\", "/")
    print("Using:", install_path)
    project_rprofile = str(BASE_DIR / ".Rprofile")
    project_rlib = str(BASE_DIR / "Rlibs")

    os.environ["R_LIBS_USER"] = project_rlib
    os.environ["R_LIBS"] = project_rlib  # added as a safeguard

    #subprocess.run(["Rscript", install_path], check=True)

app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

def tmp_creator(request):
    """
    Creates all necessary temporary directories.
    :param request: Incoming FastAPI request.
    :return: TemplateResponse
        Rendered HTML error page.
    """
    for path in (Config.TMP_PATH, Config.RESULT_PATH):
        try:
            os.makedirs(path, exist_ok=True)
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return error_message(request)

def config_creator(path_to_metadata):
    """
    Creates or loads a configuration file at the given path.
    If the file does not exist, an empty file is created. The function then
    returns a RawConfigParser instance with the file's contents loaded.
    """
    if os.path.exists(path_to_metadata):
        with open(path_to_metadata, 'w') as file:
            pass
    config_parser = configparser.RawConfigParser()
    config_parser.read(path_to_metadata)
    return config_parser

def file_saver(files, request):
    """
    Saves uploaded files to a temporary directory and checks for a CSV file.
    :param files: Uploaded files from the web API.
    :param request: Incoming FastAPI request.
    :return: TemplateResponse or None
        Rendered HTML error/feedback page when validation fails; otherwise None.
    """
    no_csv = True
    try:
        for file in files:
            contents = file.file.read()
            if file.filename is None:
                raise HTTPException(status_code=400, detail="No file name")
            elif '.csv' in file.filename:
                no_csv = False
                continue
            tmp_path = os.path.join(f'{Config.TMP_PATH}{file.filename}')
            with open(tmp_path, "wb") as f:
                f.write(contents)
            file.file.close()
    except Exception as e:
        logger.error(f"OS error while creating path: {e}")
        return error_message(request)
    finally:
        if no_csv:
            logger.info(f"No .csv file detected.")
            return feedback_message(
                request,
                {"title": "No .csv file detected",
                 "detail": "Upload a .csv that includes your FASTA file names and group assignments."})
    return None

def csv_table_creator(table_data):
    """
    Creates .csv file from user web page table.
    :param table_data: Uploaded data table from the web API.
    """
    data = json.loads(table_data)
    with open(f'{Config.TMP_PATH}fasta_table.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["FASTA_id", "FASTA_path", "group"])
        writer.writerows([
            [row[0], f"{Config.TMP_PATH}{row[0]}", row[1]]
            for row in data
        ])

def alignment_checker(files, request):
    """
    Checks if only one alignment file was provided by user.
    :param files: Uploaded files from the web API.
    :param request: Incoming FastAPI request.
    :return: TemplateResponse or None
        Rendered HTML feedback page when validation fails; otherwise None.
    """
    alignment = [f for f in files if 'alignment' in f.filename.lower()]
    if len(alignment) == 0:
        logger.info(f"No alignment file detected... Please send a single alignment.fasta file.")
        return feedback_message(
            request,
            {"title": "No alignment file detected",
             "detail": f"Please send a single alignment.fasta file. "
                       f"Make sure that the alignment file includes 'alignment' in its name."})
    if len(alignment) > 1:
        logger.info(f"More than one alignment file detected... Please send a single alignment.fasta file.")
        return feedback_message(
            request,
            {"title": "No alignment file detected",
             "detail": f"More than one alignment file detected. "
                       f"Make sure only single file includes a word 'alignment'."})
    os.rename(f'{Config.TMP_PATH}{alignment[0].filename}', f'{Config.TMP_PATH}{Config.ALIGNMENT_FILE}')
    return None

def alignment_creator(request):
    """
    Creates an alignment based on fasta files provided by the user.
    :param request: Incoming FastAPI request.
    :return: TemplateResponse or None
        Rendered HTML error/feedback page when validation fails; otherwise None.
    """
    try:
        r.source('../R/run_custom_alignment.R')
        run_custom_alignment = r['run_custom_alignment']
        sample_table = r(f"read.csv('{Config.TMP_PATH}fasta_table.csv')")
        run_custom_alignment(sample_table)
        shutil.move(Config.ALIGNMENT_FILE, f'{Config.TMP_PATH}{Config.ALIGNMENT_FILE}')
    except (RRuntimeError, FileNotFoundError) as e:
        logger.error(f"Error: {e}")
        return feedback_message(
            request,
            {"title": "Files for generating an alignment have not been provided",
             "detail": f"Please send all fasta files necessary for creating an alignment"})
    except Exception as e:
        logger.error(f"Error: {e}")
        return error_message(request)
    return None

def statistical_tracks_generator(selected_options, request):
    """
    Generates ready-to-use circos compatible tracks using custom R scripts for statistical analyses.
    :param selected_options: Options checked by the user via webpage.
    :param request: Incoming FastAPI request.
    :return: TemplateResponse or None
        Rendered HTML error/feedback page when validation fails; otherwise None.
    """
    try:
        for script in Config.R_SCRIPTS.values():
            r(f'source("{script}")')
        sample_table = r(f"read.csv('{Config.TMP_PATH}fasta_table.csv')")
        preparing_circos_data = r['prepare_circos_data']
        preparing_circos_data(sample_table, selected_options, Config.ALIGNMENT_FILE)
        txt_files = glob.glob(os.path.join(Config.PY_SCRIPTS_PATH, "*.txt"))
        for f in txt_files:
            try:
                shutil.move(f, Config.RESULT_PATH)
            except Exception as e:
                logger.error(f"Failed to move {f}: {e}")
                return error_message(request)
        if not txt_files:
            logger.info("No .txt result files found in current directory.")
    except (RRuntimeError, Exception) as e:
        logger.error(f"Error: {e}")
        return error_message(request)
    return None

def gene_annotator(request):
    """
    Generates gene annotation for gene name track on circos using Chloe.jl.
    :param request: Incoming FastAPI request.
    :return: TemplateResponse or None
        Rendered HTML error/feedback page when validation fails; otherwise None.
    """
    try:
        if not os.path.exists(f'{Config.CHLOE_PATH}'):
            os.makedirs(f'{Config.CHLOE_PATH}')
        consensus = generate_consensus_fasta(path=Config.TMP_PATH, file=Config.ALIGNMENT_FILE)
        with open(f'{Config.CHLOE_PATH}consensus.fasta', 'w') as f:
            f.write('>consensus.fasta\n')
            f.write(consensus)
        subprocess.run(['bash', './chloe_runner.sh', Config.RESULT_PATH], check=True)
        fc.create_gene_name(fc.file_finder(f"{Config.RESULT_PATH}"), f"{Config.RESULT_PATH}")
    except Exception as e:
        logger.error(f"Error: {e}")
        return error_message(request)
    return None

def config_writer(meta_data, metadata):
    """
    Saves a configuration file based on current metadata variable.
    """
    with open(meta_data, 'w') as configfile:
        metadata.write(configfile)

def feedback_message(request, context):
    """
    Returns feedback with current app state using the 'feedback.html' template.
    :param request: The incoming FastAPI request.
    :return: TemplateResponse
        Rendered HTML error page.
    """
    return templates.TemplateResponse(
        request=request,
        name="feedback.html",
        context=context
    )

def error_message(request):
    """
    Returns an error page response using the 'feedback.html' template.
    :param request: The incoming FastAPI request.
    :return: TemplateResponse
        Rendered HTML error page.
    """
    return templates.TemplateResponse(
        request=request,
        name="feedback.html",
        context={"title": "Internal app error",
                 "detail": "Internal application failure. Check log file for more information."}
    )

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

@app.post("/upload")
async def upload(request: Request,
                 options: List[str] = Form(...),
                 table_data: str = Form(...),
                 files: List[UploadFile] = File(...)):
    try:
        logger.info("Reading the form data from request...")
        selected_options = options

        logger.info("Creating all temporary directories...")
        tmp_creator(request)

        logger.info("Creating metadata.ini for circos tracks...")
        metadata = config_creator(f"{Config.RESULT_PATH}{Config.META_DATA}")

        logger.info("Checking for .csv file and saving all provided files to temporary directories...")
        file_saver(files, request)

        logger.info("Creating files based on data provided from user...")
        csv_table_creator(table_data)

        if 'is_Alignment' in selected_options:
            logger.info("Creating alignment from provided .fasta gene files...")
            alignment_checker(files, request)
        else:
            alignment_creator(request)

        logger.info("Processing all data for statistical analysis with circos track generation...")
        statistical_tracks_generator(selected_options, request)

        # TODO: Enable sending gff/bam(?) file by user
        if "annotate" in selected_options:
            logger.info("Running Chloe gene annotator for circos visualisation...")
            gene_annotator(request)




        # TODO: DIRE NEED TO CORRECT WHOLE CIRCOS TRACKS GENERATING PIPELINE
        for section in ['MetaData', 'OverallPlotInfo']:
            if not metadata.has_section(section):
                metadata.add_section(section)

        # TODO: though these files are not created based off options chosen by the user,
        #       in the current version it's possible that gene_name file won't exist if user choses "no annotation" option
        #       -> in the future enabling sending gff/bam file by user and requirement that annotation NEEDS to be as a track
        #          will resolve this
        for visual_track in ['karyotype', 'highlights', 'gene_name']:
            metadata.set('MetaData', visual_track, f"{visual_track}.txt")

        # TODO: loop below for improvement - after user inserts only single file it will become useless
        #fasta_iter = 1 # variable for future development of more than single fasta file
        for file in files:
            if file.filename.endswith('fasta'):
                metadata.set('MetaData', f'fasta', file.filename)
            for option in selected_options:
                if file.filename.find('snp') >= 0 and option == 'SNP':
                    if file.filename.endswith('perc.txt'):
                        metadata.set('OverallPlotInfo', f'file_snp_perc', file.filename)
                    elif file.filename.endswith('snp.txt'):
                        metadata.set('OverallPlotInfo', f'file_snp', file.filename)
                    elif file.filename.endswith('mt.txt'):
                        metadata.set('OverallPlotInfo', f'file_snp_mt', file.filename)
                elif file.filename.find('ind') >= 0 and option == 'IND':
                    if file.filename.endswith('perc.txt'):
                        metadata.set('OverallPlotInfo', f'file_ind_perc', file.filename)
                    elif file.filename.endswith('ind.txt'):
                        metadata.set('OverallPlotInfo', f'file_ind', file.filename)
                    elif file.filename.endswith('mt.txt'):
                        metadata.set('OverallPlotInfo', f'file_ind_mt', file.filename)
                elif file.filename.find('popGenome') >= 0 and option == 'P_DIV':
                    metadata.set('OverallPlotInfo', f'file_p_div', file.filename)

        # Overwriting metadata.ini file:
        config_writer(Config.META_DATA, metadata)

        # Run the circos shell file:
        subprocess.run('../circos_project.sh', shell=True)
        return {"message": f"Successfuly uploaded... Circos generator task completed."}

    finally:
        for path in (Config.TMP_PATH, Config.RESULT_PATH, Config.CHLOE_PATH):
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
        logger.info("All temporary files deleted.")


# Only for testing purposes
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
