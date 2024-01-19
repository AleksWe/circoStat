import logging
import sys
import textwrap

import plotting
import configparser


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


#def modification_starter(config):
#    logging.info("   INFO: starting modifications \n")
#    while True:
#        try:
#            plot_info = int(input("How many plots do you need: "))
#            # modification = int(input("Insert number: position (1), color (2): "))
#            break
#        except ValueError as e:
#            logging.error(f"   INFO: {e} - Not a valid value. Enter a number.")
#    #new_config = total_modifier(modification, circos_conf)
#    config_writer(new_config)


def plot_finder(circos_conf):
    new_string = circos_conf[circos_conf.find('<plot>'):circos_conf.find('<plot>')].strip()
    return new_string


def plot_generator(config):
    try:
        new_circos_conf = ''
        kariotype = config.get('MetaData', 'karyotype')
        try:
            plot_info = int(config.get('GeneralPlotData', 'number_of_plots'))
        except ValueError as e:
            logging.error(f"   INFO: {e} - Not a valid value. Enter a number.")
        new_circos_conf = 'karyotype = ' + kariotype + '\n' + '<<include ideogram.conf>>' + '\n'
        for i in range(plot_info):
            file = config.get('DetailPlotInfo', 'file')
            r1 = config.get('DetailPlotInfo', 'r1')
            r0 = config.get('DetailPlotInfo', 'r0')
            plotter = plotting.Plotter(file, r0, r1)
            new_plot = plotter.line_plotting()
            new_circos_conf += new_plot
        new_circos_conf += plotter.image_adder()
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


def config_reader(path):
    with open(path) as f:
        circos_conf = f.read()
    return circos_conf


def config_writer(new_config, name):
    with open(name, "w", newline="") as file:
        file.write(new_config)


def main():
    META_DATA = "metadata.ini"
    PATH = "circos.conf"

    create_logger()
    logging.info("   INFO: starting data reading")

    # circos_conf = config_reader(PATH)
    #modification_starter(configer)

    configer = meta_data(META_DATA)
    config_writer(plot_generator(configer), PATH)


if __name__ == '__main__':
    main()
