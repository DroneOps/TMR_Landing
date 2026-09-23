import cv2

class TelemetryHUD:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.thickness = 2
        
        # Paleta de colores (BGR)
        self.color_text = (255, 255, 255)
        self.color_ok = (0, 255, 0)
        self.color_warning = (0, 255, 255)
        self.color_danger = (0, 0, 255)
        self.bg_color = (0, 0, 0)

    def draw(self, frame, telemetry, mission_state="INACTIVO", target_pos=None):
        if frame is None:
            return None
            
        # Extraer datos
        bat = telemetry.get("battery", 0)
        alt = telemetry.get("tof_cm", 0) # Usamos el ToF (Láser) por ser mejor para aterrizar
        is_flying = telemetry.get("is_flying", False)
        
        # 1. Dibujar fondo semi-transparente para lectura clara
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (320, 150), self.bg_color, -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        # 2. Dibujar Batería (Cambia de color si es baja)
        c_bat = self.color_ok if bat > 20 else self.color_danger
        cv2.putText(frame, f"BATERIA: {bat}%", (10, 30), self.font, self.font_scale, c_bat, self.thickness)

        # 3. Dibujar Altura y Estado Físico
        c_flight = self.color_ok if is_flying else self.color_warning
        cv2.putText(frame, f"ALTURA: {alt} cm", (10, 60), self.font, self.font_scale, self.color_text, self.thickness)
        cv2.putText(frame, f"MOTORES: {'ON' if is_flying else 'OFF'}", (160, 60), self.font, self.font_scale, c_flight, self.thickness)

        # 4. Dibujar Estado de la Misión (La variable que querías añadir)
        cv2.putText(frame, f"ESTADO: {mission_state}", (10, 90), self.font, 0.7, self.color_warning, 2)

        # 5. Dibujar Info del Objetivo (ArUco)
        if target_pos is not None:
            x, y, z = target_pos
            cv2.putText(frame, f"ARUCO -> X:{x:.1f} Y:{y:.1f} Z:{z:.1f}", (10, 130), self.font, self.font_scale, self.color_ok, self.thickness)
        else:
            cv2.putText(frame, "ARUCO -> NO DETECTADO", (10, 130), self.font, self.font_scale, self.color_danger, self.thickness)

        return frame