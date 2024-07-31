import logging
import sys
from subprocess import Popen, PIPE
import plotting as p
import configparser
import os


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

# def total_modifier(modification, circos_conf):
#     if modification == 1:
#         new_config = position_modifier(circos_conf)
#         return new_config
#     elif modification == 2:
#         new_config = color_modifier(circos_conf)
#         return new_config


def plot_finder(circos_conf):
    new_string = circos_conf[circos_conf.find('<plot>'):circos_conf.find('<plot>')].strip()
    return new_string


def plot_generator(config):
    try:
        new_circos_conf = ''
        kariotype = config.get('MetaData', 'karyotype')
        try:
            plot_info = int(config.get('OverallPlotInfo', 'number_of_plots'))  # for GUI it shouldn't be possible not to write a number
        except ValueError as e:                                                # f.ex it could be checked out on frontend side
            logging.error(f"   INFO: {e} - Not a valid value. Enter a number.")
            sys.exit(0)
        new_circos_conf += p.Plotter.kariotype_adder(kariotype)
        new_circos_conf += p.Plotter.ideogram_adder()
        new_circos_conf += p.Plotter.plot_starter()
        plotter_one = p.Plotter(file=config.get('MetaData', 'gene_name'))
        new_circos_conf += plotter_one.name_plotter()
        for i in range(1, plot_info+1):
            file = config.get('OverallPlotInfo', f'file{i}')
            r1 = config.get('OverallPlotInfo', f'r1{i}')
            r0 = config.get('OverallPlotInfo', f'r0{i}')
            plotter = p.Plotter(file, r0, r1)
            if config.get('OverallPlotInfo', f'plot_type{i}') == 'line':
                new_plot = plotter.line_plotting()
            if config.get('OverallPlotInfo', f'plot_type{i}') == 'scatter':
                new_plot = plotter.scatter_plotting()
            # if config.get('OverallPlotInfo', f'plot_type{i}') == 'bar':
            #     new_plot = plotter.bar_plotting()
            new_circos_conf += new_plot
        new_circos_conf += p.Plotter.plot_ender()
        new_circos_conf += p.Plotter.image_adder()
        return new_circos_conf
    except configparser.NoSectionError as e:
        logging.error(f"   INFO: {e} - Not a valid value. Validate meta_data.ini data.")


def position_modifier(circos_conf):
    logging.info("   INFO: starting position modifications \n")
    new_string = plot_finder(circos_conf)
    return circos_conf


def color_modifier(circos_conf):
    logging.info("   INFO: starting color modifications \n")
    what_color = input("What color would you like")
    new_string = plot_finder(circos_conf)
    if what_color == 'blue':
        new_color = " blue"
        modified_string = new_string.replace("color      = black", "color      = blue")
        modified_conf = circos_conf.replace(new_string, modified_string)
    return circos_conf


#def config_reader(path):
#    with open(path) as f:
#        circos_conf = f.read()
#    return circos_conf


def config_writer(new_config, name):
    with open(name, "w", newline="") as file:
        file.write(new_config)


def main():
    # Calling function to log every step of the way
    create_logger()
    #logging.info("   INFO: starting data reading")

    # Creating config variable that holds all names from META_DATA
    config = meta_data(META_DATA)

    # Generating .txt files from .R script for config.ini
    #files = [config.get('MetaData', 'fasta1'), config.get('MetaData', 'fasta2')]

    # Write a newly generated circos.conf to file
    config_writer(plot_generator(config), PATH)

    # modification_starter(configer)


if __name__ == '__main__':
    main()
