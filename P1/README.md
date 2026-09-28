# Práctica 1 de Visión por Computador

## Autoría

- Beatriz Chaves Marrero
- Marcos Peña Armario

## Descripción

Este repositorio contiene el cuaderno `VC_P1.ipynb`, correspondiente a la primera práctica de la asignatura Visión por Computador.

El cuaderno incluye:

- Creación manual de una textura de tablero de ajedrez.
- Creación de una imagen estilo Mondrian mediante rectángulos de OpenCV.
- Detección del píxel más claro y más oscuro de los fotogramas de la cámara.
- Comparación entre una solución manual y una solución optimizada con `cv2.minMaxLoc`.
- Propuesta propia de pop art basada en la cámara, un collage de cuatro ventanas y círculos cuyo radio depende de la intensidad de cada zona.

## Ejecución

El cuaderno se puede abrir con Jupyter Notebook o Visual Studio Code con la extensión de Jupyter.

Instalaciones necesarias:

```bash
pip install opencv-python numpy matplotlib
```

La propuesta de pop art y las tareas relacionadas con la cámara necesitan una webcam. Para finalizar las ventanas de OpenCV hay que pulsar `ESC`.

## Fuentes consultadas

- OpenCV, funciones de dibujo: https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html
- OpenCV, `minMaxLoc`: https://docs.opencv.org/4.x/d2/de8/group__core__array.html#gaedb9f7d6c218f3f3d3f4c8f2c4e2c4c4
- Referencia sobre Andy Warhol y su obra: https://temasycomentariosartepaeg.blogspot.com/p/autor-andy-warhol-1928-1987-titulo.html
- Referencia sobre Mondrian: https://www3.gobiernodecanarias.org/medusa/ecoescuela/sa/2017/04/17/descubriendo-a-mondrian/

También se incluye dentro del cuaderno la conversación de IA utilizada como apoyo para resolver dudas sobre la fluidez de la cámara y la propuesta de pop art. La IA se utilizó como apoyo y el resultado fue revisado y adaptado por los autores.
