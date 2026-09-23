import sys
import os
import cv2
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from control.tello_driver import TelloDriver
from vision.vision_system import VisionSystem
from ui.telemetry_hud import TelemetryHUD
from logic.state_machine import StateMachine, MisionState

def main():
    print("--- PRUEBA EN SECO: MÁQUINA DE ESTADOS ---")
    print("Mueve el dron con la mano para engañar a los sensores y ver si los estados cambian.")
    
    driver = TelloDriver()
    vision = VisionSystem(flip_code=0, marker_size_cm=10.0)
    hud = TelemetryHUD()
    fsm = StateMachine()

    driver.connect()
    time.sleep(3)
    
    # Engañamos a la FSM pasándola directo a BÚSQUEDA para saltarnos la espera del despegue
    fsm.set_state(MisionState.BUSQUEDA)

    while True:
        frame_crudo = driver.get_frame()
        if frame_crudo is None or not hasattr(frame_crudo, 'shape'): continue
            
        # 1. Obtenemos lo que "ve" el dron
        frame_limpio, ids, pos_cm = vision.update(frame_crudo)
        if frame_limpio is None: continue
        
        # 2. Obtenemos lo que "siente" el dron
        telem = driver.get_telemetry()
        
        is_visible = (pos_cm is not None)
        
        # 3. ALIMENTAMOS AL CEREBRO (FSM)
        # Le pasamos la visión y la altura del láser. 
        # La FSM decidirá en qué estado estamos.
        estado_actual = fsm.update(is_visible, pos_cm, telem["tof_cm"])
        
        # 4. MOSTRAMOS EL RESULTADO
        frame_final = hud.draw(frame_limpio, telem, mission_state=estado_actual, target_pos=pos_cm)
        cv2.imshow("FSM Dry Run", frame_final)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()