class Config:
    ALIGNMENT_FILE = 'Alignment.fasta'
    CONSENSUS_FILE = 'consensus.fasta'
    R_PATH = 'R'
    TMP_PATH = 'tmp'
    PY_SCRIPTS_PATH = 'src'
    RESULT_PATH = 'results'
    CHLOE_PATH = 'chloe'
    CHLOE_RUNNER_SCRIPT = 'chloe_runner.sh'
    META_DATA = "metadata.ini"
    SECTION_FOR_META = "FilesConfig"
    CIRCOS_CONF_TEMPLATE = "templates/circos.conf.template"
    ALIGNMENT_R_SCRIPT = 'run_custom_alignment.R'
    R_SCRIPTS = {
        'prepare': 'prepare_circos_data.R',
        'snp': 'get_snp_profiles.R',
        'pdiv': 'calculate_pop_stats.R',
        'nuc_div': 'run_spider.R'
    }
    OPTION_MAP = {'SNP':'snp_track.txt',
                  'P_DIV':'pop_track_',
                  'NUC_DIV':'spider_track_'}
    ALL_TEMPORARY = [TMP_PATH, RESULT_PATH]