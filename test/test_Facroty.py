import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from DSTVParser.parsers.factory import NCFileParserFactory

if __name__ == '__main__':
    base_dir = os.path.dirname(__file__) 
    parent_dir = os.path.dirname(base_dir)
    nc_path = os.path.join(parent_dir, "Examples", "722.nc")
    nc1_path = os.path.join(parent_dir, "Examples", "2501.nc1")

    if os.path.exists(nc_path):
        print("File trovato!")
    else:
        print("File NON trovato!")
    if os.path.exists(nc1_path):
        print("File trovato!")
    else:
        print("File NON trovato!")
        
    nc_part = NCFileParserFactory.create_parser(nc_path)
    nc_profile = nc_part.parse()

    print('Profilo nc:')
    nc_header = nc_profile.get_header()
    print(nc_header)

    nc1_part = NCFileParserFactory.create_parser(nc1_path)
    nc1_profile = nc1_part.parse()

    print('Profilo nc1:')
    nc1_header = nc1_profile.get_header()
    print(nc1_header)