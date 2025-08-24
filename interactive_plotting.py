from DSTVParser.exporters.interactive_plotter import InteractiveProfilePlotter
from DSTVParser.exporters.compose_profile_faces import ComposeProfileFaces
from DSTVParser.parsers.factory import NCFileParserFactory
from DSTVParser.parsers.nc_file_parser import *

file_path = r"Examples\2519.nc1"
#file_path = r"Examples\Issue#1.nc1"

part_nc = NCFileParserFactory.create_parser(file_path)
profile = part_nc.parse()

profile_faces = ComposeProfileFaces(profile, offset_between_faces=000)

plotter = InteractiveProfilePlotter(profile_faces)
fig = plotter.plot_all_faces(with_offset=True)
# fig = plotter.plot_face('o')
plotter.show(fig)

# plotter.save('profile_plot.png')







