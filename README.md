# DSTV Reader
DSTV Reader is a Python library for parsing and analyzing DSTV files commonly used in the structural steel industry.
It allows easy extraction of profile information, detection of inclined cuts, and basic automation of file classification.

## Features
Parse DSTV files and extract profile headers and geometry

Support both .nc and .nc1 files

Detect inclined cuts on flanges and webs

Allowing classification and sorting files based on detected features

Modular structure: easy to extend or integrate into larger workflows

## Clone the repository:

```bash
git clone https://github.com/serg-you-lin/DSTVParser.git
```

## Requirements

- Python 3.9+

## Development notes
This project is under active development.
Some features related to NC1 profiles are currently incomplete due to the lack of available sample files for proper development and testing. Contributions or example files are welcome to help expand support.

# How to Use
## Basic example
```bash
from DSTVParser import NCFileParser

nc_file = "your_file.nc"
parser = NCFileParser(str(nc_file))
profile = parser.parse()

print(profile.get_header())
```

## Example use case: Split Profiles by feature
One common use case is to split NC profiles based on profile type or specific geometric characteristics, such as the presence of holes or inclined cuts.

```bash
from DSTVParser import NCFileParser

input_folder = "your_folder"
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
```

This script:
- Scans a folder containing .nc files
- Parses each file using the NCFileParser
- Checks for inclined flange/web cuts
- Copies the file into either the Inclined cuts or Straights folder, accordingly,  
  allowing for organized separation and easier management of files based on their geometric features for further processing or review.

## Inspection scripts
"exaples" folder contains manual inspections scripts used during the develop. They are not automatic tests.

## License
MIT License — feel free to use, modify, and share with attribution.

## Contributions
Pull requests are welcome! If you find issues or have suggestions, please open an issue in the repository.

## Author
Federico Sidraschi https://www.linkedin.com/in/federico-sidraschi-059a961b9/
