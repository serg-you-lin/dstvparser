from typing import List, Optional
from dstvparser.models.nc_part import NCPart

class DSTVFileParser:
    """Classe base per parser di file NC/NC1"""
    def __init__(self, filename: str):
        self.filename = filename
        self.current_profile = None
        self.current_face_type = None
        self.current_points = []
        self.debug = False
        self.log_sections = {
            'BO': False,
            'AK': False,
            'SI': False,
            'header': True,
            'default': True
        }

    def log(self, message: str, section: str = 'default'):
        if self.debug and self.log_sections.get(section, False):
            print(message)
            
    def parse(self) -> Optional[NCPart]:
        """Metodo principale di parsing del file - da implementare nelle sottoclassi"""
        raise NotImplementedError("Il metodo parse deve essere implementato nelle sottoclassi")
    
    def _create_profile_from_header(self, header_lines: List[str]):
        """Metodo base per creare profilo dall'header - potrebbe essere sovrascritto"""
        raise NotImplementedError("Metodo da implementare nelle sottoclassi")