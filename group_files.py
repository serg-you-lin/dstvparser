from pathlib import Path
from DSTVParser.parsers.nc_file_parser import NCFileParser

input_folder = Path("Examples/files")
sets_by_type = {}

for file_path in input_folder.glob("*.nc"):
    try:
        parser = NCFileParser(str(file_path))
        profile = parser.parse()
        profile_type = profile.code_profile

        if profile_type not in sets_by_type:
            sets_by_type[profile_type] = []

        sets_by_type[profile_type].append(file_path.name)

    except Exception as e:
        print(f"Failed to process {file_path.name}: {e}")

# Print grouped profiles
for profile_type, files in sets_by_type.items():
    print(f"{profile_type}:", len(files))
    # for file_name in files:
    #     print(f"  - {file_name}")
