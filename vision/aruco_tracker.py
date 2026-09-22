import cv2

class ArucoTracker:
  def __init__(self):
    self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
    self.parameters = cv2.aruco.DetectorParameters()
    self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
    
  def detect(self, frame):
    # Cambiar a escala de grises para facilitar la lectura
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = self.detector.detectMarkers(gray)
  
    # Obtener el centro del aruco
    centro = None
    if ids is not None:
      c = corners[0][0]
      centro_x = int((c[0][0] + c[2][0]) / 2)
      centro_y = int((c[0][1] + c[2][1]) / 2)
      centro = (centro_x, centro_y)
      
    return corners, ids, centro 
  
  def draw_markers(self, frame, corners, ids, centro):
    if ids is not None:
      cv2.aruco.drawDetectedMarkers(frame, corners, ids)
      # Dibujar marcador
      if centro is not None:
        id_num = ids.flatten()[0]
        
        cv2.circle(frame, centro, 5, (0, 255, 0), -1)
        cv2.putText(frame, f"ID: {id_num} Centro: {centro}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
      
    return frame
    
  