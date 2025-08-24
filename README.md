# DSTV Reader
DSTV Reader is a Python library for parsing and analyzing DSTV files commonly used in the structural steel industry.
It allows easy extraction of profile information, detection of inclined cuts, and basic automation of file classification.

## Features
Parse DSTV files and extract profile headers and geometry

Support both .nc and .nc1 files

Detect inclined cuts on flanges and webs

Allowing classification and sorting files based on detected features

Modular structure: easy to extend or integrate into larger workflows

Plotting profie faces with features with Matplotlib

Exporting DFX files of profile faces

## Clone the repository:

```bash
git clone https://github.com/serg-you-lin/DSTVParser.git
```

## Requirements

- Python 3.9+
- Required libraries listed in `requirements.txt`

Install all dependencies with:

```bash
pip install -r requirements.txt
```
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
For a complete example, see RunExample.py.

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

You can find an example of such usage in:
```bash
isolate_skew_cuts.py
```
This script:
- Scans a folder containing .nc files
-Parses each file using the NCFileParser
-Checks for inclined flange/web cuts
-Copies the file into either the Inclined cuts or Straights folder, accordingly

You can export dxf files from profile faces, and plotting them as well. New implementation of interactive plotting (measurement allowed)
Take a look on these examples:
```bash
plotting_faces.py
interactive_plotting.py
dxf_exporter.py
```

## License
MIT License — feel free to use, modify, and share with attribution.

## Contributions
Pull requests are welcome! If you find issues or have suggestions, please open an issue in the repository.

## Author
Federico Sidraschi https://www.linkedin.com/in/federico-sidraschi-059a961b9/
