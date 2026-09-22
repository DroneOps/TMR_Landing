import cv2
import numpy as np

class ArucoTracker:
    def __init__(self, marker_size_cm=10.0):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        
        # Tamaño real del ArUco impreso en centímetros
        self.marker_size = marker_size_cm
        
        # Matriz intrínseca aproximada para DJI Tello (Resolución 960x720)
        # Lo ideal es calibrar tu propia cámara, pero esto sirve para arrancar.
        self.camera_matrix = np.array([
            [920.0, 0.0, 480.0],  # fx, 0, cx
            [0.0, 920.0, 360.0],  # 0, fy, cy
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)
        
        # Asumimos distorsión cero para empezar
        self.dist_coeffs = np.zeros((4,1), dtype=np.float32)
        
        # Definir las 4 esquinas del ArUco en el mundo 3D (Z=0)
        # El centro del ArUco es el punto (0,0,0)
        half = self.marker_size / 2.0
        self.obj_points = np.array([
            [-half,  half, 0], # Arriba-Izquierda
            [ half,  half, 0], # Arriba-Derecha
            [ half, -half, 0], # Abajo-Derecha
            [-half, -half, 0]  # Abajo-Izquierda
        ], dtype=np.float32)

    def detect_and_estimate(self, frame):
        """Detecta el marcador y calcula su posición en centímetros."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = self.detector.detectMarkers(gray)
        
        pos_cm = None  # (X, Y, Z) en centímetros
        
        if ids is not None:
            # Tomamos las esquinas del primer marcador detectado
            img_points = corners[0][0]
            
            # solvePnP calcula la rotación (rvec) y traslación (tvec)
            exito, rvec, tvec = cv2.solvePnP(
                self.obj_points, 
                img_points, 
                self.camera_matrix, 
                self.dist_coeffs,
                flags=cv2.SOLVEPNP_IPPE_SQUARE # Algoritmo optimizado para cuadrados
            )
            
            if exito:
                # tvec contiene [X, Y, Z] en centímetros respecto a la cámara
                # Al apuntar hacia abajo:
                # X = Izquierda/Derecha del dron
                # Y = Adelante/Atrás del dron
                # Z = Altura desde el dron hasta la plataforma
                x_cm = float(tvec[0][0])
                y_cm = float(tvec[1][0])
                z_cm = float(tvec[2][0])
                
                pos_cm = (x_cm, y_cm, z_cm)
                
                # Dibujar los ejes 3D sobre el marcador para visualizar la orientación
                cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvec, tvec, self.marker_size / 2)
                
        return corners, ids, pos_cm