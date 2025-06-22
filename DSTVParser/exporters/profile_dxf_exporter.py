from typing import List, Tuple, Dict, Optional, Union
import math
import ezdxf
from ezdxf.math import Vec2
from DSTVParser.utils.drawers import calculate_slot_points

class ProfileDXFExporter:
    """Classe per esportare un profilo e le sue facce in formato DXF"""
    
    def __init__(self, profile_faces):
        """
        Inizializza l'esportatore DXF con un oggetto ComposeProfileFaces
        
        Args:
            profile_faces: Oggetto ComposeProfileFaces contenente le facce del profilo
        """
        self.profile_faces = profile_faces
        self.doc = None
        self.modelspace = None
        self.colors = {
            1: (255, 0, 0),     # Rosso
            3: (0, 255, 0),     # Verde
            5: (0, 0, 255),     # Blu
            6: (0, 255, 255)    # Ciano
        }
        
        # Inizializza il documento DXF
        self._initialize_dxf()
    
    def _initialize_dxf(self):
        """Inizializza il documento DXF con le impostazioni di base"""
        self.doc = ezdxf.new('R2010')  # Usa un formato DXF moderno
        
        # Modifica lo stile di testo 'Standard' esistente invece di crearne uno nuovo
        if 'Standard' in self.doc.styles:
            standard_style = self.doc.styles.get('Standard')
            standard_style.dxf.font = 'arial.ttf'
        
        # Crea i layer colorati per ogni tipo di faccia
        layer_names = {
            'o': 'Flangia_Superiore',
            'u': 'Flangia_Inferiore',
            'v': 'Anima_Frontale',
            'h': 'Anima_Posteriore',
            'holes': 'Fori',
            'slots': 'Asole'
        }
        
        # Crea i layer nel documento DXF
        for face_key, layer_name in layer_names.items():
            if face_key in self.profile_faces.face_colors:
                color = self.profile_faces.face_colors[face_key]
                self.doc.layers.new(name=layer_name, dxfattribs={'color': color})
            else:
                self.doc.layers.new(name=layer_name)
        
        # Ottiene lo spazio modello per aggiungere entità
        self.modelspace = self.doc.modelspace()
    
    def _add_contour(self, contour_points: List[Tuple], layer_name: str):
        """
        Aggiunge un contorno al documento DXF come LWPOLYLINE
        
        Args:
            contour_points: Lista di tuple (x, y) rappresentanti il contorno
            layer_name: Nome del layer su cui disegnare il contorno
        """
        if not contour_points:
            return
            
        # Crea una polilina con i punti del contorno
        points = [(p[0], p[1]) for p in contour_points]
        
        # Chiude il contorno se necessario (controlla se il primo e l'ultimo punto coincidono)
        if points[0] != points[-1]:
            # Aggiungi il primo punto alla fine per chiudere il contorno
            points.append(points[0])
        
        # Aggiunge la polilina al modelspace sul layer specificato
        self.modelspace.add_lwpolyline(points, dxfattribs={'layer': layer_name})
    
    def _add_circle(self, center: Tuple[float, float], diameter: float, layer_name: str):
        """
        Aggiunge un cerchio al documento DXF
        
        Args:
            center: Tuple (x, y) rappresentante il centro del cerchio
            diameter: Diametro del cerchio
            layer_name: Nome del layer su cui disegnare il cerchio
        """
        self.modelspace.add_circle(center=center, radius=diameter/2, dxfattribs={'layer': layer_name})
    
    def _add_slot(self, center: Tuple[float, float], diameter: float, cc_distance: float, 
              angle: float, layer_name: str):
        """Aggiunge un'asola al documento DXF usando semicerchi"""
        # Usa cc_distance invece di length per essere coerente con show_slots
        center1, center2, radius, (p1, p2, p3, p4) = calculate_slot_points(center, diameter, cc_distance, angle)
        angle_rad = math.radians(angle)
        
        # Semicerchi invece di cerchi completi
        self.modelspace.add_arc(center=center1, radius=radius, 
                            start_angle=math.degrees(angle_rad + math.pi/2),
                            end_angle=math.degrees(angle_rad - math.pi/2),
                            dxfattribs={'layer': layer_name})
        
        self.modelspace.add_arc(center=center2, radius=radius,
                            start_angle=math.degrees(angle_rad - math.pi/2), 
                            end_angle=math.degrees(angle_rad + math.pi/2),
                            dxfattribs={'layer': layer_name})
        
        # Linee tangenti
        self.modelspace.add_line(start=p1, end=p2, dxfattribs={'layer': layer_name})
        self.modelspace.add_line(start=p3, end=p4, dxfattribs={'layer': layer_name})

    
    def _add_text(self, position: Tuple[float, float], text: str, height: float = 10, layer_name: str = 'Standard'):
        """
        Aggiunge testo al documento DXF
        
        Args:
            position: Tuple (x, y) rappresentante la posizione del testo
            text: Testo da aggiungere
            height: Altezza del testo
            layer_name: Nome del layer su cui aggiungere il testo
        """
        self.modelspace.add_text(
            text=text, 
            dxfattribs={
                'layer': layer_name,
                'height': height,
                'style': 'Standard'
            }
        ).set_pos(position, align='LEFT')
    
    def _add_face_to_dxf(self, face_key: str, with_offset: bool = False, add_labels: bool = True):
        """
        Metodo privato per aggiungere una singola faccia al documento DXF corrente
        
        Args:
            face_key: Chiave della faccia da aggiungere
            with_offset: Se True, usa gli offset per il posizionamento
            add_labels: Se True, aggiunge etichette con i nomi delle facce
        """
        # Ottieni i dati della faccia
        face_data = self.profile_faces.get_features_for_exporting(face_key, with_offset)
        if not face_data:
            return
            
        face = face_data[face_key]
        layer_name = self.profile_faces.face_names[face_key].replace(' ', '_')
        
        print(f"{face_key}: offset = {face['offset']}")
        
        # Verifica se il contorno è vuoto
        has_contour = face['contour'] and len(face['contour']) > 0
        
        # Aggiungi contorno se esiste
        if has_contour:
            self._add_contour(face['contour'], layer_name)
        else:
            # Se non c'è un contorno, aggiungi un messaggio nel DXF
            if with_offset:
                # Trova l'offset per il messaggio
                offsets = self.profile_faces.get_offsets()
                offset_x = offsets.get(face_key, {}).get('x', 0)
                offset_y = offsets.get(face_key, {}).get('y', 0)
                text_pos = (offset_x, offset_y)
            else:
                text_pos = (0, 0)
                
            self._add_text(
                text_pos, 
                f"La faccia '{face['name']}' non contiene un contorno", 
                height=15
            )
        
        # Aggiungi fori
        for hole in face['holes']:
            self._add_circle(hole['center'], hole['diameter'], 'Fori')
        
        # Aggiungi asole
        for slot in face['slots']:
            self._add_slot(
                slot['center'], 
                slot['diameter'], 
                slot['cc_distance'],
                slot['angle'], 
                'Asole'
            )
        
        # Aggiungi etichette se richiesto
        if add_labels:
            if has_contour:
                # Posiziona l'etichetta vicino all'angolo inferiore sinistro del contorno
                x_coords = [p[0] for p in face['contour']]
                y_coords = [p[1] for p in face['contour']]
                label_x = min(x_coords)
                label_y = min(y_coords) - 20
            else:
                # Se il contorno non esiste, posiziona l'etichetta a un punto predefinito
                if with_offset:
                    offsets = self.profile_faces.get_offsets()
                    label_x = offsets.get(face_key, {}).get('x', 0)
                    label_y = offsets.get(face_key, {}).get('y', 0) - 40
                else:
                    label_x = 0
                    label_y = -40
            
            # Aggiungi il nome della faccia
            self._add_text((label_x, label_y), face['name'], height=15)

    def export_face(self, face_key: str, file_path: Optional[str] = None, add_labels: bool = True):
        """
        Esporta una singola faccia in un file DXF
        """
        if face_key not in self.profile_faces.faces:
            raise ValueError(f"Faccia '{face_key}' non trovata")
            
        # Reinizializza il documento DXF per una nuova faccia
        self._initialize_dxf()
        
        # Usa il metodo privato per aggiungere la faccia
        self._add_face_to_dxf(face_key, with_offset=False, add_labels=add_labels)
        
        # Genera il nome del file se non specificato
        if file_path is None:
            face_data = self.profile_faces.get_features_for_exporting(face_key)
            face = face_data[face_key]
            file_path = f"{face['name'].replace(' ', '_')}.dxf"
        
        # Salva il file DXF
        self.doc.saveas(file_path)
        
        return file_path

    def export_all_faces(self, base_file_path: str = "profilo", separate_files: bool = False, add_labels: bool = False):
        """
        Esporta tutte le facce del profilo in uno o più file DXF
        """
        if separate_files:
            # Crea un file separato per ogni faccia
            result_files = []
            for face_key in self.profile_faces.faces:
                if self.profile_faces.has_features(face_key):
                    file_path = f"{base_file_path}_{face_key}.dxf"
                    try:
                        result_files.append(self.export_face(face_key, file_path, add_labels))
                    except ValueError as e:
                        print(f"Errore nell'esportazione della faccia '{face_key}': {str(e)}")
            return result_files
        else:
            # Reinizializza il documento DXF per tutte le facce
            self._initialize_dxf()
            
            # Per ogni faccia con caratteristiche
            for face_key in self.profile_faces.faces:
                if not self.profile_faces.has_features(face_key):
                    continue
                    
                try:
                    # Usa il metodo privato per aggiungere la faccia con offset
                    self._add_face_to_dxf(face_key, with_offset=True, add_labels=add_labels)
                    
                except Exception as e:
                    print(f"Errore nell'esportazione della faccia '{face_key}': {str(e)}")
            
            # Salva il file DXF completo
            file_path = f"{base_file_path}_completo.dxf"
            self.doc.saveas(file_path)
            
        return file_path
    
    
        
