import sys
import os

# Asegurar que Python encuentre los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision.image_processor import ImageProcessor
from vision.aruco_tracker import ArucoTracker

class VisionSystem:
    def __init__(self, flip_code=0, marker_size_cm=10.0):
        # La clase "padre" instancia a sus "hijos" internamente
        self.processor = ImageProcessor(flip_code=flip_code)
        self.tracker = ArucoTracker(marker_size_cm=marker_size_cm)

    def update(self, frame_crudo):
        """
        Recibe un frame crudo directamente del dron.
        Se encarga de limpiarlo, buscar el ArUco y devolver todo listo.
        """
        if frame_crudo is None or not hasattr(frame_crudo, 'shape') or frame_crudo.size == 0:
            return None, None, None

        # 1. El procesador limpia el efecto espejo
        frame_limpio = self.processor.process_frame(frame_crudo)
        
        # 2. El tracker hace la matemática 3D
        corners, ids, pos_cm = self.tracker.detect_and_estimate(frame_limpio)
        
        return frame_limpio, ids, pos_cm