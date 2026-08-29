class Config:
    ALIGNMENT_FILE = 'Alignment.fasta'
    CONSENSUS_FILE = 'consensus.fasta'
    TMP_PATH = '../tmp/'
    PY_SCRIPTS_PATH = '../src/'
    RESULT_PATH = '../results/'
    CHLOE_PATH = '../chloe/'
    META_DATA = "metadata.ini"
    SECTION_FOR_META = "FilesConfig"
    CIRCOS_CONF_TEMPLATE = "../templates/circos.conf.template"
    R_SCRIPTS = {
        'prepare': '../R/prepare_circos_data.R',
        'snp': '../R/get_snp_profiles.R',
        'pdiv': '../R/calculate_pop_stats.R',
        'nuc_div': '../R/run_spider.R'
    }
    OPTION_MAP = {'SNP':'snp_track.txt',
                  'P_DIV':'pop_track_',
                  'NUC_DIV':'spider_track_'}
    ALL_TEMPORARY = [TMP_PATH, RESULT_PATH]