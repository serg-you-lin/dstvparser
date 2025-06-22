import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from typing import List, Tuple, Dict, Optional
from DSTVParser.utils.drawers import calculate_slot_points

class ProfilePlotter:
    """Classe per visualizzare le facce di un profilo usando matplotlib"""
    
    def __init__(self, profile_faces):
        """Inizializza con un oggetto ComposeProfileFaces"""
        self.profile_faces = profile_faces
        
        # Mappa dei colori matplotlib per le facce
        self.color_map = {
            1: 'r',  # Rosso
            2: 'b',  # Blu
            3: 'g',  # Verde
            4: 'c',  # Ciano
            5: 'b',  # Blu
            6: 'c',  # Ciano
            7: 'k'   # Nero
        }
    
    def _draw_single_face(self, face_data, ax):
        """Metodo privato per disegnare una singola faccia su un asse dato"""
        # Ottieni il colore matplotlib
        color = self.color_map.get(face_data['color'], 'k')
        
        # Disegna il contorno
        contour = face_data['contour']
        if contour:
            self._draw_contour(face_data, ax, color)
        
        # Disegna i fori
        self._draw_holes(face_data, ax, color, True)
        
        # Disegna le asole
        self._draw_slots(face_data, ax, color)
        
        # Imposta titolo e assi
        ax.set_title(f"{face_data['name']}")
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_aspect('equal')
    
    def _draw_contour(self, face_data, ax, color):
        contour = face_data['contour']
        if contour:
            x_coords = [p[0] for p in contour]
            y_coords = [p[1] for p in contour]
            
            # Chiudi il poligono connettendo l'ultimo punto con il primo
            if len(x_coords) > 1:
                x_coords.append(x_coords[0])
                y_coords.append(y_coords[0])
            
            # Disegna il contorno
            ax.plot(x_coords, y_coords, f"{color}-", linewidth=2)
            
            # Aggiungi numeri ai punti
            for j, (x, y) in enumerate(zip(x_coords[:-1], y_coords[:-1])):
                ax.text(x, y, str(j+1), fontsize=8, ha='center', va='center', 
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='circle'))
                    


    def _draw_slots(self, face_data, ax, color):
        """Disegna le asole usando semicerchi con plt.Circle e plot"""
        for slot in face_data['slots']:
            center_x, center_y = slot['center']
            diameter = slot['diameter']
            cc_distance = slot['cc_distance'] 
            angle = slot['angle']
            
            center1, center2, radius, (p1, p2, p3, p4) = calculate_slot_points(
                (center_x, center_y), diameter, cc_distance, angle)
            
            # Semicerchi con plt.Circle specificando l'angolo di inizio/fine o vedi tu se mettere ARC se è più semplice
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
        


    def _draw_holes(self, face_data, ax, color, show_holes=True):
        for hole in face_data['holes']:
            center_x, center_y = hole['center']
            radius = hole['diameter'] / 2
            
            # Disegna il cerchio
            circle = plt.Circle((center_x, center_y), radius, fill=False, color=color, linestyle='--')
            ax.add_patch(circle)
            
            # Aggiungi label con diametro
            ax.text(center_x, center_y - radius - 5, f"Ø{hole['diameter']}", 
                    horizontalalignment='center', verticalalignment='top', fontsize=8, color=color)
        
    def plot_face(self, face_key, with_offset=False, show_holes=True, show_slots=True):
        """Visualizza una singola faccia del profilo"""
        if face_key not in self.profile_faces.faces:
            print(f"Faccia {face_key} non trovata!")
            return
            
        # Ottieni i dati della faccia
        plot_data = self.profile_faces.get_features_for_exporting(face_key, with_offset)
        face_data = plot_data[face_key]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Usa il metodo privato per disegnare
        self._draw_single_face(face_data, ax)
        
        # Aggiungi legenda
        ax.legend()
        
        return fig
    
    def plot_all_faces(self, with_offset=True, show_holes=True, show_slots=True):
        """Visualizza tutte le facce del profilo"""
        # Ottieni tutte le facce da plottare
        plot_data = self.profile_faces.get_features_for_exporting(with_offset=with_offset)
        
        # Crea una figura con subplots
        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        axs = axs.flatten()
        
        # Ordine delle facce per il plot
        face_order = ['o', 'u', 'v', 'h']
        
        for i, face_key in enumerate(face_order):
            if face_key not in plot_data:
                continue
                
            ax = axs[i]
            face_data = plot_data[face_key]
            
            # Riutilizza il metodo di disegno
            self._draw_single_face(face_data, ax)
        
        # Rimuovi subplot vuoti
        for i in range(len(face_order), 4):
            fig.delaxes(axs[i])
        
        plt.tight_layout()
        return fig
    
    
    def show(self, fig=None):
        """Mostra il grafico corrente o uno specifico"""
        if fig:
            plt.figure(fig.number)
        plt.show()
    
    def save(self, filename, fig=None, dpi=300):
        """Salva il grafico corrente o uno specifico"""
        if fig:
            fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        else:
            plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Grafico salvato come {filename}")



                        



            