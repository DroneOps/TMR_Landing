import sys
import os
import cv2
import time

# Asegurar que Python encuentre los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from control.tello_driver import TelloDriver
from ui.telemetry_hud import TelemetryHUD  

def main():
    print("--- INICIANDO TEST DEL HARDWARE CON HUD ---")
    driver = TelloDriver()
    hud = TelemetryHUD()  
    
    driver.connect()
    print("[INFO] Esperando a que inicialice el video...")
    time.sleep(3)

    print("\n[CONTROLES DE PRUEBA]")
    print(" 't' -> Despegar  |  'l' -> Aterrizar")
    print(" 'w/a/s/d' -> Mover |  'q' -> Salir\n")

    while True:
        frame_crudo = driver.get_frame()
        if frame_crudo is None or not hasattr(frame_crudo, 'shape') or frame_crudo.size == 0:
            continue
        
        frame_bgr = cv2.cvtColor(frame_crudo, cv2.COLOR_RGB2BGR)
        
        # 1. Obtenemos todos los datos del hardware en una línea
        telem = driver.get_telemetry()
        
        # 2. El HUD hace todo el trabajo pesado de dibujo. 
        frame_final = hud.draw(frame_bgr, telem, mission_state="TEST MANUAL", target_pos=None)

        cv2.imshow("Test Tello Driver", frame_final)

        # Controles de teclado
    
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            driver.land()
            break
        elif key == ord('t'):
            driver.takeoff(extra_height_cm=25)
        elif key == ord('l'):
            driver.land()
            
        # Prueba de velocidades limitadas
        roll, pitch = 0, 0
        if key == ord('w'): pitch = 20
        elif key == ord('s'): pitch = -20
        elif key == ord('a'): roll = -20
        elif key == ord('d'): roll = 20
        
        if roll != 0 or pitch != 0:
            driver.set_velocity(roll, pitch, throttle=0, yaw=0)
        else:
            # Presiona barra espaciadora para frenar de golpe en el aire
            if key == ord(' '): 
                driver.set_velocity(0, 0, 0, 0)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()