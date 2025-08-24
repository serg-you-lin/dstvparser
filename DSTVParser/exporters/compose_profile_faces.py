from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from DSTVParser.utils.profile_schemas import PROFILE_SCHEMAS

class ComposeProfileFaces:
    """Classe per convertire un oggetto NCPart in facce plottabili"""
    
    def __init__(self, nc_part, offset_between_faces: float = 0):
        """Inizializza con un oggetto NCPart"""
        self.part = nc_part
        self.profile_type = nc_part.profile_type
        self
        
        # Colori predefiniti per le facce
        self.face_colors = {
            'o': 1,  # Rosso
            'u': 5,  # Blu
            'v': 3,  # Verde
            'h': 6   # Ciano
        }
        
        # Ottieni i nomi delle facce dallo schema
        self.face_names = self._get_face_names_for_profile()
        
        # Inizializza le facce basandoti sui nomi disponibili per questo profilo
        self.faces = self._initialize_faces()
        
        # Calcola gli offset predefiniti per il posizionamento delle facce
        self.calc_default_offsets(offset_between_faces=offset_between_faces)
        
        # Compone le facce
        self.compose_faces()
        
    def _get_face_names_for_profile(self):
        """
        Ottiene i nomi delle facce per il tipo di profilo corrente.
        
        Returns:
            dict: Dizionario con i nomi delle facce per il profilo corrente
        """
        schema = PROFILE_SCHEMAS.get(self.profile_type)
        faces = schema.get('faces', {}) if schema else {}
        # print(f"Profilo: {self.profile_type}, Facce: {faces}")
        return faces
       
    
    def _initialize_faces(self):
        """
        Inizializza le facce basandoti sui nomi disponibili per questo profilo.
        
        Returns:
            dict: Dizionario delle facce inizializzate
        """
        faces = {}
        
        # Inizializza solo le facce definite nello schema per questo profilo
        for face_key, face_name in self.face_names.items():
            faces[face_key] = {
                'name': face_name,
                'color': self.face_colors.get(face_key, 1),  # Colore predefinito se non trovato
                'contour': [],
                'holes': [],
                'slots': [],
                'notches': []
            }
        
        return faces

    def _clamp_web_contour_if_needed(self, face_key: str, contour: list) -> list:
        """
        Se il profilo è di tipo I e la faccia è il web ('v'),
        ritaglia il contorno eliminando le parti sopra/sotto le flange.
        """
        if not contour:
            return []
        
        # Applichiamo solo ai profili I e solo al web
        if self.profile_type.upper().startswith("I") and face_key == "v":
            dims = self.part.dimensions
            profile_height = dims.get("profile_height")
            flange_thickness = dims.get("flange_thickness")
        
            
            if profile_height and flange_thickness:
                y_coords = [pt[1] for pt in contour]
                min_y, max_y = min(y_coords), max(y_coords)

                bottom_limit = min_y + flange_thickness
                top_limit = max_y - flange_thickness

                clamped = [
                (pt[0], min(max(pt[1], bottom_limit), top_limit), pt[2] if len(pt) > 2 else 0)
                for pt in contour
                ]
                
                return clamped
            
        return list(contour)


    def get_available_faces(self):
        """
        Restituisce le chiavi delle facce disponibili per il profilo corrente.
        
        Returns:
            list: Lista delle chiavi delle facce disponibili
        """
        return list(self.faces.keys())
    
    def get_face_height(self, face_key: str) -> float:
        """
        Calcola l'altezza (Y max - Y min) del contorno della faccia.
        Se il contorno è vuoto, restituisce una altezza di default.
        """
        face = self.faces.get(face_key, {})
        contour = face.get('contour', [])

        if not contour:
            return 200.0  # fallback di sicurezza

        y_coords = [pt[1] for pt in contour]
        return max(y_coords) - min(y_coords)


    def calc_default_offsets(self, offset_between_faces):
        """Calcola gli offset predefiniti per le facce"""
        # Prende le dimensioni del profilo
        web_height = self.part.dimensions.get('web_height', 300)
        flange_width = self.part.dimensions.get('flange_width', 300)
        
        length = self.part.length

        face_heights = {
            'o': self.get_face_height('o'),
            'u': self.get_face_height('u'),
            'v': self.get_face_height('v'),
            'h': self.get_face_height('h'),
        }

        y_cursor = 0
        self.offsets = {}

        for face_key in ['o', 'u', 'v', 'h']:
            self.offsets[face_key] = (0, y_cursor)
            y_cursor -= offset_between_faces
        
    def get_offsets(self):
        """Restituisce gli offset calcolati per le facce"""
        return self.offsets
        
    def compose_faces(self):
        """Estrae i contorni dalle facce dell'NCPart e li aggiunge alla struttura delle facce"""
        
        # Mappa dei contorni dell'NCPart
        part_contours = {
            'o': getattr(self.part, 'o_contour', []),
            'u': getattr(self.part, 'u_contour', []),
            'v': getattr(self.part, 'v_contour', []),
            'h': getattr(self.part, 'h_contour', [])
        }

        # Aggiungi contorni alle rispettive facce
        for face_key in self.faces.keys():
            if face_key in part_contours:
                raw_contour = part_contours[face_key]
                self.faces[face_key]['contour'] = self._clamp_web_contour_if_needed(face_key, raw_contour)
            else:
                self.faces[face_key]['contour'] = []
                print(f"Warning: Contorno per faccia '{face_key}' non trovato nell'NCPart")


        # Aggiungi fori alle rispettive facce
        for hole in self.part.holes:
            if hole.face in self.faces:
                self.faces[hole.face]['holes'].append(hole)
        
        # Aggiungi asole alle rispettive facce
        for slot in self.part.slots:
            if slot.face in self.faces:
                self.faces[slot.face]['slots'].append(slot)
        
        # Aggiungi notch (intagli) se presenti
        if hasattr(self.part, 'notches'):
            for notch in self.part.notches:
                if notch.face in self.faces:
                    self.faces[notch.face]['notches'].append(notch)
    
    def get_face(self, face_key):
        """Restituisce una specifica faccia con tutti i suoi elementi"""
        if face_key in self.faces:
            return self.faces[face_key]
        return None
    
    def get_all_faces(self):
        """Restituisce tutte le facce"""
        return self.faces
    
    def get_face_with_features(self, face_key):
        """Restituisce una faccia completa di contorno, fori e asole"""
        if face_key not in self.faces:
            return None
            
        face = self.faces[face_key]
        return {
            'name': face['name'],
            'color': face['color'],
            'contour': face['contour'],
            'holes': face['holes'],
            'slots': face['slots'],
            'notches': face['notches']
        }
    
    def has_features(self, face_key):
        """Verifica se una faccia ha caratteristiche (contorno, fori, asole, intagli)"""
        if face_key not in self.faces:
            return False
            
        face = self.faces[face_key]
        return (len(face['contour']) > 0 or 
                len(face['holes']) > 0 or 
                len(face['slots']) > 0 or
                len(face['notches']) > 0)
    
    def get_dimensions(self, face_key=None):
        """Calcola le dimensioni di una faccia o di tutte le facce"""
        if face_key is not None:
            # Restituisce le dimensioni di una faccia specifica
            if face_key not in self.faces or not self.faces[face_key]['contour']:
                return None
                
            contour = self.faces[face_key]['contour']
            
            # Estrai le coordinate x e y dal contorno
            x_coords = [point[0] for point in contour]
            y_coords = [point[1] for point in contour]
            
            # Calcola larghezza e altezza
            width = max(x_coords) - min(x_coords) if x_coords else 0
            height = max(y_coords) - min(y_coords) if y_coords else 0
            
            return {
                'width': width,
                'height': height,
                'min_x': min(x_coords) if x_coords else 0,
                'max_x': max(x_coords) if x_coords else 0,
                'min_y': min(y_coords) if y_coords else 0,
                'max_y': max(y_coords) if y_coords else 0
            }
        else:
            # Restituisce le dimensioni di tutte le facce
            dims = {}
            for key in self.faces:
                dims[key] = self.get_dimensions(key)
            return dims
    
    def get_contour_points(self, face_key, with_offset=False):
        """Estrae i punti del contorno, opzionalmente con offset applicato"""
        if face_key not in self.faces:
            return []
            
        contour = self.faces[face_key]['contour']
        
        if with_offset:
            offset_x, offset_y = self.offsets[face_key]
            return [(p[0] + offset_x, p[1] + offset_y, p[2]) for p in contour]
        
        return contour
    
    def get_features_for_exporting(self, face_key=None, with_offset=False):
        """Prepara i dati per la manipolazione di una o tutte le facce"""
        result = {}
        
        # Funzione per applicare offset ai punti di un contorno
        def apply_offset(points, offset):
            return [(p[0] + offset[0], p[1] + offset[1], p[2] if len(p) > 2 else 0) for p in points]
        
        # Funzione per estrarre solo coordinate X e Y da una lista di punti
        def extract_xy(points):
            return [(p[0], p[1]) for p in points]
        
        if face_key is not None:
            # Prepara i dati per una faccia specifica
            if face_key not in self.faces:
                return {}
                
            face = self.faces[face_key]
            offset = self.offsets[face_key] if with_offset else (0, 0)
            
            # Prepara contorni
            contour_points = face['contour']
            if with_offset:
                contour_points = apply_offset(contour_points, offset)
            
            # Prepara fori
            holes_data = []
            for hole in face['holes']:
                hole_x = hole.x + offset[0] if with_offset else hole.x
                hole_y = hole.y + offset[1] if with_offset else hole.y
                holes_data.append({
                    'center': (hole_x, hole_y),
                    'diameter': hole.diameter,
                    'type': hole.hole_type
                })
            
            # Prepara asole
            slots_data = []
            for slot in face['slots']:
                slot_x = slot.x + offset[0] if with_offset else slot.x
                slot_y = slot.y + offset[1] if with_offset else slot.y
                slots_data.append({
                    'center': (slot_x, slot_y),
                    'diameter': slot.diameter,
                    'cc_distance': slot.cc_distance,
                    'angle': slot.angle,
                    'length': slot.length
                })
            
            result[face_key] = {
                'name': face['name'],
                'color': face['color'],
                'contour': extract_xy(contour_points),
                'holes': holes_data,
                'slots': slots_data,
                'offset': offset
            }
        else:
            # Prepara i dati per tutte le facce
            for key in self.faces:
                result.update(self.get_features_for_exporting(key, with_offset))
        
        return result