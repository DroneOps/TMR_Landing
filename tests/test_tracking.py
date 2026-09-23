import sys
import os
import cv2
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from control.tello_driver import TelloDriver
from vision.vision_system import VisionSystem
from ui.telemetry_hud import TelemetryHUD
from logic.navigator import Navigator

def main():
    print("--- TEST DE VUELO 1: SEGUIMIENTO X, Y (SIN DESCENSO) ---")
    
    driver = TelloDriver()
    vision = VisionSystem(flip_code=0, marker_size_cm=10.0)
    hud = TelemetryHUD()
    navigator = Navigator() # Aquí viven tus PIDs

    driver.connect()
    time.sleep(3)

    print("\n[CONTROLES]")
    print(" 't' -> Despegar")
    print(" 'l' -> Aterrizar")
    print(" 'q' -> Aterrizar de emergencia y salir")

    while True:
        frame_crudo = driver.get_frame()
        if frame_crudo is None or not hasattr(frame_crudo, 'shape'): continue
            
        frame_limpio, ids, pos_cm = vision.update(frame_crudo)
        if frame_limpio is None: continue
        
        telem = driver.get_telemetry()
        
        # --- LÓGICA AISLADA DE SEGUIMIENTO ---
        cmd_roll, cmd_pitch = 0, 0
        estado = "HOVER (SIN OBJETIVO)"

        if pos_cm is not None:
            estado = "SIGUIENDO ARUCO"
            # Calculamos velocidades para X y Y
            cmd_roll, cmd_pitch = navigator.calculate_commands(pos_cm, telem["vel_x"], telem["vel_y"])
            
            # Enviar comandos al dron (Limitamos Z y Yaw a 0 para que no baje ni gire)
            driver.set_velocity(cmd_roll, cmd_pitch, throttle=0, yaw=0)
        else:
            # Si no ve nada, se queda quieto en el aire
            if driver.is_flying:
                driver.set_velocity(0, 0, 0, 0)
        
        # --- INTERFAZ ---
        frame_final = hud.draw(frame_limpio, telem, mission_state=estado, target_pos=pos_cm)
        cv2.imshow("Test Seguimiento", frame_final)

        # --- CONTROLES MANUALES ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('t'):
            driver.takeoff()
        elif key == ord('l') or key == ord('q'):
            driver.land()
            if key == ord('q'): break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()