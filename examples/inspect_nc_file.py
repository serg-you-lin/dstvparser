from pathlib import Path
from dstvparser.parsers.nc_file_parser import NCFileParser

if __name__ == '__main__':
    data_dir = Path(__file__).parent / "data"
    nc_path = data_dir /"516_AK_test_UPN 200.nc_N°8 pz.nc"

    if nc_path.exists():
        print("File found!")
    else:
        print("File NOT found!")

    part_nc = NCFileParser(str(nc_path))
    profile = part_nc.parse()

    header = profile.get_header()
    print(header)

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