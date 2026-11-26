"""
CATÁLOGO: solo DATOS. Aquí se describen las imágenes, los Pokémon y las emociones.
Para ajustar posiciones/tamaños o añadir Pokémon, solo se toca este archivo.

Unidades: todas las distancias y tamaños van en "escalas" (distancia entre ojos).
  a > 0 -> hacia la derecha de la cara (en pantalla)   |   b > 0 -> hacia abajo (b < 0 = arriba)
"""
import os

# Landmarks de MediaPipe (los del paso 1)
FRENTE, BARBILLA, NARIZ = 10, 152, 1
MEJILLAS = (50, 280)
LABIO_SUP, LABIO_INF = 13, 14
PARPADO_IZQ, PARPADO_DER = 145, 374

# =====================================================================
# 1) RUTAS DE LAS IMÁGENES   <<<<<<<<<<<<<<  AQUÍ VAN TUS RUTAS
#    Relativas a la carpeta assets/. Todas PNG con fondo transparente.
# =====================================================================
CARPETA = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(CARPETA, "assets")

IMAGENES = {
    # --- Pokémon ---
    "pikachu_orejas":   "pokemons/pikachu/pikachu_orejas.png",
    "pikachu_mofletes":  "pokemons/pikachu/pikachu_mofletes.png",
    "eevee_orejas":     "pokemons/eevee/eevee_orejas.png",
    "eevee_busto":      "pokemons/eevee/eevee_busto.png",
    "psyduck_pelo":     "pokemons/psyduck/psyduck_pelo.png",
    "psyduck_pico_sup": "pokemons/psyduck/psyduck_pico_sup.png",
    "psyduck_pico_inf": "pokemons/psyduck/psyduck_pico_inf.png",
    "mankey_hocico":    "pokemons/mankey/mankey_hocico.png",
    "mankey_orejas":      "pokemons/mankey/mankey_orejas.png",
    "meowth_moneda":      "pokemons/meowth/meowth_moneda.png",
    "meowth_bigotes":      "pokemons/meowth/meowth_bigotes.png",
    "snorlax_orejas":   "pokemons/snorlax/snorlax_orejas.png",
    "snorlax_colmillos": "pokemons/snorlax/snorlax_colmillos.png",
    # --- Detalles de emoción (OpenMoji / Twemoji) ---
    "chispa":           "emociones/chispa.png",
    "exclamacion":      "emociones/exclamacion.png",
    "lagrima":          "emociones/lagrima.png",
    "enfado":           "emociones/enfado.png",
    "sudor":            "emociones/sudor.png",
    "zzz":              "emociones/zzz.png",
}

# =====================================================================
# 2) POKÉMON: lista de piezas. Se dibujan EN ORDEN (la última queda encima)
# =====================================================================
POKEMONS = {
    "pikachu": [
        {"tipo": "png", "img": "pikachu_orejas", "ancla": FRENTE, "b": -0.7, "ancho": 2.4},
        {"tipo": "png", "img": "pikachu_mofletes", "ancla": MEJILLAS, "b": 0.2, "ancho_anclas": 1.6},
    ],
    "eevee": [
        {"tipo": "png", "img": "eevee_busto",  "ancla": BARBILLA, "b": 0.7,  "ancho": 3.0},
        {"tipo": "png", "img": "eevee_orejas", "ancla": FRENTE, "b": -0.9, "ancho": 2.2},
    ],
    "psyduck": [
        {"tipo": "png", "img": "psyduck_pelo",     "ancla": FRENTE,    "b": -0.5,  "ancho": 0.5},
        {"tipo": "png", "img": "psyduck_pico_inf", "ancla": LABIO_INF, "b": 0.15,  "ancho": 1.3},
        {"tipo": "png", "img": "psyduck_pico_sup", "ancla": LABIO_SUP, "b": -0.15, "ancho": 1.4},
    ],
    "mankey": [
        {"tipo": "png", "img": "mankey_orejas",   "ancla": FRENTE, "b": -0.8, "ancho": 2.4},
        {"tipo": "png", "img": "mankey_hocico", "ancla": NARIZ,  "b": 0.1,  "ancho": 4.0},
    ],
    "meowth": [
        {"tipo": "png", "img": "meowth_moneda", "ancla": FRENTE, "b": -0.3, "ancho": 0.9},
        {"tipo": "png", "img": "meowth_bigotes", "ancla": MEJILLAS, "b": 0.0, "ancho": 2.3},
    ],
    "snorlax": [
        {"tipo": "png", "img": "snorlax_orejas", "ancla": FRENTE, "b": -0.5, "ancho": 2.4},
        {"tipo": "png", "img": "snorlax_colmillos", "ancla": LABIO_INF, "b": 0.1,  "ancho": 0.7},
    ],
}

# =====================================================================
# 3) EMOCIONES: qué Pokémon se pone y qué detalles se añaden
#    (las 7 clases de FER2013)
# =====================================================================
EMOCIONES = {
    "feliz": {"pokemon": "pikachu", "detalles": [
        {"tipo": "png", "img": "chispa", "ancla": MEJILLAS[0], "a": -0.1, "b": 0.2, "ancho": 0.8, "anim": "parpadear"},
        {"tipo": "png", "img": "chispa", "ancla": MEJILLAS[1], "a": 0.1, "b": 0.2, "ancho": 0.8, "anim": "parpadear"},
    ]},
    "sorpresa": {"pokemon": "psyduck", "detalles": [
        {"tipo": "png", "img": "exclamacion", "ancla": FRENTE, "a": 1.0, "b": -0.8, "ancho": 0.9, "anim": "latir", "rotar": True},
    ]},
    "triste": {"pokemon": "eevee", "detalles": [
        {"tipo": "png", "img": "lagrima", "ancla": PARPADO_IZQ, "b": 0.2, "ancho": 0.25, "anim": "caer", "recorrido": 1.2},
        {"tipo": "png", "img": "lagrima", "ancla": PARPADO_DER, "b": 0.2, "ancho": 0.25, "anim": "caer", "recorrido": 1.2},
    ]},
    "enfado": {"pokemon": "mankey", "detalles": [
        {"tipo": "png", "img": "enfado", "ancla": FRENTE, "a": 0.7, "b": 0.0, "ancho": 0.6, "anim": "latir"},
    ]},
    "miedo": {"pokemon": "meowth", "detalles": [
        {"tipo": "png", "img": "sudor", "ancla": FRENTE, "a": -0.85, "b": 0.2, "ancho": 0.3, "anim": "caer", "recorrido": 0.8},
    ]},
    "neutral": {"pokemon": "snorlax", "detalles": [
        {"tipo": "png", "img": "zzz", "ancla": FRENTE, "a": 1.0, "b": -0.9, "ancho": 0.7, "anim": "flotar"},
    ]},
}

# Teclas para elegir la emoción a mano (hasta que tengamos el modelo)
TECLAS = {"1": "feliz", "2": "sorpresa", "3": "triste", "4": "enfado",
          "5": "asco", "6": "miedo", "7": "neutral"}