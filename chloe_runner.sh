#!/bin/bash

# Change directory to chloe
cd chloe

# Annotate consensus and generate file in .gff format:
julia --project=. chloe.jl annotate --gff *.fasta

# Copy generated file to main directory, remove lingering fasta files:
cp *.gff3 *.fasta *.fa ../
rm *.fasta *.fa
cd ..