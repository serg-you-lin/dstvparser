import math
from typing import Tuple

def calculate_slot_points(center: Tuple[float, float], diameter: float, 
                         length: float, angle: float):
    """
    Calcola tutti i punti necessari per disegnare un'asola.
    
    Returns:
        tuple: (center1, center2, radius, tangent_points)
        dove tangent_points = (p1, p2, p3, p4) per le linee
    """
    radius = diameter / 2
    angle_rad = math.radians(angle)
    
    # Centri dei semicerchi
    half_length = length / 2
    dx = math.cos(angle_rad) * half_length
    dy = math.sin(angle_rad) * half_length
    
    center1 = (center[0] - dx, center[1] - dy)
    center2 = (center[0] + dx, center[1] + dy)
    
    # Punti di tangenza per le linee
    perp_angle = angle_rad + math.pi/2
    perp_dx = math.cos(perp_angle) * radius
    perp_dy = math.sin(perp_angle) * radius
    
    p1 = (center1[0] + perp_dx, center1[1] + perp_dy)
    p2 = (center2[0] + perp_dx, center2[1] + perp_dy)
    p3 = (center2[0] - perp_dx, center2[1] - perp_dy)
    p4 = (center1[0] - perp_dx, center1[1] - perp_dy)
    
    return center1, center2, radius, (p1, p2, p3, p4)

# Le tue funzioni aggiornate:

def _add_slot(self, center: Tuple[float, float], diameter: float, length: float, 
              angle: float, layer_name: str):
    """Aggiunge un'asola al documento DXF usando semicerchi"""
    center1, center2, radius, (p1, p2, p3, p4) = calculate_slot_points(center, diameter, length, angle)
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


def show_slots(face_data, ax, color):
    """Disegna le asole usando semicerchi con plt.Circle e plot"""
    for slot in face_data['slots']:
        center_x, center_y = slot['center']
        diameter = slot['diameter']
        cc_distance = slot['cc_distance']  # o slot['length'] se hai cambiato
        angle = slot['angle']
        
        center1, center2, radius, (p1, p2, p3, p4) = calculate_slot_points(
            (center_x, center_y), diameter, cc_distance, angle)
        
        # Semicerchi con plt.Circle specificando l'angolo di inizio/fine
        # Oppure continui a usare cerchi completi se è più semplice
        circle1 = plt.Circle(center1, radius, fill=False, color=color, linestyle='--')
        circle2 = plt.Circle(center2, radius, fill=False, color=color, linestyle='--')
        ax.add_patch(circle1)
        ax.add_patch(circle2)
        
        # Linee tangenti
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color + '-')
        ax.plot([p3[0], p4[0]], [p3[1], p4[1]], color + '-')
        
        # Label
        ax.text(center_x, center_y - radius - 5, f"Ø{diameter}x{slot['length']}", 
                horizontalalignment='center', verticalalignment='top', color=color)