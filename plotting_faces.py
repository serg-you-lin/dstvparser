from DSTVParser.exporters.profile_plotter import ProfilePlotter
from DSTVParser.exporters.compose_profile_faces import ComposeProfileFaces
from DSTVParser.parsers.nc_file_parser import *

file_path = r"Examples\722.nc"

part_nc = NCFileParser(file_path)
profile = part_nc.parse()

profile_faces = ComposeProfileFaces(profile)
plotter = ProfilePlotter(profile_faces)
# plotter.plot_face('o')
plotter.plot_all_faces()
plotter.show()
# plotter.save('profile_plot.png')







