from djitellopy import Tello

class TelloDriver:
    def __init__(self):
        self.drone = Tello()
        self.is_flying = False

    def connect(self):
        self.drone.connect()
        print(f"[HW] Tello Conectado. Batería: {self.drone.get_battery()}%")
        self.drone.streamon()

    def takeoff(self, extra_height_cm=0):
        if not self.is_flying:
            self.drone.takeoff()
            self.is_flying = True
            
            # Si queremos que suba más después de despegar
            if extra_height_cm > 0:
                print(f"[HW] Subiendo {extra_height_cm} cm adicionales...")
                # move_up acepta valores entre 20 y 500 cm
                self.drone.move_up(extra_height_cm)

    def land(self):
        if self.is_flying:
            self.drone.land()
            self.is_flying = False

    def get_frame(self):
        return self.drone.get_frame_read().frame

    def get_speeds(self):
        """Retorna la velocidad actual en X (lateral) y Y (frontal) en cm/s"""
        vel_x = self.drone.get_speed_y()  
        vel_y = self.drone.get_speed_x()  
        return vel_x, vel_y

    def set_velocity(self, roll, pitch, throttle=0, yaw=0):
        """Envía las velocidades físicas a los motores"""
        if self.is_flying:
            self.drone.send_rc_control(roll, pitch, throttle, yaw)
        else:
            print(f"[HW Simulación] Motores apagados. Comando: Roll={roll}, Pitch={pitch}")
            
    def get_telemetry(self):
        """Devuelve un diccionario con el estado actual de los sensores del hardware."""
        return {
            "battery": self.drone.get_battery(),
            "height_cm": self.drone.get_height(),      # Altura barométrica
            "tof_cm": self.drone.get_distance_tof(),   # Altura por láser (muy precisa a baja altura)
            "vel_x": self.drone.get_speed_y(),         # Lateral
            "vel_y": self.drone.get_speed_x(),         # Frontal
            "vel_z": self.drone.get_speed_z(),         # Vertical
            "is_flying": self.is_flying
        }