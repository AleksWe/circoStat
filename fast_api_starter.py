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

meta_data = "metadata.ini"
app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)


def config_creator(config):
    if os.path.exists(meta_data):
        with open(meta_data, 'w') as file:
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

    # Create a ./tmp directory
    try:
        os.makedirs("./tmp/", exist_ok=True)
    except PermissionError:
        print("No permission to make a ./tmp/ directory")
    except OSError as e:
        print(e)

    # Create csv file from user input table_data:
    data = json.loads(table_data)
    with open('./tmp/fasta_table.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["FASTA_id", "group", "FASTA_path"])
        writer.writerows([row + [f"./tmp/{row[0]}"] for row in data])

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
            tmp_path = os.path.join(f'./tmp/{file.filename}')
            with open(tmp_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            return f"There was an error uploading the file(s): {e}"
        finally:
            file.file.close()

    # TODO: Run run_custom_alignment.R - za pomocą uruchomienia R z poziomu pythona
    #  może za pomocą rpy2? pip install rpy2
    #### tu musi być wywołanie skryptu R z robieniem alignmentu run_custom_alignment.R
    #result = subprocess.run(
    #    ["Rscript", "run_custom_alignment.R"],
    #    capture_output=True,
    #    text=True
    #)
    #print(result.stdout)

    # TODO: Chloe to be run only if user chooses to make annotations:
    # TODO: If annotate = False, then check if gff file is sent from user
    # Run Chloe shell to annotate genes:
    annotate = True
    if annotate:
        for file in files:
            tmp_path = os.path.join(f'./tmp/{file.filename}')
            if tmp_path and tmp_path.endswith((".fasta",".fa")):
                if not os.path.exists('./chloe/'):
                    os.makedirs('./chloe/')
                shutil.move(tmp_path, './chloe/')
        try:
            subprocess.run('./chloe_runner.sh')
        except FileNotFoundError as e:
            print("Fasta file not found in folder. ERROR:", e)

    # Run script that generates gene_names, highlights, karyotype:
    try:
        subprocess.call(['python3', 'file_creating.py'])
    except FileNotFoundError as e:
        print("The .gff3 or .gff file not found in folder. ERROR:", e)

    # Create config metadata.ini and overwrite it
    config = config_creator(meta_data)

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
    config_writer(meta_data, config)

    # Run the circos shell file:
    subprocess.run('./circos_project.sh', shell=True)
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
