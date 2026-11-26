"""
PASO 11 - El modelo de emociones decide el Pokémon
  1) MediaPipe localiza la cara (landmarks)
  2) Se recorta la cara, se ENDEREZA y se deja como en FER2013 (gris, 48x48, ecualizada)
  3) El modelo predice la emoción cada N frames y se suaviza con una votación
  4) Se dibuja el filtro de esa emoción (pasos 5 y 6)

Teclas: a  modo automático (modelo) / manual (teclas)
        1-7 elegir emoción en modo manual | 0 sin filtro
        v  ver/ocultar la cara 48x48 que recibe el modelo | Esc salir
"""
import os
import time
from collections import deque, Counter

import cv2
import numpy as np
import mediapipe as mp
import joblib

from filtro_utils import geometria_cara
from catalogo import EMOCIONES, TECLAS
from dibujo import cargar_imagenes, dibujar_emocion
from emociones_utils import preprocesar, extraer, NOMBRE_ES

CARPETA = os.path.dirname(os.path.abspath(__file__))
MODELO_CARA = os.path.join(CARPETA, "modelos", "face_landmarker.task")
MODELO_EMOCIONES = os.path.join(CARPETA, "modelos", "modelo_emociones.joblib")

# --- Parámetros del reconocimiento ---
PREDECIR_CADA = 6      # predecir 1 de cada N frames (el modelo tarda ~50 ms)
N_VOTOS = 7            # nº de predicciones recientes que votan
MARGEN = 1.15          # tamaño del recorte respecto a la cara (FER2013 incluye algo de margen)

# ---------------------------------------------------------------
# Carga de modelos e imágenes
# ---------------------------------------------------------------
imgs = cargar_imagenes()

paquete = joblib.load(MODELO_EMOCIONES)
clasificador = paquete["modelo"]
TIPO_CARACT = paquete["caract"]
CLASES = paquete["clases"]
print(f"Modelo de emociones: {TIPO_CARACT} | clases: {CLASES} | "
      f"F1 test = {paquete['test_f1_macro']:.3f} | sklearn al entrenar: {paquete['sklearn']}")

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

latest = None
def on_result(result, output_image, timestamp_ms):
    global latest
    latest = result

with open(MODELO_CARA, "rb") as f:
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_buffer=f.read()),
        running_mode=RunningMode.LIVE_STREAM,
        num_faces=1,
        result_callback=on_result,
    )


# ---------------------------------------------------------------
# Recorte de la cara al formato FER2013
# ---------------------------------------------------------------
def recortar_cara(gris, pts, angulo):
    """Recorta un cuadrado alrededor de la cara y lo ENDEREZA (ojos horizontales),
    todo en una sola transformación afín. Devuelve la cara 48x48 preprocesada."""
    p = np.array(pts, dtype=np.float32)
    x0, y0 = p.min(axis=0)
    x1, y1 = p.max(axis=0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lado = int(max(x1 - x0, y1 - y0) * MARGEN)

    # Rotar alrededor del centro de la cara para deshacer la inclinación de la cabeza
    # (+angulo: getRotationMatrix2D gira en sentido antihorario y nuestro ángulo es horario)
    M = cv2.getRotationMatrix2D((float(cx), float(cy)), angulo, 1.0)
    # ...y desplazar para que el centro de la cara quede en el centro del recorte
    M[0, 2] += lado / 2 - cx
    M[1, 2] += lado / 2 - cy
    cara = cv2.warpAffine(gris, M, (lado, lado), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)
    return preprocesar(cara)          # 48x48 + ecualización, IGUAL que en el entrenamiento


def predecir(cara48):
    vector = extraer(cara48, TIPO_CARACT)[None, :]     # (1, nº características)
    indice = int(clasificador.predict(vector)[0])
    return NOMBRE_ES[CLASES[indice]]                    # nombre en español = clave del catálogo


# ---------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------
cap = cv2.VideoCapture(0)
modo_auto = True
emocion_manual = "feliz"
mostrar_cara48 = True

votos = deque(maxlen=N_VOTOS)       # cola: al llenarse, el más antiguo sale solo
emocion_auto = None
ultima_pred = None
cara48 = None
n_frame = 0
t_prev, fps = time.time(), 0.0

with FaceLandmarker.create_from_options(options) as landmarker:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        t = time.time()
        n_frame += 1

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        landmarker.detect_async(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(t * 1000))

        hay_cara = latest is not None and latest.face_landmarks
        if hay_cara:
            pts = [(int(lm.x * w), int(lm.y * h)) for lm in latest.face_landmarks[0]]
            geo = geometria_cara(pts)

            # 1) Reconocer la emoción (solo cada PREDECIR_CADA frames)
            if modo_auto and n_frame % PREDECIR_CADA == 0:
                gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # ANTES de dibujar el filtro
                cara48 = recortar_cara(gris, pts, geo[1])
                ultima_pred = predecir(cara48)
                votos.append(ultima_pred)
                emocion_auto = Counter(votos).most_common(1)[0][0]   # la más votada

            # 2) Dibujar el filtro de la emoción
            emocion = emocion_auto if modo_auto else emocion_manual
            if emocion in EMOCIONES:
                dibujar_emocion(frame, pts, geo, emocion, imgs, t)
        else:
            votos.clear()          # sin cara: se olvidan las predicciones antiguas
            emocion_auto = None

        # ---------------- Información en pantalla ----------------
        fps = 0.9 * fps + 0.1 / max(t - t_prev, 1e-6)
        t_prev = t

        if modo_auto:
            estado = f"AUTO: {emocion_auto or '-'}  (ultima: {ultima_pred or '-'})"
            if emocion_auto in EMOCIONES:
                estado += f" -> {EMOCIONES[emocion_auto]['pokemon']}"
        else:
            estado = f"MANUAL: {emocion_manual or 'sin filtro'}"
        cv2.putText(frame, estado, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"{fps:.0f} FPS", (w - 90, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "a auto/manual | 1-7 emocion | v cara48 | Esc salir", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Votos actuales como barras (cuánto apoya cada emoción)
        if modo_auto and votos:
            for i, (emo, n) in enumerate(Counter(votos).most_common()):
                y = 60 + 22 * i
                cv2.rectangle(frame, (10, y - 12), (10 + int(120 * n / N_VOTOS), y + 4), (0, 200, 255), -1)
                cv2.putText(frame, f"{emo} {n}", (140, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # La cara que "ve" el modelo, ampliada en la esquina
        if mostrar_cara48 and cara48 is not None and modo_auto:
            vista = cv2.resize(cara48, (144, 144), interpolation=cv2.INTER_NEAREST)
            frame[h - 190:h - 46, w - 154:w - 10] = cv2.cvtColor(vista, cv2.COLOR_GRAY2BGR)
            cv2.putText(frame, "entrada del modelo", (w - 170, h - 196),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        cv2.imshow("Paso 11 - Emociones Pokemon", frame)
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == 27:
            break
        elif tecla == ord('a'):
            modo_auto = not modo_auto
            votos.clear()
        elif tecla == ord('v'):
            mostrar_cara48 = not mostrar_cara48
        elif tecla == ord('0'):
            modo_auto, emocion_manual = False, None
        elif chr(tecla) in TECLAS:
            modo_auto, emocion_manual = False, TECLAS[chr(tecla)]

cap.release()
cv2.destroyAllWindows()
