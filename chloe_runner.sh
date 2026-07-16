#!/bin/bash

RESULT_DIR="$1"

# Change directory to chloe
cd chloe

# Annotate consensus and generate file in .gff format:
julia --project=. chloe.jl annotate --gff *.fasta

# Copy generated files to main directory, remove lingering fasta files:
cp *.gff3 *.gff "$RESULT_DIR"
cd ..