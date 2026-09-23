import time

class MisionState:
    ESPERA = "ESPERA"
    DESPEGUE = "DESPEGUE"
    BUSQUEDA = "BUSQUEDA"
    SEGUIMIENTO = "SEGUIMIENTO"
    DESCENSO = "DESCENSO"
    PUNTO_CIEGO = "PUNTO_CIEGO"
    ATERRIZAJE = "ATERRIZAJE"

class StateMachine:
    def __init__(self):
        self.state = MisionState.ESPERA
        self.last_state_time = time.time()
        
        # Contadores de tiempo para Histéresis (Anti-rebote)
        self.time_target_visible = 0.0
        self.time_target_lost = 0.0
        self.time_centered = 0.0
        
        # Parámetros de tolerancia
        self.error_max_cm = 15.0  # Radio máximo aceptable para considerar que estamos centrados
        self.altura_touchdown_cm = 15.0  # A qué altura del ToF cortamos motores

    def set_state(self, new_state):
        """Cambia el estado y reinicia el cronómetro del estado."""
        if self.state != new_state:
            print(f"[FSM] Cambio de estado: {self.state} -> {new_state}")
            self.state = new_state
            self.last_state_time = time.time()

    def update(self, is_visible, pos_cm, tof_cm):
        """
        El núcleo de la toma de decisiones.
        is_visible: Booleano. ¿Vemos el ArUco en este frame?
        pos_cm: Tupla (X, Y, Z) del PnP (Visión). Puede ser None.
        tof_cm: Distancia del sensor láser del Tello al piso/plataforma.
        """
        current_time = time.time()
        time_in_state = current_time - self.last_state_time

        # 1. ACTUALIZAR CRONÓMETROS DE VISIÓN (Histéresis)
        if is_visible:
            if self.time_target_visible == 0.0:
                self.time_target_visible = current_time
            self.time_target_lost = 0.0  # Reiniciar contador de pérdida
        else:
            if self.time_target_lost == 0.0:
                self.time_target_lost = current_time
            self.time_target_visible = 0.0  # Reiniciar contador de visión
            self.time_centered = 0.0        # Si no lo vemos, no estamos centrados

        # Calcular cuánto tiempo llevamos viendo o perdiendo el objetivo
        duracion_visible = current_time - self.time_target_visible if is_visible else 0.0
        duracion_perdido = current_time - self.time_target_lost if not is_visible else 0.0

        # 2. EVALUAR TRANSICIONES SEGÚN EL ESTADO ACTUAL
        if self.state == MisionState.ESPERA:
            # La transición a DESPEGUE se hace manualmente desde main.py
            pass

        elif self.state == MisionState.DESPEGUE:
            # Damos 4 segundos para que el dron suba y se estabilice
            if time_in_state > 4.0:
                self.set_state(MisionState.BUSQUEDA)

        elif self.state == MisionState.BUSQUEDA:
            # Si vemos el ArUco por medio segundo continuo, empezamos a seguirlo
            if is_visible and duracion_visible > 0.5:
                self.set_state(MisionState.SEGUIMIENTO)

        elif self.state == MisionState.SEGUIMIENTO:
            if not is_visible and duracion_perdido > 2.0:
                # Lo perdimos por mucho tiempo, abortar seguimiento y volver a buscar
                self.set_state(MisionState.BUSQUEDA)
            
            elif is_visible and pos_cm is not None:
                x_cm, y_cm, z_cm = pos_cm
                
                # Checar si estamos centrados
                if abs(x_cm) < self.error_max_cm and abs(y_cm) < self.error_max_cm:
                    if self.time_centered == 0.0:
                        self.time_centered = current_time
                    
                    # Si llevamos 2 segundos perfectamente centrados, ¡podemos bajar!
                    if (current_time - self.time_centered) > 2.0:
                        self.set_state(MisionState.DESCENSO)
                else:
                    self.time_centered = 0.0 # Nos salimos del centro

        elif self.state == MisionState.DESCENSO:
            # Ya estamos bajando guiados por el PID usando el PnP (Z de visión)
            
            if not is_visible:
                # Entramos al punto ciego o lo perdimos de verdad
                if tof_cm < 40.0: 
                    # Estamos muy cerca del suelo/plataforma. Seguro es el punto ciego.
                    self.set_state(MisionState.PUNTO_CIEGO)
                elif duracion_perdido > 1.5:
                    # Estábamos altos y se perdió. Abortar descenso.
                    self.set_state(MisionState.BUSQUEDA)
            
            elif tof_cm < self.altura_touchdown_cm:
                # Vemos el ArUco pero el láser ya marca que estamos a punto de chocar
                self.set_state(MisionState.ATERRIZAJE)

        elif self.state == MisionState.PUNTO_CIEGO:
            # Ya no usamos visión, solo bajamos a ciegas leyendo el ToF
            if tof_cm < self.altura_touchdown_cm:
                self.set_state(MisionState.ATERRIZAJE)
            elif duracion_perdido > 4.0:
                # Llevamos mucho tiempo en punto ciego y no tocamos tierra. Abortar.
                self.set_state(MisionState.BUSQUEDA)

        elif self.state == MisionState.ATERRIZAJE:
            # Estado terminal, no hay salida de aquí. El main.py apagará los motores.
            pass

        return self.state