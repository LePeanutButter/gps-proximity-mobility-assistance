"""
main.py
Punto de entrada del firmware para ESP32 (MicroPython).
En Wokwi, este es el archivo que se ejecuta automaticamente al
iniciar la simulacion.
"""

from controller import Controller
from models import Destination


def main():
    controller = Controller()

    # Ejemplo opcional: fijar un destino de prueba.
    # Comenta estas dos lineas si solo quieres probar deteccion de obstaculos.
    destino_prueba = Destination("Parada de bus", latitude=4.6486, longitude=-74.0637)
    controller.set_destination(destino_prueba)

    controller.run()


if __name__ == "__main__":
    main()
