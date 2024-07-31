# Use the official Ubuntu image
FROM ubuntu:jammy
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Install necessary python packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget

# Base R image
FROM rocker/r-base:latest

# Copy folder files to current directory
COPY . .

# Install mamba solver for python venv
RUN wget -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-24.3.0-0-Linux-x86_64.sh"
RUN bash Miniforge3.sh -b -p /opt/conda && \
    rm Miniforge3.sh
    
# Add conda to the PATH
ENV PATH="/opt/conda/bin:${PATH}"

# Create and activate a mamba environment
#RUN mamba create -n circos #-f package-list.txt 
RUN mamba create -n circos
RUN echo "mamba activate circos" >> /root/.bashrc

# Install all required packages and dependencies
RUN pip install -r requirements.txt
RUN mamba install -c bioconda perl-list-moreutils perl-params-validate perl-clone
RUN conda install bioconda::perl-gd circos=0.69

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run your application
CMD ["bash", "-c", "source activate circos && uvicorn fast_api_starter:app --host 0.0.0.0 --port 8000"]