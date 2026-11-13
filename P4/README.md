# Práctica 4a y 4b de Visión por Computador

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

La práctica 4b añade el reconocimiento del texto de las matrículas (OCR). Comparamos EasyOCR con SmolVLM y los integra en un pipeline que genera un vídeo demostrando los resultados y archivos CSV con detecciones por fotograma y un resumen por vehículo.


## Dataset

Se ha usado un dataset externo [UC3M-LP](https://github.com/ramajoballester/UC3M-LP) que contiene imágenes `.jpg` de las matrículas y sus anotaciones `.json`, este dataset se ha preparado y tratado para su utilización en la práctica de la siguiente manera:

Se elaboró un script que basicamente empareja cada imagen con su JSON por nombre de archivo y convierte el polígono de cada matrícula en una caja delimitadora YOLO de la clase `license_plate`. Las coordenadas se normalizan con las dimensiones indicadas en el JSON y las imágenes sin matrículas reciben un archivo de etiqueta vacío.

Se conservan las particiones originales de entrenamiento y prueba. Como no hay un conjunto de validación, se separa aleatoriamente un 20 % del entrenamiento.

El conversor también genera el YAML de configuración y `ground_truth.csv`, que guarda el texto de referencia y las coordenadas de las matrículas para la práctica de OCR.

Los asteriscos representan caracteres ocultos y deben tratarse como comodines al evaluar el OCR.

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

En cuanto a la práctica 4b se ha seleccionado con una semilla (42) cien matrículas del conjunto de prueba con un máximo de dos carácteres ocultos en total, posteriormente, se comparan las lecturas de EasyOCR y SmolVLM sobre los mismos recortes:

* Para EasyOCR se prueban la imagen original y variantes ampliadas con CLAHE

* Con SmolVLM se evalúa con una indicaciónn general y otra que describe los formatos de matrícula españoles

## Resultados

### Práctica 4A: Detección de vehículos y matrículas:

**Entrenamiento y evaluación:** El mejor peso del entrenamiento obtuvo en validación 
una precisión de **0,984**, un recall de **0,982**, mAP@0.5 de **0,984** y mAP@0.5:0.95 
de **0,882**. En el conjunto de prueba, con 395 imágenes y 491 matrículas anotadas, 
obtuvo precisión **0,953**, recall **0,960**, mAP@0.5 **0,987** y mAP@0.5:0.95 **0,
865**. La inferencia registrada en el conjunto de prueba fue de 58,4 ms por imagen, con 
entrada de 1280 píxeles y GPU T4.

![Curvas del entrenamiento del detector de matrículas](Resultados_P4a/curvas_entrenamiento.png)

Ejemplo de detección de matrículas en un fotograma del vídeo:

![Detecciones de matrículas](Resultados_P4a/deteccion_matriculas.png)

La demostración de vídeo procesa un tramo de 30 segundos: las cajas verdes y sus 
identificadores corresponden al seguimiento de personas y vehículos; las cajas rojas 
muestran las matrículas detectadas.

[Descargar el vídeo de demostración P4a](Resultados_P4a/video_demostracion.mp4)

### Práctica 4b: Reconocimiento de caracteres en matrículas:

**Entrenamiento y evaluación:** La evaluación de OCR mide el acierto exacto, el acierto tolerante a los caracteres censurados, la tasa de error de caracteres y el tiempo por matrícula.

Para procesar el video, el detector de matrículas se ejecuta sobre el fotograma completo, con el mismo tamaño que en el entrenamiento, cada matrícula se asocia al vehículo cuya caja contiene el centro de la matrícula, además, si hay varias cajas candidatas, se elige la del vehículo con menor tamaño, esto lo hacemos para evitar detectar primero sobre el recorte del vehículo, donde la escala de la matrícula no coincide con la usada en la del entrenamiento.

El OCR comprueba que las lecturas encajen en el formato de las matrículas y corrige algunas confusiones entre letras y números, se limita el número de intentos por vehículo y se combinan varias lecturas válidas mediante una votación ponderada, por último, las lecturas que no encajan en un formato válido se descartan.

[Descargar el vídeo de demostración P4b](Resultados_P4b/video_demostracion_b.mp4)


## Fuentes consultadas

* [Documentación oficial de Ultralytics YOLO11](https://docs.ultralytics.com/models/yolo11/)
* [UC3M-LP: dataset de detección y reconocimiento de matrículas](https://github.com/ramajoballester/UC3M-LP)
* Ramajo-Ballester, A., Armingol, J. M. y de la Escalera, A. [Dual license plate recognition and visual features encoding for vehicle identification](https://doi.org/10.1016/j.robot.2023.104608)
* [EasyOCR](https://github.com/JaidedAI/EasyOCR)
* [SmolVLM-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-Instruct)


## Uso de IA

Para la realización de esta práctica se utilizó la IA de manera didáctica y como forma de comprobar y contrastar resultados, además, todo código proporcionado por la IA fue revisado y comprobado antes de la entrega.

