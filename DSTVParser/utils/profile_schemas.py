PROFILE_SCHEMAS = { # 'I' profiles 
    'I': {
        'fields': ['profile_height', 'flange_width', 'flange_thickness', 'web_thickness'],
        'indices': {'NC1': [10, 11, 12, 13], 'NC': [9, 10, 11, 12]},
        'faces': {
            'o': 'Top Flange',
            'u': 'Bottom Flange',
            'v': 'Web'
        }                
    },                           
    'U': {  # 'U' profiles
        'fields': ['profile_height', 'flange_width', 'thickness'],
        'indices': {'NC1': [10, 11, 12], 'NC': [9, 10, 11]},
        'faces': {
            'o': 'Top Flange',
            'u': 'Bottom Flange',
            'v': 'Web'
        }
    },
    'L': {   # Angle profiles
        'fields': ['width', 'height', 'thickness'],
        'indices': {'NC1': [10, 11, 12], 'NC': [9, 10, 11]},
        'faces': {
            'u': 'Side #1',
            'v': 'Front Side #2'
        }
    },
    'B': {    # Sheets/Plates
        'fields': ['lenght', 'width', 'thickness'],
        'indices': {'NC1': [], 'NC': [8, 9, 12]},
        'faces': {
            'v': 'Plate'
        }
    },
    'RU': {   # Rounds bars
        'fields': [],
        'indices': {'NC1': [], 'NC': []},
        'faces': {}
    },
    'RO': {   # Rounded Tube
        'fields': ['radious', 'thickness'],
        'indices': {'NC1': [], 'NC': [9, 10]},
        'faces': {}
    },
    'M': {    # Rectangular tube
        'fields': ['side_1_size', 'side_2_size', 'thickness'],
        'indices': {'NC1': [], 'NC': [9, 10, 11]},
        'faces': {
            'o': 'Top Side #1',
            'u': 'Bottom Side #1',
            'v': 'Front Side #2',
            'h': 'Behind  Side #2'
        }
    },
    'C': {    #   'C' Profiles
        'fields': ['flange_width', 'web_height', 'thickness'],
        'indices': {'NC1': [], 'NC': [9, 10, 11]},
        'faces': {
            'o': 'Top Flange',
            'u': 'Bottom Flange',
            'v': 'Web'
        }
    },
    'T': {    # 'T' Profiles
        'fields': ['flange_width', 'web_height', 'flange_thickness', 'web_thickness'],
        'indices': {'NC1': [], 'NC': [9, 10, 11, 12]},
        'faces': {
            'o': 'Front Web',
            'h': 'Top flange'
        }
    }
}


if __name__ == "__main__":
    profile_type = 'U'     # ad esempio 'I', 'U', 'L', ecc.
    file_type = 'NC'       # 'NC' oppure 'NC1'

    schema = PROFILE_SCHEMAS.get(profile_type)
    if schema is None:
        raise ValueError(f"Profilo '{profile_type}' non riconosciuto")

    fields = schema.get('fields', [])
    indices = schema.get('indices', {}).get(file_type, [])
    faces = schema.get('faces', {})

    print("Fields:", fields)
    print("Indices:", indices)
    print("Faces:", faces)