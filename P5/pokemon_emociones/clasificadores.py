"""
Los dos modelos de emociones (SVM y CNN) con la misma interfaz:
    prob = clf.probabilidades(cara48)   # 6 valores en el orden de CLASES
"""
import time
import numpy as np
import joblib

from emociones_utils import CLASES, extraer

class ClasificadorSVM:
    nombre = "SVM"
    predecir_cada = 6   # tarda ~50 ms, así que no se predice en todos los frames

    def __init__(self, ruta):
        paquete = joblib.load(ruta)
        self.modelo = paquete["modelo"]
        self.caract = paquete["caract"]
        print(f"SVM cargada ({self.caract}, F1 test = {paquete['test_f1_macro']:.3f})")

    def probabilidades(self, cara48):
        # La SVM solo da la clase ganadora: se devuelve como 1 para esa clase y 0 para el resto
        indice = int(self.modelo.predict(extraer(cara48, self.caract)[None, :])[0])
        prob = np.zeros(len(CLASES), dtype=np.float32)
        prob[indice] = 1.0
        return prob

class ClasificadorCNN:
    nombre = "CNN"
    predecir_cada = 2

    def __init__(self, ruta):
        import tensorflow as tf
        import keras
        self.modelo = keras.models.load_model(ruta)

        # Llamar al modelo directamente es lento con una sola imagen (~50 ms).
        # Compilándolo con tf.function se ejecuta como un grafo y es mucho más rápido.
        self._predecir = tf.function(
            lambda x: self.modelo(x, training=False),
            input_signature=[tf.TensorSpec(shape=(1, 48, 48, 1), dtype=tf.float32)],
        )

        vacia = np.zeros((48, 48), dtype=np.uint8)
        self.probabilidades(vacia)          # la primera llamada compila
        t0 = time.time()
        for _ in range(20):
            self.probabilidades(vacia)
        print(f"CNN cargada ({1000 * (time.time() - t0) / 20:.1f} ms por imagen)")

    def probabilidades(self, cara48):
        x = cara48[None, :, :, None].astype(np.float32)   # (1, 48, 48, 1); el /255 va dentro del modelo
        return self._predecir(x).numpy()[0]
