from DSTVParser.exporters.profile_dxf_exporter import ProfileDXFExporter
from DSTVParser.exporters.compose_profile_faces import ComposeProfileFaces
from DSTVParser.parsers.factory import NCFileParserFactory
import os


file_path = r"Examples\issue#1.nc1"
file_path = r"Examples\2519.nc1"

part_nc = NCFileParserFactory.create_parser(file_path)
profile = part_nc.parse()

# Getting folder path from file path
folder_path = file_path.rsplit('\\', 1)[0]  

# Generate profile faces
profile_faces = ComposeProfileFaces(profile)

# Create dxf exporter instance
exporter = ProfileDXFExporter(profile_faces)

#generate output file name based on input file name
base_name = os.path.basename(file_path)
if base_name.endswith((".nc1", ".nc")):
    output_file_name = os.path.splitext(base_name)[0]
else:
    raise ValueError("File extensione not supported")


# Esporting all faces to a DXF file (with face names as labels)
output_file = exporter.export_all_faces(os.path.join(folder_path, output_file_name), separate_files=True, add_labels=True)
print(f"File DXF completo generato: {output_file}")

# Exporting a specific face to a DXF file
# exporter.export_face('o', os.path.join(folder_path, "flangia_superiore.dxf"))

