# Práctica 3 de Visión por Computador

## Autoría

* Beatriz Chaves Marrero | https://github.com/bezz75
* Marcos Peña Armario | https://github.com/marcpear

## Descripción

Este repositorio contiene los cuardernos `VC_P4a.ipynb` y `VC_P4b.ipynb`, los cuales corresponden a la práctica 4a y 4b de la asignatura Visión por Computador.

Para la realización de la práctica se uso Google Colab a modo de ejecución para proporcionar un entorno que nos permitiera usar una GPU en lugar de nuestras CPU.

Respecto a la práctica 4a combinamos dos detectores:

- Un modelo YOLO11n preentrenado para localizar personas y vehículos en el vídeo.
- Un detector YOLO11n ajustado para localizar matrículas, entrenado con UC3M-LP.

El cuaderno verifica visualmente las anotaciones, entrena y evalúa el detector de matrículas y muestra una demostración de vídeo anotada.

FALTA 4b AQUI


## Ejecución

Los cuadernos están preparados para Google Colab, para poder ejecutarlos se debe:

1. Abrir `VC_P4a.ipynb` o `VC_P4b.ipynb` en Google Colab.
2. Seleccionar un entorno de ejecución con GPU; la ejecución registrada se hizo con una NVIDIA T4.
3. Ejecutar las celdas en orden. El cuaderno descarga el dataset y el vídeo desde los enlaces configurados en la sección de rutas, así que solamente se deben descargar los cuadernos

Para repetir la ejecución, los enlaces de descarga del dataset, el vídeo y opcionalmente los pesos deben seguir teniendo acceso compartido.

Los parámetros principales del detector de matrículas (Práctica 4a):

* Modelo inicial: `yolo11n.pt`.
* Resolución de entrenamiento: 1280 píxeles.
* Épocas: 30, con paciencia de 10.
* Tamaño de lote: 4.
* Clase detectada: `license_plate`.

FALTA 4b AQUÍ

## Resultados

**Preparación del dataset**: FALTA LA PREPARACIÓN

### Práctica 4A: Detección de vehículos y matrículas:

**Entrenamiento y evaluación:** el mejor peso del entrenamiento obtuvo en validación una precisión de **0,984**, un recall de **0,982**, mAP@0.5 de **0,984** y mAP@0.5:0.95 de **0,882**. En el conjunto de prueba, con 395 imágenes y 491 matrículas anotadas, obtuvo precisión **0,953**, recall **0,960**, mAP@0.5 **0,987** y mAP@0.5:0.95 **0,865**. La inferencia registrada en el conjunto de prueba fue de 58,4 ms por imagen, con entrada de 1280 píxeles y GPU T4.

![Curvas del entrenamiento del detector de matrículas](Resultados_P4a/curvas_entrenamiento.png)

Ejemplo de detección de matrículas en un fotograma del vídeo:

![Detecciones de matrículas](Resultados_P4a/deteccion_matriculas.png)

La demostración de vídeo procesa un tramo de 30 segundos: las cajas verdes y sus identificadores corresponden al seguimiento de personas y vehículos; las cajas rojas muestran las matrículas detectadas.

[Ver o descargar el vídeo de demostración](Resultados_P4a/video_demostracion.mp4)


## Fuentes consultadas

* [Documentación oficial de Ultralytics YOLO11](https://docs.ultralytics.com/models/yolo11/)
* [UC3M-LP: dataset de detección y reconocimiento de matrículas](https://github.com/ramajoballester/UC3M-LP)
* Ramajo-Ballester, A., Armingol, J. M. y de la Escalera, A. [Dual license plate recognition and visual features encoding for vehicle identification](https://doi.org/10.1016/j.robot.2023.104608). *Robotics and Autonomous Systems*, 172, 104608 (2024).


## Uso de IA

Para la realización de esta práctica se utilizó la IA de manera didáctica y como forma de comprobar y contrastar resultados, además, todo código proporcionado por la IA fue revisado y combrobado antes de la entrega.

