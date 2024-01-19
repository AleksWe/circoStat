import textwrap


class Plotter:

    def __init__(self, file, r0, r1):
        self.file = file
        self.r1 = r1
        self.r0 = r0

    def name_plotter(self):
        result =

    def line_plotting(self):
        result = f"""<plot>\n\nshow  = yes\ntype  = line\n\n
                file  = {self.file}
                r1    = {self.r1}
                r0    = {self.r0}
                max   = 1.0
                min   = 0.0
                glyph            = rectangle
                glyph_size       = 8
                color            = red
                stroke_color     = dred
                stroke_thickness = 1\n\n</plot>\n\n
        """
        result = result.replace(' ', '')
        return result

    def image_adder(self):
        result = f"""<image>\n<<include etc/image.conf>>\n</image>\n\n<<include etc/colors_fonts_patterns.conf>>\n<<include etc/housekeeping.conf>>
        """
        return result
