import sys
import os
import time
import cv2
from djitellopy import Tello

# Asegurar que Python encuentre los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision.image_processor import ImageProcessor
from vision.aruco_tracker import ArucoTracker
from control.pid_controller import PIDController

def main():
    print("--- INICIANDO TEST DE PID EN SECO (SIN MOTORES) ---")
    processor = ImageProcessor(flip_code=0) 
    tracker = ArucoTracker()
    
    # Controladores PID para X y Y
    # (Kp, Ki, Kd, min_vel, max_vel)
    pid_x = PIDController(0.2, 0.0, 0.1, -50, 50)
    pid_y = PIDController(0.2, 0.0, 0.1, -50, 50)

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
        
        # Validaciones de seguridad para el frame
        if frame_crudo is None: 
          continue
        
        alto, ancho = frame_crudo.shape[:2]
        
        # Procesamiento visual
        frame_limpio = processor.process_frame(frame_crudo)
        corners, ids, centro = tracker.detect(frame_limpio)
        frame_final = tracker.draw_markers(frame_limpio, corners, ids, centro)

        # 1. Definir el Setpoint (el centro de la cámara)
        centro_pantalla_x = ancho // 2
        centro_pantalla_y = alto // 2
        
        # Dibujar una mira (cruz) indicando el objetivo ideal
        cv2.line(frame_final, (centro_pantalla_x - 20, centro_pantalla_y), (centro_pantalla_x + 20, centro_pantalla_y), (0, 0, 255), 2)
        cv2.line(frame_final, (centro_pantalla_x, centro_pantalla_y - 20), (centro_pantalla_x, centro_pantalla_y + 20), (0, 0, 255), 2)

        # 2. Calcular e imprimir velocidades si vemos el ArUco
        if centro is not None:
            # Calcular velocidades con el PID
            vel_x = pid_x.update(centro_pantalla_x, centro[0])
            vel_y = pid_y.update(centro_pantalla_y, centro[1])
            
            # Dibujar una línea visual conectando el centro de la pantalla con el ArUco
            cv2.line(frame_final, (centro_pantalla_x, centro_pantalla_y), centro, (255, 0, 0), 2)
            
            # Mostrar los valores crudos en pantalla
            cv2.putText(frame_final, f"Vel X (Roll): {vel_x}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame_final, f"Vel Y (Pitch): {vel_y}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        else:
            cv2.putText(frame_final, "Sin objetivo...", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Test de PID (Simulado)", frame_final)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    tello.streamoff()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()