"""
Funciones comunes a los dos prototipos (filtro de emociones y Fruit Ninja):
cámara, detectores de MediaPipe, carga de imágenes y colocación de PNG con
transparencia sobre la cara.
"""
import math
import os
import time
from pathlib import Path
from urllib.request import urlretrieve

import cv2
import mediapipe as mp
import numpy as np

CARPETA_MODELOS = Path(__file__).resolve().parent.parent / "modelos"
URL_MODELOS = {
    "face_landmarker.task": "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
                            "face_landmarker/float16/1/face_landmarker.task",
    "hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
                            "hand_landmarker/float16/1/hand_landmarker.task",
}

# Esquinas exteriores de los ojos (con la imagen en espejo, el 33 queda a la izquierda)
OJO_IZQ, OJO_DER = 33, 263


# ---------------------------------------------------------------- archivos

def leer_png(ruta):
    """Lee un PNG conservando la transparencia. cv2.imread no admite rutas con ñ
    en Windows, así que se leen los bytes y OpenCV solo los decodifica."""
    if not os.path.exists(ruta):
        return None
    return cv2.imdecode(np.fromfile(ruta, dtype=np.uint8), cv2.IMREAD_UNCHANGED)


def ruta_modelo(nombre):
    """Ruta a un modelo de MediaPipe en P5/modelos. Si no está, se descarga."""
    ruta = CARPETA_MODELOS / nombre
    if not ruta.exists():
        CARPETA_MODELOS.mkdir(exist_ok=True)
        print(f"Descargando {nombre}...")
        temporal = ruta.with_suffix(".tmp")      # así no queda un archivo a medias si se corta
        urlretrieve(URL_MODELOS[nombre], temporal)
        temporal.replace(ruta)
    return ruta


# ---------------------------------------------------------------- MediaPipe

def crear_detector_cara(num_caras=1):
    """Face Landmarker en modo VIDEO. El modelo se pasa en bytes porque
    MediaPipe tampoco abre rutas con ñ en Windows."""
    opciones = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_buffer=ruta_modelo("face_landmarker.task").read_bytes()),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_faces=num_caras,
    )
    return mp.tasks.vision.FaceLandmarker.create_from_options(opciones)


def crear_detector_manos(num_manos=1):
    opciones = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_buffer=ruta_modelo("hand_landmarker.task").read_bytes()),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=num_manos,
    )
    return mp.tasks.vision.HandLandmarker.create_from_options(opciones)


class Reloj:
    """Marcas de tiempo en ms para el modo VIDEO, que deben ser siempre crecientes."""
    def __init__(self):
        self.inicio = time.monotonic()
        self.ultimo = -1

    def ms(self):
        self.ultimo = max(self.ultimo + 1, int((time.monotonic() - self.inicio) * 1000))
        return self.ultimo


def imagen_mediapipe(frame):
    """Frame de OpenCV (BGR) -> imagen de MediaPipe (RGB)."""
    return mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


def a_pixeles(landmarks, ancho, alto):
    """Landmarks normalizados (0-1) -> lista de puntos (x, y) en píxeles."""
    return [(int(lm.x * ancho), int(lm.y * alto)) for lm in landmarks]


# ---------------------------------------------------------------- cámara y teclado

def abrir_camara(indice=0, ancho=640, alto=480):
    camara = cv2.VideoCapture(indice)
    if not camara.isOpened():
        camara.release()
        raise RuntimeError("No se pudo abrir la webcam.")
    camara.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
    return camara


def hay_que_salir(tecla, ventana):
    """Q o Esc, o cerrar la ventana con la X."""
    return tecla in (ord("q"), ord("Q"), 27) or cv2.getWindowProperty(ventana, cv2.WND_PROP_VISIBLE) < 1


# ---------------------------------------------------------------- geometría y dibujo

def geometria_cara(pts):
    """
    A partir de los ojos calcula:
      escala: distancia entre ojos en píxeles (unidad para posiciones y tamaños)
      angulo: inclinación de la cabeza en grados
      u, v:   vectores unitarios hacia la derecha y hacia abajo de la cara
    """
    a = np.array(pts[OJO_IZQ], dtype=np.float32)
    b = np.array(pts[OJO_DER], dtype=np.float32)
    d = b - a
    escala = float(np.hypot(d[0], d[1]))
    angulo = math.degrees(math.atan2(d[1], d[0]))
    u = d / escala
    v = np.array([-u[1], u[0]])
    return escala, angulo, u, v


def escalar(img, ancho_objetivo):
    """Redimensiona manteniendo la proporción."""
    h, w = img.shape[:2]
    ancho = max(1, int(ancho_objetivo))
    alto = max(1, int(ancho * h / w))
    interp = cv2.INTER_AREA if ancho < w else cv2.INTER_LINEAR
    return cv2.resize(img, (ancho, alto), interpolation=interp)


def rotar(img, angulo):
    """Rota la imagen ampliando el lienzo para que no se corten las esquinas."""
    h, w = img.shape[:2]
    centro = (w / 2, h / 2)
    # OpenCV gira en sentido antihorario y nuestro ángulo es horario, de ahí el signo
    M = cv2.getRotationMatrix2D(centro, -angulo, 1.0)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nuevo_w, nuevo_h = int(w * cos + h * sin), int(w * sin + h * cos)
    M[0, 2] += nuevo_w / 2 - centro[0]
    M[1, 2] += nuevo_h / 2 - centro[1]
    return cv2.warpAffine(img, M, (nuevo_w, nuevo_h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def pegar_sticker(frame, sticker, cx, cy, opacidad=1.0):
    """Mezcla un PNG con transparencia centrado en (cx, cy). Si se sale del frame
    solo se pega la parte visible."""
    H, W = frame.shape[:2]
    h, w = sticker.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))

    # Zona del frame donde cae el sticker
    fx0, fy0 = max(x0, 0), max(y0, 0)
    fx1, fy1 = min(x0 + w, W), min(y0 + h, H)
    if fx0 >= fx1 or fy0 >= fy1:
        return

    # Parte del sticker que corresponde a esa zona
    trozo = sticker[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]

    alfa = trozo[:, :, 3:4].astype(np.float32) / 255.0 * opacidad
    color = trozo[:, :, :3].astype(np.float32)
    fondo = frame[fy0:fy1, fx0:fx1].astype(np.float32)
    frame[fy0:fy1, fx0:fx1] = (alfa * color + (1 - alfa) * fondo).astype(np.uint8)


def colocar_sticker(frame, sticker, centro, ancho_px, angulo, opacidad=1.0):
    """Escala, rota y pega un PNG con su centro en 'centro'."""
    s = escalar(sticker, ancho_px)
    s = rotar(s, angulo)
    pegar_sticker(frame, s, centro[0], centro[1], opacidad)
