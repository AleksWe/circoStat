#!/bin/bash

# Run python script to generate circos.conf
python3 circos_manipulator.py

# Run circos generator
circos --conf circos.conf

# Copy image in browser -- DOCELOWO KOPIOWANIE AUTOMATYCZNE, AKTUALNIE RĘCZNIE W INSTRUKCJI
#docker cp circos_docker:circos.png /circos_result /circos.png

