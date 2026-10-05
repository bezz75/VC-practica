# Práctica 2 de Visión por Computador

## Autoría

* Beatriz Chaves Marrero | https://github.com/bezz75
* Marcos Peña Armario | https://github.com/marcpear

## Descripción

Este repositorio contiene el cuaderno "VC_P2.ipynb", correspondiente a la segunda práctica de la asignatura Visión por Computador, además de la imagen "mandril.jpg" la cual se usará en las diversas tareas del cuaderno.

El cuaderno incluye:

* La cuenta de píxeles blancos por filas determinando el valor máximo de píxeles blancos y mostrando el número de sus filas y sus respectivas posiciones.
* Aplicación de umbralizado a una imagen anterior resultante de Sobel y la realización posterior del conteo por filas y columnas calculando el valor máximo de la cuenta por filas y columnas. Además, comparativa con la versión de Canny.
* Propuesta propia de procesamiento la cual trabaja la censura de la piel con una difuminación en esa área.

## Ejecución

El cuaderno se puede abrir con Jupyter Notebook o Visual Studio Code con la extensión de Jupyter.

Instalaciones necesarias:

```bash
pip install opencv-python numpy matplotlib
```

Las tareas relacionadas con la cámara necesitan una webcam. Para finalizar las ventanas de OpenCV hay que pulsar 'ESC'.



## Resultados

**Tarea 1:** Realiza la cuenta de píxeles blancos por filas (en lugar de por columnas). Determina el valor máximo de píxeles blancos para filas, maxfil, mostrando el número de filas y sus respectivas posiciones, con un número de píxeles blancos mayor o igual que 0.90\*maxfil. Resalta con alguna primitiva gráfica en la imagen de Canny las filas que cumplen dicha condición.



**Resultado:** Al comienzo Se aplicó el detector de bordes de Canny y se contabilizó el porcentaje de píxeles blancos (contornos) por cada fila de la imagen. Para normalizar los datos se identificó la fila con mayor densidad de píxeles (maxfil) y se estableció un umbral de corte equivalente al 90% de ese valor. El algoritmo encontró un total de 9 filas que cumplían con esta condición, y las marcó dibujando líneas horizontales verdes directamente sobre la imagen binaria. Como complemento al análisis, se generó una gráfica que muestra la distribución de los píxeles blancos por fila y la ubicación del umbral límite.

![Resultado Tarea 1](Resultados/tarea1.png)

**Tarea 2:** Aplica umbralizado a la imagen resultante de Sobel (convertida a 8 bits), y posteriormente realiza el conteo por filas y columnas similar al realizado en el ejemplo con la salida de Canny de píxeles no nulos. Calcula el valor máximo de la cuenta por filas y columnas, y determina las filas y columnas por encima del 0.90\*máximo. Remarca con alguna primitiva gráfica dichas filas y columnas sobre la imagen del mandril. Visualiza los resultados obtenidos para la imagen (o una de tu elección) con Canny y Sobe tras umbralizar ¿Cómo se comparan los resultados obtenidos a partir de Sobel y Canny?



**Resultado:** Se aplicó un umbral (valor 90) a la imagen procesada con el operador de Sobel para binarizarla. A continuación, se realizó el recuento de píxeles blancos tanto por filas como por columnas. Se superó el umbral del 90% del máximo en 23 filas y en 5 columnas, las cuales fueron remarcadas en verde sobre la imagen.

Al comparar ambos métodos, se concluye que Canny proporciona contornos mucho más finos y definidos gracias a su algoritmo interno de histéresis (dos umbrales). Por el contrario, Sobel detecta cambios de intensidad de forma más bruta y su resultado final depende en gran medida del umbral manual que elijamos; en esta ejecución en particular, Sobel produjo bastante más "ruido" o líneas destacadas que Canny.

![Resultado Tarea 2.1](Resultados/tarea2_1.png)
![Resultado Tarea 2.2](Resultados/tarea2_2.png)

**Tarea 3:** Tras ver los vídeos My little piece of privacy, Messa di voce y Virtual air guitar] proponer un demostrador reinterpretando la parte de procesamiento de la imagen, tomando como punto de partida alguna de dichas instalaciones.



**Resultado:** Se desarrolló un demostrador inspirado en My Little Piece of Privacy que utiliza la webcam para censurar en tiempo real las regiones detectadas como piel. Para ello, cada fotograma se convierte al espacio de color HSV y se genera una máscara con los tonos seleccionados. Después, se extraen los contornos y se filtran por área, proporción entre anchura y altura y ocupación de sus filas y columnas. Las regiones que cumplen estas condiciones se difuminan con un filtro gaussiano y se muestran delimitadas en la imagen.

La combinación de proyecciones y filtros geométricos ayuda a descartar algunas regiones del fondo, como formas muy alargadas o poco compactas. Sin embargo, como la detección se basa en el color y la forma, no identifica la piel de manera infalible: otros elementos con características similares también podrían ser censurados.


![Resultado Tarea 3](Resultados/tarea3.png)




## Fuentes consultadas

* OpenCV, funciones de dibujo: https://docs.opencv.org/4.x/dc/da5/tutorial\_py\_drawing\_functions.html

* Niklas Roy - My Little piece of privacy:

&#x20;  https://www.niklasroy.com/project/88/my-little-piece-of-privacy

* Manual web de Matplotlib.pyplot:

&#x20;  https://matplotlib.org/stable/api/\_as\_gen/matplotlib.pyplot.plot.html



