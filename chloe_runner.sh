#!/bin/bash

RESULT_DIR="$1"
OPTION="$2"
ANNOTATE_PATH="$3"

# Change directory
cd "$ANNOTATE_PATH" || exit 1

# For generating annotation, annotate consensus and generate file in .gff format:
if [ "$OPTION" = "generate_annot" ]; then
  julia --project=. chloe.jl annotate --gff *.fasta || exit 1
fi

# Copy generated files to main directory, remove lingering fasta files:
cp *.gff3 "$RESULT_DIR" || exit 1
cd .. || exit 1