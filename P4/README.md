# Práctica 4a y 4b de Visión por Computador

## Autoría

* Beatriz Chaves Marrero | https://github.com/bezz75
* Marcos Peña Armario | https://github.com/marcpear

## Descripción

Este repositorio contiene los cuardernos `VC_P4a.ipynb` y `VC_P4b.ipynb`, los cuales corresponden a la práctica 4a y 4b de la asignatura Visión por Computador. Se ejecutaron en Google Colab (GPU NVIDIA T4) para disponer de GPU.

Práctica 4a. Prototipo que procesa el vídeo de test para detectar y seguir personas y vehículos, detectar las matrículas de los vehículos, contar el total de cada clase y volcar a disco un vídeo anotado y un CSV. Combina dos detectores:

YOLO11n preentrenado (COCO) con el seguimiento BoT-SORT de Ultralytics, para personas, bicicletas, coches, motos, autobuses y camiones.
YOLO11n ajustado para matrículas, entrenado con UC3M-LP (una sola clase, license_plate).

Práctica 4b. Añade el reconocimiento del texto de las matrículas (OCR). Compara EasyOCR con SmolVLM y los integra en el pipeline, que genera el vídeo y los CSV con el texto leído.

<<Sección 4b: se revisará en el siguiente paso>>

## Dataset

Se ha usado un dataset externo [UC3M-LP](https://github.com/ramajoballester/UC3M-LP) que contiene fotografías nocturnas de 5184×3888 píxeles con varios coches por imagen (hasta dos matrículas por imagen), con una anotación .json por imagen que incluye el polígono de cada matrícula y su texto. Este dataset se ha preparado y tratado para su utilización en la práctica creando un script que hizo lo siguiente:

- Empareja cada imagen con su JSON por nombre de archivo.
- Convierte el polígono de cada matrícula en la caja delimitadora YOLO de la clase license_plate, normalizada con el tamaño de imagen indicado en el JSON.
- Conserva las particiones originales de entrenamiento y prueba y separa aleatoriamente (semilla 42) un 20 % del entrenamiento como validación.
- Genera el YAML de configuración y ground_truth.csv, con el texto de referencia y las coordenadas de cada matrícula para la práctica 4b. Los asteriscos del texto son caracteres ocultos o ilegibles y deben tratarse como comodines al evaluar el OCR.

Para reducir el tiempo de lectura de las imágenes en Colab, el cuaderno trabaja con una copia reducida a 1920 píxeles de ancho (UC3M_RS.zip); las etiquetas, al estar normalizadas, no cambian.

| Partición | Imágenes | Matrículas |
|---|---|---|
| Entrenamiento | 1264 | 1667 |
| Validación | 316 | 389 |
| Prueba | 395 | 491 |

El conjunto procesado (`UC3M_RS.zip`) se descarga automáticamente desde el cuaderno. <<Enlace de descarga>>

## Ejecución

Los cuadernos están preparados para Google Colab, para poder ejecutarlos se debe:

1. Abrir `VC_P4a.ipynb` o `VC_P4b.ipynb` en Google Colab.
2. Seleccionar un entorno de ejecución con GPU (la ejecución registrada se hizo con una T4).
3. Ejecutar las celdas en orden. Los cuadernos descargan el dataset, el vídeo y los pesos desde los enlaces de la sección de configuración, por lo que solo hay que descargar los cuadernos.

El entrenamiento del detector de matrículas (sección 4.1 de VC_P4a.ipynb) es opcional y tarda unos 60 minutos en una T4; si se omite, el cuaderno descarga los pesos ya entrenados (best.pt, 5,5 MB). <<Enlace a los pesos y/o ruta en el repositorio>>

Los parámetros principales del detector de matrículas (Práctica 4a):

* Modelo inicial: `yolo11n.pt`.
* Resolución de entrenamiento: 1280 píxeles.
* Épocas: 40, con paciencia de 10.
* Tamaño de lote: 4.
* Optimizador: AdamW con selección automática de Ultralytics (lr inicial 0,002)
* Clase: `license_plate`.

## Resultados

### Práctica 4A: Detección de vehículos y matrículas:

Se entrenó YOLO11n durante 40 épocas (59 minutos en una T4, unos 89 s por época). Las pérdidas de entrenamiento y validación descienden juntas y sin divergir: box_loss pasa de 1,11 a 0,47 en entrenamiento y de 1,02 a 0,48 en validación; cls_loss baja de 5,60 (primera época, con la cabeza de clasificación todavía sin ajustar) a 0,30; dfl_loss, de 1,02 a 0,83.

Al final la pérdida de validación es similar a la de entrenamiento, por lo que no se ve sobreajuste.

El mAP@0.5 supera 0,95 en la segunda época y se mantiene entre 0,97 y 0,99 desde la época 10. El mAP@0.5:0.95, que exige cajas más precisas, mejora de forma sostenida: 0,57 en la primera época, 0,79 en la décima, 0,85 en la vigésima y 0,89 en la última. Su media sube de 0,855 (épocas 21-30) a 0,876 (épocas 31-40), lo que coincide con el cierre del aumento mosaic en las últimas diez épocas y con el descenso del learning rate (de 1,9·10⁻³ a 7·10⁻⁵). La mejor época fue la 40 y la parada anticipada no se activó, así que más épocas podrían refinar algo más las cajas.

![Curvas del entrenamiento del detector de matrículas](Resultados_P4a/curvas_entrenamiento.png)

Estas métricas se miden sobre UC3M-LP (fotografías nocturnas con matrículas grandes), no sobre el vídeo de test, para el que no disponemos de anotaciones.

Ejemplo de detección de matrículas en un fotograma del vídeo:

![Detecciones de matrículas](Resultados_P4a/deteccion_matriculas.png)

La demostración de vídeo procesa un tramo de 30 segundos: las cajas verdes y sus 
identificadores corresponden al seguimiento de personas y vehículos; las cajas rojas 
muestran las matrículas detectadas.

[Descargar el vídeo de demostración P4a](Resultados_P4a/video_demostracion.mp4)

#### Pipeline sobre el vídeo de test

El vídeo (1920×1080, 25 fps, 2832 fotogramas) se procesa en dos pasadas:

1. **Detección y seguimiento.** YOLO11n preentrenado con BoT-SORT sobre personas, bicicletas, coches, motos, autobuses y camiones. Para cada vehículo se busca la matrícula **dentro de su recorte** con el detector entrenado (umbral 0,25 y entrada de 640 px), de esta manera la matrícula ocupa un tamaño parecido al visto en el entrenamiento, y queda asociada al identificador del vehículo.
2. **Salida.** Cada identificador recibe su clase más frecuente a lo largo del vídeo, y solo se cuentan los identificadores presentes en al menos 25 fotogramas, para no contar detecciones esporádicas. Se escribe el vídeo anotado a resolución original (cajas verdes con identificador y clase, cajas rojas para matrículas, contador en pantalla) y los CSV.

Archivos de salida: <<enlaces o rutas>>

* `salida_p4a.mp4`: vídeo anotado.
* `resultado_p4a.csv`: una fila por detección (9725 filas) con `fotograma, tipo_objeto, confianza, identificador_tracking, x1, y1, x2, y2, matricula, confianza_matricula, mx1, my1, mx2, my2, texto_matricula`. `matricula` indica si se detectó matrícula; `texto_matricula` queda vacío en 4a y lo rellena la práctica 4b.
* `resumen_vehiculos_p4a.csv`: una fila por identificador con su clase, primer y último fotograma, número de fotogramas, si es estable y si se detectó matrícula.

#### Conteo y validación manual

Contamos a mano los elementos del vídeo y los comparamos con el sistema:

| Clase | Manual | Sistema: identificadores totales | Sistema: estables (≥25 fotogramas) |
|---|---|---|---|
| Personas | 14 | 16 | 13 |
| Coches | 30 | 40 | 38 |
| Guaguas | 1 | 1 | 1 |
| Motos | 3 | 1 | 0 |
| Bicicletas | 2 | 1 | 0 |
| Matrículas (sin las 2 mátriculas de moto) | 27 | 31 | 31 |

El sistema detecta matrícula en 31 de los 39 vehículos estables.

#### Limitaciones

* **Coches sobrecontados** (38 frente a 30): el seguimiento pierde y recupera algunos vehículos, sobre todo los aparcados o parcialmente tapados, y les asigna identificadores nuevos. Esto también explica que haya más matrículas contadas (31) que visibles (27).
* **Motos y bicicletas infravaloradas**: cruzan rápido, aparecen pocos fotogramas y el filtro de 25 fotogramas las descarta. Además, el detector de matrículas no detecta las de las motos (el dataset es de coches y esas matrículas son pequeñas).
* **Matrículas lejanas**: a partir de cierta distancia la matrícula mide pocas decenas de píxeles y se pierde.
* **Métricas del detector** medidas en UC3M-LP, no en el vídeo; para el vídeo solo disponemos de la comparación de conteos anterior.

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
