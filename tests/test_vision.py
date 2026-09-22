import sys
import os
import time
import cv2
from djitellopy import Tello

# Esto permite que Python encuentre tu carpeta 'vision' desde la carpeta 'tests'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision.image_processor import ImageProcessor
from vision.aruco_tracker import ArucoTracker

def main():
    processor = ImageProcessor(flip_code=0) 
    tracker = ArucoTracker()

    tello = Tello()
    tello.connect()
    print(f"Batería: {tello.get_battery()}%")
    
    tello.streamon()
    print("[INFO] Esperando a que inicialice el video...")
    time.sleep(3) 
    
    frame_read = tello.get_frame_read()

    print("Presiona 'q' para salir.")

    while True:
        frame_crudo = frame_read.frame
        
        if frame_crudo is None:
            continue
        
        frame_limpio = processor.process_frame(frame_crudo)
        corners, ids, centro = tracker.detect(frame_limpio)
        frame_final = tracker.draw_markers(frame_limpio, corners, ids, centro)

        cv2.imshow("Test de Modulos de Vision", frame_final)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Limpieza
    tello.streamoff()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()