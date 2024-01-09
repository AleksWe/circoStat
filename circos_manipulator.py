import logging
import sys

PATH = "circos.conf"


def config_reader(path):
    with open(path) as f:
        circos_conf = f.read()
    return circos_conf


def config_writer(new_config):
    with open("new_circos.conf", "w", newline="") as file:
        file.write(new_config)


def total_modifier(modification, circos_conf):
    if modification == 1:
        new_config = position_modifier(circos_conf)
        return new_config
    elif modification == 2:
        new_config = color_modifier(circos_conf)
        return new_config


def modification_starter(circos_conf):
    logging.info("   INFO: starting modifications \n")
    while True:
        try:
            modification = int(input("Insert number: position (1), color (2): "))
            break
        except ValueError as e:
            logging.error(f"   INFO: {e} - Not a valid value. Enter a number.")
    new_config = total_modifier(modification, circos_conf)
    config_writer(new_config)


def plot_finder(circos_conf):
    new_string = circos_conf[circos_conf.find('<plot>'):circos_conf.find('<plot>')].strip()
    return new_string


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


def create_logger():
    # Create a handler
    log = logging.getLogger('test')
    handler = logging.StreamHandler(sys.stdout)
    log.addHandler(handler)
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def main():
    create_logger()
    logging.info("   INFO: starting data reading")
    circos_conf = config_reader(PATH)
    modification_starter(circos_conf)


if __name__ == '__main__':
    main()
