import cv2
import time
import sys
import os

# Asegurar que Python encuentre los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision.vision_system import VisionSystem
from control.tello_driver import TelloDriver
from logic.navigator import Navigator

def main():
    print("--- INICIANDO SISTEMA SEPARADO ---")
    
    # Instancias independientes
    driver = TelloDriver()
    vision_module = VisionSystem()
    navigator = Navigator()

    driver.connect()
    time.sleep(3) 
    
    while True:
        frame_crudo = driver.get_frame()
      
        frame_limpio, ids, pos_cm = vision_module.update(frame_crudo)
        
        # 2. LEER SENSOR INERCIAL (Velocidades)
        vel_x, vel_y = driver.get_speeds()
        
        # 3. CALCULAR LÓGICA DE NAVEGACIÓN
        # El navigator decide qué hacer, sin saber de dónde vienen los datos
        cmd_roll, cmd_pitch = navigator.calculate_commands(pos_cm, vel_x, vel_y)
        
        # 4. ENVIAR AL HARDWARE
        # Si vemos el ArUco (o si el Kalman está compensando), nos movemos. 
        # Si no queremos movernos, enviamos (0,0,0,0)
        driver.set_velocity(cmd_roll, cmd_pitch, throttle=0, yaw=0)
        
        # Interfaz y controles de teclado omitidos por brevedad...
        cv2.imshow("Camara", frame_limpio)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            driver.land()
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()