"""
Herramientas del MODELO DE EMOCIONES.
Se importa tanto desde los notebooks de entrenamiento (pasos 9 y 10)
como desde el script de la webcam (paso 11).

REGLA DE ORO: la imagen se procesa EXACTAMENTE IGUAL al entrenar y al predecir.
Por eso estas funciones viven en un único archivo que usan ambos.
"""
import numpy as np
import cv2
from skimage.feature import hog, local_binary_pattern

# Clases usadas (sin disgust). El orden define la etiqueta numérica: angry=0, fear=1...
CLASES = ["angry", "fear", "happy", "neutral", "sad", "surprise"]
NOMBRE_ES = {"angry": "enfado", "fear": "miedo", "happy": "feliz",
             "neutral": "neutral", "sad": "triste", "surprise": "sorpresa"}

TAM = 48   # FER2013: caras de 48x48 en escala de grises


# ---------------------------------------------------------------
# 1) PREPROCESADO (común a entrenamiento y webcam)
# ---------------------------------------------------------------
def preprocesar(gris):
    """Recibe una cara en gris (cualquier tamaño) y devuelve 48x48 ecualizada (uint8).
    La ecualización de histograma reparte los niveles de gris de 0 a 255:
    reduce la diferencia entre caras muy oscuras/claras y entre FER2013 y tu webcam."""
    if gris.shape != (TAM, TAM):
        gris = cv2.resize(gris, (TAM, TAM), interpolation=cv2.INTER_AREA)
    return cv2.equalizeHist(gris)


# ---------------------------------------------------------------
# 2) CARACTERÍSTICAS
# ---------------------------------------------------------------
def caract_pixeles(img):
    """Los propios píxeles como vector (48*48 = 2304 valores entre 0 y 1)."""
    return img.astype(np.float32).ravel() / 255.0


# HOG: histograma de orientaciones del gradiente por celdas
HOG_PARAMS = dict(orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2),
                  block_norm="L2-Hys")

def caract_hog(img):
    """48x48 -> 6x6 celdas de 8x8 -> 5x5 bloques de 2x2 celdas x 9 orientaciones = 900 valores."""
    return hog(img, **HOG_PARAMS).astype(np.float32)


# LBP: patrón binario local + histogramas por celdas
LBP_P, LBP_R = 8, 1          # 8 vecinos a radio 1
LBP_CELDA = 8                # celdas de 8x8 -> rejilla 6x6
LBP_BINS = LBP_P + 2         # método "uniform" -> 10 valores posibles

def caract_lbp(img):
    """Histograma LBP de cada celda, concatenados: 6x6 celdas x 10 bins = 360 valores."""
    codigos = local_binary_pattern(img, LBP_P, LBP_R, method="uniform")
    hists = []
    for y in range(0, TAM, LBP_CELDA):
        for x in range(0, TAM, LBP_CELDA):
            celda = codigos[y:y + LBP_CELDA, x:x + LBP_CELDA]
            h, _ = np.histogram(celda, bins=LBP_BINS, range=(0, LBP_BINS))
            hists.append(h / h.sum())          # normalizar: proporciones, no recuentos
    return np.concatenate(hists).astype(np.float32)


EXTRACTORES = {"pixeles": caract_pixeles, "hog": caract_hog, "lbp": caract_lbp}

def extraer(img, tipo):
    """Características de UNA imagen ya preprocesada. tipo: 'pixeles', 'hog', 'lbp' o 'hog+lbp'."""
    return np.concatenate([EXTRACTORES[t](img) for t in tipo.split("+")])
