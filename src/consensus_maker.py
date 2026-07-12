import sys
from collections import Counter
from Bio import AlignIO
from Bio.Data import IUPACData

def generate_consensus_fasta(path='../tmp',file='Alignment.fasta'):
    try:
        iupac_values = IUPACData.ambiguous_dna_values
        iupac_values.pop('X', None)
        alignment = AlignIO.read(f"{path}{file}", "fasta")
        consensus = ""
        for i in range(len(alignment[0])):
            alignment_column = alignment[:,i]
            counted_nuc = Counter([c for c in alignment_column if c != '-'])
            if counted_nuc:
                max_value = max(counted_nuc.values())
                most_common = ''.join([base for base, count in counted_nuc.items() if count == max_value])
                for value, key in iupac_values.items():
                    if set(most_common.upper()) == set(key):
                        consensus += value
                        break
            else:
                consensus += '-'

        return consensus
    except Exception as e:
        print("Error during consensus_maker.py run:", e)
        sys.exit()

def main():
    generate_consensus_fasta()

if __name__ == '__main__':
    main()