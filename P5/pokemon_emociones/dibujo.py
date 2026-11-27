"""
Dibuja los Pokémon y los detalles de cada emoción a partir de lo definido en catalogo.py.
"""
import os
import math
import cv2
import numpy as np

from filtro_utils import colocar_sticker, leer_png
from catalogo import ASSETS, IMAGENES, POKEMONS, EMOCIONES

LADO_MAX = 800   # las imágenes más grandes se reducen al cargarlas


def cargar_imagenes():
    imgs = {}
    for nombre, ruta_rel in IMAGENES.items():
        img = leer_png(os.path.join(ASSETS, ruta_rel))
        if img is None:
            print(f"Aviso: no se encuentra {ruta_rel}")
        elif img.ndim != 3 or img.shape[2] != 4:
            print(f"Aviso: {ruta_rel} no tiene canal alfa")
        else:
            # Reducir una sola vez aquí evita redimensionar imágenes enormes en cada frame
            lado = max(img.shape[:2])
            if lado > LADO_MAX:
                f = LADO_MAX / lado
                img = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
            imgs[nombre] = img
    print(f"Imágenes cargadas: {len(imgs)}/{len(IMAGENES)}")
    return imgs

def animar(pieza, t):
    """Devuelve (desplazamiento vertical extra, factor de tamaño, opacidad) según la animación."""
    anim = pieza.get("anim")
    db, f, op = 0.0, 1.0, pieza.get("opacidad", 1.0)

    if anim == "caer":          # baja y se desvanece, en bucle
        fase = (t * pieza.get("vel", 0.8)) % 1.0
        db = fase * pieza.get("recorrido", 1.0)
        op *= 1.0 - fase
    elif anim == "latir":
        f = 1.0 + 0.15 * math.sin(2 * math.pi * 2.0 * t)
    elif anim == "flotar":
        db = 0.08 * math.sin(2 * math.pi * 0.8 * t)
    elif anim == "parpadear":
        op *= 0.5 + 0.5 * math.sin(2 * math.pi * 3.0 * t)

    return db, f, op

def dibujar_pieza(frame, pts, geo, pieza, imgs, t):
    img = imgs.get(pieza["img"])
    if img is None:
        return

    escala, angulo, u, v = geo
    db, f, op = animar(pieza, t)

    # Si el ancla son varios landmarks se usa su punto medio (p. ej. las dos mejillas)
    ancla = pieza["ancla"]
    if isinstance(ancla, (tuple, list)):
        base = np.mean([pts[i] for i in ancla], axis=0)
    else:
        base = np.array(pts[ancla], dtype=np.float32)

    centro = base + pieza.get("a", 0.0) * escala * u + (pieza.get("b", 0.0) + db) * escala * v

    if "ancho_anclas" in pieza:
        # Ancho proporcional a la distancia real entre las dos anclas
        p, q = (np.array(pts[i], dtype=np.float32) for i in ancla[:2])
        ancho_px = pieza["ancho_anclas"] * np.hypot(*(q - p))
    else:
        ancho_px = pieza["ancho"] * escala

    ang = angulo if pieza.get("rotar", True) else 0.0
    colocar_sticker(frame, img, centro, ancho_px * f, ang, op)

def dibujar_emocion(frame, pts, geo, emocion, imgs, t):
    conf = EMOCIONES[emocion]
    for pieza in POKEMONS[conf["pokemon"]] + conf["detalles"]:
        dibujar_pieza(frame, pts, geo, pieza, imgs, t)
