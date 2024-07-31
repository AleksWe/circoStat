import configparser
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
    configParser = configparser.RawConfigParser()
    configParser.read(config)
    return configParser


def config_writer(meta_data, config):
    with open(meta_data, 'w') as configfile:
        config.write(configfile)


@app.post("/upload")
async def upload(request: Request,
                 files: List[UploadFile] = File(...)):
    # Read the form data from the request
    form_data = await request.form()

    # Extract the chart selections dynamically
    chart_data = {}
    for key, value in form_data.items():
        if key.startswith('chart'):
            chart_data[key] = value
    print(chart_data)

    # For now, we will just print the option and the file name
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

    if not config.has_section('FastaFiles'):
        config.add_section('FastaFiles')

    i = 1
    for file in files:
        config.set('FastaFiles', f'fasta{i}', file.filename)
        i += 1

    # Overwriting metadata.ini file:
    config_writer(meta_data, config)

    subprocess.run('./circos_project.sh', shell=True)
    return {"message": f"Successfuly uploaded. Circos generator proceeding..."}


# Access the form at 'http://0.0.0.0:8000/' from your browser
@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Only for testing purposes
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
