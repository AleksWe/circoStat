class Config:
    ALIGNMENT_FILE = 'Alignment.fasta'
    CONSENSUS_FILE = 'consensus.fasta'
    TMP_PATH = '../tmp/'
    PY_SCRIPTS_PATH = '../src/'
    RESULT_PATH = '../results/'
    CHLOE_PATH = '../chloe/'
    META_DATA = "metadata.ini"
    R_SCRIPTS = {
        'prepare': '../R/prepare_circos_data.R',
        'snp': '../R/get_snp_profiles.R',
        'pdiv': '../R/calculate_pop_stats.R',
        'nuc_div': '../R/run_spider.R'
    }