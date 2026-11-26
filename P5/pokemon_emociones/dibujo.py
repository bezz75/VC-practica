"""
DIBUJO: lógica genérica. Sabe dibujar cualquier pieza del catálogo.
No sabe nada de Pikachu ni de Eevee: todo lo lee de catalogo.py
"""
import os
import math
import cv2
import numpy as np

from filtro_utils import punto_en_cara, colocar_sticker, circulo_transparente
from catalogo import ASSETS, IMAGENES, POKEMONS, EMOCIONES


def leer_png(ruta):
    """Lee un PNG conservando el alfa, aunque la ruta tenga ñ o tildes.
    cv2.imread falla en Windows con rutas no-ASCII (el mismo problema de MediaPipe):
    Python lee los bytes y OpenCV solo los decodifica."""
    if not os.path.exists(ruta):
        return None
    datos = np.fromfile(ruta, dtype=np.uint8)
    return cv2.imdecode(datos, cv2.IMREAD_UNCHANGED)


def cargar_imagenes():
    """Carga todas las imágenes del catálogo. Las que falten se avisan y se omiten."""
    imgs = {}
    for nombre, ruta_rel in IMAGENES.items():
        ruta = os.path.join(ASSETS, ruta_rel)
        img = leer_png(ruta)
        if img is None:
            print(f"[AVISO] No encuentro {ruta_rel}  -> '{nombre}' no se dibujará")
        elif img.ndim != 3 or img.shape[2] != 4:
            print(f"[AVISO] {ruta_rel} no tiene canal alfa -> '{nombre}' no se dibujará")
        else:
            imgs[nombre] = img
    print(f"Imágenes cargadas: {len(imgs)}/{len(IMAGENES)}")
    return imgs


def animar(pieza, t):
    """Según la animación de la pieza y el tiempo t (segundos), devuelve:
    db (desplazamiento extra hacia abajo, en escalas), f (factor de tamaño), op (opacidad)."""
    anim = pieza.get("anim")
    db, f, op = 0.0, 1.0, pieza.get("opacidad", 1.0)

    if anim == "caer":                       # baja y se desvanece, en bucle
        fase = (t * pieza.get("vel", 0.8)) % 1.0          # va de 0 a 1 y vuelve a empezar
        db = fase * pieza.get("recorrido", 1.0)
        op *= 1.0 - fase
    elif anim == "latir":                    # crece y encoge
        f = 1.0 + 0.15 * math.sin(2 * math.pi * 2.0 * t)
    elif anim == "flotar":                   # sube y baja suavemente
        db = 0.08 * math.sin(2 * math.pi * 0.8 * t)
    elif anim == "parpadear":                # aparece y desaparece
        op *= 0.5 + 0.5 * math.sin(2 * math.pi * 3.0 * t)

    return db, f, op


def dibujar_pieza(frame, pts, geo, pieza, imgs, t):
    escala, angulo, u, v = geo
    db, f, op = animar(pieza, t)
    
    ancla = pieza["ancla"]
    if isinstance(ancla, (tuple, list)):
        # Varias anclas -> punto medio entre ellas (p. ej. las dos mejillas)
        base = np.mean([pts[i] for i in ancla], axis=0)
    else:
        base = np.array(pts[ancla], dtype=np.float32)

    centro = (base
              + pieza.get("a", 0.0) * escala * u
              + (pieza.get("b", 0.0) + db) * escala * v)
    
    if pieza["tipo"] == "circulo":
        circulo_transparente(frame, centro, pieza["radio"] * escala * f, pieza["color"], op)

    elif pieza["tipo"] == "png":
        img = imgs.get(pieza["img"])
        if img is None:                      # PNG que falta: se omite sin romper nada
            return
        ang = angulo if pieza.get("rotar", True) else 0.0
        if "ancho_anclas" in pieza:
            # Tamaño relativo a la distancia REAL entre las dos anclas (p. ej. las mejillas)
            p = np.array(pts[pieza["ancla"][0]], dtype=np.float32)
            q = np.array(pts[pieza["ancla"][1]], dtype=np.float32)
            ancho_px = pieza["ancho_anclas"] * np.hypot(*(q - p))
        else:
            ancho_px = pieza["ancho"] * escala
        colocar_sticker(frame, img, centro, ancho_px * f, ang, op)

def dibujar_emocion(frame, pts, geo, emocion, imgs, t):
    """Dibuja el Pokémon asociado a la emoción y, encima, sus detalles."""
    conf = EMOCIONES[emocion]
    for pieza in POKEMONS[conf["pokemon"]]:
        dibujar_pieza(frame, pts, geo, pieza, imgs, t)
    for pieza in conf["detalles"]:
        dibujar_pieza(frame, pts, geo, pieza, imgs, t)