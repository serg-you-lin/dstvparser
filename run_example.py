from DSTVParser.parsers.nc_file_parser import *

file_path = r"Examples\553.nc"
# file_path = r"Examples\722.nc"
# file_path = r"Examples\4026.nc"

part_nc = NCFileParser(file_path)
profile = part_nc.parse()
header = profile.get_header()
print(header)

top_flange = profile.o_contour
print(f"Top flange points: {top_flange}.")


# Query on holes
if profile and profile.has_holes():
    print("\nHoles details:")
    for hole in profile.holes:
        print(f"Hole type {hole.hole_type}: x={hole.x}, y={hole.y}, diameter={hole.diameter}, "
            f"hole_type={hole.Hole_type}, face={hole.face}"
            f"{f', depth={hole.depth}' if hole.hole_type == 'countersink' else ''}")

if profile:
# Bases analysis
    if profile.has_holes():
        print("Profile has holes")
    
    if profile.has_slots():
        print("Profile has slot")

    if profile.has_worked_areas():
        print('Profile has worked areas')
    
    # Total resume
    summary = profile.get_features_summary()
    print(f"Resume features: {summary}")
    
    # Analysis on each face
    holes_by_face = profile.get_holes_by_face()
    for face, holes in holes_by_face.items():
        print(f"Face {face}: {len(holes)} holes")
    
    # profile dimensions
    print(f"Dimensions: ",profile.dimensions)

    holes = profile.has_holes()
    print('Does profile have holes?', holes)
    
    inclined_flange = profile.flange_skew_cut()
    print('Has inclined cut on flange?', inclined_flange)
    inclined_web = profile.web_skew_cut()
    print("Has inclined cut on web?", inclined_web)