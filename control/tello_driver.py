import time
from djitellopy import Tello
from control.pid_controller import PIDController
from control.kalman import KalmanPosicion

class TelloDriver:
    def __init__(self):
        # 1. Hardware
        self.drone = Tello()
        self.is_flying = False
        
        # 2. Controladores PID (Calculan qué tan rápido movernos)
        # Eje X: Izquierda / Derecha (Roll)
        self.pid_x = PIDController(kp=2, ki=0.0, kd=0.5, min_out=-50, max_out=50)
        # Eje Y: Adelante / Atrás (Pitch)
        self.pid_y = PIDController(kp=2, ki=0.0, kd=0.5, min_out=-50, max_out=50)
        
        # 3. Filtros de Kalman (Adivinan dónde estamos si perdemos la cámara)
        # Usamos dt=0.1 asumiendo un ciclo de visión a 10 fps
        self.kalman_x = KalmanPosicion(dt=0.1, std_acc=5.0, std_vision=2.0)
        self.kalman_y = KalmanPosicion(dt=0.1, std_acc=5.0, std_vision=2.0)

    def connect(self):
        """Inicia la conexión y el video."""
        self.drone.connect()
        print(f"[TELLO] Conectado. Batería: {self.drone.get_battery()}%")
        self.drone.streamon()

    def takeoff(self):
        if not self.is_flying:
            print("[TELLO] Iniciando despegue...")
            self.drone.takeoff()
            self.is_flying = True

    def land(self):
        if self.is_flying:
            print("[TELLO] Aterrizando...")
            self.drone.land()
            self.is_flying = False
            
    def hover(self):
        """Frena los motores y se queda quieto en el aire."""
        self.drone.send_rc_control(0, 0, 0, 0)

    def get_frame(self):
        """Retorna el frame crudo del dron."""
        frame_read = self.drone.get_frame_read()
        return frame_read.frame
      
    def track_target(self, pos_cm, is_target_visible):
        # Definimos el objetivo físico: queremos que el error en X y Y sea 0 centímetros
        setpoint_x_cm = 0.0
        setpoint_y_cm = 0.0
        
        # Velocidades actuales del dron (cm/s) leídas del IMU
        vel_x_drone = self.drone.get_speed_y()  
        vel_y_drone = self.drone.get_speed_x()  
        
        # 1. Predicción del Filtro de Kalman (siempre ocurre)
        est_x = self.kalman_x.predict(vel_x_drone)
        est_y = self.kalman_y.predict(vel_y_drone)
        
        # 2. Actualización con la cámara
        if is_target_visible and pos_cm is not None:
            aruco_x_cm, aruco_y_cm, aruco_z_cm = pos_cm
            
            # Inyectamos la distancia física real al filtro
            est_x = self.kalman_x.update(aruco_x_cm)
            est_y = self.kalman_y.update(aruco_y_cm)
            
        # 3. Cálculo del PID usando centímetros
        # Fíjate que el setpoint ahora es siempre 0.0
        cmd_roll = self.pid_x.update(setpoint_x_cm, est_x)
        cmd_pitch = self.pid_y.update(setpoint_y_cm, est_y)
        
        # Enviar comando a los motores
        if self.is_flying:
            self.drone.send_rc_control(cmd_roll, cmd_pitch, 0, 0)