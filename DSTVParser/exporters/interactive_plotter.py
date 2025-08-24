import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from typing import List, Tuple, Dict, Optional
from matplotlib.widgets import Button
from DSTVParser.utils.drawers import calculate_slot_points

class MeasurementTool:
    """Classe per gestire le misurazioni tra due punti"""
    
    def __init__(self):
        self.first_point = None
        self.first_marker = None
        self.measuring = False
        self.measurements = []  # Lista di tuple (line, annotation, markers)


class InteractiveProfilePlotter:
    """Classe per visualizzare le facce di un profilo con interattività matplotlib"""
    
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
        
        # Variabili per l'interattività
        self.annotations = []
        self.markers = []
        self.measurement_tool = MeasurementTool()
        self.measure_mode = False  # Modalità misurazione attiva/disattiva
        self.current_fig = None
        self.all_axes = []
        self.all_face_data = {}
        
    def _find_closest_point(self, click_x, click_y, ax, face_key):
        """Trova il punto più vicino al click in una specifica faccia"""
        if face_key not in self.all_face_data:
            return None
            
        face_data = self.all_face_data[face_key]
        min_distance = float('inf')
        closest_point = None
        
        # Cerca nei punti del contorno
        if face_data['contour']:
            for i, (x, y) in enumerate(face_data['contour']):
                distance = math.sqrt((x - click_x)**2 + (y - click_y)**2)
                if distance < min_distance and distance < 10:  # Tolleranza di 10 unità
                    min_distance = distance
                    closest_point = (x, y, f"Vertex {i+1}", f"Face: {face_data['name']}")
        
        # Cerca nei centri dei fori
        for i, hole in enumerate(face_data['holes']):
            x, y = hole['center']
            distance = math.sqrt((x - click_x)**2 + (y - click_y)**2)
            if distance < min_distance and distance < 15:  # Tolleranza maggiore per i centri
                min_distance = distance
                closest_point = (x, y, f"Hole {i+1}", f"Ø{hole['diameter']}")
        
        # Cerca nei centri delle asole
        for i, slot in enumerate(face_data['slots']):
            x, y = slot['center']
            distance = math.sqrt((x - click_x)**2 + (y - click_y)**2)
            if distance < min_distance and distance < 15:  # Tolleranza maggiore per i centri
                min_distance = distance
                closest_point = (x, y, f"Slot {i+1}", f"Ø{slot['diameter']}x{slot['length']}")
        
        return closest_point
    
    def _on_click(self, event):
        """Gestisce i click del mouse per mostrare coordinate o misurare"""
        if not event.inaxes or event.inaxes not in self.all_axes:
            return
            
        if event.button == 1:  # Click sinistro
            x, y = event.xdata, event.ydata
            
            # Determina quale faccia è stata cliccata
            ax = event.inaxes
            face_key = None
            for i, axis in enumerate(self.all_axes):
                if axis == ax:
                    face_keys = ['o', 'u', 'v', 'h']
                    if i < len(face_keys):
                        face_key = face_keys[i]
                    break
            
            if not face_key:
                return
            
            # Se siamo in modalità misurazione
            if self.measure_mode:
                self._handle_measurement_click(x, y, ax, face_key)
            else:
                # Modalità normale - mostra coordinate
                self._handle_coordinate_click(x, y, ax, face_key)
    
    def _handle_coordinate_click(self, x, y, ax, face_key):
        """Gestisce il click per mostrare le coordinate"""
        # Trova il punto più vicino
        closest_point = self._find_closest_point(x, y, ax, face_key)
        
        if closest_point:
            point_x, point_y, point_type, point_info = closest_point
            
            # Calcola una posizione che eviti il titolo
            if point_y > (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.7 + ax.get_ylim()[0]:
                xytext_offset = (20, -60)  # Sotto il punto
            else:
                xytext_offset = (20, 20)   # Sopra il punto
            
            annotation_text = f"{point_type}\nX: {point_x:.2f}\nY: {point_y:.2f}\n{point_info}"
            
            ann = ax.annotate(
                annotation_text,
                xy=(point_x, point_y),
                xytext=xytext_offset,
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8, edgecolor='gray'),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                fontsize=9
            )
            
            # Aggiungi un marker sul punto
            marker = ax.plot(point_x, point_y, 'ro', markersize=8, 
                           markerfacecolor='red', markeredgecolor='darkred')[0]
            
            # Salva per poter cancellare dopo
            self.annotations.append(ann)
            self.markers.append(marker)
            
            # Ridisegna
            self.current_fig.canvas.draw()
    
    def _handle_measurement_click(self, x, y, ax, face_key):
        """Gestisce il click per le misurazioni"""
        # Trova il punto più vicino
        closest_point = self._find_closest_point(x, y, ax, face_key)
        
        if closest_point:
            point_x, point_y, point_type, point_info = closest_point
            
            if not self.measurement_tool.measuring:
                # Primo punto della misurazione
                self.measurement_tool.first_point = (point_x, point_y)
                self.measurement_tool.first_marker = ax.plot(point_x, point_y, 'go', markersize=10, 
                                                           markerfacecolor='lime', markeredgecolor='darkgreen')[0]
                self.measurement_tool.measuring = True
                
                # Annotazione temporanea per il primo punto
                temp_ann = ax.annotate(
                    f"P1: {point_type}\nClick secondo punto",
                    xy=(point_x, point_y),
                    xytext=(20, 20),
                    textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                    fontsize=9
                )
                self.annotations.append(temp_ann)
                
            else:
                # Secondo punto della misurazione
                x1, y1 = self.measurement_tool.first_point
                x2, y2 = point_x, point_y
                
                # Calcola la distanza
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                # Rimuovi l'annotazione temporanea
                if self.annotations:
                    self.annotations[-1].remove()
                    self.annotations.pop()
                
                # Disegna la linea di misurazione
                line = ax.plot([x1, x2], [y1, y2], 'g-', linewidth=2, alpha=0.7)[0]
                
                # Marker per il secondo punto
                second_marker = ax.plot(x2, y2, 'go', markersize=10, 
                                      markerfacecolor='lime', markeredgecolor='darkgreen')[0]
                
                # Posizione per l'annotazione della distanza (centro della linea)
                center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
                
                # Calcola l'offset per evitare che l'annotazione sia sulla linea
                # Perpendicolare alla linea di misurazione
                line_angle = math.atan2(y2 - y1, x2 - x1)
                perp_angle = line_angle + math.pi / 2
                offset_dist = 20
                
                offset_x = center_x + offset_dist * math.cos(perp_angle)
                offset_y = center_y + offset_dist * math.sin(perp_angle)
                
                # Annotazione con la distanza
                distance_ann = ax.annotate(
                    f"Distanza: {distance:.2f} mm",
                    xy=(center_x, center_y),
                    xytext=(offset_x, offset_y),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.9, edgecolor='blue'),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1', color='blue'),
                    fontsize=10,
                    weight='bold'
                )
                
                # Salva tutti gli elementi della misurazione
                measurement = (line, distance_ann, [self.measurement_tool.first_marker, second_marker])
                self.measurement_tool.measurements.append(measurement)
                
                # Reset per la prossima misurazione
                self.measurement_tool.measuring = False
                self.measurement_tool.first_point = None
                self.measurement_tool.first_marker = None
        
        # Ridisegna
        self.current_fig.canvas.draw()
    
    def _erase_annotations(self, event):
        """Cancella tutte le annotazioni, marker e misurazioni"""
        # Rimuovi tutte le misurazioni
        for line, annotation, markers in self.measurement_tool.measurements:
            line.remove()
            annotation.remove()
            for marker in markers:
                marker.remove()
        
        # Se c'è una misurazione in corso, pulisci anche quella
        if self.measurement_tool.measuring and self.measurement_tool.first_marker:
            self.measurement_tool.first_marker.remove()
        
        # Rimuovi tutte le annotazioni normali
        for ann in self.annotations:
            ann.remove()
        
        # Rimuovi tutti i marker normali
        for marker in self.markers:
            marker.remove()
        
        # Pulisci tutte le liste
        self.annotations.clear()
        self.markers.clear()
        self.measurement_tool.measurements.clear()
        self.measurement_tool.measuring = False
        self.measurement_tool.first_point = None
        self.measurement_tool.first_marker = None
        
        # Ridisegna
        self.current_fig.canvas.draw()
    
    def _toggle_measure_mode(self, event):
        """Attiva/disattiva la modalità misurazione"""
        self.measure_mode = not self.measure_mode
        
        # Reset della misurazione corrente se disattivata
        if not self.measure_mode and self.measurement_tool.measuring:
            if self.measurement_tool.first_marker:
                self.measurement_tool.first_marker.remove()
            if self.annotations:  # Rimuovi l'annotazione temporanea
                self.annotations[-1].remove()
                self.annotations.pop()
            
            self.measurement_tool.measuring = False
            self.measurement_tool.first_point = None
            self.measurement_tool.first_marker = None
            self.current_fig.canvas.draw()
        
        # Aggiorna il colore del bottone
        if hasattr(self, 'measure_button'):
            if self.measure_mode:
                self.measure_button.color = 'lightgreen'
                self.measure_button.hovercolor = 'green'
                self.measure_button.label.set_text('Measure: ON')
            else:
                self.measure_button.color = 'lightgray'
                self.measure_button.hovercolor = 'gray'
                self.measure_button.label.set_text('Measure: OFF')
            
            self.current_fig.canvas.draw()
    
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
            
            # Semicerchi con plt.Circle
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
        """Visualizza una singola faccia del profilo con interattività"""
        if face_key not in self.profile_faces.faces:
            print(f"Faccia {face_key} non trovata!")
            return
            
        # Ottieni i dati della faccia
        plot_data = self.profile_faces.get_features_for_exporting(face_key, with_offset)
        face_data = plot_data[face_key]
        
        # Salva i dati per l'interattività
        self.all_face_data = {face_key: face_data}
        
        fig, ax = plt.subplots(figsize=(12, 8))
        self.current_fig = fig
        self.all_axes = [ax]
        
        # Usa il metodo privato per disegnare
        self._draw_single_face(face_data, ax)
        
        # Abilita interattività
        self._setup_interactivity()
        
        return fig
    
    def plot_all_faces(self, with_offset=True, show_holes=True, show_slots=True):
        """Visualizza tutte le facce del profilo con interattività"""
        # Ottieni tutte le facce da plottare
        plot_data = self.profile_faces.get_features_for_exporting(with_offset=with_offset)
        
        # Salva tutti i dati per l'interattività
        self.all_face_data = plot_data
        
        # Crea una figura con subplots
        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        axs = axs.flatten()
        
        self.current_fig = fig
        self.all_axes = []
        
        # Ordine delle facce per il plot
        face_order = ['o', 'u', 'v', 'h']
        
        for i, face_key in enumerate(face_order):
            if face_key not in plot_data:
                continue
                
            ax = axs[i]
            face_data = plot_data[face_key]
            self.all_axes.append(ax)
            
            # Riutilizza il metodo di disegno
            self._draw_single_face(face_data, ax)
        
        # Rimuovi subplot vuoti
        for i in range(len(face_order), 4):
            fig.delaxes(axs[i])
        
        # Abilita interattività
        self._setup_interactivity()
        
        plt.tight_layout()
        return fig
    
    def _setup_interactivity(self):
        """Configura l'interattività per la figura corrente"""
        if not self.current_fig:
            return
            
        # Connetti eventi mouse
        self.current_fig.canvas.mpl_connect('button_press_event', self._on_click)
        
        # Bottone Erase
        ax_erase = plt.axes([0.02, 0.02, 0.08, 0.04])
        self.erase_button = Button(ax_erase, 'Erase')
        self.erase_button.on_clicked(self._erase_annotations)
        
        # Bottone Measure
        ax_measure = plt.axes([0.12, 0.02, 0.12, 0.04])
        self.measure_button = Button(ax_measure, 'Measure: OFF')
        self.measure_button.color = 'lightgray'
        self.measure_button.hovercolor = 'gray'
        self.measure_button.on_clicked(self._toggle_measure_mode)
        
        # Istruzioni per l'utente aggiornate
        instructions = ("Modalità normale: Click per coordinate | "
                       "Modalità Measure: Click su 2 punti per distanza | "
                       "Erase cancella tutto")
        self.current_fig.suptitle(instructions, fontsize=10, y=0.98)
    
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

