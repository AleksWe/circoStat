import os
import shutil

import gffpandas.gffpandas as gffpd
from pathlib import Path

def file_finder(path):
    """
    Find a .gff/.gff3 file in the current directory
    :return: .gff/.gff3 file in a dataframe form
    """
    if os.path.exists(path):
        for file in Path(path).iterdir():
            if file.suffix in ['.gff3','.gff']:
                return gffpd.read_gff3(file)
    raise FileNotFoundError("No result directory or annotation (.gff3, .gff) found.")

def select_attribute(annotation_file, attribute, to_columns=True):
    """
    Read annotation and select feature for Circos-compatible track generation.
    """
    selected = annotation_file.filter_feature_of_type([attribute])
    if selected.df.empty:
        raise ValueError("No features found for length detection")
    if to_columns:
        selected = selected.attributes_to_columns()
    return selected

def create_gene_name(annotation_file, path):
    """
    Generate a Circos-compatible gene_name.txt file based on genome length.
    """
    genes = select_attribute(annotation_file, 'gene')
    df_genes = genes[['seq_id', 'start', 'end', 'Name']]
    df_genes.to_csv(f'{path}gene_name.txt', index=False, sep=' ', header=None)
    return

def create_highlight(annotation_file, path):
    """
    Generate a Circos-compatible highlight.txt file based on genome length.
    """
    genes = select_attribute(annotation_file, 'gene')
    df_highlight = genes[['seq_id', 'start', 'end']]
    df_highlight.to_csv(f'{path}highlights.txt', index=False, sep=' ', header=None)
    return

def create_karyotype(annotation_file, path):
    """
    Generate a Circos-compatible karyotype.txt file based on genome length.
    """
    selected = annotation_file.df
    data = f'chr - {selected.seq_id[0]} 1 {selected.start.min()} {selected.end.max()} grey'
    with open(f'{path}karyotype.txt', "w") as text_file:
        text_file.write(data)
    return

if __name__ == '__main__':
    annotation = file_finder()
    create_gene_name(annotation)
    create_highlight(annotation)
    create_karyotype(annotation)
