import time

class PIDController:
    def __init__(self, kp, ki, kd, min_out, max_out):
        self.kp = kp  # Constante Proporcional (La fuerza bruta del movimiento)
        self.ki = ki  # Constante Integral (Corrige el error acumulado con el tiempo)
        self.kd = kd  # Constante Derivativa (Frena el dron para evitar que se pase de largo)
        
        self.min_out = min_out  # Velocidad mínima (ej. -100 en Tello)
        self.max_out = max_out  # Velocidad máxima (ej. 100 en Tello)
        
        self.prev_error = 0
        self.integral = 0
        self.prev_time = time.time()

    def update(self, setpoint, current_value):
        """
        Calcula la velocidad a la que debe moverse el dron.
        setpoint: Dónde queremos que esté (el centro de la imagen).
        current_value: Dónde está ahora (el centro del ArUco).
        """
        current_time = time.time()
        dt = current_time - self.prev_time
        
        # Evitar división por cero
        if dt <= 0.0:
            dt = 0.001
            
        error = setpoint - current_value
        
        # Proporcional
        p = self.kp * error
        
        # Integral
        self.integral += error * dt
        i = self.ki * self.integral
        
        # Derivativo
        derivada = (error - self.prev_error) / dt
        d = self.kd * derivada
        
        # Guardar valores para la siguiente iteración
        self.prev_error = error
        self.prev_time = current_time
        
        # Calcular salida total
        output = p + i + d
        
        # Limitar la salida a las velocidades máximas del dron (Clamping)
        output = max(self.min_out, min(self.max_out, output))
        
        return int(output)