import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from DSTVParser.parsers.factory import NCFileParserFactory
from DSTVParser.exporters.compose_profile_faces import ComposeProfileFaces
from DSTVParser.exporters.profile_plotter import ProfilePlotter

if __name__ == '__main__':
    base_dir = os.path.dirname(__file__) 
    parent_dir = os.path.dirname(base_dir)
    nc_path = os.path.join(parent_dir, "Examples", "722.nc")

    if os.path.exists(nc_path):
        print("File trovato!")
    else:
        print("File NON trovato!")
        
    nc_part = NCFileParserFactory.create_parser(nc_path)
    profile = nc_part.parse()

    profile_faces = ComposeProfileFaces(profile)
    plotter = ProfilePlotter(profile_faces)
    # plotter.plot_face('o')
    plotter.plot_all_faces()
    plotter.show()
    # plotter.save('profile_plot.png')

    