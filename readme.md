# AutoCircos project

## Program goal
Automatic generation of Circos for visualisation of genomic data based on 
raw FASTA files containing nucleic acid sequences.

## Overall program flow
The program contains a single docker image, which consists of:
   - **Dockerfile**:
     - create Python and R virtual environments,
     - install all necessary libraries and dependencies,
     - activate python env and expose a service at localhost with port 8000 by starting a *fast_api_starter.py* script;
   - **fast_api_starter.py** - a FastAPI framework starter that reads a request from user and activates the *circos_project.sh*;
   - **circos_project.sh** - cascade launching of R, Python and Circos scripts;
   - **R script**, that generates text file containing the start and end position on the genome;
   - **metadata.ini** - configuration file with all information needed for Circos: names, number of charts, chart types and position - modified based on user input;
   - **Python scripts**:
     - **circos_manipulator.py** - main script that generates and modifies the circos.conf file
     - **plotting.py** - class with methods for circos.conf modifications (start and end of chart, parameters, chart type)
   - **circos files** originally acquired from the Circos project and based on the documentation provided

## Detailed program flow
1) Insert FASTA files (containing nucleoid acids sequences) via API served by FastAPI framework. 
The API can be accessed at http://0.0.0.0:8000/ from your browser. After selecting all options click the *SUBMIT* button.
2) The *fast_api_stater.py* analyses the data passed by the user and runs the *circos_project.sh*
3) The R script, that adjusts the passed FASTA files for the circos visualisation, is triggered.
4) Running the main program (circos_manipulator.py), which generates the circos.conf file
5) Based on the generated circos file, the previously created *circos virtual environment* generated the visualisation
6) Using the docker command, copy a created visualisation on your local memory/disc

## Prerequisites
Docker on Linux

## Installation
1) Use the ______ image provided ***here***.
2) After installing Docker on your Linux, 
   - Use the following command to run the docker image:
   ```docker
   docker run -it --name circos_docker_v2 -p 8000:8000 circos_docker_v2
   ```
   - Access API at http://0.0.0.0:8000/. After selecting all options, click on the **submit** button.
   - After getting the final "circos.png created" message at your terminal, copy created visualisation from docker to
   your local directory (at current path).
   ```docker
   docker cp circos_docker_v2:circos.png circos.png
   ```

## Contributing
Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
