"""
Configuración de los filtros: imágenes, piezas de cada Pokémon y detalles de cada emoción.

Las posiciones y tamaños se expresan en "escalas" (distancia entre los ojos), así el filtro
se adapta a la distancia a la cámara:
  a > 0  desplaza hacia la derecha de la cara
  b > 0  desplaza hacia abajo (b < 0 hacia arriba)
"""
import os

# Landmarks de MediaPipe usados como anclas
FRENTE, BARBILLA, NARIZ = 10, 152, 1
MEJILLAS = (50, 280)
LABIO_SUP, LABIO_INF = 13, 14
PARPADO_IZQ, PARPADO_DER = 145, 374

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Rutas relativas a assets/ (PNG con fondo transparente)
IMAGENES = {
    "pikachu_orejas":    "pokemons/pikachu/pikachu_orejas.png",
    "pikachu_mofletes":  "pokemons/pikachu/pikachu_mofletes.png",
    "eevee_orejas":      "pokemons/eevee/eevee_orejas.png",
    "eevee_busto":       "pokemons/eevee/eevee_busto.png",
    "psyduck_pelo":      "pokemons/psyduck/psyduck_pelo.png",
    "psyduck_pico_sup":  "pokemons/psyduck/psyduck_pico_sup.png",
    "psyduck_pico_inf":  "pokemons/psyduck/psyduck_pico_inf.png",
    "mankey_hocico":     "pokemons/mankey/mankey_hocico.png",
    "mankey_orejas":     "pokemons/mankey/mankey_orejas.png",
    "meowth_moneda":     "pokemons/meowth/meowth_moneda.png",
    "meowth_bigotes":    "pokemons/meowth/meowth_bigotes.png",
    "snorlax_orejas":    "pokemons/snorlax/snorlax_orejas.png",
    "snorlax_colmillos": "pokemons/snorlax/snorlax_colmillos.png",
    "chispa":            "emociones/chispa.png",
    "exclamacion":       "emociones/exclamacion.png",
    "lagrima":           "emociones/lagrima.png",
    "enfado":            "emociones/enfado.png",
    "sudor":             "emociones/sudor.png",
    "zzz":               "emociones/zzz.png",
}

# Piezas de cada Pokémon. Se dibujan en orden, así que la última queda por encima.
POKEMONS = {
    "pikachu": [
        {"img": "pikachu_orejas",   "ancla": FRENTE,   "b": -0.7, "ancho": 2.4},
        {"img": "pikachu_mofletes", "ancla": MEJILLAS, "b": 0.2,  "ancho_anclas": 1.6},
    ],
    "eevee": [
        {"img": "eevee_busto",  "ancla": BARBILLA, "b": 0.7,  "ancho": 3.0},
        {"img": "eevee_orejas", "ancla": FRENTE,   "b": -0.9, "ancho": 2.2},
    ],
    "psyduck": [
        {"img": "psyduck_pelo",     "ancla": FRENTE,    "b": -0.5,  "ancho": 0.5},
        {"img": "psyduck_pico_inf", "ancla": LABIO_INF, "b": 0.15,  "ancho": 1.3},
        {"img": "psyduck_pico_sup", "ancla": LABIO_SUP, "b": -0.15, "ancho": 1.4},
    ],
    "mankey": [
        {"img": "mankey_orejas", "ancla": FRENTE, "b": -0.4, "ancho": 2.4},
        {"img": "mankey_hocico", "ancla": NARIZ,  "b": -0.1, "ancho": 1.0},
    ],
    "meowth": [
        {"img": "meowth_moneda",  "ancla": FRENTE,   "b": -0.3, "ancho": 0.9},
        {"img": "meowth_bigotes", "ancla": MEJILLAS, "b": 0.0,  "ancho": 2.3},
    ],
    "snorlax": [
        {"img": "snorlax_orejas",    "ancla": FRENTE,    "b": -0.5, "ancho": 2.4},
        {"img": "snorlax_colmillos", "ancla": LABIO_INF, "b": 0.1,  "ancho": 0.7},
    ],
}

# Pokémon y detalles animados de cada emoción (anim: caer, latir, flotar o parpadear)
EMOCIONES = {
    "feliz": {"pokemon": "pikachu", "detalles": [
        {"img": "chispa", "ancla": MEJILLAS[0], "a": -0.1, "b": 0.2, "ancho": 0.8, "anim": "parpadear"},
        {"img": "chispa", "ancla": MEJILLAS[1], "a": 0.1,  "b": 0.2, "ancho": 0.8, "anim": "parpadear"},
    ]},
    "sorpresa": {"pokemon": "psyduck", "detalles": [
        {"img": "exclamacion", "ancla": FRENTE, "a": 1.0, "b": -0.8, "ancho": 0.9, "anim": "latir"},
    ]},
    "triste": {"pokemon": "eevee", "detalles": [
        {"img": "lagrima", "ancla": PARPADO_IZQ, "b": 0.2, "ancho": 0.25, "anim": "caer", "recorrido": 1.2},
        {"img": "lagrima", "ancla": PARPADO_DER, "b": 0.2, "ancho": 0.25, "anim": "caer", "recorrido": 1.2},
    ]},
    "enfado": {"pokemon": "mankey", "detalles": [
        {"img": "enfado", "ancla": FRENTE, "a": 0.7, "ancho": 0.6, "anim": "latir"},
    ]},
    "miedo": {"pokemon": "meowth", "detalles": [
        {"img": "sudor", "ancla": FRENTE, "a": -0.85, "b": 0.2, "ancho": 0.3, "anim": "caer", "recorrido": 0.8},
    ]},
    "neutral": {"pokemon": "snorlax", "detalles": [
        {"img": "zzz", "ancla": FRENTE, "a": 1.0, "b": -0.9, "ancho": 0.7, "anim": "flotar"},
    ]},
}

# Teclas del modo manual
TECLAS = {"1": "feliz", "2": "sorpresa", "3": "triste", "4": "enfado",
          "5": "miedo", "6": "neutral"}
