import configparser

import src.plotting as p
from src.config import Config


def meta_data(path):
    """
    Read from metadata.ini file
    :param path: Path to metadata.ini file
    :return: config file
    """
    config_parser = configparser.RawConfigParser()
    config_parser.read(path)
    return config_parser


def circos_conf_writer(new_config, path):
    """
    Write a newly generated circos.conf to file
    :param new_config: modified circos.conf data
    :param path: path to file circos configuration file
    """
    with open(path, "w", newline="") as file:
        file.write(new_config)


def plot_generator(config_parser, section, starting_point = 0.895):
    new_circos = p.CircosConfBuild(config_parser)
    with open(Config.CIRCOS_CONF_TEMPLATE,'r') as file:
        template_circos_conf = file.read()
    new_circos.add(template_circos_conf)
    new_circos.add(new_circos.plots_starter())
    new_circos.add(p.Plotter.gene_name_plot())
    groups = {item.strip() for item in config_parser.get(section,"groups").split(",")}
    r0, r1 = starting_point, starting_point + 0.100
    if config_parser.has_option(section,'snp'):
        snp_plot = p.Plotter(chart_type='scatter',
                             file_name=config_parser.get(section,'snp'),
                             r0=f"{r0}r", r1=f"{r1}r", color="vvdred", glyph="circle", glyph_size="8p")
        new_circos.add(snp_plot.create_plot())
        r0, r1 = new_circos.coordinates_setter(r0)
    for prefix in ('p_div_', 'nuc_div_'):
        for name in groups:
            if config_parser.has_option(section, f'{prefix}{name}'):
                div_plot = p.Plotter(chart_type='line',
                                     file_name=config_parser.get(section,f'{prefix}{name}'),
                                     r0=f"{r0}r", r1=f"{r1}r", color="vvdred")
                new_circos.add(div_plot.create_plot())
                r0, r1 = new_circos.coordinates_setter(r0)
    new_circos.add(new_circos.plots_ender())
    circos_conf = new_circos.build()
    return circos_conf


def main():
    # Creating config variable that holds all names from META_DATA
    config = meta_data(Config.META_DATA)
    circos_conf_writer(plot_generator(config, Config.SECTION_FOR_META), '../circos.conf')


if __name__ == '__main__':
    main()
