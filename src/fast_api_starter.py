import configparser
import csv
import json
import os
import shutil
from pathlib import Path
import uvicorn
from typing import List
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Form, File, UploadFile, Request, HTTPException
from fastapi.templating import Jinja2Templates
import subprocess
from starlette.staticfiles import StaticFiles
from rpy2.robjects import r
from rpy2.rinterface_lib.embedded import RRuntimeError

BASE_DIR = Path(__file__).resolve().parent.parent
ALIGNMENT_FILE = 'Alignment.fasta'
TMP_PATH = '../tmp/'
META_DATA = "metadata.ini"
R_SCRIPTS = {
    'prepare': '../R/prepare_circos_data.R',
    'snp': '../R/get_snp_profiles.R',
    'pdiv': '../R/calculate_pop_stats.R',
    'nuc_div': '../R/run_spider.R'
}

if not os.path.exists("/.dockerenv"):
    #TODO: sprawdzenie czy pakiety R są zainstalowane - tylko do debug mode
    #r['source'](str(BASE_DIR / "install_packages.R"))
    print('Program not in docker - debug mode')
    path = str(BASE_DIR / ".Rprofile")
    r['source'](path)

app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

def config_creator(config):
    if os.path.exists(META_DATA):
        with open(META_DATA, 'w') as file:
            pass
    configParser = configparser.RawConfigParser()
    configParser.read(config)
    return configParser


def config_writer(meta_data, config):
    with open(meta_data, 'w') as configfile:
        config.write(configfile)


@app.post("/upload")
async def upload(options: List[str] = Form(...),
                 table_data: str = Form(...),
                 files: List[UploadFile] = File(...)):
    # Read the form data from the request
    selected_options = options

    # Create a ../tmp directory
    try:
        os.makedirs(TMP_PATH, exist_ok=True)
    except PermissionError:
        print("No permission to make a /tmp directory")
    except OSError as e:
        print(e)

    # Create csv file from user input table_data:
    data = json.loads(table_data)
    with open(f'{TMP_PATH}fasta_table.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["FASTA_id", "group", "FASTA_path"])
        writer.writerows([row + [f"{TMP_PATH}{row[0]}"] for row in data])

    # TODO: oddzielić input zaczytywania z pliku .csv, który ma uzupełniać tylko frontend
    #  (nie jest potrzebny później, bo ważniejsze są dane, które są jako tabela na stronie
    #  - mogą być poprawiane przez użytkownika)
    # Read files from user input and put them in ./tmp directory
    for file in files:
        try:
            contents = file.file.read()
            file_name = file.filename
            if file_name is None:
                raise HTTPException(status_code=400, detail="Brak nazwy pliku")
            tmp_path = os.path.join(f'{TMP_PATH}{file.filename}')
            with open(tmp_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            return f"There was an error uploading the file(s): {e}"
        finally:
            file.file.close()

    # If passed .fasta file is an alignment, then save it to Alignment.fasta
    # TODO: On FRONTEND Give info to user that alignment.fasta should have "alignment" in name
    if 'is_Alignment' in selected_options:
        alignment = [f for f in files if 'alignment' in f.filename.lower()]
        if len(alignment) == 0:
            return {"message": f"No alignment file detected... Please send a single Alignment.fasta file."}
        if len(alignment) > 1:
            return {"message": f"More than one alignment file detected... Please send a single Alignment.fasta file."}
        os.rename(f'{TMP_PATH}{alignment[0].filename}', f'{TMP_PATH}{ALIGNMENT_FILE}')
    else:
        try:
            r.source('../R/run_custom_alignment.R')
            run_custom_alignment = r['run_custom_alignment']
            sample_table = r(f"read.csv('{TMP_PATH}fasta_table.csv')")
            run_custom_alignment(sample_table)
            shutil.move(ALIGNMENT_FILE, f'{TMP_PATH}{ALIGNMENT_FILE}')
        except (RRuntimeError, Exception) as e:
            return {"message": f"Error: {e}"}

    try:
    # TODO: other tracks for P_DIV and NUC_DIV
        if 'SNP' in selected_options:
            r.source('../R/get_snp_profiles.R')
            get_snp = r['get_snp_profiles']
            get_snp(f"{TMP_PATH}{ALIGNMENT_FILE}")
        sample_table = r(f"read.csv('{TMP_PATH}fasta_table.csv')")
        function_to_run = r['prepare_circos_data']
        prepared_circos_data = function_to_run(sample_table)
    except (RRuntimeError, Exception) as e:
        return {"message": f"Error: {e}"}

    print(prepared_circos_data)

    ## TODO: RUN ALL CALCULATIONS BASED ON USER INPUT
    #if 'PIV_D' in selected_options:
    #    piv_D = prepared_circos_data[1]
    #if 'IND' in selected_options:
    #    ind = prepared_circos_data[2]

    # TODO: Chloe to be run only if user chooses to make annotations:
    # TODO: If annotate = False, then check if gff file is sent from user
    # Run Chloe shell to annotate genes:
    annotate = True
    if annotate:
        for file in files:
            tmp_path = os.path.join(f'{TMP_PATH}{file.filename}')
            if tmp_path and tmp_path.endswith((".fasta",".fa")):
                if not os.path.exists('../chloe/'):
                    os.makedirs('../chloe/')
                shutil.move(tmp_path, '../chloe/')
        try:
            subprocess.run('../chloe_runner.sh')
        except FileNotFoundError as e:
            print("Fasta file not found in folder. ERROR:", e)

    # Run script that generates gene_names, highlights, karyotype:
    try:
        subprocess.call(['python3', 'file_creating.py'])
    except FileNotFoundError as e:
        print("The .gff3 or .gff file not found in folder. ERROR:", e)

    # Create config metadata.ini and overwrite it
    config = config_creator(META_DATA)

    if not config.has_section('MetaData'):
        config.add_section('MetaData')
    if not config.has_section('OverallPlotInfo'):
        config.add_section('OverallPlotInfo')

    # TODO: files below are not to be created based off of option chosen by the user (annotate or not, that is the question) ????
    for file in os.listdir(os.getcwd()):
        if file.find('karyotype') >= 0:  # for improvement
            config.set('MetaData', 'karyotype', file)
        elif file.find('gene_name') >= 0:  # for improvement
            config.set('MetaData', 'gene_name', file)
        elif file.find('highlights') >= 0:  # for improvement
            config.set('MetaData', 'highlights', file)

    # TODO: loop below for improvement - after user inserts only single file it will become useless
    #fasta_iter = 1 # variable for future development of more than single fasta file
    for file in files:
        if file.filename.endswith('fasta'):
            config.set('MetaData', f'fasta', file.filename)
        for option in selected_options:
            if file.filename.find('snp') >= 0 and option == 'SNP':
                if file.filename.endswith('perc.txt'):
                    config.set('OverallPlotInfo', f'file_snp_perc', file.filename)
                elif file.filename.endswith('snp.txt'):
                    config.set('OverallPlotInfo', f'file_snp', file.filename)
                elif file.filename.endswith('mt.txt'):
                    config.set('OverallPlotInfo', f'file_snp_mt', file.filename)
            elif file.filename.find('ind') >= 0 and option == 'IND':
                if file.filename.endswith('perc.txt'):
                    config.set('OverallPlotInfo', f'file_ind_perc', file.filename)
                elif file.filename.endswith('ind.txt'):
                    config.set('OverallPlotInfo', f'file_ind', file.filename)
                elif file.filename.endswith('mt.txt'):
                    config.set('OverallPlotInfo', f'file_ind_mt', file.filename)
            elif file.filename.find('popGenome') >= 0 and option == 'P_DIV':
                config.set('OverallPlotInfo', f'file_p_div', file.filename)

    # Overwriting metadata.ini file:
    config_writer(META_DATA, config)

    # Run the circos shell file:
    subprocess.run('../circos_project.sh', shell=True)
    return {"message": f"Successfuly uploaded... Circos generator task completed."}

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

# Only for testing purposes
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
