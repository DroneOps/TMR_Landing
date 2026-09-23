import sys
import os
import time
import cv2
from djitellopy import Tello

# Esto permite que Python encuentre tu carpeta 'vision' desde la carpeta 'tests'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Importamos solo la clase unificadora
from vision.vision_system import VisionSystem

def main():
    # 2. Inicializamos el sistema completo con una sola línea
    vision = VisionSystem(flip_code=0, marker_size_cm=10.0)

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
        
        # 3. Toda la lógica de validación, limpieza, detección y cálculo 3D en un solo método
        frame_final, ids, pos_cm = vision.update(frame_crudo)
        if frame_final is None:
            continue
            
        # Opcional: Imprimir las coordenadas 3D en pantalla para validar
        if pos_cm is not None:
            x, y, z = pos_cm
            cv2.putText(frame_final, f"Distancias - X:{x:.1f}cm Y:{y:.1f}cm Z:{z:.1f}cm", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Test de Modulos de Vision", frame_final)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Limpieza
    tello.streamoff()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()