"""
Filtro Pokémon según la emoción detectada en la webcam.

Teclas:
  M    cambiar de modelo (CNN / SVM)
  A    modo automático / manual
  1-6  elegir emoción a mano   0  sin filtro
  V    mostrar la cara 48x48 que recibe el modelo
  Q    o Esc para salir
"""
import os
import sys
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np

# Funciones compartidas con el Fruit Ninja (P5/comun)
RAIZ_P5 = Path.cwd().resolve()
while not (RAIZ_P5 / "comun").exists() and RAIZ_P5 != RAIZ_P5.parent:
    RAIZ_P5 = RAIZ_P5.parent
sys.path.insert(0, str(RAIZ_P5 / "comun"))

from filtro_utils import (crear_detector_cara, Reloj, imagen_mediapipe, a_pixeles,
                          abrir_camara, hay_que_salir, geometria_cara)
from catalogo import EMOCIONES, TECLAS
from dibujo import cargar_imagenes, dibujar_emocion
from emociones_utils import preprocesar, CLASES, NOMBRE_ES
from clasificadores import ClasificadorCNN, ClasificadorSVM

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_CNN = os.path.join(CARPETA, "modelos", "modelo_emociones_cnn.keras")
RUTA_SVM = os.path.join(CARPETA, "modelos", "modelo_emociones.joblib")
VENTANA = "Emociones Pokemon"

N_SUAVIZADO = 8    # predicciones que se promedian
UMBRAL = 0.45      # probabilidad media mínima para cambiar de emoción
MARGEN = 1.15      # margen del recorte de la cara (las caras de FER2013 tienen algo de margen)
NOMBRES = [NOMBRE_ES[c] for c in CLASES]


def recortar_cara(gris, pts, angulo):
    """Recorta un cuadrado alrededor de la cara, lo endereza (ojos en horizontal)
    y lo deja en el formato de FER2013."""
    p = np.array(pts, dtype=np.float32)
    x0, y0 = p.min(axis=0)
    x1, y1 = p.max(axis=0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lado = int(max(x1 - x0, y1 - y0) * MARGEN)

    M = cv2.getRotationMatrix2D((float(cx), float(cy)), angulo, 1.0)
    M[0, 2] += lado / 2 - cx
    M[1, 2] += lado / 2 - cy
    cara = cv2.warpAffine(gris, M, (lado, lado), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)
    return preprocesar(cara)


def dibujar_informacion(frame, estado, fps, prob_media, emocion_auto, cara48):
    h, w = frame.shape[:2]
    cv2.putText(frame, estado, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"{fps:.0f} FPS", (w - 90, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "M modelo | A auto/manual | 1-6 emocion | V cara48 | Q salir", (10, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # Barras con la probabilidad media de cada emoción y una línea en el umbral
    if prob_media is not None:
        ancho_max = 120
        for i, (nombre, p) in enumerate(zip(NOMBRES, prob_media)):
            y = 60 + 22 * i
            color = (0, 165, 255) if nombre == emocion_auto else (180, 180, 180)
            cv2.rectangle(frame, (10, y - 12), (10 + int(ancho_max * p), y + 4), color, -1)
            cv2.putText(frame, f"{nombre} {p:.0%}", (140, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1, cv2.LINE_AA)
        x_umbral = 10 + int(ancho_max * UMBRAL)
        cv2.line(frame, (x_umbral, 44), (x_umbral, 60 + 22 * 5 + 4), (255, 255, 255), 1)

    if cara48 is not None:
        vista = cv2.resize(cara48, (144, 144), interpolation=cv2.INTER_NEAREST)
        frame[h - 190:h - 46, w - 154:w - 10] = cv2.cvtColor(vista, cv2.COLOR_GRAY2BGR)
        cv2.putText(frame, "entrada del modelo", (w - 170, h - 196),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)


imgs = cargar_imagenes()

clasificadores = []
for Clase, ruta in [(ClasificadorCNN, RUTA_CNN), (ClasificadorSVM, RUTA_SVM)]:
    if os.path.exists(ruta):
        clasificadores.append(Clase(ruta))
    else:
        print(f"Aviso: no se encuentra {ruta}")
if not clasificadores:
    raise FileNotFoundError("No hay ningún modelo de emociones en modelos/")

camara = abrir_camara()
detector = None

try:
    detector = crear_detector_cara()
    reloj = Reloj()

    i_clf = 0
    modo_auto = True
    emocion_manual = "feliz"
    mostrar_cara48 = True
    historial = deque(maxlen=N_SUAVIZADO)
    prob_media = None
    emocion_auto = None
    cara48 = None
    n_frame = 0
    t_prev, fps = time.time(), 0.0

    while True:
        ok, frame = camara.read()
        if not ok:
            print("No se pudo leer la webcam.")
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        t = time.time()
        n_frame += 1
        clf = clasificadores[i_clf]

        resultado = detector.detect_for_video(imagen_mediapipe(frame), reloj.ms())

        if resultado.face_landmarks:
            pts = a_pixeles(resultado.face_landmarks[0], w, h)
            geo = geometria_cara(pts)

            if modo_auto and n_frame % clf.predecir_cada == 0:
                # El recorte se hace antes de dibujar el filtro encima
                gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cara48 = recortar_cara(gris, pts, geo[1])
                historial.append(clf.probabilidades(cara48))

                # Se promedian las últimas predicciones y solo se cambia de emoción
                # si el modelo está bastante seguro
                prob_media = np.mean(historial, axis=0)
                mejor = int(np.argmax(prob_media))
                if prob_media[mejor] >= UMBRAL:
                    emocion_auto = NOMBRES[mejor]

            emocion = emocion_auto if modo_auto else emocion_manual
            if emocion in EMOCIONES:
                dibujar_emocion(frame, pts, geo, emocion, imgs, t)
        else:
            historial.clear()
            prob_media, emocion_auto = None, None

        fps = 0.9 * fps + 0.1 / max(t - t_prev, 1e-6)
        t_prev = t

        if modo_auto:
            estado = f"AUTO [{clf.nombre}]: {emocion_auto or '-'}"
            if emocion_auto in EMOCIONES:
                estado += f" -> {EMOCIONES[emocion_auto]['pokemon']}"
        else:
            estado = f"MANUAL: {emocion_manual or 'sin filtro'}"
        dibujar_informacion(frame, estado, fps,
                            prob_media if modo_auto else None, emocion_auto,
                            cara48 if (modo_auto and mostrar_cara48) else None)

        cv2.imshow(VENTANA, frame)
        tecla = cv2.waitKey(1) & 0xFF
        if hay_que_salir(tecla, VENTANA):
            break

        letra = chr(tecla).lower()
        if letra == "m":
            i_clf = (i_clf + 1) % len(clasificadores)
            historial.clear()
            prob_media, emocion_auto = None, None
        elif letra == "a":
            modo_auto = not modo_auto
            historial.clear()
        elif letra == "v":
            mostrar_cara48 = not mostrar_cara48
        elif letra == "0":
            modo_auto, emocion_manual = False, None
        elif letra in TECLAS:
            modo_auto, emocion_manual = False, TECLAS[letra]

finally:
    camara.release()
    if detector is not None:
        detector.close()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
