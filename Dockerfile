
#### Ubuntu with Julia
# Use the official Ubuntu image
FROM ubuntu:jammy

ENV R_VERSION=4.4.1 DEBIAN_FRONTEND=noninteractive \
    R_HOME=/usr/local/lib/R LD_LIBRARY_PATH=/usr/local/lib/R/lib \
    TZ=Etc/UTC \
    LANG=C.UTF-8 LC_ALL=C.UTF-8

# Make tmp dir for R installation
RUN mkdir -p /tmp && chmod 1777 /tmp

# Install necessary packages (git, python, curl, wget, r-base)
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    ca-certificates git python3 python3-pip wget curl build-essential \
    libcurl4-openssl-dev libssl-dev libxml2-dev libfontconfig1-dev zlib1g-dev\
    libblas-dev liblapack-dev gfortran libpcre2-dev liblzma-dev libbz2-dev  \
    libreadline-dev xorg-dev libcairo2-dev libsqlite3-dev libmariadb-dev libpq-dev libssh2-1-dev unixodbc-dev libsodium-dev \
    pkg-config libharfbuzz-dev libfribidi-dev libfreetype6-dev libpng-dev libuv1-dev \
    tzdata \
    #r-base r-base-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# R PACKAGES FROM packages.txt

# Download and install R
RUN cd /tmp && \
    wget -q -c https://cran.r-project.org/src/base/R-4/R-${R_VERSION}.tar.gz && \
    tar -xf R-${R_VERSION}.tar.gz && \
    cd R-${R_VERSION} && \
    ./configure --enable-R-shlib && \
    make -j"$(nproc)" && \
    make install && \
    cd / && \
    rm -rf /tmp/R-${R_VERSION} /tmp/R-${R_VERSION}.tar.gz

# Put your project exactly where it is outside Docker
WORKDIR /circoStat

# Copy your entire repo into /project
COPY . /circoStat

# Install packages (parallel install)
RUN Rscript -e 'stopifnot(as.character(getRversion()) == "4.4.1")' \
    && Rscript /circoStat/install_packages.R

# Clean up package lists to reduce image size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

## Julia and Chloe:
# Install Julia
RUN wget -q -O /tmp/julia.tar.gz \
    https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.3-linux-x86_64.tar.gz && \
    tar -xzf /tmp/julia.tar.gz -C /opt && \
    mv /opt/julia-1.9.3 /opt/julia && \
    ln -s /opt/julia/bin/julia /usr/local/bin/julia && \
    rm /tmp/julia.tar.gz

RUN julia -e 'using Pkg; Pkg.add(["BioSequences", "BioAlignments"])'

RUN git clone https://github.com/ian-small/chloe /circoStat/chloe && \
    cd /circoStat/chloe && git checkout 27aac371ce341de0649a5106f3c18a96df4bcf3a

RUN git clone https://github.com/ian-small/chloe_references /circoStat/chloe_references && \
    cd /circoStat/chloe_references && git checkout 37e68271a7af1f799c5b8bcc3781d7abec071f2a

RUN cd /circoStat/chloe && julia --project=. -e 'using Pkg; Pkg.instantiate();'

# Copy folder files to current directory
COPY . .

# Install mamba solver for python venv
RUN wget -q -O /tmp/Miniforge3.sh \
    https://github.com/conda-forge/miniforge/releases/download/24.3.0-0/Miniforge3-24.3.0-0-Linux-x86_64.sh && \
    bash /tmp/Miniforge3.sh -b -p /opt/conda && \
    rm /tmp/Miniforge3.sh

# Add conda to PATH
ENV PATH="/opt/conda/bin:${PATH}"

# Create and activate a mamba environment
#RUN mamba create -n circos #-f package-list.txt
RUN mamba create -n circos -c conda-forge python=3.13 pip -y
#RUN echo "source activate circos" >> /root/.bashrc

# Install all required packages and dependencies
RUN mamba install -n circos -c conda-forge -c bioconda  \
    perl-list-moreutils perl-params-validate perl-clone perl-gd \
    circos=0.69 -y
RUN mamba run -n circos python -m pip install --no-cache-dir -r /circoStat/requirements.txt

# Expose the port that FastAPI will run on
EXPOSE 8000

# Chmod files
RUN chmod +x /circoStat/chloe_runner.sh

# Command to run your application
#CMD ["bash", "-c", "source activate circos && uvicorn src.fast_api_starter:app --host 0.0.0.0 --port 8000 --no-access-log"]
CMD ["conda", "run", "--no-capture-output", "-n", "circos", "uvicorn", "src.fast_api_starter:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
