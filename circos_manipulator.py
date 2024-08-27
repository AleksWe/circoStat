import logging
import sys

import pandas as pd

import plotting as p
import configparser

# Selecting info about file names in config.ini
META_DATA = "metadata.ini"
# Path
PATH = "circos.conf"


def create_logger():
    # Create a handler
    log = logging.getLogger('test')
    handler = logging.StreamHandler(sys.stdout)
    log.addHandler(handler)
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def meta_data(META_DATA):
    configParser = configparser.RawConfigParser()
    configParser.read(META_DATA)
    return configParser


def plot_finder(circos_conf):
    new_string = circos_conf[circos_conf.find('<plot>'):circos_conf.find('<plot>')].strip()
    return new_string


def all_min_max_returner(file):
    # TODO: function as a class function
    df = pd.read_csv(file, sep='\s+', header=None)
    min_value, max_value = df[3].min(), df[3].max()
    # TODO: round value to the smallest possible value (f.ex. when min=1, round to 0; when max=426, round to 430
    return min_value, max_value


def option_checker_w_plotting(config, section, option,new_circos_conf,r0,r1, color, starting_point, type):
    file_name = config.get(section, option)
    min_value, max_value = all_min_max_returner(file_name)
    plotter = p.Plotter(file=file_name)
    if type == 'line':
        new_circos_conf += plotter.line_plotting(r0=r0, r1=r1, min_val=min_value, max_val=max_value, color=color)
    elif type == 'scatter':
        new_circos_conf += plotter.scatter_plotting(r0=r0, r1=r1, min_val=min_value, max_val=max_value, color=color)
    else:
        new_circos_conf += plotter.bar_plotting(r0=r0, r1=r1, min_val=min_value, max_val=max_value, color=color)
    starting_point -= 0.110
    r0, r1 = f'{round(starting_point, 3)}r', f'{round(starting_point + 0.10, 3)}r'
    return new_circos_conf, r0, r1, starting_point


def plot_generator(config):
    try:
        new_circos_conf = ''
        karyotype = config.get('MetaData', 'karyotype')
        new_circos_conf += p.Plotter.karyotype_adder(karyotype)
        new_circos_conf += p.Plotter.ideogram_adder()
        new_circos_conf += p.Plotter.plot_starter()
        starting_point = 0.895
        r0, r1 = f'{starting_point}r', f'{starting_point + 0.100}r'
        # For much needed improvement!!! ε=ε=ε=┏(゜ロ゜;)┛
        # TODO: add checker for file - there must be 3 plots for snp, 3 for ind, 1 for p_div
        if config.has_option('MetaData', 'gene_name'):
            file_name = config.get('MetaData', 'gene_name')
            plotter_one = p.Plotter(file=file_name)
            new_circos_conf += plotter_one.name_plotter()
        #if config.has_option('OverallPlotInfo', 'file_snp'):
        #    file_name = config.get('OverallPlotInfo', 'file_snp')
        #    min_value, max_value = all_min_max_returner(file_name)
        #    plotter = p.Plotter(file=file_name)
        #    new_circos_conf += plotter.line_plotting(r0=r0, r1=r1, min_val=min_value, max_val=max_value, color='vvdred')
        #    starting_point -= 0.100
        #    r0, r1 = f'{starting_point}r', f'{starting_point + 0.100}r'
        #if config.has_option('OverallPlotInfo', 'file_snp_mt'):
        #    file_name = config.get('OverallPlotInfo', 'file_snp_mt')
        #    min_value, max_value = all_min_max_returner(file_name)
        #    plotter = p.Plotter(file=file_name)
        #    new_circos_conf += plotter.scatter_plotting(r0=r0, r1=r1, min_val=min_value, max_val=max_value, color='vvdred')
        #    starting_point -= 0.100
        #    r0, r1 = f'{starting_point}r', f'{starting_point + 0.100}r'
        #if config.has_option('OverallPlotInfo', 'file_snp_perc'):
        #    plotter = p.Plotter(file=config.get('OverallPlotInfo', 'file_snp_perc'))
        #    new_circos_conf += plotter.bar_plotting(r0=r0, r1=r1)
        #    starting_point -= 0.100
        #    r0, r1 = f'{starting_point}r', f'{starting_point + 0.100}r'
        #if config.has_option('OverallPlotInfo', 'file_ind'):
        #    plotter = p.Plotter(file=config.get('OverallPlotInfo', 'file_ind'))
        #    new_circos_conf += plotter.line_plotting(r0=r0, r1=r1)
        #    starting_point -= 0.100
        #    r0, r1 = f'{starting_point}r', f'{starting_point + 0.100}r'
        #    new_circos_conf += plotter.scatter_plotting(r0=r0, r1=r1)
        #    starting_point -= 0.100
        #    r0, r1 = f'{starting_point}r', f'{starting_point + 0.100}r'
        #if config.has_option('OverallPlotInfo', 'file_ind_perc'):
        #    plotter = p.Plotter(file=config.get('OverallPlotInfo', 'file_ind_perc'))
        #    new_circos_conf += plotter.bar_plotting(r0=r0, r1=r1)
        #    starting_point -= 0.100
        #    r0, r1 = f'{starting_point}r', f'{starting_point + 0.100}r'
        #if config.has_option('OverallPlotInfo', 'file_p_div'):
        #    plotter = p.Plotter(file=config.get('OverallPlotInfo', 'file_p_div'))
        #    new_circos_conf += plotter.line_plotting(r0=r0, r1=r1)
        #    starting_point -= 0.100
        #    r0, r1 = f'{starting_point}r', f'{starting_point + 0.100}r'
        if config.has_option('OverallPlotInfo', 'file_snp'):
            new_circos_conf, r0, r1, starting_point = option_checker_w_plotting(config,'OverallPlotInfo','file_snp',new_circos_conf,r0,r1,'red',starting_point, type='line')
        if config.has_option('OverallPlotInfo', 'file_snp_mt'):
            new_circos_conf, r0, r1, starting_point = option_checker_w_plotting(config,'OverallPlotInfo','file_snp_mt',new_circos_conf,r0,r1,'red',starting_point, type='scatter')
        if config.has_option('OverallPlotInfo', 'file_snp_perc'):
            new_circos_conf, r0, r1, starting_point = option_checker_w_plotting(config, 'OverallPlotInfo', 'file_snp_perc', new_circos_conf, r0, r1, 'red',
                                      starting_point, type='bar')
        if config.has_option('OverallPlotInfo', 'file_ind'):
            new_circos_conf, r0, r1, starting_point = option_checker_w_plotting(config, 'OverallPlotInfo', 'file_ind', new_circos_conf, r0, r1, 'blue',
                                      starting_point, type='line')
        if config.has_option('OverallPlotInfo', 'file_ind_mt'):
            new_circos_conf, r0, r1, starting_point = option_checker_w_plotting(config, 'OverallPlotInfo', 'file_ind_mt', new_circos_conf, r0, r1, 'blue',
                                      starting_point, type='scatter')
        if config.has_option('OverallPlotInfo', 'file_ind_perc'):
            new_circos_conf, r0, r1, starting_point = option_checker_w_plotting(config, 'OverallPlotInfo', 'file_ind_perc', new_circos_conf, r0, r1, 'blue',
                                      starting_point, type='bar')
        if config.has_option('OverallPlotInfo', 'file_p_div'):
            new_circos_conf, r0, r1, starting_point = option_checker_w_plotting(config, 'OverallPlotInfo', 'file_p_div', new_circos_conf, r0, r1, 'green',
                                      starting_point, type='line')
        new_circos_conf += p.Plotter.plot_ender()
        new_circos_conf += p.Plotter.image_adder()
        return new_circos_conf
    except configparser.NoSectionError as e:
        logging.error(f"   INFO: {e} - Not a valid value. Validate meta_data.ini data.")


def position_modifier(circos_conf):
    logging.info("   INFO: starting position modifications \n")
    new_string = plot_finder(circos_conf)
    return circos_conf


def config_writer(new_config, name):
    with open(name, "w", newline="") as file:
        file.write(new_config)


def main():
    # Calling function to log every step of the way
    # create_logger()
    # logging.info("   INFO: starting data reading")

    # Creating config variable that holds all names from META_DATA
    config = meta_data(META_DATA)

    # Write a newly generated circos.conf to file
    config_writer(plot_generator(config), PATH)


if __name__ == '__main__':
    main()
