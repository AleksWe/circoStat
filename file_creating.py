import os
import gffpandas.gffpandas as gffpd
import pandas as pd


def file_finder():
    # Get the current working directory
    current_dir = os.getcwd()

    # Find a .gff3 file in the current directory
    for file in os.listdir(current_dir):
        if file.endswith(".gff3") or file.endswith(".gff"):
            gff3_file = os.path.join(current_dir, file)
            annotation = gffpd.read_gff3(gff3_file)
            return annotation
    return None


def create_gene_and_highlight(annotation):
    genes = annotation.filter_feature_of_type(['gene'])
    genes = genes.attributes_to_columns()
    # Create gene_name.txt:
    df_genes = genes[['seq_id', 'start', 'end', 'Name']]
    df_genes.to_csv('gene_name.txt', index=False, sep=' ', header=None)

    # Create highlight.txt:
    df_highlight = genes[['seq_id', 'start', 'end']]
    df_highlight['background_color'] = 'fill_color=vvlgrey,r0=0.20r,r1=1.10r'
    df_highlight.to_csv('highlights.txt', index=False, sep=' ', header=None)
    return


def create_karyotype_snv(annotation):
    data = annotation.attributes_to_columns()
    data = data.iloc[0]
    data = f'chr - {data.seq_id} cp {data.start} {data.end} chrcp'
    with open('karyotype_SNV.txt', "w") as text_file:
        text_file.write(data)
    return


def main():
    annotation = file_finder()
    create_gene_and_highlight(annotation)
    create_karyotype_snv(annotation)


main()
