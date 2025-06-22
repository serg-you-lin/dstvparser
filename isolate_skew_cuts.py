from pathlib import Path
import shutil
from DSTVParser.parsers.factory import *

# Cartella con i file NC
folder = Path(r"Examples/files")

# Lista per tenere traccia dei profili con tagli inclinati
inclined_profiles = []

# Itera sui file NC
for file_path in folder.glob("*.nc"):
    try:
        # Parser e profilo
        parser = NCFileParserFactory.create_parser(str(file_path))
        profile = parser.parse()
        dimensions = profile.get_header()
        
        # Skip sheet metal
        if dimensions['profile_type'] == 'B':
            continue
            
        # Verify there are inclined cuts
        has_flange_cut = profile.flange_skew_cut()
        has_web_cut = profile.web_skew_cut()
        
        # If at elast 1 inclined cut
        if has_flange_cut or has_web_cut:
            output_folder = folder.parent / 'Inclined cuts'
            inclined_profiles.append(dimensions)  # Save profile info
        else:
            output_folder = folder.parent / 'Straights'
            
        # Create folder e copy file
        output_folder.mkdir(exist_ok=True)
        shutil.copy2(file_path, output_folder / file_path.name)
        
    except Exception as e:
        print(f"Error with {file_path.name}: {e}")

# Print info on skew cuts profiles
print(f"\nFound {len(inclined_profiles)} profiles with inclined cut:")
for profile in inclined_profiles:
    print(f"- {profile['code_profile']} (ID: {profile['piece_id']})")
