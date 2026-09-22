import cv2

class ImageProcessor:
  def __init__(self, flip_code=0):
    # flip_code: 0 (vertical), 1 (horizontal), -1 (ambos)
    # Modificar si es necesario voltear el cuadro de la imagen
    self.flip_code = flip_code
    
  def process_frame(self, frame):
    if frame is None:
      return None

    # Frame volteado
    corrected_frame = cv2.flip(frame, self.flip_code)
    # Ajuste de sistema de color
    bgr_frame = cv2.cvtColor(corrected_frame, cv2.COLOR_RGB2BGR)
    return bgr_frame
  
  
