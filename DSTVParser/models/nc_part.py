from dataclasses import dataclass
from typing import List, Tuple, Optional
import os
from collections import defaultdict

@dataclass
class Hole:
    """Rappresenta un foro circolare nel profilo"""
    x: float
    y: float
    diameter: float
    Hole_type: float
    face: str  # 'o', 'u', 'v', 'h'
    hole_type: str = 'normal'  # 'normal', 'threaded', 'countersink'
    depth: float = 0.0  # per fori svasati

@dataclass
class Slot:
    """Rappresenta un'asola nel profilo"""
    x: float
    y: float
    diameter: float
    hole_type : float
    cc_distance: float
    height: float
    angle: float
    length: float
    face: str  # 'o', 'u', 'v', 'h'

@dataclass
class Notch:
    """Rappresenta una tacca nel profilo"""
    x: float
    y: float
    z: float
    notch_type: str  
    face: str        # 'o', 'u', 'v', 'h'

class NCPart:
    """Classe base per tutte le parti NC"""
    def __init__(
        self,
        order_id: str,
        piece_id: str,
        material: str,
        quantity: int,
        profile_type: str,
        code_profile: str,
        length: float,
        dimensions: dict[str, float] = None
    ):
        self.order_id = order_id
        self.piece_id = piece_id
        self.material = material
        self.quantity = quantity
        self.profile_type = profile_type
        self.code_profile = code_profile
        self.length = length
        self.dimensions = dimensions or {}
        
        # Liste per memorizzare le diverse features
        self.holes: List[Hole] = []
        self.slots: List[Slot] = []
        self.notches: List[Notch] = []
        self.o_contour: List[Tuple[float, float, float]] = []  
        self.u_contour: List[Tuple[float, float, float]] = []  
        self.v_contour: List[Tuple[float, float, float]] = []  
        self.h_contour: List[Tuple[float, float, float]] = []  

    def add_hole(self, x: float, y: float, diameter: float, tipologia: float, face: str, 
                hole_type: str = 'normal', depth: float = 0.0):
        """Aggiunge un foro"""
        self.holes.append(Hole(x, y, diameter, tipologia, face, hole_type, depth))

    def add_slot(self, x: float, y: float, diameter: float, hole_type: float, cc_distance: float, height: float, angle: float, length: float, face: str):
        """Aggiunge un'asola"""
        self.slots.append(Slot(x, y, diameter, hole_type, cc_distance, height, angle, length, face))

    def add_notch(self, x: float, y: float, z: float, notch_type: str, face: str):
        """Aggiunge una tacca al profilo"""
        self.notches.append(Notch(x, y, z, notch_type, face))

    def add_contour_points(self, contour_type: str, points: List[Tuple[float, float, float]]):
        """Aggiunge punti a un contorno specifico"""
        if contour_type == 'o':
            self.o_contour.extend(points)
        elif contour_type == 'u':
            self.u_contour.extend(points)
        elif contour_type == 'v':
            self.v_contour.extend(points)
        elif contour_type == 'h':
            self.h_contour.extend(points)

    def has_holes(self) -> bool:
        """Verifica se il profilo ha dei fori."""
        return len(self.holes) > 0
    
    def has_slots(self) -> bool:
        """Verifica se il profilo ha delle asole."""
        return len(self.slots) > 0
    
    def has_notches(self)  -> bool:
        """Verifica se il profilo ha delle tacche"""
        return len(self.notches) > 0
    
    def has_worked_areas(self)  -> bool:
        return any(len(contour) > 5 for contour in [self.o_contour, self.u_contour, self.v_contour, self.h_contour])
    
    def flange_skew_cut(self) -> bool:
        # Verifica validità dei contorni
        if not hasattr(self, 'o_contour') or len(self.o_contour) < 5 or \
        not hasattr(self, 'u_contour') or len(self.u_contour) < 5:
            return False
        
        # Controlla inclinazione e ottiene i delta
        o_incl, o_delta = check_inclination(self.o_contour)
        u_incl, u_delta = check_inclination(self.u_contour)

        # Devono essere entrambi inclinati e con gli stessi delta (entro una tolleranza)
        if o_incl and u_incl:
            tolerance = 0.1  # puoi regolare questo valore
            delta_simili = abs(o_delta[0] - u_delta[0]) < tolerance and \
                abs(o_delta[1] - u_delta[1]) < tolerance
            return delta_simili
        return False

    def web_skew_cut(self) -> bool:
        # Determina quale contorno usare
        valid_face = []
        if hasattr(self, 'h_contour') and len(self.h_contour) >= 5:
            valid_face.append('h')
        if hasattr(self, 'v_contour') and len(self.v_contour) >= 5:
            valid_face.append('v')
        
        if len(valid_face) == 2:
            h_incl, h_delta = check_inclination(self.h_contour)
            v_incl, v_delta = check_inclination(self.v_contour)
            
            # Devono essere entrambi inclinati e con gli stessi delta
            if h_incl and v_incl:
                tolerance = 0.1  # puoi regolare questo valore
                delta_simili = abs(h_delta[0] - v_delta[0]) < tolerance and \
                    abs(h_delta[1] - v_delta[1]) < tolerance
                return delta_simili
            return False
        
        elif len(valid_face) == 1:
            incl, delta = check_inclination(getattr(self, f"{valid_face[0]}_contour"))
            return incl
        
        return False

    def get_holes_by_face(self) -> dict[str, List[Hole]]:
        """Raggruppa i fori per faccia del profilo."""
        holes_by_face = defaultdict(list)
        for hole in self.holes:
            holes_by_face[hole.face].append(hole)
        return dict(holes_by_face)
    
    def get_slots_by_face(self) -> dict[str, List[Slot]]:
        """Raggruppa le asole per faccia del profilo."""
        slots_by_face = defaultdict(list)
        for slot in self.slots:
            slots_by_face[slot.face].append(slot)
        return dict(slots_by_face)

    def get_holes_count(self) -> int:
        """Restituisce il numero totale di fori."""
        return len(self.holes)

    def get_slots_count(self) -> int:
        """Restituisce il numero totale di asole."""
        return len(self.slots)
    
    def get_features_summary(self) -> dict[str, int]:
        """Restituisce un riepilogo delle caratteristiche del profilo."""
        return {
            'holes': self.get_holes_count(),
            'slots': self.get_slots_count(),
            'o_contour_points': len(self.o_contour),
            'u_contour_points': len(self.u_contour),
            'v_contour_points': len(self.v_contour),
            'h_contour_points': len(self.h_contour)
        }

    def has_contour(self, face: str) -> bool:
        """Verifica se esiste un contorno per una determinata faccia."""
        contours = {
            'o': self.o_contour,
            'u': self.u_contour,
            'v': self.v_contour,
            'h': self.h_contour
        }
        return len(contours.get(face, [])) > 0

    def get_holes_by_diameter(self, diameter: float) -> List[Hole]:
        """Trova tutti i fori con un determinato diametro."""
        return [hole for hole in self.holes if hole.diameter == diameter]

    def get_holes_coordinates_by_face(self) -> dict[str, List[Tuple[float, float]]]:
        """Restituisce le coordinate dei fori raggruppate per faccia."""
        holes_by_face = defaultdict(list)
        for hole in self.holes:
            holes_by_face[hole.face].append((hole.x, hole.y))
        return dict(holes_by_face)

    def get_slots_by_length(self, length: float) -> List[Slot]:
        """Trova tutte le asole con una determinata lunghezza."""
        return [slot for slot in self.slots if slot.length == length]
    
    def get_notches_by_type(self) -> dict[str, List[Notch]]:
        """Raggruppa le tacche per tipo (tangenziale 't' o foro 'w')"""
        return {
            't': [n for n in self.notches if n.notch_type == 't'],
            'w': [n for n in self.notches if n.notch_type == 'w']
        }
        
    def get_header(self):
        return {'order_id': self.order_id,
            'piece_id': self.piece_id,
            'material': self.material,
            'quantity': self.quantity,
            'profile_type': self.profile_type,
            'code_profile': self.code_profile,
            'lenght': self.length}


def check_inclination(contour: List[Tuple[float, float, float]], tolerance: float = 0.1) -> Tuple[bool, Tuple[float, float]]:
    """
    Verifica se un contorno ha tagli inclinati confrontando le x dei punti 
    tra il livello superiore e inferiore.
    
    Args:
        contour: Lista di tuple (x, y, z)
        tolerance: Tolleranza per considerare due valori come uguali
    Returns:
        Tuple[bool, Tuple[float, float]]: (ha_inclinazione, (delta_x_sinistra, delta_x_destra))
    """
    if len(contour) != 5:
        return False, (0, 0)

    # Trova y min e max
    min_y = min(p[1] for p in contour)
    max_y = max(p[1] for p in contour)

    # Trova x min e max per ogni livello y
    min_y_x = [p[0] for p in contour if abs(p[1] - min_y) <= tolerance]
    max_y_x = [p[0] for p in contour if abs(p[1] - max_y) <= tolerance]

    # Trova i delta tra i punti corrispondenti dei due livelli
    delta_x_left = abs(min(min_y_x) - min(max_y_x))   # Delta sul lato sinistro
    delta_x_right = abs(max(min_y_x) - max(max_y_x))  # Delta sul lato destro

    has_inclination = delta_x_left > tolerance or delta_x_right > tolerance

    return has_inclination, (delta_x_left, delta_x_right)