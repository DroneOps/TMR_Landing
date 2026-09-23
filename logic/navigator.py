import sys
import os

# Asegurar que Python encuentre los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from control.pid_controller import PIDController
from control.kalman import KalmanPosicion


class Navigator:
    def __init__(self):
        # Controladores PID para X (Roll) y Y (Pitch)
        self.pid_x = PIDController(kp=1.75, ki=0.0, kd=0.4, min_out=-50, max_out=50)
        self.pid_y = PIDController(kp=1.9, ki=0.0, kd=0.4, min_out=-50, max_out=50)
        
        # Filtros de Kalman
        self.kalman_x = KalmanPosicion(dt=0.1, std_acc=5.0, std_vision=2.0)
        self.kalman_y = KalmanPosicion(dt=0.1, std_acc=5.0, std_vision=2.0)
        
        # Objetivo (El centro perfecto)
        self.setpoint_x = 0.0
        self.setpoint_y = 0.0

    def calculate_commands(self, pos_cm, drone_speed_x, drone_speed_y):
        """
        Recibe la posición del objetivo y la velocidad actual del dron.
        Devuelve (cmd_roll, cmd_pitch).
        """
        # 1. Predecir siempre (incluso si no vemos el ArUco)
        est_x = self.kalman_x.predict(drone_speed_x)
        est_y = self.kalman_y.predict(drone_speed_y)
        
        # 2. Actualizar si tenemos visión
        if pos_cm is not None:
            aruco_x_cm, aruco_y_cm, aruco_z_cm = pos_cm
            est_x = self.kalman_x.update(aruco_x_cm)
            est_y = self.kalman_y.update(aruco_y_cm)
            
        # 3. Calcular fuerzas
        cmd_roll = self.pid_x.update(self.setpoint_x, est_x)
        cmd_pitch = self.pid_y.update(self.setpoint_y, est_y)
        
        return cmd_roll, -cmd_pitch