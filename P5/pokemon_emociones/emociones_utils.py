"""
Preprocesado y características del modelo de emociones.
Lo usan tanto los notebooks de entrenamiento como el prototipo, para que la cara
se procese igual al entrenar y al predecir.
"""
import numpy as np
import cv2
from skimage.feature import hog, local_binary_pattern

# Clases de FER2013 usadas (se descarta disgust). El índice es la etiqueta numérica.
CLASES = ["angry", "fear", "happy", "neutral", "sad", "surprise"]
NOMBRE_ES = {"angry": "enfado", "fear": "miedo", "happy": "feliz",
             "neutral": "neutral", "sad": "triste", "surprise": "sorpresa"}

TAM = 48

def preprocesar(gris):
    """Cara en gris de cualquier tamaño -> 48x48 con el histograma ecualizado."""
    if gris.shape != (TAM, TAM):
        gris = cv2.resize(gris, (TAM, TAM), interpolation=cv2.INTER_AREA)
    return cv2.equalizeHist(gris)

def caract_pixeles(img):
    return img.astype(np.float32).ravel() / 255.0

# HOG: 6x6 celdas de 8x8 px, bloques de 2x2 celdas, 9 orientaciones -> 900 valores
HOG_PARAMS = dict(orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2),
                  block_norm="L2-Hys")

def caract_hog(img):
    return hog(img, **HOG_PARAMS).astype(np.float32)

# LBP uniforme (8 vecinos, radio 1): histograma de 10 bins por celda de 8x8 -> 360 valores
LBP_P, LBP_R = 8, 1
LBP_CELDA = 8
LBP_BINS = LBP_P + 2

def caract_lbp(img):
    codigos = local_binary_pattern(img, LBP_P, LBP_R, method="uniform")
    hists = []
    for y in range(0, TAM, LBP_CELDA):
        for x in range(0, TAM, LBP_CELDA):
            celda = codigos[y:y + LBP_CELDA, x:x + LBP_CELDA]
            h, _ = np.histogram(celda, bins=LBP_BINS, range=(0, LBP_BINS))
            hists.append(h / h.sum())
    return np.concatenate(hists).astype(np.float32)

EXTRACTORES = {"pixeles": caract_pixeles, "hog": caract_hog, "lbp": caract_lbp}

def extraer(img, tipo):
    """tipo: 'pixeles', 'hog', 'lbp' o combinaciones como 'hog+lbp'."""
    return np.concatenate([EXTRACTORES[t](img) for t in tipo.split("+")])