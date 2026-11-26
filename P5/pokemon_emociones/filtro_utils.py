"""
Herramientas reutilizables para los filtros.
Se importa desde otros scripts:  from filtro_utils import ...
"""
import math
import cv2
import numpy as np

# Índices de landmarks (comprobados en el paso 1: con espejo, el 33 queda a la izquierda)
OJO_IZQ, OJO_DER = 33, 263
FRENTE, BARBILLA, NARIZ = 10, 152, 1
MEJILLA_IZQ, MEJILLA_DER = 50, 280
LABIO_SUP, LABIO_INF = 13, 14
PARPADO_IZQ, PARPADO_DER = 145, 374


# ---------------- PASO 2: medir la cara ----------------
def geometria_cara(pts):
    """Devuelve escala (px), angulo (grados), u (derecha de la cara), v (abajo de la cara)."""
    a = np.array(pts[OJO_IZQ], dtype=np.float32)
    b = np.array(pts[OJO_DER], dtype=np.float32)
    d = b - a
    escala = float(np.hypot(d[0], d[1]))
    angulo = math.degrees(math.atan2(d[1], d[0]))
    u = d / escala
    v = np.array([-u[1], u[0]])
    return escala, angulo, u, v


def punto_en_cara(pts, ancla, escala, u, v, a=0.0, b=0.0):
    """Punto desplazado desde un landmark 'ancla' en coordenadas de la cara:
    a escalas hacia la derecha de la cara y b escalas hacia abajo (b negativo = arriba)."""
    return np.array(pts[ancla], dtype=np.float32) + a * escala * u + b * escala * v


# ---------------- PASO 4: transformar el sticker ----------------
def escalar(img, ancho_objetivo):
    h, w = img.shape[:2]
    ancho = max(1, int(ancho_objetivo))
    alto = max(1, int(ancho * h / w))
    interp = cv2.INTER_AREA if ancho < w else cv2.INTER_LINEAR
    return cv2.resize(img, (ancho, alto), interpolation=interp)


def rotar(img, angulo):
    h, w = img.shape[:2]
    centro = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(centro, -angulo, 1.0)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nuevo_w, nuevo_h = int(w * cos + h * sin), int(w * sin + h * cos)
    M[0, 2] += nuevo_w / 2 - centro[0]
    M[1, 2] += nuevo_h / 2 - centro[1]
    return cv2.warpAffine(img, M, (nuevo_w, nuevo_h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


# ---------------- PASO 3 + 5: mezclar de forma ROBUSTA ----------------
def pegar_sticker(frame, sticker, cx, cy, opacidad=1.0):
    """Pega un sticker RGBA con su CENTRO en (cx, cy), aunque se salga del frame.
    'opacidad' (0-1) multiplica el alfa: sirve para fundidos."""
    H, W = frame.shape[:2]
    h, w = sticker.shape[:2]

    # Rectángulo que ocuparía el sticker (puede salirse del frame)
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    x1, y1 = x0 + w, y0 + h

    # 1) Intersección con el frame
    fx0, fy0 = max(x0, 0), max(y0, 0)
    fx1, fy1 = min(x1, W), min(y1, H)
    if fx0 >= fx1 or fy0 >= fy1:
        return                       # completamente fuera: no hay nada que pegar

    # 2) El trozo correspondiente del sticker (desplazado lo que se haya recortado)
    sx0, sy0 = fx0 - x0, fy0 - y0
    sx1, sy1 = sx0 + (fx1 - fx0), sy0 + (fy1 - fy0)
    trozo = sticker[sy0:sy1, sx0:sx1]

    # 3) Alpha blending (paso 3) solo en esa zona
    a = trozo[:, :, 3:4].astype(np.float32) / 255.0 * opacidad
    s = trozo[:, :, :3].astype(np.float32)
    zona = frame[fy0:fy1, fx0:fx1].astype(np.float32)
    frame[fy0:fy1, fx0:fx1] = (a * s + (1 - a) * zona).astype(np.uint8)


def colocar_sticker(frame, sticker, centro, ancho_px, angulo, opacidad=1.0):
    """Todo en uno: escalar -> rotar -> pegar centrado."""
    s = escalar(sticker, ancho_px)
    s = rotar(s, angulo)
    pegar_sticker(frame, s, centro[0], centro[1], opacidad)


# ---------------- Formas dibujadas semitransparentes ----------------
def circulo_transparente(frame, centro, radio, color, opacidad=0.5):
    """Círculo relleno semitransparente (mofletes). Misma fórmula del alpha blending,
    pero con un alfa constante: cv2.addWeighted hace  opacidad*capa + (1-opacidad)*frame."""
    capa = frame.copy()
    cv2.circle(capa, (int(centro[0]), int(centro[1])), int(radio), color, -1)
    cv2.addWeighted(capa, opacidad, frame, 1 - opacidad, 0, dst=frame)