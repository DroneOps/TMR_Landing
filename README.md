# TMR Landing Challenge - TELLO

Este proyecto implementa un sistema de aterrizaje autónomo sobre una plataforma móvil para el Torneo Mexicano de Robótica (TMR) - Categoría Drones Autónomos.

El sistema utiliza un dron **DJI Tello** equipado con un espejo a 45 grados para simular una cámara cenital, visión por computadora (OpenCV) para detectar **Marcadores ArUco**, y controladores PID para la alineación dinámica.

## Hardware y Modificaciones

- **Dron:** DJI Tello.
- **Modificación Óptica:** Espejo montado a 45° frente a la cámara frontal para redirigir la visión hacia abajo. _(Nota: El software compensa la inversión de imagen generada por el espejo)._
- **Objetivo:** Marcador ArUco impreso y colocado sobre una plataforma móvil/fija.
- **Procesamiento:** Computadora base ejecutando el script (vía WiFi al Tello).

## Arquitectura del Proyecto

El proyecto está diseñado de forma modular para separar la visión artificial, el control de vuelo y la toma de decisiones:

```text
tello_aruco_landing/
│
├── main.py                   # Punto de entrada. Inicializa los módulos y corre el bucle principal.
│
├── config/
│   └── settings.json         # Constantes: velocidades máximas, ID del ArUco, tamaño del marcador, ganancias PID.
│
├── vision/
│   ├── image_processor.py    # Captura y corrección de frame (enderezar e invertir la imagen del espejo).
│   └── aruco_tracker.py      # Detección del ArUco y estimación de pose (X, Y, Z, rotación).
│
├── control/
│   ├── tello_driver.py       # Wrapper de djitellopy (conexión, despegue, comandos de velocidad).
│   └── pid_controller.py     # Controladores PID para suavizar y calcular la velocidad de alineación.
│
├── logic/
│   └── state_machine.py      # Máquina de estados: BUSCAR, ALINEAR, SEGUIR, ATERRIZAR.
│
├── tests/
│   ├── test_vision_only.py   # Pruebas de cámara y corrección de espejo (sin encender motores).
│   ├── test_pid.py           # Simulación para afinar las ganancias del PID.
│   └── test_telemetry.py     # Lectura de batería y sensores del Tello.
│
└── logs/                     # Archivos de depuración y grabación de video de las pruebas.
```

## ¿Por qué esta estructura?

1. **Aislamiento del Hardware (Espejo):** Toda la corrección geométrica del espejo ocurre exclusivamente en `image_processor.py`. El resto del sistema recibe imágenes y coordenadas limpias.
2. **Máquina de Estados:** Aterrizar sobre un objetivo móvil requiere fases claras. `state_machine.py` previene que el dron intente descender antes de haber igualado la velocidad de la plataforma.
3. **Entorno de Pruebas Seguro:** La carpeta `tests/` permite probar la detección visual con el dron en mano, minimizando el riesgo de accidentes antes de los vuelos reales.

## Próximos Pasos (To-Do)

- [✓] Escribir el módulo de corrección de imagen (`image_processor.py`) y probarlo con `test_vision.py`.
- [ ] Escribir logica de la máquina de estados.
- [ ] Escribir controlador PID.
- [ ] Escribir modulo de telemetria y registro de logs.
- [ ] Implementar modulos en el programa principal
