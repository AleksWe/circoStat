class Plotter:

    def __init__(self, file, r0='1r', r1='1.3r'):
        self.file = file
        self.r1 = r1
        self.r0 = r0

    @staticmethod
    def plot_starter():
        return f'\n<plots>\n\n'

    @staticmethod
    def plot_ender():
        return '\n</plots>\n\n'

    @staticmethod
    def ideogram_adder():
        return '<<include ideogram.conf>>' + '\n'

    @staticmethod
    def karyotype_adder(file):
        karyotype = file
        return 'karyotype = ' + karyotype + '\n'

    def name_plotter(self):
        result = f"""<plot>
            type       = text
            color      = black
            label_font = default
            label_size = 42p

            file  = {self.file}

            r0 = {self.r0}
            r1 = {self.r1}
            padding = 2p
            rpadding = 2p
            
            show_links     = yes
            link_dims	= 6p
            link_thickness = 2p
            link_color     = red
            label_snuggle  = yes
            max_snuggle_distance = 2r
            snuggle_tolerance = 0.5
            snuggle_sampling = 2
            </plot>
        """
        result = result.replace(' ', '')
        return result

    def scatter_plotting(self, r0, r1, min_val, max_val, color):
        result = f"""
            <plot>
            type	= scatter
            file    = {self.file}
            min     = {min_val}
            max     = {max_val}
            r0      = {r0}
            r1      = {r1}
            
            
            glyph            = circle
            glyph_size       = 20
            color            = vvd{color}
            stroke_color     = d{color}
            stroke_thickness = 1
            
            <axes>
            <axis>
            spacing   = 0.05r
            color     = lgrey
            thickness = 1
            
            </axis>
            </axes>
            
            </plot>
        """
        result = result.replace(' ', '')
        return result

    def line_plotting(self, r0, r1, min_val, max_val, color):
        result = f"""
            <plot>
            type	= line
            file    = {self.file}
            color   = vvd{color}
            min     = {min_val}
            max     = {max_val}
            r0      = {r0}
            r1      = {r1}
            thickness = 3

            <axes>
            <axis>
            spacing   = 0.05r
            color     = lgrey
            thickness = 1

            </axis>
            </axes>

            </plot>
        """
        result = result.replace(' ', '')
        return result

    def bar_plotting(self, r0, r1, min_val, max_val, color):
        result = f"""
            <plot>
            type	= histogram
            file    = {self.file}
            color   = vd{color}
            min  = {min_val}
            max  = {max_val}
            r0      = {r0}
            r1      = {r1}
            thickness = 3
            extend_bin  = no
            fill_color  = vvd{color}
            
            <axes>
            <axis>
            spacing   = 0.05r
            color     = lgrey
            thickness = 1

            </axis>
            </axes>

            </plot>
        """
        result = result.replace(' ', '')
        return result

    @staticmethod
    def image_adder():
        result = f"""<image>\n<<include etc/image.conf>>\n</image>\n\n<<include etc/colors_fonts_patterns.conf>>\n<<include etc/housekeeping.conf>>
        """
        return result

