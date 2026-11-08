
#### Ubuntu with Julia
# Use the official Ubuntu image
FROM ubuntu:jammy
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV R_VERSION=4.4.1 DEBIAN_FRONTEND=noninteractive \
    R_HOME=/usr/local/lib/R LD_LIBRARY_PATH=/usr/local/lib/R/lib \
    TZ=Etc/UTC \
    LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install necessary packages (git, python, curl, wget, r-base)
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    --assume-yes ca-certificates git python3 python3-pip wget curl build-essential \
    libcurl4-openssl-dev libssl-dev libxml2-dev libfontconfig1-dev \
    libblas-dev liblapack-dev gfortran libpcre2-dev liblzma-dev libbz2-dev  \
    libreadline-dev xorg-dev libxml2-dev libcairo2-dev libsqlite3-dev libmariadbd-dev libpq-dev libssh2-1-dev unixodbc-dev libsodium-dev \
    pkg-config libharfbuzz-dev libfribidi-dev libfreetype6-dev libpng-dev libuv1-dev \
    tzdata r-base r-base-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# R PACKAGES FROM packages.txt

# Download and install R
RUN wget -c https://cran.r-project.org/src/base/R-4/R-${R_VERSION}.tar.gz \
    && tar -xf R-${R_VERSION}.tar.gz \
    && cd R-${R_VERSION} \
    && ./configure --enable-R-shlib\
    && make -j$(nproc) \
    && make install \
    && cd .. \
    && rm -rf R-${R_VERSION} R-${R_VERSION}.tar.gz

# Put your project exactly where it is outside Docker
WORKDIR /circoStat

# Copy your entire repo into /project
COPY . /circoStat

# Install renv
#RUN Rscript -e "install.packages('renv', repos='https://cloud.r-project.org')"

# Create a clean renv project
#RUN mkdir -p renv && \
#    Rscript -e "renv::activate()"

# Copy only the package requirements and installer
COPY packages.txt install_packages.R ./

# Install packages (parallel install)
RUN Rscript -e 'stopifnot(as.character(getRversion()) == "4.4.1")' \
    && Rscript /circoStat/install_packages.R

# Generate renv.lock from installed packages
#RUN Rscript -e "renv::snapshot(prompt = FALSE)"

# Install CRAN packages
#RUN R -e "install.packages(c('spider','ape','ff','gtools'), repos='https://cloud.r-project.org')"

# Install Bioconductor packages
#RUN R -e "BiocManager::install(c('Biostrings','msa'), ask=FALSE)"

# Install archived PopGenome
#RUN R -e "install.packages( \
#    'https://cran.r-project.org/src/contrib/Archive/PopGenome/PopGenome_2.7.5.tar.gz', \
#    repos=NULL, \
#    type='source' \
#)"

# Clean up package lists to reduce image size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

## Julia and Chloe:
# Install Julia
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.3-linux-x86_64.tar.gz && \
    tar -xvzf julia-1.9.3-linux-x86_64.tar.gz && \
    mv julia-1.9.3 /opt/julia && \
    ln -s /opt/julia/bin/julia /usr/local/bin/julia

RUN julia -e 'using Pkg; Pkg.add(["BioSequences", "BioAlignments"])'

RUN git clone https://github.com/ian-small/chloe /circoStat/chloe && \
    cd /circoStat/chloe && git checkout 27aac371ce341de0649a5106f3c18a96df4bcf3a

RUN git clone https://github.com/ian-small/chloe_references /circoStat/chloe_references && \
    cd /circoStat/chloe_references && git checkout 37e68271a7af1f799c5b8bcc3781d7abec071f2a

RUN cd /circoStat/chloe && julia --project=. -e 'using Pkg; Pkg.instantiate();'

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
RUN mamba create -n circos python=3.13
RUN echo "mamba activate circos" >> /root/.bashrc

# Install all required packages and dependencies
RUN pip install -r /circoStat/requirements.txt
RUN mamba install -n circos -c bioconda perl-list-moreutils perl-params-validate perl-clone -y
RUN mamba install -n circos -c bioconda perl-gd circos=0.69 -y

# Expose the port that FastAPI will run on
EXPOSE 8000

# Chmod files
RUN chmod +x /circoStat/chloe_runner.sh

# Command to run your application
CMD ["bash", "-c", "source activate circos && uvicorn src.fast_api_starter:app --host 0.0.0.0 --port 8000 --no-access-log"]
