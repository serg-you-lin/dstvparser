from typing import List, Optional
import re
import os
from DSTVParser.parsers.dstv_file_parser import DSTVFileParser
from DSTVParser.models.nc_part import NCPart
from DSTVParser.utils.utilities import *
from DSTVParser.utils.profile_schemas import PROFILE_SCHEMAS


class NC1FileParser(DSTVFileParser):
    """Parser per file NC1 con formato differente"""
    def parse(self) -> Optional[NCPart]:
        """Metodo di parsing del file NC1"""
        self.log(f"\nInizio parsing del file NC1: {self.filename}")
        try:
            with open(self.filename, 'r') as file:
                lines = file.readlines()
            
            header_data = []
            in_header = False
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                code = line[:2]
                self.log(f"Processo linea NC1: '{line}' (codice: {code})")
                
                if code == 'ST':  # Esempio di codice diverso per l'header
                    in_header = True
                    continue
                
                if in_header:
                    if code in ['BO', 'AK', 'SI', 'EN']:  # Esempi di sezioni diverse
                        in_header = False
                        self._create_profile_from_header(header_data)
                        self.log("Ho creato il profilo", section='header')
                        self.log(f"Profilo creato: {self.current_profile}", section='header')
                    else:
                        header_data.append(line)
                        continue

                # Gestione sezioni specifiche del formato NC1
                if code == 'BO': 
                    current_section = 'BO' 
                    continue
                elif code == 'AK':  # Contours - equivalente all'AK
                    current_section = 'AK'
                    continue
                elif code == 'SI':  # Markings - equivalente al SI
                    current_section = 'SI'
                    continue
                elif code == 'EN':
                    self.log("Fine file NC1")
                    break

                # Parsing del contenuto (adattato al formato NC1)
                if current_section == 'BO':
                    self._parse_bo_line(line)
                elif current_section == 'AK':
                    self._parse_ak_line(line)
                elif current_section == 'SI':
                    self._parse_si_line(line)
            
            return self.current_profile
            
        except Exception as e:
            self.log(f"ERRORE durante il parsing NC1: {e}")
            import traceback
            self.log(traceback.format_exc())
            # Restituisci il profilo corrente se esiste, altrimenti None
            return self.current_profile if hasattr(self, 'current_profile') and self.current_profile else None

    def _create_profile_from_header(self, header_lines: List[str]):
        """Crea il profilo dai dati dell'header per file NC1"""
        try:
            self.log("\nCreazione profilo da header NC1:", section='header')
            
            file_type = 'NC1'
            profile_type = header_lines[8]
            self.log(f"Tipo di profilo: {profile_type}", section='header')          
            
            schema = PROFILE_SCHEMAS.get(profile_type)
            if schema is None:
                raise ValueError(f"Profilo '{profile_type}' non riconosciuto")
        

            # Ottieni i nomi delle dimensioni e gli indici corrispondenti
            fields = schema.get('fields', [])
            indices = schema.get('indices', {}).get(file_type, [])

            # Crea dizionario dimensioni leggendo i valori dall’header
            dimensions = {
                name: float(header_lines[idx].split(',')[0].strip())  # Pulisce valori tipo "1000,0"
                for name, idx in zip(fields, indices)
            }

            
            self.current_profile = NCPart(
                order_id=header_lines[1],
                piece_id=header_lines[2],  
                material=header_lines[5],
                quantity=int(header_lines[3]),
                profile_type=profile_type,
                code_profile=header_lines[7],
                length=float(header_lines[9].split(',')[0]),  
                dimensions=dimensions
            )
            
            self.log(f"Creato profilo NC1 tipo {profile_type}: {self.current_profile.code_profile}")
            self.log(f"Dimensioni: {dimensions}", section='header')

        except Exception as e:
            self.log(f"ERRORE nella creazione del profilo NC1: {e}")
            raise

    def _parse_holes(self, line: str) -> bool:
        self.log(f"Profilo corrente in _parse_holes: {self.current_profile}", section='BO')
        """Parser dedicato per i fori (5 valori dopo BO)"""
        parts = line.split()
        # Log dettagliato per debug
        for i, part in enumerate(parts):
            self.log(f"Parte {i}: '{part}'", section='BO')

        if len(parts) != 4:  # face + x + y + diam + type
            self.log(f"Non è un foro: attesi 4 valori, trovati {len(parts)}", section='BO')
            return False
        
        try:
            face = parts[0]
            x = convert_to_float(parts[1])
            y = convert_to_float(parts[2])
            diameter = convert_to_float(parts[3])
            
            self.log(f"Valori convertiti: face='{face}', x={x}, y={y}, diameter={diameter}", section='BO')
            #self.current_profile.add_hole(x, y, diameter, face)
            self.current_profile.add_hole(x, y, diameter, tipologia = 'normal', face=face)
            self.log(f"Aggiunto foro: x={x}, y={y}, diameter={diameter}, face={face}", section='BO')
            return True
        except ValueError:
            return False

    def _parse_slots(self, line: str) -> bool:
        """Parser dedicato per le asole"""
        self.log("Not yet implemented")
        return
        
    def _parse_contour(self, line: str) -> bool:
        """Parser dedicato per i punti del contorno (4 valori dopo AK)"""
        parts = line.split()

        self.log(f"Split parts: {parts}", section='AK')
        if len(parts) < 4:
            self.log("Line too short, expected at least 4 parts.", section='AK')
            return False
            
        try:
            if parts[0] in ['v', 'o', 'u', 'h']:
                if self.current_points and self.current_face_type:
                    face = self.current_face_type

                self.current_face_type = parts[0]
                face = self.current_face_type
                self.current_points = []
                x = convert_to_float(parts[1])
                y = convert_to_float(parts[2])
                angle = convert_to_float(parts[3])

            else:
                face = self.current_face_type
                x = convert_to_float(parts[0])
                y = convert_to_float(parts[1])
                angle = convert_to_float(parts[2])

            
            self.current_profile.add_contour_points(face, [(x, y, angle)])
            self.log(f"Aggiunto punto contorno: face={face}, x={x}, y={y}, angle={angle}", section='AK')
            return True
        except ValueError:
            return False

    def _parse_bo_line(self, line: str):
        """Gestisce le linee dopo BO (fori e asole)"""
        if not self.current_profile:
            self.log("ATTENZIONE: current_profile è None in _parse_bo_line", section='BO')
            return
            
        # Prima prova a parsare come asola (ha più parametri)
        if self._parse_slots(line):
            return
            
        # Se non è un'asola, prova a parsare come foro
        if self._parse_holes(line):
            return
            
        self.log(f"Linea BO non riconosciuta: {line}", section='BO')


    def _parse_ak_line(self, line: str):
        """Gestisce le linee dopo AK (contorni)"""
        if not self.current_profile:
            return
            
        if self._parse_contour(line):
            return
            
        self.log(f"Linea AK non riconosciuta: {line}", section='AK')
        
    def _parse_si_line(self, line: str):
        """Gestisce le linee dopo SI (marcature)"""
        self.log(f"Ignorata linea SI: {line}")
        pass  # Per ora ignoriamo le marcature


if __name__ == '__main__':
    

    base_dir = os.path.dirname(__file__) 
    parent_dir = os.path.dirname(base_dir)
    nc1_path = os.path.join(parent_dir, "Examples", "2501.nc1")

    if os.path.exists(nc1_path):
        print("File found!")
    else:
        print("File NOT found!")
    
        
    part_nc1 = NC1FileParser(nc1_path)
    profile = part_nc1.parse()
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