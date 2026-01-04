from pathlib import Path
from dstvparser.parsers.nc1_file_parser import NC1FileParser

if __name__ == '__main__':
    data_dir = Path(__file__).parent / "data"
    nc1_path = data_dir / "2501.nc1"

    if nc1_path.exists():
        print("File found!")
    else:
        print("File NOT found!")
    
        
    part_nc1 = NC1FileParser(nc1_path)
    profile = part_nc1.parse()
    header = profile.get_header()
    print(header)

    print('Tipologia profilo: ', profile.profile_type)

    print('Does profile have holes?? ', profile.has_holes())
    print('Does profile have slots?? ', profile.has_slots())

    print("Dimensions: ", profile.dimensions)

    print("Material: ", profile.material)
    
    top_flange = profile.o_contour
    bottom_flange = profile.u_contour
    front_web = profile.v_contour
    behind_web = profile.h_contour

    print(f"Top flange points: {top_flange}.")
    print(f"Bottom flange points: {bottom_flange}.")
    print(f"Front web points: {front_web}.")
    print(f"Behind web points: {behind_web}.")