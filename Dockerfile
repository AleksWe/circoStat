#### R
# Base R image
# FROM rocker/r-base:latest

#### Ubuntu with Julia
# Use the official Ubuntu image
FROM ubuntu:jammy
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
#RUN apt-get install --assume-yes git && apt-get update && apt-get clean all \

# Set the work directory
WORKDIR /usr/src/app

# Install necessary packages (git, python, curl, wget)
RUN apt-get update && \
    apt-get install --assume-yes git python3 python3-pip wget curl build-essential \
    libcurl4-openssl-dev libssl-dev libxml2-dev libfontconfig1-dev \
    libblas-dev liblapack-dev gfortran libpcre2-dev liblzma-dev libbz2-dev


### Installing R and R packages
ARG R_VERSION=4.3.1
ENV PATH /opt/R/${R_VERSION}/bin:$PATH

# Install R
RUN wget -q https://cdn.rstudio.com/r/ubuntu-2204/R-${R_VERSION}-ubuntu-2204.tar.gz -O /tmp/R-${R_VERSION}.tar.gz && \
    mkdir -p /opt/R && \
    tar zx -C /opt/R -f /tmp/R-${R_VERSION}.tar.gz && \
    rm /tmp/R-${R_VERSION}.tar.gz

# Install littler (provides install2.r command)
RUN /opt/R/${R_VERSION}/bin/R -e "install.packages('littler', repos='https://cloud.r-project.org')" && \
    ln -s /opt/R/${R_VERSION}/lib/R/library/littler/bin/r /usr/local/bin/install2.r    

# Install R packages using install.packages in R
RUN /opt/R/${R_VERSION}/bin/R -e "install.packages(c('spider', 'ape'), repos='https://cloud.r-project.org')"

# Clean up package lists to reduce image size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*


## Julia and Chloe:
# Install Julia
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.3-linux-x86_64.tar.gz && \
    tar -xvzf julia-1.9.3-linux-x86_64.tar.gz && \
    mv julia-1.9.3 /opt/julia && \
    ln -s /opt/julia/bin/julia /usr/local/bin/julia
#RUN curl -fsSL https://install.julialang.org | sh -s -- --yes

# Install Julia packages
#RUN julia -e 'using Pkg; Pkg.add(["HTTP", "CSV", "DataFrames"])'

# Cloning Chloe repository and mandatory Chleo references
RUN git clone https://github.com/ian-small/chloe && \
    git clone --depth 1 https://github.com/ian-small/chloe_references

# Change directory to chloe, run `Pkg.instantiate()` to install dependencies based on the Project.toml file
#RUN julia -e 'import Pkg; Pkg.instantiate()'
RUN cd chloe && julia --project=. -e 'using Pkg; Pkg.instantiate();' && cd ..

# Set the work directory
#WORKDIR /usr/src/app

# Copy folder files to current directory
COPY . .

# Install mamba solver for python venv
RUN wget -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/download/24.3.0-0/Miniforge3-24.3.0-0-Linux-x86_64.sh"
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
