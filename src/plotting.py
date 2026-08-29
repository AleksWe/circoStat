class CircosConfBuild:
    """
    General circos.conf modifications builder.
    :meta_data: config file with file names information
    :lines: empty storage for new modified configuration
    """

    def __init__(self, metadata):
        self.metadata = metadata
        self.lines = []

    @staticmethod
    def plots_starter():
       return f'\n<plots>\n\n'

    @staticmethod
    def plots_ender():
       return '\n</plots>\n\n'

    @staticmethod
    def coordinates_setter(r0):
        return round(r0 - 0.100, 3), round(r0, 3)

    def add(self, text):
        self.lines.append(text)

    def build(self):
        return "\n".join(self.lines)

class Plotter:
    """
    A single plot section in a Circos configuration.
    :chart_type: type of Circos plot
    :file_name: name of file with plot configuration
    :r0: inner radius of the plot
    :r1: outer radius of the plot
    :kwargs: additional plot-specific Circos parameters
    """

    def __init__(self, chart_type, file_name, r0, r1, color,**kwargs):
        self.type = chart_type
        self.file_name = file_name
        self.r0 = r0
        self.r1 = r1
        self.color = color
        self.options = kwargs

    @staticmethod
    def gene_name_plot():
        plot = f"""
        <plot>
        type       = text
        color      = black
        label_font = default
        label_size = 42p
        
        file  = results/gene_name.txt
        
        r0 = 1r
        r1 = 1.3r
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
        return plot

    def create_plot(self):
        plot = ["<plot>",
                f"    type = {self.type}",
                f"    file = results/{self.file_name}",
                f"    r0 = {self.r0}",
                f"    r1 = {self.r1}",
                f"    color = {self.color}"
                ]

        for key, value in self.options.items():
            plot.append(f"    {key} = {value}")

        plot.append("</plot>")

        return "\n".join(plot)