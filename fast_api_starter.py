import configparser
import os
from pathlib import Path

import uvicorn
from typing import List
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.templating import Jinja2Templates
import subprocess
from fastapi.middleware.cors import CORSMiddleware
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
                 files: List[UploadFile] = File(...)):
    # Read the form data from the request
    selected_options = options

    # For now, we will just print the options and the file names
    print(f"Chosen options: {selected_options}")
    print(f"Uploaded Files: {[file.filename for file in files]}")
    for file in files:
        try:
            contents = file.file.read()
            with open(file.filename, "wb") as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()

    config = config_creator(meta_data)

    if not config.has_section('MetaData'):
        config.add_section('MetaData')
    if not config.has_section('OverallPlotInfo'):
        config.add_section('OverallPlotInfo')

    #fasta_iter = 1 # variable for future development of more than single fasta file
    for file in files:
        if file.filename.endswith('fasta'):
            config.set('MetaData', f'fasta', file.filename)
            # fasta_iter += 1
        elif file.filename.find('karyotype') >= 0:  # for improvement
            config.set('MetaData', 'karyotype', file.filename)
        elif file.filename.find('gene_name') >= 0:  # for improvement
            config.set('MetaData', 'gene_name', file.filename)

    for file in files:
        for option in selected_options:
            if file.filename.find('snp') >= 0 and option == 'SNP':
                if file.filename.endswith('perc.txt'):
                    config.set('OverallPlotInfo', f'file_snp_perc', file.filename)
                elif file.filename.endswith('snp.txt'):
                    config.set('OverallPlotInfo', f'file_snp', file.filename)
            elif file.filename.find('ind') >= 0 and option == 'IND':
                if file.filename.endswith('perc.txt'):
                    config.set('OverallPlotInfo', f'file_ind_perc', file.filename)
                elif file.filename.endswith('ind.txt'):
                    config.set('OverallPlotInfo', f'file_ind', file.filename)
            elif file.filename.find('popGenome') >= 0 and option == 'P_DIV':
                config.set('OverallPlotInfo', f'file_p_div', file.filename)

    # Overwriting metadata.ini file:
    config_writer(meta_data, config)

    subprocess.run('./circos_project.sh', shell=True)
    return {"message": f"Successfuly uploaded... Circos generator task completed."}


# Access the form at 'http://0.0.0.0:8000/' from your browser
@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Only for testing purposes
#if __name__ == '__main__':
#    uvicorn.run(app, host='127.0.0.1', port=8000)
