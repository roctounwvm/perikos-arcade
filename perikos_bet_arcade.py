import os
import json
import random
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template_string, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-change-this"
)

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("ADVERTENCIA: DATABASE_URL no esta configurada.")

AVATARES_DB = {
    1: {"nombre": "Robot Píxel", "rareza": "COMUN", "color": "#888888", "icon": "🤖"},
    2: {"nombre": "Fantasma Retro", "rareza": "COMUN", "color": "#888888", "icon": "👻"},
    3: {"nombre": "Champiñón Verde", "rareza": "COMUN", "color": "#888888", "icon": "🍄"},
    4: {"nombre": "Moneda de Bronce", "rareza": "COMUN", "color": "#888888", "icon": "🪙"},
    5: {"nombre": "Slime Verde", "rareza": "COMUN", "color": "#888888", "icon": "🧪"},
    6: {"nombre": "Alien Píxel", "rareza": "COMUN", "color": "#888888", "icon": "👾"},
    7: {"nombre": "Poción Roja", "rareza": "COMUN", "color": "#888888", "icon": "🍷"},
    8: {"nombre": "Cerezas 8-Bit", "rareza": "COMUN", "color": "#888888", "icon": "🍒"},
    9: {"nombre": "Cactus Arcade", "rareza": "COMUN", "color": "#888888", "icon": "🌵"},
    10: {"nombre": "Espada de Madera", "rareza": "COMUN", "color": "#888888", "icon": "🗡️"},
    11: {"nombre": "Escudo de Madera", "rareza": "COMUN", "color": "#888888", "icon": "🛡️"},
    12: {"nombre": "Control Arcade", "rareza": "COMUN", "color": "#888888", "icon": "🎮"},
    13: {"nombre": "Casete Retro", "rareza": "COMUN", "color": "#888888", "icon": "📻"},
    14: {"nombre": "Disquete 3.5", "rareza": "COMUN", "color": "#888888", "icon": "💾"},
    15: {"nombre": "Bloque Píxel", "rareza": "COMUN", "color": "#888888", "icon": "🧱"},
    16: {"nombre": "Corazón de Vida", "rareza": "COMUN", "color": "#888888", "icon": "❤️"},
    17: {"nombre": "Estrella Simple", "rareza": "COMUN", "color": "#888888", "icon": "⭐"},
    18: {"nombre": "Calavera Píxel", "rareza": "COMUN", "color": "#888888", "icon": "💀"},

    19: {"nombre": "Mago Azul", "rareza": "RARO", "color": "#0088ff", "icon": "🧙‍♂️"},
    20: {"nombre": "Caballero de Hierro", "rareza": "RARO", "color": "#0088ff", "icon": "⚔️"},
    21: {"nombre": "Ninja de la Sombra", "rareza": "RARO", "color": "#0088ff", "icon": "🥷"},
    22: {"nombre": "Dragón Verde", "rareza": "RARO", "color": "#0088ff", "icon": "🐉"},
    23: {"nombre": "Ciberpunk Girl", "rareza": "RARO", "color": "#0088ff", "icon": "👩‍💻"},
    24: {"nombre": "Samurái Neón", "rareza": "RARO", "color": "#0088ff", "icon": "👘"},
    25: {"nombre": "Esqueleto Guerrero", "rareza": "RARO", "color": "#0088ff", "icon": "☠️"},
    26: {"nombre": "Cíclope de Fuego", "rareza": "RARO", "color": "#0088ff", "icon": "👁️"},
    27: {"nombre": "Vampiro Nocturno", "rareza": "RARO", "color": "#0088ff", "icon": "🧛"},
    28: {"nombre": "Hombre Lobo", "rareza": "RARO", "color": "#0088ff", "icon": "🐺"},
    29: {"nombre": "Rey Arcade", "rareza": "RARO", "color": "#0088ff", "icon": "🤴"},
    30: {"nombre": "Reina de Espadas", "rareza": "RARO", "color": "#0088ff", "icon": "👸"},
    31: {"nombre": "Pirata Píxel", "rareza": "RARO", "color": "#0088ff", "icon": "🏴‍☠️"},
    32: {"nombre": "Vikingo del Trueno", "rareza": "RARO", "color": "#0088ff", "icon": "🪓"},

    33: {"nombre": "Fénix Dorado", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "🦅"},
    34: {"nombre": "Mecha Titán", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "🤖"},
    35: {"nombre": "Demonio Neón", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "👿"},
    36: {"nombre": "Arcángel Píxel", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "👼"},
    37: {"nombre": "Dragón Causal", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "🐲"},
    38: {"nombre": "Señor del Tiempo", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "⏳"},
    39: {"nombre": "Cyborg Alpha", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "🦾"},
    40: {"nombre": "Nigromante Void", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "🔮"},
    41: {"nombre": "Dios del Rayo", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "⚡"},
    42: {"nombre": "Golem de Cristal", "rareza": "LEGENDARIO", "color": "#ff00ff", "icon": "💎"},

    43: {"nombre": "Periko Cósmico", "rareza": "MITICO", "color": "#ff0055", "icon": "🌌"},
    44: {"nombre": "Emperador Oscuro", "rareza": "MITICO", "color": "#ff0055", "icon": "👺"},
    45: {"nombre": "Dios del Caos", "rareza": "MITICO", "color": "#ff0055", "icon": "🔥"},
    46: {"nombre": "Valquiria Carmesí", "rareza": "MITICO", "color": "#ff0055", "icon": "💃"},
    47: {"nombre": "Ente Cuántico", "rareza": "MITICO", "color": "#ff0055", "icon": "⚛️"},

    48: {"nombre": "El Creador Periko", "rareza": "SECRETO", "color": "#ffff00", "icon": "👁️‍🗨️"},
    49: {"nombre": "Entidad Glitch 404", "rareza": "SECRETO", "color": "#ffff00", "icon": "👾"},
    50: {"nombre": "Periko Absoluto", "rareza": "SECRETO", "color": "#ffff00", "icon": "👑"}
}

MODO_MANTENIMIENTO = False
MODO_CARNAVAL = False
MODO_OSCURO = False
MODO_DIVINO = False
COSTO_MAQUINA_COLORES = 10000  # cada giro cuesta 10,000
COSTO_MONEDA_PRESTIGIO = 1000000000  # 1,000,000,000 perikoins por 1 moneda de prestigio (legacy, no se usa)

# Precios escalados de prestigio
# Base: 10 cuatrillones (1e16), se duplica cada compra
# Tope: 5.15 quintillones (5.15e18)
PRESTIGIO_PRECIO_BASE = 10_000_000_000_000_000   # 10 cuatrillones
PRESTIGIO_PRECIO_TOPE = 5_150_000_000_000_000_000  # 5.15 quintillones


# Sistema de nivel / EXP
EXP_POR_VICTORIA = 10  # EXP ganada por cada partida ganada
NIVEL_MAXIMO = 500     # Nivel maximo

# Registro de movimientos (10 min)
REGISTRO_MOVIMIENTOS = []       # lista de dicts: {timestamp, usuario, tipo, cantidad, juego}
REGISTRO_ACTIVO = False         # True = grabando movimientos
REGISTRO_DURACION = 600         # 10 minutos en segundos


def exp_necesaria(nivel):
    """EXP necesaria para subir del nivel actual al siguiente.
    Nivel 1->2: 10 EXP
    Nivel 2->3: 15 EXP
    Nivel 3->4: 20 EXP
    ...
    Formula: 5 + (nivel * 5)
    """
    return 5 + (nivel * 5)


def titulo_por_nivel(nivel, username=None, titulo_custom=None):
    """Devuelve el titulo del jugador. Si tiene titulo_custom lo usa."""
    if titulo_custom:
        return titulo_custom
    if nivel >= 400:
        return "💀 Leyenda"
    elif nivel >= 300:
        return "🔥 Maestro"
    elif nivel >= 200:
        return "⚡ Veterano"
    elif nivel >= 150:
        return "🌟 Elite"
    elif nivel >= 100:
        return "⚔ Guerrero"
    elif nivel >= 75:
        return "🗡 Aspirante"
    elif nivel >= 50:
        return "🛡 Soldado"
    elif nivel >= 30:
        return "🎯 Aprendiz"
    elif nivel >= 15:
        return "🍄 Novato"
    elif nivel >= 5:
        return "🌱 Principiante"
    else:
        return "🐣 Recluta"



def calcular_precio_prestigio(prestigio_actual):
    """
    Calcula el precio del siguiente prestigio.
    prestige 1 -> 10 cuatrillones (1e16)
    prestige 2 -> 20 cuatrillones (2e16)
    prestige 3 -> 40 cuatrillones (4e16)
    ...
    prestige 10 -> 5.12 quintillones (5.12e18)
    A partir de ahi el precio se fija en 5.15 quintillones.
    """
    n = prestigio_actual  # numero de prestigios que YA tiene; el proximo es n+1
    precio = PRESTIGIO_PRECIO_BASE * (2 ** n)
    if precio > PRESTIGIO_PRECIO_TOPE:
        precio = PRESTIGIO_PRECIO_TOPE
    return precio


def formatear_precio_prestigio(precio):
    """Formatea el precio de prestigio en formato legible."""
    if precio >= 1_000_000_000_000_000_000:
        valor = precio / 1_000_000_000_000_000_000
        return f"{valor:.2f} quintillones"
    elif precio >= 1_000_000_000_000_000:
        valor = precio / 1_000_000_000_000_000
        # Si es entero, mostrar sin decimales
        if valor == int(valor):
            return f"{int(valor)} cuatrillones"
        return f"{valor:.2f} cuatrillones"
    elif precio >= 1_000_000_000_000:
        valor = precio / 1_000_000_000_000
        if valor == int(valor):
            return f"{int(valor)} trillones"
        return f"{valor:.2f} trillones"
    elif precio >= 1_000_000_000:
        valor = precio / 1_000_000_000
        if valor == int(valor):
            return f"{int(valor)} billones"
        return f"{valor:.2f} billones"
    else:
        return f"{precio:,} P"

COLORES_NOMBRE = {
    "BLANCO": {
        "nombre": "Blanco",
        "tipo": "TIENDA",
        "precio": 500,
        "css": "#ffffff"
    },

    "ROJO": {
        "nombre": "Rojo",
        "tipo": "TIENDA",
        "precio": 750,
        "css": "#ff0000"
    },

    "AZUL": {
        "nombre": "Azul",
        "tipo": "TIENDA",
        "precio": 1000,
        "css": "#0088ff"
    },

    "VERDE": {
        "nombre": "Verde",
        "tipo": "TIENDA",
        "precio": 1250,
        "css": "#00ff66"
    },

    "AMARILLO": {
        "nombre": "Amarillo",
        "tipo": "TIENDA",
        "precio": 1500,
        "css": "#ffff00"
    },

    "NARANJA": {
        "nombre": "Naranja",
        "tipo": "TIENDA",
        "precio": 1750,
        "css": "#ff7700"
    },

    "MORADO": {
        "nombre": "Morado",
        "tipo": "TIENDA",
        "precio": 2000,
        "css": "#aa00ff"
    },

    "ROSADO": {
        "nombre": "Rosado",
        "tipo": "TIENDA",
        "precio": 2250,
        "css": "#ff69b4"
    },

    "CELESTE": {
        "nombre": "Celeste",
        "tipo": "TIENDA",
        "precio": 2500,
        "css": "#00ccff"
    },

    "GRIS": {
        "nombre": "Gris",
        "tipo": "TIENDA",
        "precio": 3000,
        "css": "#888888"
    },

    # DESDE AQUI: COLORES EXCLUSIVOS DE LA MAQUINA

    "FUEGO": {
        "nombre": "Fuego",
        "tipo": "MAQUINA",
        "rareza": "RARO",
        "css": "linear-gradient(90deg,#ff0000,#ffff00)"
    },

    "HIELO": {
        "nombre": "Hielo",
        "tipo": "MAQUINA",
        "rareza": "RARO",
        "css": "linear-gradient(90deg,#00ffff,#ffffff)"
    },

    "NEON": {
        "nombre": "Neón",
        "tipo": "MAQUINA",
        "rareza": "RARO",
        "css": "linear-gradient(90deg,#00ff00,#00ffff,#ff00ff)"
    },

    "OCEANO": {
        "nombre": "Océano",
        "tipo": "MAQUINA",
        "rareza": "RARO",
        "css": "linear-gradient(90deg,#0066ff,#00ffff)"
    },

    "ATARDECER": {
        "nombre": "Atardecer",
        "tipo": "MAQUINA",
        "rareza": "RARO",
        "css": "linear-gradient(90deg,#ff5500,#ff00aa)"
    },

    "ELECTRICO": {
        "nombre": "Eléctrico",
        "tipo": "MAQUINA",
        "rareza": "EPICO",
        "css": "linear-gradient(90deg,#0044ff,#ffffff)"
    },

    "TOXICO": {
        "nombre": "Tóxico",
        "tipo": "MAQUINA",
        "rareza": "EPICO",
        "css": "linear-gradient(90deg,#00ff00,#99ff00)"
    },

    "GALAXIA": {
        "nombre": "Galaxia",
        "tipo": "MAQUINA",
        "rareza": "LEGENDARIO",
        "css": "linear-gradient(90deg,#ff69b4,#7700ff,#220044)"
    },

    "LAVA": {
        "nombre": "Lava",
        "tipo": "MAQUINA",
        "rareza": "LEGENDARIO",
        "css": "linear-gradient(90deg,#ff0000,#ff7700,#ffff00)"
    },

    "AURORA": {
        "nombre": "Aurora",
        "tipo": "MAQUINA",
        "rareza": "LEGENDARIO",
        "css": "linear-gradient(90deg,#00ffcc,#00ffff,#aa00ff)"
    },

    "ARCOIRIS": {
        "nombre": "Arcoíris",
        "tipo": "MAQUINA",
        "rareza": "LEGENDARIO",
        "css": "linear-gradient(90deg,#ff0000,#ffff00,#00ff00,#00ffff,#0088ff,#ff00ff)"
    },

    "VOID": {
        "nombre": "Void",
        "tipo": "MAQUINA",
        "rareza": "MITICO",
        "css": "linear-gradient(90deg,#000000,#330066,#aa00ff)"
    },

    "SANGRE": {
        "nombre": "Sangre",
        "tipo": "MAQUINA",
        "rareza": "MITICO",
        "css": "linear-gradient(90deg,#330000,#ff0000,#660000)"
    },

    "VENENO": {
        "nombre": "Veneno",
        "tipo": "MAQUINA",
        "rareza": "MITICO",
        "css": "linear-gradient(90deg,#003300,#00ff00,#66ff00)"
    },

    "COSMICO": {
        "nombre": "Cósmico",
        "tipo": "MAQUINA",
        "rareza": "MITICO",
        "css": "linear-gradient(90deg,#ff00ff,#2200ff,#00ffff)"
    },

    "DIAMANTE": {
        "nombre": "Diamante",
        "tipo": "MAQUINA",
        "rareza": "MITICO",
        "css": "linear-gradient(90deg,#ffffff,#00ffff,#0088ff)"
    },

    "DORADO": {
        "nombre": "Dorado",
        "tipo": "MAQUINA",
        "rareza": "MITICO",
        "css": "linear-gradient(90deg,#aa6600,#ffff00,#ffffff)"
    },

    "NEGRO_INFERNAL": {
        "nombre": "Negro Infernal",
        "tipo": "MAQUINA",
        "rareza": "SECRETO",
        "css": "linear-gradient(90deg,#000000,#ff0000,#000000)"
    },

    "GALAXIA_ROSA": {
        "nombre": "Galaxia Rosa",
        "tipo": "MAQUINA",
        "rareza": "SECRETO",
        "css": "linear-gradient(90deg,#ff69b4,#aa00ff,#220044)"
    },

    "SUPERNOVA": {
        "nombre": "Supernova",
        "tipo": "MAQUINA",
        "rareza": "SECRETO",
        "css": "linear-gradient(90deg,#ffffff,#ffff00,#ff6600,#ff0000)"
    },

    "DRAGON": {
        "nombre": "Dragón",
        "tipo": "MAQUINA",
        "rareza": "SECRETO",
        "css": "linear-gradient(90deg,#ff0000,#ff00ff,#7700ff)"
    },

    "GLITCH": {
        "nombre": "Glitch",
        "tipo": "MAQUINA",
        "rareza": "SECRETO",
        "css": "linear-gradient(90deg,#ff0000,#00ffff,#ff00ff,#00ff00)"
    },

    "VOID_COSMICO": {
        "nombre": "Void Cósmico",
        "tipo": "MAQUINA",
        "rareza": "ULTRA",
        "css": "linear-gradient(90deg,#000000,#220044,#ff00ff,#000000)"
    },

    "PERIKO": {
        "nombre": "Periko",
        "tipo": "MAQUINA",
        "rareza": "ULTRA",
        "css": "linear-gradient(90deg,#ffff00,#ff0055,#00ffff,#ffff00)"
    },

    "DIVINO": {
        "nombre": "Divino",
        "tipo": "MAQUINA",
        "rareza": "ULTRA",
        "css": "linear-gradient(90deg,#ffffff,#ffff00,#ffffff)"
    }
}


def get_db():
    if "db" not in g:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL no esta configurada.")

        g.db = psycopg2.connect(
            DATABASE_URL,
            connect_timeout=10,
            sslmode="require"
        )

    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    if not DATABASE_URL:
        print("DATABASE_URL no configurada. La base de datos no puede inicializarse.")
        return

    conn = psycopg2.connect(
        DATABASE_URL,
        connect_timeout=20,
        sslmode="require"
    )

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id BIGSERIAL PRIMARY KEY,
                    username VARCHAR(30) UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    perikoins BIGINT NOT NULL DEFAULT 500,
                    ultimo_rescate TIMESTAMPTZ,
                    notif_regalo BIGINT NOT NULL DEFAULT 0,
                    avatar_activo INTEGER NOT NULL DEFAULT 1,
                    avatares_desbloqueados JSONB NOT NULL DEFAULT '[1]'::jsonb,
                    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_usuarios_perikoins
                ON usuarios(perikoins DESC);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_usuarios_username
                ON usuarios(username);
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS color_nombre
                VARCHAR(50) NOT NULL DEFAULT 'BLANCO'
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS colores_desbloqueados
                JSONB NOT NULL DEFAULT '["BLANCO"]'::jsonb
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS racha_dias
                INTEGER NOT NULL DEFAULT 0
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS prestigio
                BIGINT NOT NULL DEFAULT 0
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS ultima_conexion
                DATE
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS nivel
                INTEGER NOT NULL DEFAULT 1
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS exp
                INTEGER NOT NULL DEFAULT 0
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS victorias
                INTEGER NOT NULL DEFAULT 0
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS derrotas
                INTEGER NOT NULL DEFAULT 0
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS max_perikoins
                BIGINT NOT NULL DEFAULT 500
            """)

            cur.execute("""
                ALTER TABLE usuarios
                ADD COLUMN IF NOT EXISTS titulo_custom
                TEXT DEFAULT NULL
            """)

            # Titulo exclusivo del creador
            cur.execute("""
                UPDATE usuarios
                SET titulo_custom = '👑 EL CREADOR'
                WHERE username = 'periko'
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS mensajes_globales (
                    id BIGSERIAL PRIMARY KEY,
                    mensaje TEXT NOT NULL,
                    activo BOOLEAN NOT NULL DEFAULT TRUE,
                    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_mensajes_globales_activo
                ON mensajes_globales(activo, creado_en DESC)
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS novedades (
                    id BIGSERIAL PRIMARY KEY,
                    titulo VARCHAR(200) NOT NULL,
                    contenido TEXT NOT NULL,
                    autor VARCHAR(30) NOT NULL,
                    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_novedades_creado
                ON novedades(creado_en DESC)
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS retos_bj (
                    id BIGSERIAL PRIMARY KEY,
                    retidor TEXT NOT NULL,
                    retado TEXT NOT NULL,
                    apuesta BIGINT NOT NULL,
                    estado TEXT NOT NULL DEFAULT 'pendiente',
                    mazo JSONB,
                    mano_j1 TEXT[],
                    mano_j2 TEXT[],
                    plantado_j1 BOOLEAN NOT NULL DEFAULT FALSE,
                    plantado_j2 BOOLEAN NOT NULL DEFAULT FALSE,
                    turno TEXT NOT NULL DEFAULT 'j1',
                    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    terminado_en TIMESTAMPTZ
                )
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_retos_bj_retado
                ON retos_bj(retado, estado, creado_en DESC)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_retos_bj_retidor
                ON retos_bj(retidor, estado, creado_en DESC)
            """)

        conn.commit()

    finally:
        conn.close()


def obtener_usuario(username):
    db = get_db()

    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT *
            FROM usuarios
            WHERE username = %s
            """,
            (username,)
        )

        return cur.fetchone()


def calcular_apuesta_monto(valor, saldo_actual):
    if valor == "ALLIN":
        return saldo_actual

    try:
        monto = int(valor)

        if monto <= 0:
            return 0

        return monto

    except (TypeError, ValueError):
        return 0


def actualizar_saldo(username, nuevo_saldo):
    db = get_db()

    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE usuarios
            SET perikoins = %s
            WHERE username = %s
            """,
            (nuevo_saldo, username)
        )

    db.commit()


def cargar_avatares(valor):
    if isinstance(valor, list):
        return valor

    if isinstance(valor, str):
        try:
            return json.loads(valor)
        except Exception:
            return [1]

    return [1]

def actualizar_racha(usuario):
    """
    Actualiza la racha de conexion diaria del usuario.
    Si se conecto hoy y ya estaba registrado, no cambia nada.
    Si se conecto hoy por primera vez, suma 1.
    Si paso mas de 1 dia sin conectarse, se reinicia a 1.
    """
    db = get_db()
    username = usuario["username"]
    hoy = datetime.utcnow().date()
    ultima = usuario.get("ultima_conexion")
    racha_actual = usuario.get("racha_dias", 0) or 0

    if ultima is not None:
        if isinstance(ultima, datetime):
            ultima = ultima.date()

    if ultima == hoy:
        return racha_actual

    if ultima is not None:
        diferencia = (hoy - ultima).days

        if diferencia == 1:
            nueva_racha = racha_actual + 1
        else:
            nueva_racha = 1
    else:
        nueva_racha = 1

    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE usuarios
            SET racha_dias = %s,
                ultima_conexion = %s
            WHERE username = %s
            """,
            (nueva_racha, hoy, username)
        )

    db.commit()

    return nueva_racha


def obtener_estilo_color(color_nombre):
    color = COLORES_NOMBRE.get(
        color_nombre,
        COLORES_NOMBRE["BLANCO"]
    )

    css = color.get("css", "#ffffff")

    if css.startswith("linear-gradient"):
        return (
            f"background:{css};"
            "-webkit-background-clip:text;"
            "-webkit-text-fill-color:transparent;"
            "background-clip:text;"
        )

    return f"color:{css};"


def dar_exp(username, cantidad=EXP_POR_VICTORIA):
    """Otorga EXP al usuario tras ganar una partida.
    Si la EXP acumulada alcanza el requerido, sube de nivel.
    La EXP se reinicia a 0 al subir de nivel.
    Puede subir multiples niveles de una vez.
    """
    db = get_db()

    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT nivel, exp FROM usuarios WHERE username = %s FOR UPDATE",
            (username,)
        )
        fila = cur.fetchone()

        if not fila:
            db.rollback()
            return

        nivel_actual = fila["nivel"]
        exp_actual = fila["exp"]

        if nivel_actual >= NIVEL_MAXIMO:
            db.commit()
            return

        exp_actual += cantidad

        while nivel_actual < NIVEL_MAXIMO and exp_actual >= exp_necesaria(nivel_actual):
            exp_actual -= exp_necesaria(nivel_actual)
            nivel_actual += 1

        if nivel_actual >= NIVEL_MAXIMO:
            nivel_actual = NIVEL_MAXIMO
            exp_actual = 0

        cur.execute(
            "UPDATE usuarios SET nivel = %s, exp = %s WHERE username = %s",
            (nivel_actual, exp_actual, username)
        )

    db.commit()


CSS = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PERIKOS BET ARCADE</title>

<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
rel="stylesheet">

<style>

* {
    box-sizing:border-box;
    font-family:'Press Start 2P',cursive;
}

body {
    background-color:#0d001a;
    background-image:
        linear-gradient(rgba(255,0,128,.15) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,0,128,.15) 1px,transparent 1px);
    background-size:30px 30px;
    color:#00ffcc;
    display:flex;
    flex-direction:column;
    align-items:center;
    min-height:100vh;
    margin:0;
    padding:20px 0;
}

.arcade-box {
    background:#1a0033;
    border:5px solid #ff007f;
    box-shadow:0 0 25px #ff007f,inset 0 0 15px #ff007f;
    border-radius:18px;
    padding:25px;
    width:92%;
    max-width:560px;
    text-align:center;
}

h1 {
    color:#ffff00;
    font-size:15px;
    line-height:1.6;
}

input,select {
    width:100%;
    padding:12px;
    margin:8px 0 15px;
    background:#000;
    border:2px solid #00ffcc;
    color:#fff;
    border-radius:5px;
}

label {
    display:block;
    text-align:left;
    font-size:8px;
    color:#ff7700;
    margin-top:8px;
}

button {
    font-family:'Press Start 2P',cursive;
}

.btn {
    background:#ff0055;
    color:#fff;
    border:0;
    border-bottom:5px solid #990033;
    padding:14px 8px;
    font-size:9px;
    border-radius:8px;
    cursor:pointer;
    width:100%;
    margin-top:8px;
    text-decoration:none;
    display:block;
    transition:transform .15s ease,filter .15s ease,box-shadow .15s ease;
}

.btn:hover {
    filter:brightness(1.3);
    transform:translateY(-3px) scale(1.02);
    box-shadow:0 0 15px currentColor;
}

.game-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
    margin:12px 0;
}

.game-card {
    background:linear-gradient(145deg,#1a002e,#2a0044);
    border:3px solid #ff007f;
    border-bottom:5px solid #990033;
    border-radius:12px;
    padding:16px 8px;
    cursor:pointer;
    text-decoration:none;
    color:#fff;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    gap:8px;
    transition:transform .15s ease,filter .15s ease,box-shadow .15s ease;
    min-height:100px;
}

.game-card:hover {
    filter:brightness(1.3);
    transform:translateY(-3px) scale(1.02);
    box-shadow:0 0 18px #ff007f;
}

.game-card:active {
    transform:translateY(2px) scale(.98);
}

.game-card .game-icon {
    font-size:30px;
    line-height:1;
}

.game-card .game-name {
    font-size:7px;
    text-align:center;
    line-height:1.4;
    color:#fff;
}

.game-card.g-dados { border-color:#ff0055; box-shadow:0 0 10px rgba(255,0,85,.3); }
.game-card.g-dados:hover { box-shadow:0 0 20px #ff0055; }

.game-card.g-ruleta { border-color:#ffff00; box-shadow:0 0 10px rgba(255,255,0,.3); }
.game-card.g-ruleta:hover { box-shadow:0 0 20px #ffff00; }

.game-card.g-cartas { border-color:#00ffcc; box-shadow:0 0 10px rgba(0,255,204,.3); }
.game-card.g-cartas:hover { box-shadow:0 0 20px #00ffcc; }

.game-card.g-moneda { border-color:#ff7700; box-shadow:0 0 10px rgba(255,119,0,.3); }
.game-card.g-moneda:hover { box-shadow:0 0 20px #ff7700; }

.game-card.g-slots { border-color:#ff00ff; box-shadow:0 0 10px rgba(255,0,255,.3); }
.game-card.g-slots:hover { box-shadow:0 0 20px #ff00ff; }

.game-card.g-derby { border-color:#00ff66; box-shadow:0 0 10px rgba(0,255,102,.3); }
.game-card.g-derby:hover { box-shadow:0 0 20px #00ff66; }

.game-card.g-blackjack { border-color:#ff4444; box-shadow:0 0 10px rgba(255,68,68,.3); }
.game-card.g-blackjack:hover { box-shadow:0 0 20px #ff4444; }

.game-card.g-crash { border-color:#ff6600; box-shadow:0 0 10px rgba(255,102,0,.3); }
.game-card.g-crash:hover { box-shadow:0 0 20px #ff6600; }

/* === CRASH GAME STYLES === */
.crash-container {
    margin:15px 0;
    text-align:center;
}
.crash-graph {
    position:relative;
    width:100%;
    height:180px;
    background:#080808;
    border:2px solid #ff6600;
    border-radius:10px;
    overflow:hidden;
    margin:10px 0;
}
.crash-line {
    position:absolute;
    bottom:0;
    left:0;
    width:0;
    height:0;
    border-radius:2px;
    transition:none;
}
.crash-multiplier {
    position:absolute;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    font-size:28px;
    font-weight:bold;
    color:#ff6600;
    text-shadow:0 0 20px #ff6600, 0 0 40px rgba(255,102,0,.5);
    z-index:3;
    animation:crashPulse .15s infinite alternate;
}
.crash-multiplier.crashed {
    color:#ff0033;
    text-shadow:0 0 20px #ff0033, 0 0 40px rgba(255,0,51,.5);
    animation:none;
}
.crash-multiplier.cashed {
    color:#00ff66;
    text-shadow:0 0 20px #00ff66, 0 0 40px rgba(0,255,102,.5);
    animation:none;
}
.crash-rocket {
    position:absolute;
    font-size:26px;
    z-index:4;
    transition:none;
}
.crash-rocket.exploded {
    animation:explode .6s ease-out forwards;
}
.crash-history {
    display:flex;
    flex-wrap:wrap;
    gap:4px;
    margin:10px 0;
    justify-content:center;
}
.crash-history-item {
    font-size:7px;
    padding:2px 6px;
    border-radius:3px;
    border:1px solid #333;
}
.crash-history-item.green { color:#00ff66; border-color:#00ff6644; background:#00ff6611; }
.crash-history-item.red { color:#ff0033; border-color:#ff003344; background:#ff003311; }
.crash-bet-area {
    margin:10px 0;
}
.crash-cashout-btn {
    display:inline-block;
    background:linear-gradient(145deg,#00cc44,#00ff66);
    color:#000;
    border:2px solid #00ff66;
    padding:12px 30px;
    font-size:9px;
    font-family:'Press Start 2P',monospace;
    cursor:pointer;
    text-transform:uppercase;
    animation:cashoutPulse .4s infinite alternate;
    margin-top:8px;
}
.crash-cashout-btn:hover {
    box-shadow:0 0 20px #00ff66;
}
.crash-cashout-btn:disabled {
    opacity:.4;
    cursor:not-allowed;
    animation:none;
}
@keyframes crashPulse {
    0% { transform:translate(-50%,-50%) scale(1); }
    100% { transform:translate(-50%,-50%) scale(1.06); }
}
@keyframes cashoutPulse {
    0% { box-shadow:0 0 5px #00ff66; transform:scale(1); }
    100% { box-shadow:0 0 20px #00ff66; transform:scale(1.04); }
}
@keyframes explode {
    0% { transform:scale(1); opacity:1; }
    40% { transform:scale(1.8); opacity:.8; }
    100% { transform:scale(0); opacity:0; }
}

/* === DERBY MEJORADO STYLES === */
.derby-bet-type {
    margin:8px 0;
    text-align:center;
}
.derby-bet-type select {
    width:90%;
    font-size:7px;
}
.derby-bet-extra {
    margin:8px 0;
    text-align:center;
}
.derby-bet-extra select {
    width:90%;
    font-size:7px;
}
.derby-odds-table {
    width:100%;
    font-size:7px;
    border-collapse:collapse;
    margin:8px 0;
    text-align:center;
}
.derby-odds-table th {
    color:#00ffcc;
    padding:4px;
    border-bottom:1px solid #00ffcc33;
}
.derby-odds-table td {
    padding:3px 4px;
    color:#ccc;
}
.derby-exacta-info {
    font-size:7px;
    color:#ffaa00;
    margin:5px 0;
    text-align:center;
    border:1px dashed #ffaa0044;
    padding:6px;
    border-radius:5px;
}
.derby-podium {
    margin:15px 0;
    text-align:center;
}
.derby-podium-position {
    display:inline-block;
    margin:0 8px;
    text-align:center;
    vertical-align:bottom;
}
.derby-podium-position.p1 .podium-bar { height:60px; background:linear-gradient(#ffcc00,#aa8800); border:2px solid #ffcc00; }
.derby-podium-position.p2 .podium-bar { height:45px; background:linear-gradient(#cccccc,#888888); border:2px solid #ccc; }
.derby-podium-position.p3 .podium-bar { height:32px; background:linear-gradient(#cc6633,#884422); border:2px solid #cc6633; }
.podium-bar {
    width:60px;
    border-radius:4px 4px 0 0;
    margin:0 auto;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:6px;
    color:#000;
    font-weight:bold;
}
.podium-icon {
    font-size:20px;
    margin-bottom:4px;
}

@media (max-width:380px) {
    .game-card .game-icon { font-size:24px; }
    .game-card .game-name { font-size:6px; }
    .game-card { min-height:85px; padding:12px 6px; }
    .game-grid { gap:8px; }
}

.btn:active {
    transform:translateY(2px) scale(.98);
}

.btn-yellow {
    background:#ffff00;
    color:#000;
}

.btn-green {
    background:#00ffcc;
    color:#000;
}

.btn-purple {
    background:#ff00ff;
}

.btn-red {
    background:#ff0000;
}

.badge {
    background:#ffff00;
    color:#000;
    padding:10px;
    font-size:9px;
    border-radius:7px;
    display:inline-block;
    margin-bottom:10px;
}

.msg {
    color:#ff00ff;
    font-size:8px;
    line-height:1.6;
    margin:12px 0;
    animation:messageAppear .35s ease-out;
}

.win {
    color:#00ff00;
    background:rgba(0,255,0,.1);
    border:2px dashed #00ff00;
    padding:12px;
    border-radius:8px;
    font-size:9px;
    line-height:1.6;
    margin:15px 0;
    animation:winAppear .45s ease-out;
}

.grid {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:7px;
}

.chip {
    background:#000;
    color:#00ffcc;
    border:2px solid #00ffcc;
    padding:10px 4px;
    border-radius:5px;
    cursor:pointer;
    font-size:7px;
    transition:transform .15s ease,filter .15s ease,box-shadow .15s ease;
}

.chip:hover {
    transform:translateY(-3px) scale(1.02);
    filter:brightness(1.25);
    box-shadow:0 0 15px #00ffcc;
}

.chip:active {
    transform:translateY(2px) scale(.98);
}

.allin {
    grid-column:span 3;
    background:#ff0055;
    color:#fff;
    border:2px solid #ffff00;
    padding:12px;
    border-radius:5px;
    cursor:pointer;
    font-size:8px;
    transition:transform .15s ease,filter .15s ease,box-shadow .15s ease;
}

.allin:hover {
    transform:translateY(-3px) scale(1.02);
    filter:brightness(1.25);
    box-shadow:0 0 15px #ff0055;
}

.allin:active {
    transform:translateY(2px) scale(.98);
}

.racha-badge {
    display:inline-flex;
    align-items:center;
    gap:6px;
    background:linear-gradient(135deg,#ff4400,#ff8800,#ffcc00);
    color:#000;
    padding:6px 14px;
    border-radius:20px;
    font-size:9px;
    margin:6px 0 10px;
    animation:streakPulse 1.2s ease-in-out infinite;
    border:2px solid #ff6600;
    box-shadow:0 0 12px #ff6600;
}

@keyframes streakPulse {
    0%,100%{transform:scale(1);box-shadow:0 0 8px #ff6600}
    50%{transform:scale(1.06);box-shadow:0 0 20px #ff8800}
}

.racha-fire {
    animation:fireFlicker .4s ease-in-out infinite alternate;
    display:inline-block;
}

@keyframes fireFlicker {
    0%{transform:translateY(0) scale(1);filter:brightness(1)}
    100%{transform:translateY(-2px) scale(1.15);filter:brightness(1.3)}
}

.link {
    color:#ffff00;
    font-size:8px;
    text-decoration:none;
    display:block;
    margin-top:15px;
}

.game-icon {
    font-size:55px;
    margin:15px;
    animation:arcadePulse 1.5s infinite;
}

.slots {
    display:flex;
    justify-content:center;
    gap:8px;
    background:#000;
    border:3px solid #00ffcc;
    padding:15px;
    border-radius:8px;
    margin:15px 0;
}

.reel {
    width:65px;
    height:65px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#1a0033;
    border:2px solid #ff0055;
    border-radius:8px;
    font-size:28px;
}

.avatar-grid {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:7px;
    max-height:330px;
    overflow-y:auto;
    padding:5px;
}

.avatar-item {
    background:#000;
    border:2px solid #333;
    color:#fff;
    padding:8px 3px;
    border-radius:7px;
    font-size:6px;
    cursor:pointer;
    transition:transform .15s ease,filter .15s ease,box-shadow .15s ease;
}

.avatar-item.active {
    border-color:#ffff00;
    box-shadow:0 0 10px #ffff00;
}

.locked {
    opacity:.25;
}

.name-color {
    font-size:9px;
    font-weight:bold;
    padding:8px;
    margin:5px 0;
    border-radius:5px;
    background:#000;
}

.color-card {
    background:#000;
    border:2px solid #333;
    padding:12px;
    margin:8px 0;
    border-radius:8px;
}

.color-preview {
    font-size:10px;
    padding:8px;
    margin:8px 0;
    border-radius:5px;
    background:#111;
    border:1px solid #555;
}

.machine {
    background:#080010;
    border:3px solid #ff00ff;
    box-shadow:0 0 15px #ff00ff;
    padding:18px;
    margin:15px 0;
    border-radius:10px;
}

.machine-icon {
    font-size:55px;
    animation:arcadePulse 1s infinite;
}

.rarity {
    font-size:7px;
    margin-top:5px;
}

table {
    width:100%;
    border-collapse:collapse;
    font-size:7px;
}

th {
    background:#ff0055;
    color:#fff;
    padding:8px;
}

td {
    background:#000;
    color:#00ffcc;
    border:1px solid #ff007f;
    padding:8px 3px;
}

.chest {
    background:#000;
    border:2px solid #00ffcc;
    padding:15px;
    margin:10px 0;
    border-radius:8px;
}

.chest-icon {
    font-size:40px;
}

.runner {
    background:#000;
    padding:8px;
    margin:7px 0;
    border-radius:5px;
}

.bar-bg {
    height:20px;
    background:#222;
    border-radius:5px;
    overflow:hidden;
}

.bar {
    height:100%;
    transition:width 4s ease;
}

.race {
    margin:20px 0;
    text-align:left;
}

.race-title {
    color:#ffff00;
    font-size:8px;
    text-align:center;
    margin-bottom:15px;
    animation:arcadePulse 1s infinite;
}

.racer {
    margin:12px 0;
}

.racer-name {
    font-size:7px;
    margin-bottom:5px;
    color:#fff;
}

.race-track {
    position:relative;
    height:38px;
    background:#080808;
    border:2px solid #00ffcc;
    border-radius:7px;
    overflow:hidden;
}

.race-finish {
    position:absolute;
    right:5px;
    top:0;
    bottom:0;
    width:5px;
    background:#ffff00;
    box-shadow:0 0 10px #ffff00;
    z-index:1;
}

.race-runner {
    position:absolute;
    left:0;
    top:50%;
    transform:translateY(-50%);
    font-size:22px;
    z-index:2;
    transition:left 4s cubic-bezier(.15,.8,.2,1);
}

.race-glow {
    position:absolute;
    left:0;
    top:0;
    bottom:0;
    width:0%;
    opacity:.18;
    transition:width 4s cubic-bezier(.15,.8,.2,1);
}

.racer.winner .race-track {
    border-color:#ffff00;
    box-shadow:0 0 15px #ffff00;
}

.racer.winner .race-runner {
    animation:winnerBounce .35s infinite alternate;
}

.race-result {
    display:none;
    margin-top:20px;
    padding:15px;
    border:2px dashed #ffff00;
    color:#ffff00;
    text-align:center;
    animation:winAppear .5s ease-out;
}

@keyframes arcadePulse {
    0%,100% {
        transform:scale(1);
    }

    50% {
        transform:scale(1.12);
    }
}

@keyframes winAppear {
    0% {
        opacity:0;
        transform:scale(.7);
    }

    70% {
        transform:scale(1.08);
    }

    100% {
        opacity:1;
        transform:scale(1);
    }
}

@keyframes messageAppear {
    from {
        opacity:0;
        transform:translateY(-10px);
    }

    to {
        opacity:1;
        transform:translateY(0);
    }
}

@keyframes winnerBounce {
    from {
        transform:translateY(-50%) scale(1);
    }

    to {
        transform:translateY(-50%) scale(1.25);
    }
}

/* ================================
   ANIMACIONES ARCADE
================================ */

.arcade-box {
    animation:gameEntry .45s ease-out;
}

.global-banner {
    width:92%;
    max-width:560px;
    position:fixed;
    top:12px;
    left:50%;
    transform:translateX(-50%);
    z-index:9999;
    background:rgba(0,0,0,.94);
    border:2px solid #ffff00;
    color:#ffff00;
    box-shadow:0 0 18px #ffff00;
    border-radius:10px;
    padding:12px 14px;
    font-size:8px;
    line-height:1.6;
    text-align:center;
    animation:bannerDrop .55s ease-out, bannerPulse 2.5s ease-in-out infinite;
}

.global-banner-icon {
    display:inline-block;
    margin-right:6px;
    animation:arcadePulse 1.2s infinite;
}

.game-icon {
    animation:floatIcon 1.8s ease-in-out infinite;
    transform-origin:center;
    text-shadow:0 0 18px currentColor;
}

[data-game="DADOS"] .game-icon {
    animation:diceRoll 1.4s ease-in-out infinite;
}

[data-game="RULETA ROYALE"] .game-icon {
    animation:rouletteSpin 2.2s linear infinite;
}

[data-game="CARA O CRUZ"] .game-icon {
    animation:coinFlip 1.5s ease-in-out infinite;
}

[data-game="MAYOR O MENOR"] .game-icon,
[data-game="BLACKJACK"] .game-icon {
    animation:cardDeal 1.5s ease-in-out infinite;
}

[data-game="TRAGAPERRAS 8-BITS"] .game-icon {
    animation:slotMachine 1.1s ease-in-out infinite;
}

[data-game="CARRERA DE PERIKOS"] .game-icon {
    animation:raceIcon 1s ease-in-out infinite;
}

[data-game="CRASH ROCKET"] .game-icon {
    animation:crashIcon 1s ease-in-out infinite;
}

.game-result {
    animation:resultPop .5s cubic-bezier(.2,.8,.2,1);
    transform-origin:center;
}

.game-message {
    animation:messageAppear .45s ease-out;
}

select {
    transition:transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}

select:focus {
    transform:scale(1.02);
    box-shadow:0 0 16px #00ffcc;
}

.btn, .chip, .allin {
    position:relative;
    overflow:hidden;
}

.btn::after, .chip::after, .allin::after {
    content:"";
    position:absolute;
    top:-60%;
    left:-100%;
    width:55%;
    height:220%;
    background:rgba(255,255,255,.22);
    transform:rotate(20deg);
    transition:left .45s ease;
    pointer-events:none;
}

.btn:hover::after, .chip:hover::after, .allin:hover::after {
    left:135%;
}

.slot-machine {
    display:flex;
    justify-content:center;
    gap:8px;
    background:#000;
    border:3px solid #00ffcc;
    padding:15px;
    border-radius:8px;
    margin:15px 0;
    box-shadow:0 0 20px rgba(0,255,204,.35);
}

.slot-reel {
    width:65px;
    height:65px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#1a0033;
    border:2px solid #ff0055;
    border-radius:8px;
    font-size:28px;
    opacity:0;
    transform:translateY(-28px) scale(.7);
}

.slot-reel.show {
    animation:slotReveal .55s cubic-bezier(.2,.9,.2,1) forwards;
}

.slot-reel.jackpot {
    animation:slotReveal .55s cubic-bezier(.2,.9,.2,1) forwards, jackpotPulse .45s ease-in-out .55s 3;
}

@keyframes gameEntry {
    from { opacity:0; transform:translateY(12px) scale(.97); }
    to { opacity:1; transform:translateY(0) scale(1); }
}

@keyframes bannerDrop {
    from { opacity:0; transform:translate(-50%,-25px) scale(.9); }
    to { opacity:1; transform:translate(-50%,0) scale(1); }
}

@keyframes bannerPulse {
    0%,100% { box-shadow:0 0 12px #ffff00; }
    50% { box-shadow:0 0 25px #ffff00; }
}

@keyframes floatIcon {
    0%,100% { transform:translateY(0) rotate(-2deg); }
    50% { transform:translateY(-9px) rotate(2deg); }
}

@keyframes diceRoll {
    0% { transform:rotate(0) scale(1); }
    25% { transform:rotate(90deg) scale(1.08); }
    50% { transform:rotate(180deg) scale(1); }
    75% { transform:rotate(270deg) scale(1.08); }
    100% { transform:rotate(360deg) scale(1); }
}

@keyframes rouletteSpin {
    to { transform:rotate(360deg); }
}

@keyframes coinFlip {
    0%,100% { transform:rotateY(0) scale(1); }
    50% { transform:rotateY(180deg) scale(1.12); }
}

@keyframes cardDeal {
    0% { transform:translateX(-18px) rotate(-8deg) scale(.85); opacity:.4; }
    60% { transform:translateX(5px) rotate(3deg) scale(1.08); opacity:1; }
    100% { transform:translateX(0) rotate(0) scale(1); }
}

@keyframes slotMachine {
    0%,100% { transform:scale(1) rotate(0); }
    25% { transform:scale(1.08) rotate(-4deg); }
    75% { transform:scale(1.08) rotate(4deg); }
}

@keyframes raceIcon {
    0%,100% { transform:translateX(0) scale(1); }
    50% { transform:translateX(9px) scale(1.1); }
}

@keyframes crashIcon {
    0%,100% { transform:translateY(0) scale(1); }
    50% { transform:translateY(-10px) scale(1.12); }
}

@keyframes resultPop {
    0% { opacity:0; transform:scale(.72) translateY(8px); }
    70% { transform:scale(1.05) translateY(-2px); }
    100% { opacity:1; transform:scale(1) translateY(0); }
}

@keyframes slotReveal {
    0% { opacity:0; transform:translateY(-28px) scale(.7) rotateX(80deg); }
    65% { opacity:1; transform:translateY(5px) scale(1.08) rotateX(-8deg); }
    100% { opacity:1; transform:translateY(0) scale(1) rotateX(0); }
}

@keyframes jackpotPulse {
    0%,100% { transform:scale(1); filter:brightness(1); }
    50% { transform:scale(1.18); filter:brightness(1.8); }
}

.carnaval-banner {
    background: linear-gradient(90deg, #ff00ff, #ff6600, #ffff00, #00ff00, #00ffff, #ff00ff);
    background-size: 400% 100%;
    animation: carnaval-gradient 3s linear infinite;
    color: #fff;
    text-align: center;
    padding: 10px 0;
    font-weight: bold;
    font-size: 1.1em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    border-bottom: 3px solid #ff00ff;
    width: 100%;
    flex-shrink: 0;
    position: relative;
    z-index: 100;
}

@keyframes carnaval-gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* === PVP BLACKJACK STYLES === */
.game-card.g-pvp-bj { border-color:#cc00ff; box-shadow:0 0 10px rgba(204,0,255,.3); }
.game-card.g-pvp-bj:hover { box-shadow:0 0 20px #cc00ff; }
.pvp-bj-container { text-align:center; padding:10px; }
.pvp-bj-hands { display:flex; justify-content:center; gap:20px; flex-wrap:wrap; margin:10px 0; }
.pvp-bj-hand { flex:1; min-width:200px; max-width:350px; border:2px solid #cc00ff; border-radius:8px; padding:12px; background:rgba(204,0,255,.1); }
.pvp-bj-hand h3 { color:#cc00ff; font-size:9px; margin:0 0 8px; text-transform:uppercase; }
.pvp-bj-hand .cards { color:#00ffff; font-size:14px; margin:6px 0; letter-spacing:2px; }
.pvp-bj-hand .score { color:#ffff00; font-size:10px; margin:4px 0; }
.pvp-bj-hand .status { font-size:7px; margin:4px 0; }
.pvp-bj-hand .status.standing { color:#00ff66; }
.pvp-bj-hand .status.busted { color:#ff0033; }
.pvp-bj-hand .status.turn { color:#cc00ff; animation:blink 1s infinite; }
.pvp-bj-turn-indicator { color:#cc00ff; font-size:9px; animation:blink 1s infinite; margin:10px 0; }
.pvp-bj-result { margin:12px 0; padding:10px; border:2px solid #cc00ff; border-radius:8px; }
.pvp-bj-actions { margin:10px 0; }
.pvp-bj-actions form { display:inline; margin:0 4px; }
.pvp-bj-actions button { background:#cc00ff; color:#000; border:2px solid #8800aa; border-bottom:4px solid #660088; padding:8px 16px; font-family:'Press Start 2P',monospace; font-size:8px; cursor:pointer; }
.pvp-bj-actions button:hover { background:#dd33ff; }
.pvp-bj-actions button.btn-stand { background:#00cc66; border-color:#009944; border-bottom-color:#007733; color:#000; }
.pvp-bj-actions button.btn-stand:hover { background:#00dd77; }
.reto-list { margin:10px 0; text-align:left; }
.reto-item { border:1px solid #cc00ff44; background:rgba(204,0,255,.05); padding:8px; margin:6px 0; border-radius:4px; }
.reto-item .reto-info { color:#00ffff; font-size:8px; }
.reto-item .reto-actions { margin-top:6px; }
@keyframes parpadeo { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

</style>
</head>
<body>

{% if carnaval %}
<style>
.arcade-box {
    border-color: #ff00ff;
    box-shadow: 0 0 30px #ff00ff, inset 0 0 20px #ff00ff;
}
body {
    background-color: #1a0022;
    background-image:
        linear-gradient(rgba(255,0,255,.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,0,255,.18) 1px, transparent 1px);
    background-size: 30px 30px;
}
h1 { color: #ff00ff; }
.btn { background: #ff00ff; border-bottom-color: #9900aa; }
.btn-green { background: #00ffaa; }
.btn-yellow { background: #ffff00; }
.btn-red { background: #ff4466; }
.btn-purple { background: #ff44ff; }
input, select, textarea { border-color: #ff00ff; }
label { color: #ff88ff; }
.msg { border-color: #ff00ff; color: #ff88ff; }
.chip { background: #ff00ff; border-bottom-color: #9900aa; }
.link { color: #ff88ff; }
.game-card { border-color: #ff00ff; background: rgba(255,0,255,.12); }
.game-card:hover { box-shadow: 0 0 16px #ff00ff; background: rgba(255,0,255,.22); }
.game-card .game-icon { filter: hue-rotate(90deg); }
</style>
<div class="carnaval-banner">
    🎭 ¡MODO CARNAVAL ACTIVADO! 🎭 — Ganancias x2 · EXP x2 — 🎉🎊
</div>
{% endif %}

{% if oscuro %}
<style>
.oscuro-banner {
    background: linear-gradient(90deg, #111111, #330000, #111111, #001133, #111111);
    background-size: 400% 100%;
    animation: oscuro-gradient 3s linear infinite;
    color: #ff3333;
    text-align: center;
    padding: 10px 0;
    font-weight: bold;
    font-size: 1.1em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
    border-bottom: 3px solid #ff0000;
    width: 100%;
    flex-shrink: 0;
    position: relative;
    z-index: 100;
}
@keyframes oscuro-gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.arcade-box {
    border-color: #330000;
    box-shadow: 0 0 20px #220000, inset 0 0 15px #110000;
}
body {
    background-color: #050505;
    background-image:
        linear-gradient(rgba(100,0,0,.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(100,0,0,.12) 1px, transparent 1px);
    background-size: 30px 30px;
}
h1 { color: #aa0000; }
.btn { background: #440000; border-bottom-color: #220000; }
.btn-green { background: #003300; color: #00ff00; }
.btn-yellow { background: #332200; color: #ffaa00; }
.btn-red { background: #550000; }
.btn-purple { background: #220022; }
input, select, textarea { border-color: #440000; background: #0a0a0a; color: #aa0000; }
label { color: #884444; }
.msg { border-color: #440000; color: #aa0000; }
.chip { background: #440000; border-bottom-color: #220000; }
.link { color: #884444; }
.game-card { border-color: #330000; background: rgba(50,0,0,.15); }
.game-card:hover { box-shadow: 0 0 12px #440000; background: rgba(50,0,0,.25); }
</style>
<div class="oscuro-banner">
    🖤 ¡MODO OSCURO ACTIVADO! 🖤 — Ganancias x3 · EXP x3 — 🩸💀
</div>
{% endif %}

{% if divino %}
<style>
.divino-banner {
    background: linear-gradient(90deg, #00ffff, #ffff00, #00ffff, #ffff00, #00ffff);
    background-size: 400% 100%;
    animation: divino-gradient 2s linear infinite;
    color: #000;
    text-align: center;
    padding: 10px 0;
    font-weight: bold;
    font-size: 1.1em;
    text-shadow: 0 0 8px rgba(255,255,255,.6);
    border-bottom: 3px solid #00ffff;
    width: 100%;
    flex-shrink: 0;
    position: relative;
    z-index: 100;
}
@keyframes divino-gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.arcade-box {
    border-color: #00ffff;
    box-shadow: 0 0 30px #00ffff, 0 0 30px #ffff00, inset 0 0 20px #00ffff;
}
body {
    background-color: #001a1a;
    background-image:
        linear-gradient(rgba(0,255,255,.15) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,0,.1) 1px, transparent 1px);
    background-size: 30px 30px;
}
h1 { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
.btn { background: #00cccc; border-bottom-color: #008888; }
.btn-green { background: #00ffee; }
.btn-yellow { background: #ffff00; }
.btn-red { background: #00dddd; }
.btn-purple { background: #00cccc; }
input, select, textarea { border-color: #00ffff; color: #00ffff; }
label { color: #88ffff; }
.msg { border-color: #00ffff; color: #88ffff; }
.chip { background: #00ffff; border-bottom-color: #008888; }
.link { color: #88ffff; }
.game-card { border-color: #00ffff; background: rgba(0,255,255,.1); }
.game-card:hover { box-shadow: 0 0 16px #00ffff, 0 0 16px #ffff00; background: rgba(0,255,255,.2); }
</style>
<div class="divino-banner">
    ✨ ¡MODO DIVINO ACTIVADO! ✨ — Ganancias x4 · EXP x4 — 🌟⚡
</div>
{% endif %}

{% if global_mensaje %}
<div class="global-banner">
    <span class="global-banner-icon">📢</span>
    <span>{{ global_mensaje }}</span>
</div>
{% endif %}
"""


HTML_REGISTRO = CSS + """

<div class="arcade-box">

<h1>PERIKOS BET<br>ARCADE</h1>

<div class="win">
BONUS DE BIENVENIDA<br>
500 PERIKOINS GRATIS
</div>

{% if error %}
<div class="msg">{{ error }}</div>
{% endif %}

<form method="POST">

<label>GAMER TAG / USUARIO</label>
<input name="username" maxlength="30" required>

<label>PASSWORD</label>
<input type="password" name="password" required>

<button class="btn" type="submit">
CREAR CUENTA
</button>

</form>

<a class="link" href="/login">
YA TIENES CUENTA? ENTRA AQUI
</a>

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template_string(
                HTML_REGISTRO,
                error="Completa todos los campos."
            )

        if len(username) > 30:
            return render_template_string(
                HTML_REGISTRO,
                error="El usuario es demasiado largo."
            )

        db = get_db()

        try:
            with db.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO usuarios
                    (
                        username,
                        password,
                        perikoins,
                        avatares_desbloqueados
                    )
                    VALUES (%s,%s,500,%s)
                    """,
                    (
                        username,
                        generate_password_hash(password),
                        json.dumps([1])
                    )
                )

            db.commit()

            session.clear()
            session["user"] = username

            return redirect(url_for("menu"))

        except psycopg2.errors.UniqueViolation:
            db.rollback()

            return render_template_string(
                HTML_REGISTRO,
                error="Ese Gamer Tag ya existe."
            )

    return render_template_string(
        HTML_REGISTRO,
        error=None
    )


HTML_LOGIN = CSS + """

<div class="arcade-box">

<h1>PERIKOS BET<br>ARCADE</h1>

<p style="font-size:9px;color:#ff7700">
INSERT COIN TO PLAY
</p>

{% if error %}
<div class="msg">{{ error }}</div>
{% endif %}

<form method="POST">

<label>GAMER TAG</label>
<input name="username" required>

<label>PASSWORD</label>
<input type="password" name="password" required>

<button class="btn" type="submit">
ENTER ARCADE
</button>

</form>

<a class="link" href="/">
NO TIENES CUENTA? REGISTRATE
</a>

</div>

</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        usuario = obtener_usuario(username)

        if (
            usuario
            and check_password_hash(
                usuario["password"],
                password
            )
        ):
            session.clear()
            session["user"] = username

            return redirect(url_for("menu"))

        return render_template_string(
            HTML_LOGIN,
            error="Gamer Tag o contraseña incorrecta."
        )

    return render_template_string(HTML_LOGIN)


def comprobar_mantenimiento():
    if not MODO_MANTENIMIENTO:
        return None

    if request.endpoint in {"login", "logout", "admin", "health"}:
        return None

    if session.get("user"):
        usuario = obtener_usuario(session["user"])
        if usuario and usuario["username"].lower() == "periko":
            return None

    return render_template_string(
        CSS + """
        <div class="arcade-box">
            <h1 style="color:#ffff00">⚠️ MANTENIMIENTO</h1>
            <div class="msg">
                PERIKOS BET ARCADE ESTA EN MANTENIMIENTO.
                <br><br>
                SOLO LA CUENTA PERIKO PUEDE ENTRAR.
            </div>
        </div>
        </body>
        </html>
        """
    ), 503


@app.before_request
def modo_mantenimiento():
    return comprobar_mantenimiento()


def usuario_actual():
    if "user" not in session:
        return None

    return obtener_usuario(session["user"])


@app.context_processor
def contexto_global():
    """Expone el último mensaje global activo en todas las páginas."""
    global_mensaje = None

    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""
                SELECT mensaje
                FROM mensajes_globales
                WHERE activo = TRUE
                ORDER BY creado_en DESC
                LIMIT 1
            """)
            fila = cur.fetchone()
            if fila:
                global_mensaje = fila[0]
    except Exception as e:
        # Un anuncio nunca debe impedir que cargue el arcade.
        print("ERROR AL CARGAR MENSAJE GLOBAL:", e)

    return {"global_mensaje": global_mensaje, "carnaval": MODO_CARNAVAL, "oscuro": MODO_OSCURO, "divino": MODO_DIVINO}


HTML_MENU = CSS + """

<div class="arcade-box" style="max-width:640px;">

<h1>PERIKOS BET</h1>

{% if regalo %}
<div class="win">
🎁 PERIKO TE ENVIO {{ regalo }} PERIKOINS 🎁
</div>
{% endif %}

<div class="badge">
{{ avatar.icon }}

<span style="{{ color_estilo }}">
    {{ usuario.username }}
</span>

<br><br>

{{ usuario.perikoins }} P
<br>
<span style="color:#ffaa00;font-size:7px;">⭐ {{ usuario.prestigio }}</span>
</div>

{% if racha > 0 %}
<div class="racha-badge">
    <span class="racha-fire">🔥</span>
    {{ racha }} DIA{% if racha != 1 %}S{% endif %}
</div>
{% endif %}

{% if usuario.perikoins == 0 %}

<div class="msg">
TE HAS QUEDADO EN BANCARROTA!
</div>

<a class="btn btn-yellow" href="/rescate">
RESCATE DIARIO<br>
500 PERIKOINS
</a>

{% endif %}

<p style="font-size:8px;color:#ff7700">
SELECCIONA UN JUEGO
</p>

<div class="game-grid">

<a class="game-card g-dados" href="/juego/dados">
<span class="game-icon">🎲</span>
<span class="game-name">DADOS</span>
</a>

<a class="game-card g-ruleta" href="/juego/ruleta">
<span class="game-icon">🎡</span>
<span class="game-name">RULETA ROYALE</span>
</a>

<a class="game-card g-cartas" href="/juego/cartas">
<span class="game-icon">♠♥</span>
<span class="game-name">MAYOR O MENOR</span>
</a>

<a class="game-card g-moneda" href="/juego/moneda">
<span class="game-icon">🪙</span>
<span class="game-name">CARA O CRUZ</span>
</a>

<a class="game-card g-slots" href="/juego/slots">
<span class="game-icon">🎰</span>
<span class="game-name">TRAGAPERRAS 8-BITS</span>
</a>

<a class="game-card g-derby" href="/juego/derby">
<span class="game-icon">🏁</span>
<span class="game-name">CARRERA DE PERIKOS</span>
</a>

<a class="game-card g-blackjack" href="/juego/blackjack">
<span class="game-icon">🃏</span>
<span class="game-name">BLACKJACK</span>
</a>

<a class="game-card g-crash" href="/juego/crash">
<span class="game-icon">📈</span>
<span class="game-name">CRASH ROCKET</span>
</a>

<a class="game-card g-pvp-bj" href="/retar-bj">
<span class="game-icon">⚔️</span>
<span class="game-name">BJ PVP</span>
</a>

</div>

<p style="font-size:7px;color:#555;margin:10px 0 6px;">──────────────────────</p>

<a class="btn btn-yellow" href="/tienda">
📦 TIENDA DE COFRES
</a>

<a class="btn btn-green" href="/perfil">
🖼️ MI PERFIL
</a>

<a class="btn btn-purple" href="/ranking">
🏆 TOP 50
</a>

{% if es_admin %}
<a class="btn btn-red" href="/admin">
PANEL ADMIN PERIKO
</a>
{% endif %}

<a class="btn" style="background:linear-gradient(135deg,#ff6600,#ffaa00);color:#000;border-bottom:5px solid #cc5500;" href="/novedades">
📰 NOVEDADES
</a>

<a class="link" href="/logout">
[CERRAR SESION]
</a>

</div>

</body>
</html>
"""


@app.route("/menu")
def menu():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    regalo = usuario["notif_regalo"]

    if regalo and regalo > 0:
        db = get_db()

        with db.cursor() as cur:
            cur.execute(
                """
                UPDATE usuarios
                SET notif_regalo = 0
                WHERE username = %s
                """,
                (usuario["username"],)
            )

        db.commit()

    avatar = AVATARES_DB.get(
        usuario["avatar_activo"],
        AVATARES_DB[1]
    )

    color_estilo = obtener_estilo_color(
        usuario["color_nombre"]
    )

    racha = actualizar_racha(usuario)

    return render_template_string(
        HTML_MENU,
        usuario=usuario,
        avatar=avatar,
        regalo=regalo,
        color_estilo=color_estilo,
        racha=racha,
        es_admin=(
            usuario["username"].lower() == "periko"
        )
    )

def procesar_apuesta(
    usuario,
    apuesta,
    ganado,
    multiplicador,
    mensaje_gana,
    mensaje_pierde
):
    db = get_db()

    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT *
            FROM usuarios
            WHERE username = %s
            FOR UPDATE
            """,
            (usuario["username"],)
        )

        actual = cur.fetchone()

        if not actual:
            db.rollback()
            return False, "Usuario no encontrado."

        saldo = int(actual["perikoins"])

        if apuesta <= 0:
            db.rollback()
            return False, "Apuesta inválida."

        if apuesta > saldo:
            db.rollback()
            return False, "Saldo insuficiente."

        if ganado:
            mult_real = multiplicador
            modo_activo = None
            if MODO_CARNAVAL:
                mult_real = multiplicador * 2
                modo_activo = "CARNAVAL x2"
            if MODO_OSCURO:
                mult_real = multiplicador * 3
                modo_activo = "OSCURO x3"
            if MODO_DIVINO:
                mult_real = multiplicador * 4
                modo_activo = "DIVINO x4"
            if mensaje_gana:
                if modo_activo:
                    mensaje_gana += f" 🌑 ¡{modo_activo}!"
            nuevo_saldo = saldo + (apuesta * mult_real)
            mensaje = mensaje_gana
        else:
            nuevo_saldo = saldo - apuesta
            mensaje = mensaje_pierde

        cur.execute(
            """
            UPDATE usuarios
            SET perikoins = %s,
                victorias = victorias + %s,
                derrotas = derrotas + %s,
                max_perikoins = GREATEST(max_perikoins, %s)
            WHERE username = %s
            """,
            (
                nuevo_saldo,
                1 if ganado else 0,
                0 if ganado else 1,
                nuevo_saldo,
                usuario["username"]
            )
        )

    db.commit()

    # --- Registrar movimiento si el registro está activo ---
    if REGISTRO_ACTIVO:
        import time as _time
        REGISTRO_MOVIMIENTOS.append({
            "timestamp": _time.time(),
            "usuario": usuario["username"],
            "tipo": "Ganó" if ganado else "Perdió",
            "cantidad": apuesta * (multiplicador * (2 if MODO_CARNAVAL else 1) * (3 if MODO_OSCURO else 1) * (4 if MODO_DIVINO else 1)) if ganado else apuesta,
            "juego": mensaje_gana[:30] if ganado else mensaje_pierde[:30]
        })

    if ganado:
        exp_mult = 1
        if MODO_CARNAVAL:
            exp_mult = 2
        if MODO_OSCURO:
            exp_mult = 3
        if MODO_DIVINO:
            exp_mult = 4
        exp_cantidad = EXP_POR_VICTORIA * exp_mult
        dar_exp(usuario["username"], cantidad=exp_cantidad)

    return ganado, mensaje


HTML_JUEGO = CSS + """

<div class="arcade-box" data-game="{{ titulo }}">

<h1>{{ titulo }}</h1>

<div class="badge">
SALDO: {{ usuario.perikoins }} P
</div>

{% if visual %}
<div class="game-icon">
{{ visual }}
</div>
{% endif %}

{% if slot_resultados %}
<div class="game-result">
    <div class="slot-machine" id="slotMachine">
        {% for simbolo in slot_resultados %}
        <div class="slot-reel" data-slot-index="{{ loop.index0 }}">{{ simbolo }}</div>
        {% endfor %}
    </div>
</div>
{% elif resultado %}
<div class="win game-result">
RESULTADO:<br><br>
{{ resultado }}
</div>
{% endif %}

{% if mensaje %}

{% if victoria %}
<div class="win game-message">
✨ {{ mensaje }} ✨
</div>
{% else %}
<div class="msg game-message">
{{ mensaje }}
</div>
{% endif %}

{% endif %}

{% if descripcion %}
<p style="font-size:7px;color:#00ffcc">
{{ descripcion }}
</p>
{% endif %}

<form method="POST">

{% if opciones %}

<label>{{ label_opciones }}</label>

<select name="{{ nombre_opciones }}">

{% for valor, texto in opciones %}
<option value="{{ valor }}">
{{ texto }}
</option>
{% endfor %}

</select>

{% endif %}

<label>SELECCIONA TU APUESTA</label>

<div class="grid">

{% for cantidad in [10,50,100,250,500,1000,5000,10000,50000] %}

<button
class="chip"
name="apuesta"
value="{{ cantidad }}"
type="submit">
{{ cantidad }}
</button>

{% endfor %}

<button
class="allin"
name="apuesta"
value="ALLIN"
type="submit">
ALL IN
</button>

</div>

</form>

<a class="link" href="/menu">
< VOLVER AL MENU
</a>

</div>

{% if slot_resultados %}
<script>
(function () {
    const reels = document.querySelectorAll(".slot-reel");
    reels.forEach((reel, index) => {
        setTimeout(() => {
            reel.classList.add("show");
        }, index * 1000);
    });

    {% if victoria and slot_jackpot %}
    setTimeout(() => {
        reels.forEach(reel => reel.classList.add("jackpot"));
    }, 3100);
    {% endif %}
})();
</script>
{% endif %}

</body>
</html>
"""


@app.route("/juego/dados", methods=["GET", "POST"])
def dados():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""
    resultado = None
    victoria = False

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        try:
            elegido = int(request.form.get("numero", 1))
        except ValueError:
            elegido = 0

        if elegido < 1 or elegido > 6:
            mensaje = "Numero invalido."
        else:
            resultado = random.randint(1, 6)
            victoria = resultado == elegido

            if victoria:
                ganancia = apuesta * 5

                mensaje = (
                    f"ACERTASTE! Salio {resultado}. "
                    f"Ganaste {ganancia} Perikoins!"
                )

                victoria, mensaje = procesar_apuesta(
                    usuario,
                    apuesta,
                    True,
                    5,
                    mensaje,
                    ""
                )
            else:
                mensaje = (
                    f"PERDISTE. Salio {resultado}. "
                    f"Perdiste {apuesta} Perikoins."
                )

                victoria, mensaje = procesar_apuesta(
                    usuario,
                    apuesta,
                    False,
                    0,
                    "",
                    mensaje
                )

            usuario = obtener_usuario(session["user"])

    return render_template_string(
        HTML_JUEGO,
        titulo="DADOS",
        usuario=usuario,
        visual="🎲",
        resultado=resultado,
        mensaje=mensaje,
        victoria=victoria,
        descripcion="Elige un numero del 1 al 6.",
        opciones=[
            (str(n), str(n))
            for n in range(1, 7)
        ],
        label_opciones="ELIGE UN NUMERO",
        nombre_opciones="numero"
    )


@app.route("/juego/moneda", methods=["GET", "POST"])
def moneda():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""
    resultado = None
    victoria = False

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        eleccion = request.form.get("eleccion")

        if eleccion not in ["CARA", "CRUZ"]:
            mensaje = "Eleccion invalida."
        else:
            if random.random() < 0.01:
                resultado = "CANTO"
                ganancia = apuesta * 10

                mensaje = (
                    "INCREIBLE! La moneda cayo DE CANTO! "
                    f"Ganaste {ganancia} Perikoins!"
                )

                victoria, mensaje = procesar_apuesta(
                    usuario,
                    apuesta,
                    True,
                    10,
                    mensaje,
                    ""
                )
            else:
                resultado = random.choice(["CARA", "CRUZ"])
                victoria = resultado == eleccion

                if victoria:
                    ganancia = apuesta * 2

                    mensaje = (
                        f"ACERTASTE! Salio {resultado}. "
                        f"Ganaste {ganancia} Perikoins!"
                    )

                    victoria, mensaje = procesar_apuesta(
                        usuario,
                        apuesta,
                        True,
                        2,
                        mensaje,
                        ""
                    )
                else:
                    mensaje = (
                        f"PERDISTE. Salio {resultado}. "
                        f"Perdiste {apuesta} Perikoins."
                    )

                    victoria, mensaje = procesar_apuesta(
                        usuario,
                        apuesta,
                        False,
                        0,
                        "",
                        mensaje
                    )

            usuario = obtener_usuario(session["user"])

    return render_template_string(
        HTML_JUEGO,
        titulo="CARA O CRUZ",
        usuario=usuario,
        visual="🪙",
        resultado=resultado,
        mensaje=mensaje,
        victoria=victoria,
        opciones=[
            ("CARA", "CARA (x2)"),
            ("CRUZ", "CRUZ (x2)")
        ],
        label_opciones="ELIGE LADO",
        nombre_opciones="eleccion"
    )


@app.route("/juego/ruleta", methods=["GET", "POST"])
def ruleta():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""
    resultado = None
    victoria = False

    opciones = [
        ("ROJO", "ROJO (PARES)"),
        ("NEGRO", "NEGRO (IMPARES)")
    ]

    opciones += [
        (str(n), f"NUMERO {n}")
        for n in range(1, 7)
    ]

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        tipo = request.form.get("tipo_apuesta")

        resultado = random.randint(1, 6)

        color = (
            "ROJO"
            if resultado % 2 == 0
            else "NEGRO"
        )

        if tipo in ["ROJO", "NEGRO"]:
            victoria = tipo == color
            multiplicador = 2
        else:
            try:
                victoria = int(tipo) == resultado
            except Exception:
                victoria = False

            multiplicador = 5

        if victoria:
            ganancia = apuesta * multiplicador

            mensaje = (
                f"GANASTE! Salio {resultado} "
                f"({color}). "
                f"Ganaste {ganancia} Perikoins!"
            )

            victoria, mensaje = procesar_apuesta(
                usuario,
                apuesta,
                True,
                multiplicador,
                mensaje,
                ""
            )
        else:
            mensaje = (
                f"PERDISTE. Salio {resultado} "
                f"({color}). "
                f"Perdiste {apuesta} Perikoins."
            )

            victoria, mensaje = procesar_apuesta(
                usuario,
                apuesta,
                False,
                0,
                "",
                mensaje
            )

        usuario = obtener_usuario(session["user"])

    return render_template_string(
        HTML_JUEGO,
        titulo="RULETA ROYALE",
        usuario=usuario,
        visual="🎡",
        resultado=resultado,
        mensaje=mensaje,
        victoria=victoria,
        opciones=opciones,
        label_opciones="TIPO DE APUESTA",
        nombre_opciones="tipo_apuesta"
    )


@app.route("/juego/cartas", methods=["GET", "POST"])
def cartas():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""
    resultado = None
    victoria = False

    if "carta_base" not in session:
        session["carta_base"] = random.randint(2, 12)

    carta_base = session["carta_base"]

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        eleccion = request.form.get("eleccion")

        # La siguiente carta SIEMPRE será distinta a la carta base.
        cartas_posibles = [
            n for n in range(1, 14)
            if n != carta_base
        ]
        resultado = random.choice(cartas_posibles)

        if eleccion == "MAYOR":
            victoria = resultado > carta_base
        elif eleccion == "MENOR":
            victoria = resultado < carta_base
        else:
            victoria = False

        if victoria:
            ganancia = apuesta * 2

            mensaje = (
                f"ACERTASTE! Carta base {carta_base}, "
                f"salio {resultado}. "
                f"Ganaste {ganancia} Perikoins!"
            )

            victoria, mensaje = procesar_apuesta(
                usuario,
                apuesta,
                True,
                2,
                mensaje,
                ""
            )
        else:
            mensaje = (
                f"PERDISTE. Carta base {carta_base}, "
                f"salio {resultado}. "
                f"Perdiste {apuesta} Perikoins."
            )

            victoria, mensaje = procesar_apuesta(
                usuario,
                apuesta,
                False,
                0,
                "",
                mensaje
            )

        session["carta_base"] = resultado

        usuario = obtener_usuario(session["user"])
        carta_base = resultado

    return render_template_string(
        HTML_JUEGO,
        titulo="MAYOR O MENOR",
        usuario=usuario,
        visual="🃏",
        resultado=(
            f"Carta base: {carta_base}"
            if resultado is None
            else f"{carta_base} -> {resultado}"
        ),
        mensaje=mensaje,
        victoria=victoria,
        opciones=[
            ("MAYOR", "MAYOR"),
            ("MENOR", "MENOR")
        ],
        label_opciones="SIGUIENTE CARTA",
        nombre_opciones="eleccion"
    )


@app.route("/juego/slots", methods=["GET", "POST"])
def slots():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""
    resultado = None
    victoria = False
    slot_resultados = None
    slot_jackpot = False

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        simbolos = [
            "👻",
            "🍒",
            "💎",
            "🪙"
        ]

        r1 = random.choice(simbolos)
        r2 = random.choice(simbolos)
        r3 = random.choice(simbolos)

        slot_resultados = [r1, r2, r3]
        resultado = f"{r1} {r2} {r3}"

        if r1 == r2 == r3:
            slot_jackpot = True
            multiplicadores = {
                "🪙": 50,
                "💎": 20,
                "🍒": 10,
                "👻": 5
            }

            mult = multiplicadores[r1]
            ganancia = apuesta * mult

            mensaje = (
                f"JACKPOT 3x {r1}! "
                f"Ganaste {ganancia} Perikoins!"
            )

            victoria, mensaje = procesar_apuesta(
                usuario,
                apuesta,
                True,
                mult,
                mensaje,
                ""
            )

        elif r1 == r2 or r2 == r3 or r1 == r3:
            ganancia = apuesta * 2

            mensaje = (
                f"PAR DE SIMBOLOS! "
                f"Ganaste {ganancia} Perikoins!"
            )

            victoria, mensaje = procesar_apuesta(
                usuario,
                apuesta,
                True,
                2,
                mensaje,
                ""
            )

        else:
            mensaje = (
                f"SIN COINCIDENCIAS. "
                f"Perdiste {apuesta} Perikoins."
            )

            victoria, mensaje = procesar_apuesta(
                usuario,
                apuesta,
                False,
                0,
                "",
                mensaje
            )

        usuario = obtener_usuario(session["user"])

    return render_template_string(
        HTML_JUEGO,
        titulo="TRAGAPERRAS 8-BITS",
        usuario=usuario,
        visual="🎰",
        resultado=resultado,
        mensaje=mensaje,
        victoria=victoria,
        slot_resultados=slot_resultados,
        slot_jackpot=slot_jackpot
    )


def valor_blackjack(mano):
    total = 0
    ases = 0
    for carta in mano:
        rango = carta[:-1]
        if rango in ("J", "Q", "K"):
            total += 10
        elif rango == "A":
            total += 11
            ases += 1
        else:
            total += int(rango)
    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total


@app.route("/juego/blackjack", methods=["GET", "POST"])
def blackjack():
    usuario = usuario_actual()
    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""
    resultado = None
    victoria = False

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        if apuesta <= 0 or apuesta > usuario["perikoins"]:
            mensaje = "Apuesta inválida o saldo insuficiente."
        else:
            mazo = [
                f"{r}{p}"
                for r in ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
                for p in ["♠","♥","♦","♣"]
            ]
            random.shuffle(mazo)
            jugador = [mazo.pop(), mazo.pop()]
            crupier = [mazo.pop(), mazo.pop()]

            while valor_blackjack(crupier) < 17:
                crupier.append(mazo.pop())

            pj = valor_blackjack(jugador)
            pc = valor_blackjack(crupier)
            resultado = (
                f"TÚ: {' '.join(jugador)} = {pj}<br>"
                f"CRUPIER: {' '.join(crupier)} = {pc}"
            )

            blackjack_natural = pj == 21 and len(jugador) == 2
            crupier_blackjack = pc == 21 and len(crupier) == 2

            if blackjack_natural and not crupier_blackjack:
                victoria, mensaje = procesar_apuesta(
                    usuario, apuesta, True, 3,
                    f"BLACKJACK! Ganaste {apuesta * 3} Perikoins!", ""
                )
            elif pj > 21:
                victoria, mensaje = procesar_apuesta(
                    usuario, apuesta, False, 0, "",
                    f"TE PASASTE ({pj}). Perdiste {apuesta} Perikoins."
                )
            elif pc > 21 or pj > pc:
                victoria, mensaje = procesar_apuesta(
                    usuario, apuesta, True, 2,
                    f"GANASTE! Recibiste {apuesta * 2} Perikoins!", ""
                )
            elif pj == pc:
                victoria, mensaje = procesar_apuesta(
                    usuario, apuesta, True, 1,
                    f"EMPATE. Recuperaste tus {apuesta} Perikoins!", ""
                )
            else:
                victoria, mensaje = procesar_apuesta(
                    usuario, apuesta, False, 0, "",
                    f"PERDISTE. Perdiste {apuesta} Perikoins."
                )

            usuario = obtener_usuario(session["user"])

    return render_template_string(
        HTML_JUEGO,
        titulo="BLACKJACK",
        usuario=usuario,
        visual="🃏",
        resultado=resultado,
        mensaje=mensaje,
        victoria=victoria,
        descripcion="BLACKJACK = x3 · VICTORIA = x2 · EMPATE = x1",
        opciones=None,
        label_opciones=None,
        nombre_opciones=None
    )


HTML_DERBY = CSS + """

<div class="arcade-box">

<h1>🏁 CARRERA DE PERIKOS 🏁</h1>

<div class="badge">
SALDO: {{ usuario.perikoins }} P
</div>

<p style="font-size:7px;color:#00ffcc">
¡ELIGE TU PERIKO Y MIRA LA CARRERA!
</p>

{% if mensaje %}
<div class="{% if victoria %}win{% else %}msg{% endif %}">
{{ mensaje }}
</div>
{% endif %}

<form method="POST">

<label>TIPO DE APUESTA</label>

<div class="derby-bet-type">
<select name="tipo_apuesta" id="tipoApuesta" onchange="derbyToggleBetType()">
<option value="GANADOR">🏆 GANADOR — Elegir 1er lugar</option>
<option value="EXACTA">🎯 EXACTA — 1ro y 2do en orden (x{{ mult_exacta }})</option>
<option value="TRIFECTA">💎 TRIFECTA — 1ro, 2do y 3ro en orden (x{{ mult_trifecta }})</option>
</select>
</div>

<div class="derby-bet-extra" id="derbyExtra2">
<label>2do LUGAR</label>
<select name="corredor2">
{% for valor,texto in opciones %}
<option value="{{ valor }}">{{ texto }}</option>
{% endfor %}
</select>
</div>

<div class="derby-bet-extra" id="derbyExtra3">
<label>3er LUGAR</label>
<select name="corredor3">
{% for valor,texto in opciones %}
<option value="{{ valor }}">{{ texto }}</option>
{% endfor %}
</select>
</div>

<label>ELIGE CORREDOR (1er LUGAR)</label>

<select name="corredor" required>

{% for valor,texto in opciones %}

<option value="{{ valor }}">
{{ texto }}
</option>

{% endfor %}

</select>

<div class="derby-exacta-info">
💡 EXACTA: Acertar 1ro y 2do en orden exacto → x{{ mult_exacta }}<br>
💎 TRIFECTA: Acertar 1ro, 2do y 3ro en orden exacto → x{{ mult_trifecta }}<br>
⚠️ No puedes repetir corredores en la misma apuesta.
</div>

<label>SELECCIONA TU APUESTA</label>

<div class="grid">

{% for cantidad in [10,50,100,250,500,1000,5000] %}

<button
class="chip"
name="apuesta"
value="{{ cantidad }}"
type="submit">
{{ cantidad }}
</button>

{% endfor %}

<button
class="allin"
name="apuesta"
value="ALLIN"
type="submit">
ALL IN
</button>

</div>

</form>

<table class="derby-odds-table">
<tr><th>CORREDOR</th><th>CUOTA</th><th>PROB.~</th></tr>
{% for clave,texto in opciones %}
<tr><td>{{ texto }}</td><td style="color:#ffaa00;">x{{ cuotas[clave] }}</td><td>{{ probabilidades[clave] }}%</td></tr>
{% endfor %}
</table>

{% if carrera %}

<div class="race">

<div class="race-title">
🏁 ¡QUE COMIENCE LA CARRERA! 🏁
</div>

{% for corredor,data in carrera.items() %}

<div
class="racer {% if corredor == positions[0] %}winner{% endif %}"
data-score="{{ data.score }}"
>

<div class="racer-name">
{{ data.icon }} {{ data.nombre }}
{% if data.pos %}<span style="color:#ffaa00;font-size:6px;margin-left:4px;">{{ data.pos }}</span>{% endif %}
</div>

<div class="race-track">

<div
class="race-glow"
style="background:{{ data.color }}">
</div>

<div class="race-runner">
{{ data.icon }}
</div>

<div class="race-finish"></div>

</div>

</div>

{% endfor %}

<div class="derby-podium">
<div class="derby-podium-position p2">
<div class="podium-icon">{{ carrera[positions[1]].icon }}</div>
<div class="podium-bar">2do</div>
<div style="font-size:6px;color:#aaa;">{{ carrera[positions[1]].nombre }}</div>
</div>
<div class="derby-podium-position p1">
<div class="podium-icon">{{ carrera[positions[0]].icon }}</div>
<div class="podium-bar">1ro</div>
<div style="font-size:6px;color:#aaa;">{{ carrera[positions[0]].nombre }}</div>
</div>
<div class="derby-podium-position p3">
<div class="podium-icon">{{ carrera[positions[2]].icon }}</div>
<div class="podium-bar">3ro</div>
<div style="font-size:6px;color:#aaa;">{{ carrera[positions[2]].nombre }}</div>
</div>
</div>

<div id="raceResult" class="race-result">
🏆 ¡{{ carrera[positions[0]].nombre|upper }} GANÓ! 🏆
</div>

</div>

<script>

function derbyToggleBetType() {
    var tipo = document.getElementById("tipoApuesta").value;
    var ex2 = document.getElementById("derbyExtra2");
    var ex3 = document.getElementById("derbyExtra3");
    if (tipo === "GANADOR") {
        ex2.style.display = "none";
        ex3.style.display = "none";
    } else if (tipo === "EXACTA") {
        ex2.style.display = "block";
        ex3.style.display = "none";
    } else {
        ex2.style.display = "block";
        ex3.style.display = "block";
    }
}
derbyToggleBetType();

const racers = document.querySelectorAll(".racer");
const result = document.getElementById("raceResult");

racers.forEach((racer, index) => {

    const score = Number(racer.dataset.score);

    const runner = racer.querySelector(".race-runner");
    const glow = racer.querySelector(".race-glow");

    const duration = 3500 + ((100 - score) * 20);

    setTimeout(() => {

        runner.style.transition =
            `left ${duration}ms cubic-bezier(.15,.8,.2,1)`;

        glow.style.transition =
            `width ${duration}ms cubic-bezier(.15,.8,.2,1)`;

        runner.style.left = "calc(100% - 32px)";

        glow.style.width =
            Math.max(5, score - 5) + "%";

    }, index * 120);

});

setTimeout(() => {

    if (result) {
        result.style.display = "block";
    }

}, 4300);

</script>

{% endif %}

<a class="link" href="/menu">
< VOLVER AL MENU
</a>

</div>

</body>
</html>
"""


@app.route("/juego/derby", methods=["GET", "POST"])
def derby():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""
    victoria = False
    carrera = None
    ganador = None
    positions = None

    corredores = {
        "ROJO": {
            "nombre": "PERIKO ROJO",
            "icon": "🔴",
            "color": "#ff0033"
        },
        "VERDE": {
            "nombre": "PERIKO VERDE",
            "icon": "🟢",
            "color": "#00ff66"
        },
        "AZUL": {
            "nombre": "PERIKO AZUL",
            "icon": "🔵",
            "color": "#0088ff"
        },
        "DORADO": {
            "nombre": "PERIKO DORADO",
            "icon": "🟡",
            "color": "#ffff00"
        }
    }

    cuotas = {
        "ROJO": 2,
        "VERDE": 3,
        "AZUL": 4,
        "DORADO": 8
    }

    probabilidades = {
        "ROJO": 40,
        "VERDE": 28,
        "AZUL": 22,
        "DORADO": 10
    }

    mult_exacta = 8
    mult_trifecta = 30

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        corredor_elegido = request.form.get("corredor")
        tipo_apuesta = request.form.get("tipo_apuesta", "GANADOR")
        corredor2 = request.form.get("corredor2", "")
        corredor3 = request.form.get("corredor3", "")

        if corredor_elegido not in corredores:
            mensaje = "Corredor invalido."

        elif apuesta <= 0:
            mensaje = "Apuesta invalida."

        elif apuesta > usuario["perikoins"]:
            mensaje = "No tienes suficientes Perikoins."

        else:
            # Generar scores y determinar posiciones
            scores = {
                "ROJO": random.randint(30, 100),
                "VERDE": random.randint(25, 100),
                "AZUL": random.randint(20, 100),
                "DORADO": random.randint(10, 100)
            }

            # Ordenar por score descendente para obtener posiciones
            positions = sorted(
                scores.keys(),
                key=scores.get,
                reverse=True
            )
            ganador = positions[0]

            carrera = {}
            pos_labels = ["🥇", "🥈", "🥉", "4°"]
            for i, nombre in enumerate(positions):
                carrera[nombre] = {
                    **corredores[nombre],
                    "score": scores[nombre],
                    "pos": pos_labels[i]
                }

            gano = False
            mult = 0

            if tipo_apuesta == "GANADOR":
                if corredor_elegido == ganador:
                    gano = True
                    mult = cuotas[corredor_elegido]
                    mensaje = (
                        f"🏆 GANO EL {corredores[ganador]['nombre']}! "
                        f"Ganaste {apuesta * mult} Perikoins "
                        f"(x{mult})!"
                    )
                else:
                    mensaje = (
                        f"GANO EL {corredores[ganador]['nombre']}. "
                        f"Tu corredor perdió. "
                        f"Perdiste {apuesta} Perikoins."
                    )

            elif tipo_apuesta == "EXACTA":
                if not corredor2 or corredor2 not in corredores:
                    mensaje = "Selecciona un 2do corredor para la Exacta."
                elif corredor2 == corredor_elegido:
                    mensaje = "No puedes repetir corredores en la Exacta."
                else:
                    if positions[0] == corredor_elegido and positions[1] == corredor2:
                        gano = True
                        mult = mult_exacta
                        mensaje = (
                            f"🎯 EXACTA PERFECTA! "
                            f"1ro: {corredores[positions[0]]['nombre']}, "
                            f"2do: {corredores[positions[1]]['nombre']}! "
                            f"Ganaste {apuesta * mult} Perikoins "
                            f"(x{mult})!"
                        )
                    else:
                        mensaje = (
                            f"Exacta fallida. "
                            f"1ro: {corredores[positions[0]]['nombre']}, "
                            f"2do: {corredores[positions[1]]['nombre']}. "
                            f"Perdiste {apuesta} Perikoins."
                        )

            elif tipo_apuesta == "TRIFECTA":
                if not corredor2 or corredor2 not in corredores:
                    mensaje = "Selecciona 2do y 3er corredor para la Trifecta."
                elif not corredor3 or corredor3 not in corredores:
                    mensaje = "Selecciona un 3er corredor para la Trifecta."
                elif len(set([corredor_elegido, corredor2, corredor3])) < 3:
                    mensaje = "No puedes repetir corredores en la Trifecta."
                else:
                    if (positions[0] == corredor_elegido
                            and positions[1] == corredor2
                            and positions[2] == corredor3):
                        gano = True
                        mult = mult_trifecta
                        mensaje = (
                            f"💎 TRIFECTA PERFECTA! "
                            f"1ro: {corredores[positions[0]]['nombre']}, "
                            f"2do: {corredores[positions[1]]['nombre']}, "
                            f"3ro: {corredores[positions[2]]['nombre']}! "
                            f"Ganaste {apuesta * mult} Perikoins "
                            f"(x{mult})!"
                        )
                    else:
                        mensaje = (
                            f"Trifecta fallida. "
                            f"1ro: {corredores[positions[0]]['nombre']}, "
                            f"2do: {corredores[positions[1]]['nombre']}, "
                            f"3ro: {corredores[positions[2]]['nombre']}. "
                            f"Perdiste {apuesta} Perikoins."
                        )

            if gano:
                victoria, mensaje = procesar_apuesta(
                    usuario,
                    apuesta,
                    True,
                    mult,
                    mensaje,
                    ""
                )
            elif mult == 0 and mensaje and "Perdiste" in mensaje:
                victoria, mensaje = procesar_apuesta(
                    usuario,
                    apuesta,
                    False,
                    0,
                    "",
                    mensaje
                )

            usuario = obtener_usuario(session["user"])

    opciones = [
        ("ROJO", "🔴 PERIKO ROJO (x2)"),
        ("VERDE", "🟢 PERIKO VERDE (x3)"),
        ("AZUL", "🔵 PERIKO AZUL (x4)"),
        ("DORADO", "🟡 PERIKO DORADO (x8)")
    ]

    return render_template_string(
        HTML_DERBY,
        usuario=usuario,
        opciones=opciones,
        carrera=carrera,
        ganador=ganador,
        positions=positions or ["ROJO", "VERDE", "AZUL", "DORADO"],
        cuotas=cuotas,
        probabilidades=probabilidades,
        mult_exacta=mult_exacta,
        mult_trifecta=mult_trifecta,
        mensaje=mensaje,
        victoria=victoria
    )


# ============================================================
# CRASH ROCKET
# ============================================================

import math as _math

# Historial global de crashes (multiplicadores de las últimas 20 rondas)
CRASH_HISTORY = []
MAX_CRASH_HISTORY = 20


def generar_crash_point():
    """Genera un punto de crash con distribución justa.
    ~4% de probabilidad de crash instantaneo (x1.00).
    El house edge es ~3%.
    Retorna el multiplicador donde crashea."""
    e = 2.718281828459045
    r = random.random()
    if r < 0.04:
        return 1.00
    crash = max(1.00, (1 / (1 - r)) * 0.97)
    return round(crash, 2)


HTML_CRASH = CSS + """

<div class="arcade-box" data-game="CRASH ROCKET">

<h1>📈 CRASH ROCKET 🚀</h1>

<div class="badge">
SALDO: {{ usuario.perikoins }} P
</div>

<p style="font-size:7px;color:#00ffcc">
¡APUESTA Y RETÍRATE ANTES DE QUE CRASHEE!
</p>

{% if mensaje %}
<div class="{% if victoria %}win{% else %}msg{% endif %}">
{{ mensaje }}
</div>
{% endif %}

{% if not resultado %}
<form method="POST" id="crashForm">

<label>CANTIDAD A APOSTAR</label>

<div style="margin:8px auto;max-width:260px;">
<label style="font-size:7px;color:#ff6600;">RETIRARSE EN MULTIP. (ej: 1.50)</label>
<input type="number" name="cashout_target" min="1.01" max="100" step="0.01" placeholder="Auto"
  style="width:100%;padding:6px;background:#0a0a1a;border:2px solid #ff6600;color:#ff6600;font-family:'Press Start 2P',monospace;font-size:7px;text-align:center;">
</div>

<div class="grid">

{% for cantidad in [10,50,100,250,500,1000,5000,10000] %}

<button
class="chip"
name="apuesta"
value="{{ cantidad }}"
type="submit">
{{ cantidad }}
</button>

{% endfor %}

<button
class="allin"
name="apuesta"
value="ALLIN"
type="submit">
ALL IN
</button>

</div>

</form>
{% endif %}

{% if resultado %}

<div class="crash-container">

<div class="crash-graph">
    <div class="crash-multiplier {% if resultado == 'crashed' %}crashed{% elif resultado == 'cashed' %}cashed{% endif %}" id="crashMult">
        x1.00
    </div>
    <div class="crash-line" id="crashLine" style="width:0;height:0;background:linear-gradient(45deg,#ff6600,#ff0033);"></div>
    <div class="crash-rocket" id="crashRocket" style="left:5px;bottom:10px;">🚀</div>
</div>

{% if resultado == 'cashed' %}
<div class="crash-cashout-btn" style="animation:none;background:#00ff6622;border-color:#00ff66;color:#00ff66;">
    ✅ TE RETIRASTE EN x{{ cashout_mult }} — GANASTE {{ ganancia }} P
</div>
{% elif resultado == 'crashed' %}
<div class="crash-cashout-btn" style="animation:none;background:#ff003322;border-color:#ff0033;color:#ff0033;">
    💥 CRASH EN x{{ crash_point }} — PERDISTE {{ apuesta_hecha }} P
</div>
{% endif %}

<div class="crash-history">
{% for h in historial %}
<span class="crash-history-item {{ 'green' if h >= 2 else 'red' }}">x{{ h }}</span>
{% endfor %}
</div>

</div>

<script>
(function() {
    const crashPoint = {{ crash_point }};
    const cashoutMult = {{ cashout_mult | default(0) }};
    const resultado = "{{ resultado }}";
    const multEl = document.getElementById("crashMult");
    const lineEl = document.getElementById("crashLine");
    const rocketEl = document.getElementById("crashRocket");
    const graphW = lineEl.parentElement.offsetWidth;
    const graphH = 180;
    const maxDisplay = Math.max(crashPoint * 1.3, 5);
    const totalFrames = 150;
    const frameDuration = 40;
    let frame = 0;

    function animate() {
        if (frame >= totalFrames) {
            if (resultado === "crashed") {
                multEl.textContent = "x" + crashPoint.toFixed(2);
                multEl.classList.add("crashed");
                rocketEl.classList.add("exploded");
                rocketEl.textContent = "💥";
                lineEl.style.boxShadow = "0 0 15px #ff0033";
            }
            return;
        }
        frame++;
        let progress = frame / totalFrames;
        let currentMult = 1 + (crashPoint - 1) * progress;
        if (resultado === "cashed" && currentMult >= cashoutMult) {
            currentMult = cashoutMult;
            multEl.textContent = "x" + cashoutMult.toFixed(2);
            multEl.classList.add("cashed");
            rocketEl.textContent = "✅";
            const xPos = Math.min((cashoutMult / maxDisplay) * (graphW - 10), graphW - 30);
            const yPos = graphH - Math.min((cashoutMult / maxDisplay) * graphH, graphH - 15);
            rocketEl.style.left = xPos + "px";
            rocketEl.style.bottom = (graphH - yPos) + "px";
            const w = xPos + 5;
            const h = graphH - yPos;
            lineEl.style.width = w + "px";
            lineEl.style.height = h + "px";
            lineEl.style.background = "linear-gradient(45deg,#00ff66,#00cc44)";
            // Continue animation to show crash after cashout
            setTimeout(function() {
                let f2 = frame;
                function showCrash() {
                    if (f2 >= totalFrames) {
                        multEl.textContent = "CRASH x" + crashPoint.toFixed(2);
                        rocketEl.textContent = "💥";
                        return;
                    }
                    f2++;
                    let p2 = f2 / totalFrames;
                    multEl.textContent = "x" + (1 + (crashPoint - 1) * p2).toFixed(2);
                    requestAnimationFrame(showCrash);
                }
                showCrash();
            }, 600);
            return;
        }
        multEl.textContent = "x" + currentMult.toFixed(2);
        const xPos = Math.min((currentMult / maxDisplay) * (graphW - 10), graphW - 30);
        const yPos = graphH - Math.min((currentMult / maxDisplay) * graphH, graphH - 15);
        rocketEl.style.left = xPos + "px";
        rocketEl.style.bottom = (graphH - yPos) + "px";
        const w = xPos + 5;
        const h = graphH - yPos;
        lineEl.style.width = w + "px";
        lineEl.style.height = h + "px";
        setTimeout(animate, frameDuration);
    }

    setTimeout(animate, 400);
})();
</script>

{% else %}

<div class="crash-history">
{% for h in historial %}
<span class="crash-history-item {{ 'green' if h >= 2 else 'red' }}">x{{ h }}</span>
{% endfor %}
</div>

{% endif %}

<a class="link" href="/menu">
< VOLVER AL MENU
</a>

</div>

</body>
</html>
"""


@app.route("/juego/crash", methods=["GET", "POST"])
def crash():
    global CRASH_HISTORY
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    resultado = None
    crash_point = 1.00
    cashout_mult = 0
    ganancia = 0
    apuesta_hecha = 0
    mensaje = ""
    victoria = False

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        if apuesta <= 0:
            mensaje = "Apuesta invalida."

        elif apuesta > usuario["perikoins"]:
            mensaje = "No tienes suficientes Perikoins."

        else:
            crash_point = generar_crash_point()

            # Guardar en historial
            CRASH_HISTORY.insert(0, crash_point)
            if len(CRASH_HISTORY) > MAX_CRASH_HISTORY:
                CRASH_HISTORY.pop()

            # El jugador elige un multiplicador para retirarse
            # Implementamos una estrategia: el jugador selecciona su cashout
            # Usamos un selector en el form — pero para simplificar la UX
            # usamos un cashout aleatorio ponderado (simula el instinto del jugador)
            # Para más control, añadiremos un campo de cashout manual
            cashout_target = None
            cashout_str = request.form.get("cashout_target", "")

            try:
                if cashout_str:
                    cashout_target = round(float(cashout_str), 2)
                    if cashout_target < 1.01:
                        cashout_target = None
            except (ValueError, TypeError):
                cashout_target = None

            if cashout_target is None:
                # Auto-generar un cashout basado en el comportamiento típico
                # 60% retira entre x1.2-x2, 30% entre x2-x5, 10% x5+
                r = random.random()
                if r < 0.6:
                    cashout_target = round(random.uniform(1.20, 2.00), 2)
                elif r < 0.9:
                    cashout_target = round(random.uniform(2.00, 5.00), 2)
                else:
                    cashout_target = round(random.uniform(5.00, 15.00), 2)

            apuesta_hecha = apuesta

            if crash_point >= cashout_target:
                # El jugador se retiró a tiempo — gana!
                resultado = "cashed"
                cashout_mult = cashout_target
                ganancia = int(apuesta * cashout_mult)
                mult_final = cashout_mult

                mensaje = (
                    f"🚀 Te retiraste en x{cashout_mult:.2f}! "
                    f"Ganaste {ganancia} Perikoins! "
                    f"(El rocket crasheó en x{crash_point:.2f})"
                )

                victoria, mensaje = procesar_apuesta(
                    usuario,
                    apuesta,
                    True,
                    int(mult_final * 100) / 100,
                    mensaje,
                    ""
                )
                # Corregir: procesar_apuesta usa multiplicador entero, 
                # pero crash usa decimales. Recalcular manualmente.
                # procesar_apuesta ya hizo saldo += apuesta * mult,
                # pero mult es int. Necesitamos ajustar.
                # Vamos a hacerlo manual para crash:
                db = get_db()
                with db.cursor() as cur:
                    cur.execute(
                        "SELECT perikoins FROM usuarios WHERE username = %s",
                        (usuario["username"],)
                    )
                    row = cur.fetchone()
                    if row:
                        # Deshacer el procesar_apuesta y recalcular con decimal
                        saldo_actual = row[0]
                        # El procesar_apuesta ya sumó apuesta * int(mult)
                        # Necesitamos corregir: saldo correcto = saldo_sin_apuesta + ganancia_real
                        # saldo_sin_apuesta = saldo_actual - (apuesta * int(mult_final))
                        # ganancia_real = apuesta * cashout_mult
                        # pero procesar_apuesta ya restó la apuesta y sumó apuesta*mult
                        # Simplificamos: el saldo actual ya tiene el resultado de procesar_apuesta
                        # que usó mult como int. Calculemos la diferencia.
                        mult_entero_usado = int(mult_final)
                        ganancia_correcta = int(apuesta * cashout_mult)
                        ganancia_entera = apuesta * mult_entero_usado
                        diferencia = ganancia_correcta - ganancia_entera
                        nuevo = saldo_actual + diferencia
                        cur.execute(
                            "UPDATE usuarios SET perikoins = %s, max_perikoins = GREATEST(max_perikoins, %s) WHERE username = %s",
                            (nuevo, nuevo, usuario["username"])
                        )
                db.commit()

            else:
                # Crash antes de cashout — pierde
                resultado = "crashed"
                cashout_mult = 0
                ganancia = 0

                mensaje = (
                    f"💥 El rocket crasheó en x{crash_point:.2f}! "
                    f"Querías retirarte en x{cashout_target:.2f}. "
                    f"Perdiste {apuesta} Perikoins."
                )

                victoria, mensaje = procesar_apuesta(
                    usuario,
                    apuesta,
                    False,
                    0,
                    "",
                    mensaje
                )

            usuario = obtener_usuario(session["user"])

    historial = CRASH_HISTORY[:MAX_CRASH_HISTORY]

    return render_template_string(
        HTML_CRASH,
        usuario=usuario,
        resultado=resultado,
        crash_point=crash_point,
        cashout_mult=cashout_mult,
        ganancia=ganancia,
        apuesta_hecha=apuesta_hecha,
        historial=historial,
        mensaje=mensaje,
        victoria=victoria
    )


HTML_TIENDA = CSS + """

<div class="arcade-box">

<h1>TIENDA DE COFRES</h1>

<div class="badge">
SALDO: {{ usuario.perikoins }} P
<br>
<span style="color:#ffaa00;font-size:7px;">⭐ {{ usuario.prestigio }}</span>
</div>

{% if nuevo %}

<div class="win">
HAS CONSEGUIDO:
<br><br>

<span style="font-size:40px">
{{ nuevo.icon }}
</span>

<br>

{{ nuevo.nombre }}

<br>

<span style="color:{{ nuevo.color }}">
[{{ nuevo.rareza }}]
</span>

</div>

{% endif %}

{% if mensaje %}

<div class="msg">
{{ mensaje }}
</div>

{% endif %}


<!-- ============================= -->
<!-- COFRES -->
<!-- ============================= -->

<div class="chest">

<div class="chest-icon">📦</div>

<strong>COFRE NORMAL</strong>

<p style="font-size:7px;color:#aaa">
Mayormente Comun y Raro
</p>

<form method="POST">

<input
type="hidden"
name="tipo"
value="NORMAL"
>

<button class="btn" type="submit">
COMPRAR (100 P)
</button>

</form>

</div>


<div class="chest" style="border-color:#0088ff">

<div class="chest-icon">⚡</div>

<strong>COFRE ELECTRICO</strong>

<p style="font-size:7px;color:#aaa">
Mas chance de Legendario y Mitico
</p>

<form method="POST">

<input
type="hidden"
name="tipo"
value="ELECTRICO"
>

<button class="btn" type="submit">
COMPRAR (250 P)
</button>

</form>

</div>


<div class="chest" style="border-color:#ff0055">

<div class="chest-icon">🔥</div>

<strong>COFRE FUEGO</strong>

<p style="font-size:7px;color:#aaa">
Alta chance Mitico y Secreto
</p>

<form method="POST">

<input
type="hidden"
name="tipo"
value="FUEGO"
>

<button class="btn" type="submit">
COMPRAR (500 P)
</button>

</form>

</div>


<!-- ============================= -->
<!-- COLORES DE NOMBRE -->
<!-- ============================= -->

<div class="chest" style="border-color:#ffff00">

<h2 style="color:#ffff00;font-size:10px;">
🎨 COLORES DE NOMBRE
</h2>

<p style="font-size:7px;color:#aaa;line-height:1.7;">
Compra colores especiales para tu Gamer Tag.
<br>
Los colores comprados pueden equiparse desde aqui.
</p>


{% for clave,color in colores_tienda.items() %}

<div class="color-card"
style="border-color:{{ color.css }};">

<div
class="color-preview"
style="color:{{ color.css }};"
>

{{ color.nombre }}

</div>


{% if clave in colores_desbloqueados %}

<div
style="
font-size:7px;
color:#00ff00;
margin:8px 0;
"
>
✓ DESBLOQUEADO
</div>

{% if usuario.color_nombre == clave %}

<button
class="btn btn-green"
type="button"
disabled
>
✓ EQUIPADO
</button>

{% else %}

<form method="POST">

<input
type="hidden"
name="accion"
value="equipar_color"
>

<input
type="hidden"
name="color"
value="{{ clave }}"
>

<button
class="btn btn-yellow"
type="submit"
>
EQUIPAR
</button>

</form>

{% endif %}

{% else %}

<div
style="
font-size:7px;
color:#ffff00;
margin:8px 0;
"
>
💰 {{ color.precio }} PERIKOINS
</div>

<form method="POST">

<input
type="hidden"
name="accion"
value="comprar_color"
>

<input
type="hidden"
name="color"
value="{{ clave }}"
>

<button
class="btn"
type="submit"
>
COMPRAR {{ color.precio }} P
</button>

</form>

{% endif %}

</div>

{% endfor %}

</div>


<!-- ============================= -->
<!-- MAQUINA DE COLORES -->
<!-- ============================= -->

<!-- ============================= -->
<!-- MAQUINA DE COLORES -->
<!-- ============================= -->

<div class="machine">
<div class="machine-icon">🎰</div>
<h2 style="color:#ff00ff;font-size:11px;">MÁQUINA DE COLORES</h2>
<p style="font-size:7px;color:#aaa;line-height:1.8;">
GIRA LA MÁQUINA Y CONSIGUE UN COLOR EXCLUSIVO PARA TU PERFIL.<br>
COSTO POR GIRO: <span style="color:#ffff00">10,000 P</span>
</p>

{% if mensaje_maquina %}
<div class="{% if color_ganado %}win{% else %}msg{% endif %}">
{{ mensaje_maquina }}
</div>
{% endif %}

<div class="color-preview" style="{% if color_maquina %}color:{{ color_maquina.css }};{% endif %}">
{% if color_maquina %}{{ color_maquina.nombre }}{% else %}???{% endif %}
</div>

<form method="POST">
<input type="hidden" name="accion" value="girar_maquina">
<button class="btn btn-purple" type="submit">🎰 GIRAR POR 10,000 P</button>
</form>

<p style="font-size:6px;color:#888;line-height:1.7;">
RARO 45% · ÉPICO 30% · LEGENDARIO 15% · MÍTICO 8% · SECRETO 1.9% · ULTRA 0.1%
</p>
</div>

<!-- ============================= -->
<!-- MONEDAS DE PRESTIGIO -->
<!-- ============================= -->

<div class="chest" style="border-color:#ffaa00;background:linear-gradient(145deg,#1a1100,#2a2200);">

<div class="chest-icon">⭐</div>

<strong style="color:#ffaa00;">MONEDA DE PRESTIGIO</strong>

<p style="font-size:7px;color:#aaa;line-height:1.6;">
Moneda exclusiva para jugadores legendarios.<br>
Precio del siguiente prestigio: <span style="color:#ffaa00;">{{ precio_prestigio_txt }}</span>
</p>

<p style="font-size:7px;color:#888;line-height:1.5;">
⭐ Prestigio {{ usuario.prestigio }} → {{ usuario.prestigio + 1 }}<br>
El precio se duplica con cada compra.<br>
Precio máximo: 5.15 quintillones
</p>

<p style="font-size:9px;color:#ffaa00;">
⭐ PRESTIGIO ACTUAL: {{ usuario.prestigio }}
</p>

<form method="POST">
<input type="hidden" name="accion" value="comprar_prestigio">
<button class="btn btn-yellow" type="submit" style="background:#ffaa00;border-bottom-color:#aa7700;color:#000;">
COMPRAR 1 ⭐ ({{ precio_prestigio_txt }})
</button>
</form>

</div>

<a class="link" href="/menu">
< VOLVER
</a>

</div>

</body>
</html>
"""

@app.route("/tienda", methods=["GET", "POST"])
def tienda():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""
    mensaje_maquina = ""
    color_ganado = False
    color_maquina = None
    nuevo = None

    # ==========================================
    # COLORES DISPONIBLES PARA COMPRAR
    # ==========================================

    colores_tienda = {
        clave: datos
        for clave, datos in COLORES_NOMBRE.items()
        if datos.get("tipo") == "TIENDA"
    }

    # ==========================================
    # POST
    # ==========================================

    if request.method == "POST":

        accion = request.form.get("accion")

        # ======================================
        # COMPRAR COLOR
        # ======================================

        if accion == "comprar_color":

            clave = request.form.get("color")

            color = colores_tienda.get(clave)

            if not color:

                mensaje = "Color invalido."

            else:

                db = get_db()

                try:

                    with db.cursor(
                        cursor_factory=RealDictCursor
                    ) as cur:

                        cur.execute(
                            """
                            SELECT *
                            FROM usuarios
                            WHERE username = %s
                            FOR UPDATE
                            """,
                            (usuario["username"],)
                        )

                        actual = cur.fetchone()

                        if not actual:

                            db.rollback()

                            mensaje = (
                                "Usuario no encontrado."
                            )

                        else:

                            colores_desbloqueados = cargar_avatares(
                                actual["colores_desbloqueados"]
                            )

                            # ----------------------------------
                            # YA TIENE EL COLOR
                            # ----------------------------------

                            if clave in colores_desbloqueados:

                                db.rollback()

                                mensaje = (
                                    "Ya tienes este color."
                                )

                            # ----------------------------------
                            # NO TIENE SUFICIENTES PERIKOINS
                            # ----------------------------------

                            elif actual["perikoins"] < color["precio"]:

                                db.rollback()

                                mensaje = (
                                    "No tienes suficientes "
                                    "Perikoins."
                                )

                            # ----------------------------------
                            # COMPRA
                            # ----------------------------------

                            else:

                                colores_desbloqueados.append(
                                    clave
                                )

                                nuevo_saldo = (
                                    actual["perikoins"]
                                    - color["precio"]
                                )

                                cur.execute(
                                    """
                                    UPDATE usuarios
                                    SET
                                        perikoins = %s,
                                        colores_desbloqueados = %s
                                    WHERE username = %s
                                    """,
                                    (
                                        nuevo_saldo,
                                        json.dumps(
                                            colores_desbloqueados
                                        ),
                                        usuario["username"]
                                    )
                                )

                                db.commit()

                                mensaje = (
                                    f"🎨 Compraste el color "
                                    f"{color['nombre']}."
                                )

                        usuario = obtener_usuario(
                            session["user"]
                        )

                except Exception as e:

                    db.rollback()

                    print(
                        "ERROR AL COMPRAR COLOR:",
                        e
                    )

                    mensaje = (
                        "Ocurrio un error al comprar "
                        "el color."
                    )


        # ======================================
        # EQUIPAR COLOR
        # ======================================

        elif accion == "equipar_color":

            clave = request.form.get("color")

            color = colores_tienda.get(clave)

            if not color:

                mensaje = "Color invalido."

            else:

                db = get_db()

                try:

                    with db.cursor(
                        cursor_factory=RealDictCursor
                    ) as cur:

                        cur.execute(
                            """
                            SELECT *
                            FROM usuarios
                            WHERE username = %s
                            FOR UPDATE
                            """,
                            (usuario["username"],)
                        )

                        actual = cur.fetchone()

                        if not actual:

                            db.rollback()

                            mensaje = (
                                "Usuario no encontrado."
                            )

                        else:

                            colores_desbloqueados = cargar_avatares(
                                actual["colores_desbloqueados"]
                            )

                            if clave not in colores_desbloqueados:

                                db.rollback()

                                mensaje = (
                                    "No tienes desbloqueado "
                                    "este color."
                                )

                            else:

                                cur.execute(
                                    """
                                    UPDATE usuarios
                                    SET color_nombre = %s
                                    WHERE username = %s
                                    """,
                                    (
                                        clave,
                                        usuario["username"]
                                    )
                                )

                                db.commit()

                                mensaje = (
                                    f"🎨 Equipaste "
                                    f"{color['nombre']}."
                                )

                except Exception as e:

                    db.rollback()

                    print(
                        "ERROR AL EQUIPAR COLOR:",
                        e
                    )

                    mensaje = (
                        "Ocurrio un error al equipar "
                        "el color."
                    )


        # ======================================
        # GIRAR MAQUINA DE COLORES
        # ======================================

        elif accion == "girar_maquina":
            costo = COSTO_MAQUINA_COLORES
            db = get_db()
            try:
                with db.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT * FROM usuarios
                        WHERE username = %s
                        FOR UPDATE
                        """,
                        (usuario["username"],)
                    )
                    actual = cur.fetchone()

                    if not actual:
                        mensaje_maquina = "Usuario no encontrado."
                        db.rollback()
                    elif actual["perikoins"] < costo:
                        mensaje_maquina = "No tienes suficientes Perikoins para girar."
                        db.rollback()
                    else:
                        exclusivos = {
                            clave: datos
                            for clave, datos in COLORES_NOMBRE.items()
                            if datos.get("tipo") == "MAQUINA"
                        }
                        pesos = {
                            "RARO": 45,
                            "EPICO": 30,
                            "LEGENDARIO": 15,
                            "MITICO": 8,
                            "SECRETO": 1.9,
                            "ULTRA": 0.1
                        }
                        rareza = random.choices(
                            list(pesos.keys()),
                            weights=list(pesos.values()),
                            k=1
                        )[0]
                        posibles = [
                            clave for clave, datos in exclusivos.items()
                            if datos.get("rareza") == rareza
                        ]
                        clave_ganada = random.choice(posibles)
                        color_maquina = exclusivos[clave_ganada]
                        colores_nuevos = cargar_avatares(actual["colores_desbloqueados"])
                        es_nuevo = clave_ganada not in colores_nuevos
                        if es_nuevo:
                            colores_nuevos.append(clave_ganada)

                        cur.execute(
                            """
                            UPDATE usuarios
                            SET perikoins = perikoins - %s,
                                colores_desbloqueados = %s
                            WHERE username = %s
                            """,
                            (
                                costo,
                                json.dumps(colores_nuevos),
                                usuario["username"]
                            )
                        )
                        db.commit()
                        color_ganado = True
                        if es_nuevo:
                            mensaje_maquina = (
                                f"🎉 ¡CONSEGUISTE {color_maquina['nombre'].upper()}! "
                                f"Rareza: {rareza}."
                            )
                        else:
                            mensaje_maquina = (
                                f"🎰 Salió {color_maquina['nombre']}. "
                                "Ya lo tenías desbloqueado."
                            )
            except Exception as e:
                db.rollback()
                print("ERROR EN MAQUINA DE COLORES:", e)
                mensaje_maquina = "Ocurrió un error al girar la máquina."

        # ======================================
        # COMPRAR MONEDA DE PRESTIGIO
        # ======================================

        elif accion == "comprar_prestigio":
            db = get_db()
            try:
                with db.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT * FROM usuarios
                        WHERE username = %s
                        FOR UPDATE
                        """,
                        (usuario["username"],)
                    )
                    actual = cur.fetchone()

                    if not actual:
                        mensaje = "Usuario no encontrado."
                        db.rollback()
                    else:
                        costo = calcular_precio_prestigio(actual["prestigio"])
                        if actual["perikoins"] < costo:
                            precio_txt = formatear_precio_prestigio(costo)
                            mensaje = f"No tienes suficientes Perikoins. Necesitas {precio_txt}."
                            db.rollback()
                        else:
                            precio_txt = formatear_precio_prestigio(costo)
                            cur.execute(
                                """
                                UPDATE usuarios
                                SET perikoins = perikoins - %s,
                                    prestigio = prestigio + 1
                                WHERE username = %s
                                """,
                                (costo, usuario["username"])
                            )
                            db.commit()
                            nuevo_prestigio = actual["prestigio"] + 1
                            proximo_costo = calcular_precio_prestigio(nuevo_prestigio)
                            proximo_txt = formatear_precio_prestigio(proximo_costo)
                            mensaje = f"⭐ ¡Has obtenido 1 Moneda de Prestigio! (Total: {nuevo_prestigio}) Proximo: {proximo_txt}"
            except Exception as e:
                db.rollback()
                print("ERROR EN COMPRAR PRESTIGIO:", e)
                mensaje = "Ocurrió un error al comprar prestigio."

        # ======================================
        # COMPRA DE COFRES
        # ======================================

        else:

            tipo = request.form.get("tipo")

            costos = {
                "NORMAL": 100,
                "ELECTRICO": 250,
                "FUEGO": 500
            }

            costo = costos.get(tipo)

            if not costo:

                mensaje = "Tipo de cofre invalido."

            else:

                db = get_db()

                with db.cursor(
                    cursor_factory=RealDictCursor
                ) as cur:

                    cur.execute(
                        """
                        SELECT *
                        FROM usuarios
                        WHERE username = %s
                        FOR UPDATE
                        """,
                        (usuario["username"],)
                    )

                    actual = cur.fetchone()

                    if not actual:

                        db.rollback()

                        mensaje = (
                            "Usuario no encontrado."
                        )

                    elif actual["perikoins"] < costo:

                        db.rollback()

                        mensaje = (
                            "No tienes suficientes "
                            "Perikoins."
                        )

                    else:

                        if tipo == "NORMAL":

                            weights = {
                                "COMUN": 65,
                                "RARO": 25,
                                "LEGENDARIO": 8,
                                "MITICO": 2,
                                "SECRETO": 0
                            }

                        elif tipo == "ELECTRICO":

                            weights = {
                                "COMUN": 30,
                                "RARO": 40,
                                "LEGENDARIO": 20,
                                "MITICO": 9,
                                "SECRETO": 1
                            }

                        else:

                            weights = {
                                "COMUN": 10,
                                "RARO": 30,
                                "LEGENDARIO": 35,
                                "MITICO": 20,
                                "SECRETO": 5
                            }

                        rareza = random.choices(
                            list(weights.keys()),
                            weights=list(weights.values()),
                            k=1
                        )[0]

                        posibles = [
                            aid
                            for aid, item in AVATARES_DB.items()
                            if item["rareza"] == rareza
                        ]

                        avatar_id = random.choice(
                            posibles
                        )

                        nuevo = AVATARES_DB[
                            avatar_id
                        ]

                        desbloqueados = cargar_avatares(
                            actual[
                                "avatares_desbloqueados"
                            ]
                        )

                        if avatar_id not in desbloqueados:

                            desbloqueados.append(
                                avatar_id
                            )

                        nuevo_saldo = (
                            actual["perikoins"]
                            - costo
                        )

                        cur.execute(
                            """
                            UPDATE usuarios
                            SET
                                perikoins = %s,
                                avatares_desbloqueados = %s
                            WHERE username = %s
                            """,
                            (
                                nuevo_saldo,
                                json.dumps(
                                    desbloqueados
                                ),
                                usuario["username"]
                            )
                        )

                        db.commit()

    # ==========================================
    # RECARGAR USUARIO
    # ==========================================

    usuario = obtener_usuario(
        session["user"]
    )

    colores_desbloqueados = cargar_avatares(
        usuario["colores_desbloqueados"]
    )

    precio_prestigio_txt = formatear_precio_prestigio(
        calcular_precio_prestigio(usuario["prestigio"])
    )

    return render_template_string(
        HTML_TIENDA,
        usuario=usuario,
        nuevo=nuevo,
        mensaje=mensaje,
        colores_tienda=colores_tienda,
        colores_desbloqueados=colores_desbloqueados,
        mensaje_maquina=mensaje_maquina,
        color_ganado=color_ganado,
        color_maquina=color_maquina,
        precio_prestigio_txt=precio_prestigio_txt
    )

HTML_PERFIL = CSS + """

<div class="arcade-box">

<h1>MI PERFIL</h1>

<div class="badge">
{{ avatar.icon }}
<br>
{{ avatar.nombre }}
</div>

<div class="name-color" style="{{ color_estilo }}">
{{ usuario.username }}
</div>

<div class="badge" style="background:#111;border:1px solid #ffaa00;">
<span style="color:#ffaa00;font-size:10px;">{{ titulo }}</span>
</div>

<!-- STATS PRINCIPALES -->
<div class="chest" style="border-color:#00ffcc;background:#0a0a0a;">
    <h2 style="color:#00ffcc;font-size:10px;">📊 ESTADÍSTICAS</h2>
    <table style="width:100%;font-size:8px;border-collapse:collapse;">
    <tr><td style="color:#0f0;padding:3px 8px;">🏆 Victorias</td><td style="color:#0f0;font-weight:bold;">{{ usuario.victorias }}</td></tr>
    <tr><td style="color:#f44;padding:3px 8px;">💀 Derrotas</td><td style="color:#f44;font-weight:bold;">{{ usuario.derrotas }}</td></tr>
    <tr><td style="color:#ff0;padding:3px 8px;">📈 Win Rate</td><td style="color:#ff0;font-weight:bold;">{{ winrate }}%</td></tr>
    <tr><td style="color:#0ff;padding:3px 8px;">🅑 Nivel</td><td style="color:#0ff;font-weight:bold;">{{ usuario.nivel }} <span style="color:#aaa;font-size:7px;">(EXP {{ usuario.exp }}/{{ exp_siguiente }})</span></td></tr>
    <tr><td style="color:#ffaa00;padding:3px 8px;">⭐ Prestigio</td><td style="color:#ffaa00;font-weight:bold;">{{ usuario.prestigio }}</td></tr>
    <tr><td style="color:#0f0;padding:3px 8px;">💰 Perikoins</td><td style="color:#0f0;font-weight:bold;">{{ usuario.perikoins }}</td></tr>
    <tr><td style="color:#f0f;padding:3px 8px;">💎 Max Perikoins</td><td style="color:#f0f;font-weight:bold;">{{ usuario.max_perikoins }}</td></tr>
    <tr><td style="color:#aaa;padding:3px 8px;">📅 Miembro desde</td><td style="color:#ccc;font-weight:bold;">{{ fecha_registro }}</td></tr>
    </table>
</div>

<p style="font-size:8px">
AVATARES: {{ desbloqueados|length }}/50
</p>

<div class="avatar-grid">
{% for aid,item in avatares.items() %}
{% set tiene = aid in desbloqueados %}
<form method="POST">
<input type="hidden" name="accion" value="avatar">
<input type="hidden" name="avatar_id" value="{{ aid }}">
<button class="avatar-item {% if aid == usuario.avatar_activo %}active{% endif %} {% if not tiene %}locked{% endif %}" type="submit" {% if not tiene %}disabled{% endif %}>
<div style="font-size:20px">{% if tiene %}{{ item.icon }}{% else %}🔒{% endif %}</div>
<div style="color:{{ item.color }}">{{ item.rareza }}</div>
</button>
</form>
{% endfor %}
</div>

<!-- MAQUINA DE COLORES MOVIDA A TIENDA -->

<div class="chest" style="border-color:#00ffcc;">
<h2 style="color:#00ffcc;font-size:10px;">🎨 MIS COLORES</h2>
<p style="font-size:7px;color:#aaa;">{{ colores_desbloqueados|length }} colores desbloqueados</p>

{% for clave,color in colores.items() %}
{% if clave in colores_desbloqueados %}
<div class="color-card" style="border-color:{{ color.css }};">
<div class="color-preview" style="color:{{ color.css }};">{{ color.nombre }}</div>
<div style="font-size:7px;color:#aaa;">{{ color.rareza if color.tipo == 'MAQUINA' else 'TIENDA' }}</div>
{% if usuario.color_nombre == clave %}
<button class="btn btn-green" type="button" disabled>✓ EQUIPADO</button>
{% else %}
<form method="POST">
<input type="hidden" name="accion" value="equipar_color">
<input type="hidden" name="color" value="{{ clave }}">
<button class="btn btn-yellow" type="submit">EQUIPAR</button>
</form>
{% endif %}
</div>
{% endif %}
{% endfor %}
</div>

<a class="link" href="/tienda">🎨 CONSEGUIR MÁS COLORES EN LA TIENDA</a>
<a class="link" href="/menu">< VOLVER</a>

</div>

</body>
</html>
"""


@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    desbloqueados = cargar_avatares(usuario["avatares_desbloqueados"])
    colores_desbloqueados = cargar_avatares(usuario["colores_desbloqueados"])
    mensaje_color = ""
    color_ganado = False

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "avatar":
            try:
                avatar_id = int(request.form.get("avatar_id", 1))
            except (TypeError, ValueError):
                avatar_id = 1

            if avatar_id in AVATARES_DB and avatar_id in desbloqueados:
                db = get_db()
                with db.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE usuarios
                        SET avatar_activo = %s
                        WHERE username = %s
                        """,
                        (avatar_id, usuario["username"])
                    )
                db.commit()

        elif accion == "equipar_color":
            clave = request.form.get("color")
            if clave in COLORES_NOMBRE and clave in colores_desbloqueados:
                db = get_db()
                with db.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE usuarios
                        SET color_nombre = %s
                        WHERE username = %s
                        """,
                        (clave, usuario["username"])
                    )
                db.commit()
                mensaje_color = f"🎨 Equipaste {COLORES_NOMBRE[clave]['nombre']}."
                color_ganado = True
            else:
                mensaje_color = "No tienes desbloqueado este color."

        usuario = obtener_usuario(session["user"])
        colores_desbloqueados = cargar_avatares(usuario["colores_desbloqueados"])

    avatar = AVATARES_DB.get(usuario["avatar_activo"], AVATARES_DB[1])
    color_estilo = obtener_estilo_color(usuario["color_nombre"])

    exp_siguiente = exp_necesaria(usuario["nivel"]) if usuario["nivel"] < NIVEL_MAXIMO else 0

    # Calcular stats avanzadas
    titulo = titulo_por_nivel(usuario["nivel"], titulo_custom=usuario.get("titulo_custom"))
    vic = usuario.get("victorias", 0) or 0
    der = usuario.get("derrotas", 0) or 0
    winrate = round(vic / (vic + der) * 100, 1) if (vic + der) > 0 else 0.0
    creado = usuario.get("creado_en")
    fecha_registro = creado.strftime("%d/%m/%Y") if creado else "Desconocida"

    return render_template_string(
        HTML_PERFIL,
        usuario=usuario,
        avatares=AVATARES_DB,
        desbloqueados=desbloqueados,
        avatar=avatar,
        colores=COLORES_NOMBRE,
        colores_desbloqueados=colores_desbloqueados,
        color_estilo=color_estilo,
        mensaje_color=mensaje_color,
        color_ganado=color_ganado,
        exp_siguiente=exp_siguiente,
        titulo=titulo,
        winrate=winrate,
        fecha_registro=fecha_registro
    )


@app.route("/perfil/<username>")
def perfil_publico(username):
    yo = usuario_actual()
    if not yo:
        return redirect(url_for("login"))

    db = get_db()
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM usuarios WHERE username = %s",
            (username,)
        )
        objetivo = cur.fetchone()

    if not objetivo:
        return render_template_string(CSS + '<div class="arcade-box"><h1>404</h1><p>Usuario no encontrado.</p><a class="link" href="/ranking">< VOLVER</a></div></body></html>'), 404

    avatar_pub = AVATARES_DB.get(objetivo["avatar_activo"], AVATARES_DB[1])
    color_estilo_pub = obtener_estilo_color(objetivo["color_nombre"])
    titulo = titulo_por_nivel(objetivo["nivel"], titulo_custom=objetivo.get("titulo_custom"))
    vic = objetivo.get("victorias", 0) or 0
    der = objetivo.get("derrotas", 0) or 0
    winrate = round(vic / (vic + der) * 100, 1) if (vic + der) > 0 else 0.0
    creado = objetivo.get("creado_en")
    fecha_registro = creado.strftime("%d/%m/%Y") if creado else "Desconocida"

    return render_template_string(
        HTML_PERFIL_PUBLICO,
        objetivo=objetivo,
        avatar_pub=avatar_pub,
        color_estilo_pub=color_estilo_pub,
        titulo=titulo,
        winrate=winrate,
        fecha_registro=fecha_registro
    )


HTML_RANKING = CSS + """

<div class="arcade-box">

<h1>TOP 50 JUGADORES</h1>

<div style="max-height:350px;overflow:auto">

<table>

<tr>
<th>POS</th>
<th>JUGADOR</th>
<th>🅑</th>
<th>⭐</th>
<th>PERIKOINS</th>
</tr>

{% for pos,j in jugadores %}

<tr>

<td>{{ pos }}</td>

<td>
    {{ j.avatar.icon }}

    <a href="/perfil/{{ j.username }}" style="text-decoration:none;{{ j.color_estilo }}">
        {{ j.username }}
    </a>
</td>

<td style="color:#00ffcc;">
{{ j.nivel }}
</td>

<td style="color:#ffaa00;">
{{ j.prestigio }}
</td>

<td>
{{ j.perikoins }}
</td>

</tr>

{% endfor %}

</table>

</div>

<a class="link" href="/menu">
< VOLVER
</a>

</div>

</body>
</html>
"""


HTML_PERFIL_PUBLICO = CSS + """

<div class="arcade-box">

<h1>PERFIL DE {{ objetivo.username }}</h1>

<div class="badge">
{{ avatar_pub.icon }}
<br>
{{ avatar_pub.nombre }}
</div>

<div class="name-color" style="{{ color_estilo_pub }}">
{{ objetivo.username }}
</div>

<div class="badge" style="background:#111;border:1px solid #ffaa00;">
<span style="color:#ffaa00;font-size:10px;">{{ titulo }}</span>
</div>

<!-- STATS PUBLICOS -->
<div class="chest" style="border-color:#00ffcc;background:#0a0a0a;">
    <h2 style="color:#00ffcc;font-size:10px;">📊 ESTADÍSTICAS</h2>
    <table style="width:100%;font-size:8px;border-collapse:collapse;">
    <tr><td style="color:#0f0;padding:3px 8px;">🏆 Victorias</td><td style="color:#0f0;font-weight:bold;">{{ objetivo.victorias }}</td></tr>
    <tr><td style="color:#f44;padding:3px 8px;">💀 Derrotas</td><td style="color:#f44;font-weight:bold;">{{ objetivo.derrotas }}</td></tr>
    <tr><td style="color:#ff0;padding:3px 8px;">📈 Win Rate</td><td style="color:#ff0;font-weight:bold;">{{ winrate }}%</td></tr>
    <tr><td style="color:#0ff;padding:3px 8px;">🅑 Nivel</td><td style="color:#0ff;font-weight:bold;">{{ objetivo.nivel }}</td></tr>
    <tr><td style="color:#ffaa00;padding:3px 8px;">⭐ Prestigio</td><td style="color:#ffaa00;font-weight:bold;">{{ objetivo.prestigio }}</td></tr>
    <tr><td style="color:#0f0;padding:3px 8px;">💰 Perikoins</td><td style="color:#0f0;font-weight:bold;">{{ objetivo.perikoins }}</td></tr>
    <tr><td style="color:#f0f;padding:3px 8px;">💎 Max Perikoins</td><td style="color:#f0f;font-weight:bold;">{{ objetivo.max_perikoins }}</td></tr>
    <tr><td style="color:#aaa;padding:3px 8px;">📅 Miembro desde</td><td style="color:#ccc;font-weight:bold;">{{ fecha_registro }}</td></tr>
    </table>
</div>

<a class="link" href="/ranking">< VOLVER AL RANKING</a>
<a class="link" href="/menu">< VOLVER AL MENÚ</a>

</div>

</body>
</html>
"""


@app.route("/ranking")
def ranking():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    db = get_db()

    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT
                username,
                perikoins,
                avatar_activo,
                color_nombre,
                prestigio,
                nivel
            FROM usuarios
            ORDER BY perikoins DESC
            LIMIT 50
            """
        )

        jugadores_db = cur.fetchall()

    jugadores = []

    for j in jugadores_db:
        avatar = AVATARES_DB.get(
            j["avatar_activo"],
            AVATARES_DB[1]
        )

        jugadores.append({
            "username": j["username"],
            "perikoins": j["perikoins"],
            "prestigio": j["prestigio"],
            "nivel": j["nivel"],
            "avatar": avatar,
            "color_estilo": obtener_estilo_color(
                j["color_nombre"]
            )
        })
        
    return render_template_string(
        HTML_RANKING,
        jugadores=enumerate(
            jugadores,
            start=1
        )
    )


@app.route("/rescate")
def rescate():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    if usuario["perikoins"] != 0:
        return redirect(url_for("menu"))

    ahora = datetime.utcnow()
    puede = True

    if usuario["ultimo_rescate"]:
        ultimo = usuario["ultimo_rescate"]

        if (
            ahora - ultimo.replace(tzinfo=None)
            < timedelta(days=1)
        ):
            puede = False

    if puede:
        db = get_db()

        with db.cursor() as cur:
            cur.execute(
                """
                UPDATE usuarios
                SET
                    perikoins = 500,
                    ultimo_rescate = NOW()
                WHERE
                    username = %s
                    AND perikoins = 0
                """,
                (usuario["username"],)
            )

        db.commit()

    return redirect(url_for("menu"))


HTML_ADMIN = CSS + """
<div class="arcade-box">

<h1 style="color:#ff0055">PANEL ADMIN PERIKO</h1>

<div class="badge">👑 ADMINISTRADOR SUPREMO</div>

{% if mensaje %}
<div class="msg">{{ mensaje }}</div>
{% endif %}


<div class="chest" style="border-color:#ffff00;">
    <h2 style="color:#ffff00;font-size:10px;">⚠️ MODO MANTENIMIENTO</h2>
    <p style="font-size:7px;color:#aaa;line-height:1.7;">
        Estado actual: 
        <strong style="color: {% if mantenimiento %}#ff0000{% else %}#00ff00{% endif %};">
            {% if mantenimiento %}ACTIVADO{% else %}DESACTIVADO{% endif %}
        </strong>
        <br>Si está activo, solo la cuenta "periko" podrá entrar.
    </p>
    <form method="POST" action="/admin">
        <input type="hidden" name="accion_admin" value="mantenimiento">
        <button class="btn {% if mantenimiento %}btn-green{% else %}btn-red{% endif %}" type="submit">
            {% if mantenimiento %}DESACTIVAR MANTENIMIENTO{% else %}ACTIVAR MANTENIMIENTO{% endif %}
        </button>
    </form>
</div>


<div class="chest" style="border-color:#ff0055;">
    <h2 style="color:#ff0055;font-size:10px;">💀 ADMIN ABUSE</h2>
    <p style="font-size:7px;color:#aaa;line-height:1.7;">
        Modos especiales y secretos del arcade.<br>
        Carnaval, efectos visuales y más...
    </p>
    <a class="btn btn-red" href="/admin/abuse">
        💀 ENTRAR AL ADMIN ABUSE
    </a>
</div>


<div class="chest" style="border-color:#ffaa00;">
    <h2 style="color:#ffaa00;font-size:10px;">📋 REGISTRO DE MOVIMIENTOS</h2>
    <p style="font-size:7px;color:#aaa;line-height:1.7;">
        Estado actual:
        <strong style="color: {% if registro_activo %}#ffaa00{% else %}#00ff00{% endif %};">
            {% if registro_activo %}ACTIVADO 📋{% else %}DESACTIVADO{% endif %}
        </strong>
        <br>Graba todas las ganancias y pérdidas de Perikoins durante 10 min. Luego se borra solo.
    </p>
    <form method="POST" action="/admin">
        <input type="hidden" name="accion_admin" value="registro">
        <button class="btn {% if registro_activo %}btn-green{% else %}btn-red{% endif %}" type="submit">
            {% if registro_activo %}DESACTIVAR REGISTRO{% else %}ACTIVAR REGISTRO{% endif %}
        </button>
    </form>

    {% if registro_activo and registro_movimientos %}
    <div style="margin-top:10px;max-height:300px;overflow-y:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:7px;">
            <tr style="color:#ffaa00;">
                <th style="padding:3px;border:1px solid #333;text-align:left;">HACE</th>
                <th style="padding:3px;border:1px solid #333;text-align:left;">JUGADOR</th>
                <th style="padding:3px;border:1px solid #333;text-align:left;">TIPO</th>
                <th style="padding:3px;border:1px solid #333;text-align:right;">CANTIDAD</th>
            </tr>
            {% for m in registro_movimientos %}
            <tr style="color:{% if m.tipo == 'Ganó' %}#00ff00{% else %}#ff4444{% endif %};">
                <td style="padding:2px;border:1px solid #222;">{{ m.hace }}</td>
                <td style="padding:2px;border:1px solid #222;">{{ m.usuario }}</td>
                <td style="padding:2px;border:1px solid #222;">{{ m.tipo }}</td>
                <td style="padding:2px;border:1px solid #222;text-align:right;">{{ m.cantidad }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% elif registro_activo %}
    <p style="font-size:7px;color:#666;margin-top:8px;">Sin movimientos aún…</p>
    {% endif %}
</div>


<div class="chest">

<h2 style="color:#00ffcc;font-size:10px;">
🎁 REGALAR PERIKOINS
</h2>

<p style="font-size:7px;color:#aaa;line-height:1.7;">
Envía Perikoins directamente a cualquier jugador.
</p>

<form method="POST" action="/admin">

<input type="hidden" name="accion_admin" value="regalar">

<label>GAMER TAG DEL DESTINATARIO</label>

<input
name="destino"
maxlength="30"
required
>

<label>CANTIDAD DE PERIKOINS</label>

<input
type="number"
name="cantidad"
min="1"
required
>

<button
class="btn btn-green"
type="submit"
>
🎁 REGALAR PERIKOINS
</button>

</form>

</div>


<div class="chest" style="border-color:#00ffff;">

<h2 style="color:#00ffff;font-size:10px;">
📢 MENSAJE GLOBAL
</h2>

<p style="font-size:7px;color:#aaa;line-height:1.7;">
Escribe un anuncio y aparecerá automáticamente a TODOS los jugadores.
Solo habrá un mensaje global activo a la vez.
</p>

<form method="POST" action="/admin">
    <input type="hidden" name="accion_admin" value="mensaje_global">

    <label>MENSAJE PARA TODOS</label>

    <textarea
        name="mensaje_global"
        maxlength="500"
        rows="5"
        required
        style="width:100%;padding:12px;margin:8px 0 15px;background:#000;border:2px solid #00ffff;color:#fff;border-radius:5px;font-family:'Press Start 2P',cursive;font-size:8px;resize:vertical;"
        placeholder="📢 ¡NUEVO EVENTO! ..."
    ></textarea>

    <button class="btn btn-green" type="submit">
        📢 PUBLICAR PARA TODOS
    </button>
</form>

<form method="POST" action="/admin" style="margin-top:8px;">
    <input type="hidden" name="accion_admin" value="borrar_mensaje_global">
    <button class="btn btn-red" type="submit">
        🗑️ QUITAR MENSAJE GLOBAL
    </button>
</form>

{% if global_mensaje %}
<div class="msg" style="border:2px solid #00ffff;padding:10px;">
    ACTUAL:<br><br>{{ global_mensaje }}
</div>
{% endif %}

</div>


<div class="chest" style="border-color:#ff0000;">

<h2 style="color:#ff0000;font-size:10px;">
🗑️ ELIMINAR CUENTA
</h2>

<p style="font-size:7px;color:#aaa;line-height:1.7;">
ESTA ACCION ES PERMANENTE.<br>
LA CUENTA Y SUS DATOS SERAN ELIMINADOS.
</p>

<form
method="POST"
action="/admin/eliminar"
onsubmit="return confirm(
    '⚠️ ¿ESTAS SEGURO DE ELIMINAR ESTA CUENTA?\\n\\nEsta accion NO se puede deshacer.'
);"
>

<label>GAMER TAG A ELIMINAR</label>

<input
name="destino"
maxlength="30"
required
>

<button
class="btn btn-red"
type="submit"
>
🗑️ ELIMINAR CUENTA
</button>

</form>

</div>


<div class="chest" style="border-color:#ffff00;">

<h2 style="color:#ffff00;font-size:10px;">
⚡ FUNCIONES ADMIN
</h2>

<p style="font-size:7px;color:#aaa;line-height:1.8;">
🎁 REGALAR PERIKOINS<br>
🗑️ ELIMINAR CUENTAS<br>
👑 CONTROL TOTAL DEL ARCADE
</p>

</div>


<a class="link" href="/menu">
< VOLVER AL MENU
</a>

</div>

</body>
</html>
"""

HTML_ADMIN_ABUSE = CSS + """
<div class="arcade-box">

<h1 style="color:#ff0055">💀 ADMIN ABUSE</h1>

<div class="badge" style="background:#ff0055;color:#fff;">☠️ ZONA DE PODER ABSOLUTO</div>

{% if mensaje %}
<div class="msg">{{ mensaje }}</div>
{% endif %}


<div class="chest" style="border-color:#ff00ff;">
    <h2 style="color:#ff00ff;font-size:10px;">🎭 MODO CARNAVAL</h2>
    <p style="font-size:7px;color:#aaa;line-height:1.7;">
        Estado actual: 
        <strong style="color: {% if carnaval %}#ff00ff{% else %}#00ff00{% endif %};">
            {% if carnaval %}ACTIVADO 🎉{% else %}DESACTIVADO{% endif %}
        </strong>
        <br>Si está activo: colores invertidos + ganancias x2 en todos los juegos.
    </p>
    <form method="POST" action="/admin/abuse">
        <input type="hidden" name="accion_abuse" value="carnaval">
        <button class="btn {% if carnaval %}btn-green{% else %}btn-red{% endif %}" type="submit">
            {% if carnaval %}DESACTIVAR CARNAVAL{% else %}ACTIVAR CARNAVAL{% endif %}
        </button>
    </form>
</div>


<div class="chest" style="border-color:#880000;background:#1a0000;">
    <h2 style="color:#cc0000;font-size:10px;">🌑 MODO OSCURO</h2>
    <p style="font-size:7px;color:#aaa;line-height:1.7;">
        Estado actual: 
        <strong style="color: {% if oscuro %}#cc0000{% else %}#00ff00{% endif %};">
            {% if oscuro %}ACTIVADO 🌑{% else %}DESACTIVADO{% endif %}
        </strong>
        <br>Si está activo: esquema oscuro siniestro + ganancias x3 · EXP x3 en todos los juegos.
    </p>
    <form method="POST" action="/admin/abuse">
        <input type="hidden" name="accion_abuse" value="oscuro">
        <button class="btn {% if oscuro %}btn-green{% else %}btn-red{% endif %}" type="submit">
            {% if oscuro %}DESACTIVAR OSCURO{% else %}ACTIVAR OSCURO{% endif %}
        </button>
    </form>
</div>

<div class="chest" style="border-color:#00cccc;background:#001a1a;">
    <h2 style="color:#00ffff;font-size:10px;">✨ MODO DIVINO</h2>
    <p style="font-size:7px;color:#aaa;line-height:1.7;">
        Estado actual: 
        <strong style="color: {% if divino %}#00ffff{% else %}#00ff00{% endif %};">
            {% if divino %}ACTIVADO ✨{% else %}DESACTIVADO{% endif %}
        </strong>
        <br>Si está activo: esquema cyan + dorado + ganancias x4 · EXP x4 en todos los juegos.
    </p>
    <form method="POST" action="/admin/abuse">
        <input type="hidden" name="accion_abuse" value="divino">
        <button class="btn {% if divino %}btn-green{% else %}btn-red{% endif %}" type="submit">
            {% if divino %}DESACTIVAR DIVINO{% else %}ACTIVAR DIVINO{% endif %}
        </button>
    </form>
</div>

<a class="link" href="/admin">
< VOLVER AL PANEL ADMIN
</a>

</div>

</body>
</html>
"""


@app.route("/admin", methods=["GET", "POST"])
def admin():
    global MODO_MANTENIMIENTO, MODO_CARNAVAL, REGISTRO_ACTIVO, REGISTRO_MOVIMIENTOS
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    if usuario["username"].lower() != "periko":
        return redirect(url_for("menu"))

    mensaje = ""

    if request.method == "POST":
        accion_admin = request.form.get("accion_admin")

        if accion_admin == "mantenimiento":
            MODO_MANTENIMIENTO = not MODO_MANTENIMIENTO
            mensaje = (
                "Modo mantenimiento ACTIVADO."
                if MODO_MANTENIMIENTO
                else "Modo mantenimiento DESACTIVADO."
            )
        elif accion_admin == "registro":
            REGISTRO_ACTIVO = not REGISTRO_ACTIVO
            if REGISTRO_ACTIVO:
                REGISTRO_MOVIMIENTOS = []  # limpiar al activar
                mensaje = "📋 Registro de movimientos ACTIVADO — grabando por 10 min."
            else:
                REGISTRO_MOVIMIENTOS = []
                mensaje = "📋 Registro de movimientos DESACTIVADO y limpiado."

        if accion_admin == "mensaje_global":
            texto_global = request.form.get(
                "mensaje_global",
                ""
            ).strip()

            if not texto_global:
                mensaje = "El mensaje global no puede estar vacío."
            elif len(texto_global) > 500:
                mensaje = "El mensaje global es demasiado largo."
            else:
                db = get_db()
                try:
                    with db.cursor() as cur:
                        cur.execute("""
                            UPDATE mensajes_globales
                            SET activo = FALSE
                            WHERE activo = TRUE
                        """)
                        cur.execute("""
                            INSERT INTO mensajes_globales
                            (mensaje, activo)
                            VALUES (%s, TRUE)
                        """, (texto_global,))
                    db.commit()
                    mensaje = "📢 Mensaje global publicado para TODOS los jugadores."
                except Exception as e:
                    db.rollback()
                    print("ERROR AL PUBLICAR MENSAJE GLOBAL:", e)
                    mensaje = "No se pudo publicar el mensaje global."

        elif accion_admin == "borrar_mensaje_global":
            db = get_db()
            try:
                with db.cursor() as cur:
                    cur.execute("""
                        UPDATE mensajes_globales
                        SET activo = FALSE
                        WHERE activo = TRUE
                    """)
                db.commit()
                mensaje = "🗑️ Mensaje global eliminado."
            except Exception as e:
                db.rollback()
                print("ERROR AL BORRAR MENSAJE GLOBAL:", e)
                mensaje = "No se pudo eliminar el mensaje global."

        else:
            destino = request.form.get(
                "destino",
                ""
            ).strip()

            try:
                cantidad = int(
                    request.form.get(
                        "cantidad",
                        0
                    )
                )
            except ValueError:
                cantidad = 0

            if cantidad <= 0:
                mensaje = "Cantidad invalida."

            elif not destino:
                mensaje = "Destino invalido."

            else:
                db = get_db()

                with db.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE usuarios
                        SET
                            perikoins = perikoins + %s,
                            notif_regalo = notif_regalo + %s
                        WHERE username = %s
                        """,
                        (
                            cantidad,
                            cantidad,
                            destino
                        )
                    )

                    if cur.rowcount == 0:
                        db.rollback()

                        mensaje = (
                            f"El usuario {destino} no existe."
                        )
                    else:
                        db.commit()

                        mensaje = (
                            f"Regalaste {cantidad} "
                            f"Perikoins a {destino}."
                        )

    # Limpiar registros mayores a 10 min
    if REGISTRO_ACTIVO:
        import time as _time
        ahora = _time.time()
        REGISTRO_MOVIMIENTOS = [
            m for m in REGISTRO_MOVIMIENTOS
            if ahora - m["timestamp"] < REGISTRO_DURACION
        ]
        # Calcular tiempo relativo para la plantilla
        for m in REGISTRO_MOVIMIENTOS:
            segs = int(ahora - m["timestamp"])
            if segs < 60:
                m["hace"] = f"{segs}s"
            else:
                m["hace"] = f"{segs // 60}m {segs % 60}s"

    movimientos_para_mostrar = REGISTRO_MOVIMIENTOS if REGISTRO_ACTIVO else []

    return render_template_string(
        HTML_ADMIN,
        mensaje=mensaje,
        mantenimiento=MODO_MANTENIMIENTO,
        carnaval=MODO_CARNAVAL,
        registro_activo=REGISTRO_ACTIVO,
        registro_movimientos=movimientos_para_mostrar
    )

@app.route("/admin/abuse", methods=["GET", "POST"])
def admin_abuse():
    global MODO_CARNAVAL, MODO_OSCURO, MODO_DIVINO
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    if usuario["username"].lower() != "periko":
        return redirect(url_for("menu"))

    mensaje = ""

    if request.method == "POST":
        accion_abuse = request.form.get("accion_abuse")

        if accion_abuse == "carnaval":
            MODO_CARNAVAL = not MODO_CARNAVAL
            mensaje = (
                "🎭 Modo carnaval ACTIVADO — ganancias x2 · EXP x2!"
                if MODO_CARNAVAL
                else "Modo carnaval DESACTIVADO."
            )
        elif accion_abuse == "oscuro":
            MODO_OSCURO = not MODO_OSCURO
            mensaje = (
                "🌑 Modo oscuro ACTIVADO — ganancias x3 · EXP x3!"
                if MODO_OSCURO
                else "Modo oscuro DESACTIVADO."
            )
        elif accion_abuse == "divino":
            MODO_DIVINO = not MODO_DIVINO
            mensaje = (
                "✨ Modo divino ACTIVADO — ganancias x4 · EXP x4!"
                if MODO_DIVINO
                else "Modo divino DESACTIVADO."
            )

    return render_template_string(
        HTML_ADMIN_ABUSE,
        mensaje=mensaje,
        carnaval=MODO_CARNAVAL,
        oscuro=MODO_OSCURO,
        divino=MODO_DIVINO
    )

@app.route("/admin/eliminar", methods=["POST"])
def admin_eliminar():

    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    if usuario["username"].lower() != "periko":
        return redirect(url_for("menu"))

    destino = request.form.get(
        "destino",
        ""
    ).strip()

    if not destino:
        return render_template_string(
            HTML_ADMIN,
            mensaje="Debes indicar un usuario.",
            mantenimiento=MODO_MANTENIMIENTO,
            carnaval=MODO_CARNAVAL,
            registro_activo=REGISTRO_ACTIVO,
            registro_movimientos=[]
        )

    if destino.lower() == "periko":
        return render_template_string(
            HTML_ADMIN,
            mensaje="No puedes eliminar la cuenta PERIKO.",
            mantenimiento=MODO_MANTENIMIENTO,
            carnaval=MODO_CARNAVAL,
            registro_activo=REGISTRO_ACTIVO,
            registro_movimientos=[]
        )

    db = get_db()

    try:

        with db.cursor() as cur:

            cur.execute(
                """
                DELETE FROM usuarios
                WHERE username = %s
                """,
                (destino,)
            )

            if cur.rowcount == 0:
                db.rollback()

                mensaje = (
                    f"El usuario {destino} no existe."
                )

            else:
                db.commit()

                mensaje = (
                    f"La cuenta {destino} "
                    "fue eliminada correctamente."
                )

    except Exception as e:

        db.rollback()

        print("ERROR AL ELIMINAR CUENTA:", e)

        mensaje = (
            "Ocurrio un error al eliminar "
            "la cuenta."
        )

    return render_template_string(
        HTML_ADMIN,
        mensaje=mensaje,
        mantenimiento=MODO_MANTENIMIENTO,
        carnaval=MODO_CARNAVAL,
        registro_activo=REGISTRO_ACTIVO,
        registro_movimientos=[]
    )

# ==================== NOVEDADES ====================

HTML_NOVEDADES = CSS + """

<div class="arcade-box" style="max-width:640px;">

<h1>📰 NOVEDADES</h1>

<p style="font-size:7px;color:#aaa;margin-bottom:12px;">
Las últimas noticias y actualizaciones del arcade.
</p>

{% if es_admin %}
<a class="btn" style="background:linear-gradient(135deg,#ff6600,#ffaa00);color:#000;border-bottom:5px solid #cc5500;" href="/novedades/crear">
✏️ CREAR NOVEDAD
</a>
{% endif %}

{% if posts %}
{% for post in posts %}
<div class="chest" style="border-color:#ff7700;margin:12px 0;">
    <h3 style="color:#ffaa00;font-size:9px;margin-bottom:6px;">{{ post.titulo }}</h3>
    <p style="font-size:7px;color:#00ffcc;line-height:1.8;white-space:pre-wrap;">{{ post.contenido }}</p>
    <p style="font-size:6px;color:#888;margin-top:8px;">
        👤 {{ post.autor }} · {{ post.fecha }}
    </p>
    {% if es_admin %}
    <form method="POST" action="/novedades/borrar/{{ post.id }}" style="margin-top:8px;">
        <button class="btn btn-red" type="submit" style="font-size:7px;padding:6px;">
        🗑️ BORRAR
        </button>
    </form>
    {% endif %}
</div>
{% endfor %}
{% else %}
<div class="msg">
No hay novedades todavía.
</div>
{% endif %}

<a class="link" href="/menu">
< VOLVER AL MENU
</a>

</div>

</body>
</html>
"""


HTML_NOVEDADES_CREAR = CSS + """

<div class="arcade-box" style="max-width:640px;">

<h1>✏️ CREAR NOVEDAD</h1>

{% if mensaje %}
<div class="msg">{{ mensaje }}</div>
{% endif %}

<form method="POST" action="/novedades/crear">

<label>Título</label>
<input type="text" name="titulo" maxlength="200" required
    placeholder="Ej: Nuevo juego disponible!"
    value="{{ titulo_prev|default('',true) }}">

<label>Contenido</label>
<textarea name="contenido" rows="6" required
    style="width:100%;padding:12px;margin:8px 0 15px;background:#000;border:2px solid #00ffcc;color:#fff;border-radius:5px;font-family:'Press Start 2P',cursive;font-size:8px;resize:vertical;"
    placeholder="Escribe la novedad aquí...">{{ contenido_prev|default('',true) }}</textarea>

<button class="btn" style="background:linear-gradient(135deg,#ff6600,#ffaa00);color:#000;border-bottom:5px solid #cc5500;" type="submit">
📢 PUBLICAR NOVEDAD
</button>

</form>

<a class="link" href="/novedades">
< VOLVER A NOVEDADES
</a>

</div>

</body>
</html>
"""


@app.route("/novedades")
def novedades():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    es_admin = usuario["username"].lower() == "periko"

    db = get_db()
    posts = []

    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, titulo, contenido, autor,
                       TO_CHAR(creado_en, 'DD/MM/YYYY HH24:MI') AS fecha
                FROM novedades
                ORDER BY creado_en DESC
                LIMIT 50
            """)
            posts = cur.fetchall()
    except Exception as e:
        print("ERROR AL CARGAR NOVEDADES:", e)

    return render_template_string(
        HTML_NOVEDADES,
        posts=posts,
        es_admin=es_admin
    )


@app.route("/novedades/crear", methods=["GET", "POST"])
def novedades_crear():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    if usuario["username"].lower() != "periko":
        return redirect(url_for("novedades"))

    mensaje = ""
    titulo_prev = ""
    contenido_prev = ""

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()

        titulo_prev = titulo
        contenido_prev = contenido

        if not titulo:
            mensaje = "El título no puede estar vacío."
        elif not contenido:
            mensaje = "El contenido no puede estar vacío."
        elif len(titulo) > 200:
            mensaje = "El título es demasiado largo (máx 200 caracteres)."
        elif len(contenido) > 5000:
            mensaje = "El contenido es demasiado largo (máx 5000 caracteres)."
        else:
            db = get_db()
            try:
                with db.cursor() as cur:
                    cur.execute("""
                        INSERT INTO novedades (titulo, contenido, autor)
                        VALUES (%s, %s, %s)
                    """, (titulo, contenido, usuario["username"]))
                db.commit()
                return redirect(url_for("novedades"))
            except Exception as e:
                db.rollback()
                print("ERROR AL CREAR NOVEDAD:", e)
                mensaje = "No se pudo publicar la novedad."

    return render_template_string(
        HTML_NOVEDADES_CREAR,
        mensaje=mensaje,
        titulo_prev=titulo_prev,
        contenido_prev=contenido_prev
    )


@app.route("/novedades/borrar/<int:post_id>", methods=["POST"])
def novedades_borrar(post_id):
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    if usuario["username"].lower() != "periko":
        return redirect(url_for("novedades"))

    db = get_db()

    try:
        with db.cursor() as cur:
            cur.execute("""
                DELETE FROM novedades
                WHERE id = %s
            """, (post_id,))

            if cur.rowcount == 0:
                db.rollback()
            else:
                db.commit()
    except Exception as e:
        db.rollback()
        print("ERROR AL BORRAR NOVEDAD:", e)

    return redirect(url_for("novedades"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/health")
def health():
    try:
        db = get_db()

        with db.cursor() as cur:
            cur.execute("SELECT 1")

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "error",
            "database": str(e)
        }, 500


HTML_RETAR_BJ = CSS + """
<div class="arcade-box">

<h1>⚔️ RETAR BLACKJACK PVP ⚔️</h1>

<div class="badge">
SALDO: {{ usuario.perikoins }} P
</div>

<p style="font-size:7px;color:#cc00ff">
¡RETA A OTRO JUGADOR A BLACKJACK! AMBOS APUESTAN LO MISMO. EL GANADOR SE LLEVA TODO.
</p>

{% if mensaje %}
<div class="msg">
{{ mensaje }}
</div>
{% endif %}

<h3 style="font-size:9px;color:#cc00ff;margin:14px 0 8px;">🎯 CREAR NUEVO RETO</h3>

<form method="POST" action="/retar-bj">
<label>OPONENTE</label>
<input type="text" name="oponente" placeholder="Nombre del jugador" required style="width:100%;margin:4px 0;">

<label>APUESTA</label>
<div class="grid">
{% for cantidad in [10,50,100,250,500,1000,5000] %}
<button class="chip" name="apuesta" value="{{ cantidad }}" type="submit">{{ cantidad }}</button>
{% endfor %}
</div>
</form>

<h3 style="font-size:9px;color:#00ffcc;margin:14px 0 8px;">📨 RETOS RECIBIDOS</h3>
{% if retos_recibidos %}
<div class="reto-list">
{% for reto in retos_recibidos %}
<div class="reto-item">
<div class="reto-info">
⚔️ <b>{{ reto.retidor }}</b> te reta por <b>{{ reto.apuesta }} P</b>
</div>
<div class="reto-actions">
<form method="POST" action="/aceptar-reto/{{ reto.id }}">
<button class="btn-aceptar" type="submit">✅ ACEPTAR</button>
</form>
<form method="POST" action="/cancelar-reto/{{ reto.id }}">
<button class="btn-cancelar" type="submit">❌ RECHAZAR</button>
</form>
</div>
</div>
{% endfor %}
</div>
{% else %}
<p style="font-size:7px;color:#555;">No tienes retos pendientes.</p>
{% endif %}

<h3 style="font-size:9px;color:#ff6666;margin:14px 0 8px;">📤 TUS RETOS ENVIADOS</h3>
{% if retos_enviados %}
<div class="reto-list">
{% for reto in retos_enviados %}
<div class="reto-item"{% if reto.estado == 'jugando' %} style="border-color:#cc00ff;background:linear-gradient(90deg,#1a0022 0%,#33004d 100%);box-shadow:0 0 12px #cc00ff55;"{% endif %}>
<div class="reto-info">
⚔️ Retaste a <b>{{ reto.retado }}</b> por <b>{{ reto.apuesta }} P</b> — {% if reto.estado == 'jugando' %}<span style="color:#00ff88;font-size:8px;animation:parpadeo 1s infinite;">¡ACEPTADO! EN JUEGO ▶</span>{% else %}{{ reto.estado }}{% endif %}
</div>
<div class="reto-actions">
{% if reto.estado == 'pendiente' %}
<form method="POST" action="/cancelar-reto/{{ reto.id }}">
<button class="btn-cancelar" type="submit">❌ CANCELAR</button>
</form>
{% elif reto.estado == 'jugando' %}
<a class="btn" style="background:#cc00ff;color:#000;font-size:8px;padding:6px 14px;display:inline-block;text-decoration:none;border:2px solid #8800aa;border-bottom:4px solid #660088;font-family:'Press Start 2P',monospace;" href="/pvp-bj/{{ reto.id }}">⚔️ ENTRAR</a>
{% endif %}
</div>
</div>
{% endfor %}
</div>
{% else %}
<p style="font-size:7px;color:#555;">No has enviado retos.</p>
{% endif %}

<a class="link" href="/menu">&lt; VOLVER AL MENU</a>

</div>
"""


HTML_PVP_BJ = CSS + """
<div class="arcade-box">

<h1>⚔️ BLACKJACK PVP ⚔️</h1>

<div class="badge">
SALDO: {{ usuario.perikoins }} P &nbsp;|&nbsp; APUESTA: {{ reto.apuesta }} P
</div>

<p style="font-size:7px;color:#cc00ff">
{{ reto.retidor }} VS {{ reto.retado }} — BOTE: {{ reto.apuesta * 2 }} P
</p>

{% if resultado %}
<div class="pvp-bj-result">
<div class="win" style="border-color:#cc00ff;">{{ resultado }}</div>
</div>
{% endif %}

{% if mensaje %}
{% if victoria %}
<div class="win">✨ {{ mensaje }} ✨</div>
{% else %}
<div class="msg">{{ mensaje }}</div>
{% endif %}
{% endif %}

{% if not resultado %}
<div class="pvp-bj-hands">

<div class="pvp-bj-hand">
<h3>{{ reto.retidor }}</h3>
<div class="cards">{{ cartas_j1 }}</div>
<div class="score">⭐ {{ valor_j1 }}</div>
<div class="status {{ estado_j1 }}">{{ texto_j1 }}</div>
</div>

<div class="pvp-bj-hand">
<h3>{{ reto.retado }}</h3>
<div class="cards">{{ cartas_j2 }}</div>
<div class="score">⭐ {{ valor_j2 }}</div>
<div class="status {{ estado_j2 }}">{{ texto_j2 }}</div>
</div>

</div>

{% if es_mi_turno and not terminado %}
<div class="pvp-bj-turn-indicator">
🎯 ¡ES TU TURNO! Refresca si no ves cambios.
</div>
<div class="pvp-bj-actions">
<form method="POST" action="/pvp-bj/{{ reto.id }}">
<input type="hidden" name="accion" value="pedir">
<button type="submit">🃏 PEDIR CARTA</button>
</form>
<form method="POST" action="/pvp-bj/{{ reto.id }}">
<input type="hidden" name="accion" value="plantarse">
<button class="btn-stand" type="submit">✋ PLANTARSE</button>
</form>
</div>
{% elif not terminado %}
<div class="pvp-bj-turn-indicator">
⏳ ESPERANDO AL OPONENTE... Refresca para ver cambios.
</div>
{% endif %}

{% endif %}

<a class="link" href="/retar-bj">&lt; VOLVER A RETOS</a>
<a class="link" href="/menu">&lt; MENU</a>

</div>
"""



def determinar_ganador_pvp(v1, v2, bj1, bj2):
    if bj1 and not bj2:
        return 'j1', False, 'BLACKJACK NATURAL!', 3
    if bj2 and not bj1:
        return 'j2', False, 'BLACKJACK NATURAL!', 3
    if bj1 and bj2:
        return None, True, 'AMBOS BLACKJACK NATURAL', 1
    if v1 > 21 and v2 > 21:
        return None, True, 'AMBOS SE PASARON', 1
    if v1 > 21:
        return 'j2', False, 'OPONENTE SE PASO', 2
    if v2 > 21:
        return 'j1', False, 'OPONENTE SE PASO', 2
    if v1 > v2:
        return 'j1', False, 'PUNTOS MAS ALTOS', 2
    if v2 > v1:
        return 'j2', False, 'PUNTOS MAS ALTOS', 2
    return None, True, 'EMPATE', 1


def resolver_pvp_bj(reto_id, conn=None):
    own_conn = conn is None
    if own_conn:
        db = get_db()
        conn = db
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM retos_bj WHERE id = %s FOR UPDATE", (reto_id,))
            reto = cur.fetchone()
            if not reto or reto["estado"] != "jugando":
                return

            j1 = reto["retidor"]
            j2 = reto["retado"]
            apuesta = reto["apuesta"]
            mano_j1 = reto["mano_j1"] or []
            mano_j2 = reto["mano_j2"] or []
            v1 = valor_blackjack(mano_j1)
            v2 = valor_blackjack(mano_j2)
            bj1 = v1 == 21 and len(mano_j1) == 2
            bj2 = v2 == 21 and len(mano_j2) == 2

            ganador, es_empate, motivo, mult = determinar_ganador_pvp(v1, v2, bj1, bj2)

            resultado_texto = (
                j1 + ": " + " ".join(mano_j1) + " = " + str(v1) + "  |  "
                + j2 + ": " + " ".join(mano_j2) + " = " + str(v2)
            )

            if es_empate:
                cur.execute("UPDATE usuarios SET perikoins = perikoins + %s WHERE username = %s", (apuesta, j1))
                cur.execute("UPDATE usuarios SET perikoins = perikoins + %s WHERE username = %s", (apuesta, j2))
                resultado_final = "EMPATE (" + motivo + "). Se devolvieron las apuestas."
                cur.execute(
                    "UPDATE retos_bj SET estado='empate', terminado_en=NOW() WHERE id=%s",
                    (reto_id,)
                )
            else:
                ganador_nombre = j1 if ganador == 'j1' else j2
                perdedor_nombre = j2 if ganador == 'j1' else j1
                ganancia = apuesta * mult
                cur.execute(
                    "UPDATE usuarios SET perikoins = perikoins + %s, victorias = victorias + 1, max_perikoins = GREATEST(max_perikoins, perikoins + %s) WHERE username = %s",
                    (ganancia, ganancia, ganador_nombre)
                )
                cur.execute(
                    "UPDATE usuarios SET derrotas = derrotas + 1 WHERE username = %s",
                    (perdedor_nombre,)
                )
                resultado_final = ganador_nombre + " GANA (" + motivo + ")! +" + str(ganancia) + " P"
                if mult == 3:
                    resultado_final += " BLACKJACK!"
                estado_resultado = 'gano_j1' if ganador == 'j1' else 'gano_j2'
                cur.execute(
                    "UPDATE retos_bj SET estado=%s, terminado_en=NOW() WHERE id=%s",
                    (estado_resultado, reto_id)
                )

            if own_conn:
                conn.commit()

        return resultado_texto, resultado_final

    except Exception as e:
        if own_conn:
            conn.rollback()
        print("ERROR resolver_pvp_bj: " + str(e))
        return None


@app.route("/retar-bj", methods=["GET", "POST"])
def retar_bj():
    usuario = usuario_actual()
    if not usuario:
        return redirect(url_for("login"))

    mensaje = ""

    if request.method == "POST":
        oponente = request.form.get("oponente", "").strip()
        apuesta_raw = request.form.get("apuesta", "0")
        apuesta = calcular_apuesta_monto(apuesta_raw, usuario["perikoins"])

        if not oponente:
            mensaje = "Escribe un nombre de oponente."
        elif oponente.lower() == usuario["username"].lower():
            mensaje = "No puedes desafiarte a ti mismo."
        elif apuesta <= 0 or apuesta > usuario["perikoins"]:
            mensaje = "Apuesta invalida o saldo insuficiente."
        else:
            oponente_user = obtener_usuario(oponente)
            if not oponente_user:
                mensaje = "El jugador '" + oponente + "' no existe."
            elif oponente_user["perikoins"] < apuesta:
                mensaje = oponente + " no tiene suficientes Perikoins para esta apuesta."
            else:
                db = get_db()
                try:
                    with db.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute(
                            "UPDATE usuarios SET perikoins = perikoins - %s WHERE username = %s AND perikoins >= %s",
                            (apuesta, usuario["username"], apuesta)
                        )
                        if cur.rowcount == 0:
                            db.rollback()
                            mensaje = "Saldo insuficiente al momento de crear el reto."
                        else:
                            cur.execute(
                                "INSERT INTO retos_bj (retidor, retado, apuesta, estado) VALUES (%s, %s, %s, 'pendiente') RETURNING id",
                                (usuario["username"], oponente, apuesta)
                            )
                            reto_id = cur.fetchone()["id"]
                            db.commit()
                            mensaje = "Reto enviado a " + oponente + " por " + str(apuesta) + " P! ID: #" + str(reto_id)
                except Exception as e:
                    db.rollback()
                    mensaje = "Error al crear reto: " + str(e)

        usuario = obtener_usuario(session["user"])

    db = get_db()
    retos_recibidos = []
    retos_enviados = []
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM retos_bj WHERE retado = %s AND estado = 'pendiente' ORDER BY creado_en DESC",
                (usuario["username"],)
            )
            retos_recibidos = cur.fetchall()

            cur.execute(
                "SELECT * FROM retos_bj WHERE retidor = %s AND estado IN ('pendiente','jugando') ORDER BY creado_en DESC",
                (usuario["username"],)
            )
            retos_enviados = cur.fetchall()
    except Exception as e:
        print("Error cargando retos: " + str(e))

    # Auto-redirigir si el retador tiene un reto en estado 'jugando'
    for reto in retos_enviados:
        if reto["estado"] == "jugando":
            return redirect(url_for("pvp_bj", reto_id=reto["id"]))

    return render_template_string(
        HTML_RETAR_BJ,
        usuario=usuario,
        mensaje=mensaje,
        retos_recibidos=retos_recibidos,
        retos_enviados=retos_enviados
    )


@app.route("/aceptar-reto/<int:reto_id>", methods=["POST"])
def aceptar_reto(reto_id):
    usuario = usuario_actual()
    if not usuario:
        return redirect(url_for("login"))

    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM retos_bj WHERE id = %s FOR UPDATE", (reto_id,))
            reto = cur.fetchone()

            if not reto or reto["estado"] != "pendiente":
                db.rollback()
                return redirect(url_for("retar_bj"))

            if reto["retado"] != usuario["username"]:
                db.rollback()
                return redirect(url_for("retar_bj"))

            if usuario["perikoins"] < reto["apuesta"]:
                db.rollback()
                return redirect(url_for("retar_bj"))

            cur.execute(
                "UPDATE usuarios SET perikoins = perikoins - %s WHERE username = %s AND perikoins >= %s",
                (reto["apuesta"], usuario["username"], reto["apuesta"])
            )
            if cur.rowcount == 0:
                db.rollback()
                return redirect(url_for("retar_bj"))

            mazo = [
                rango + palo
                for rango in ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
                for palo in ["\u2660","\u2665","\u2666","\u2663"]
            ]
            random.shuffle(mazo)

            mano_j1 = [mazo.pop(), mazo.pop()]
            mano_j2 = [mazo.pop(), mazo.pop()]

            import json as _json
            cur.execute(
                "UPDATE retos_bj SET estado='jugando', mazo=%s::jsonb, mano_j1=%s, mano_j2=%s, turno='j1' WHERE id=%s",
                (_json.dumps(mazo), mano_j1, mano_j2, reto_id)
            )

            db.commit()
            return redirect(url_for("pvp_bj", reto_id=reto_id))

    except Exception as e:
        db.rollback()
        print("Error aceptar reto: " + str(e))

    return redirect(url_for("retar_bj"))


@app.route("/cancelar-reto/<int:reto_id>", methods=["POST"])
def cancelar_reto(reto_id):
    usuario = usuario_actual()
    if not usuario:
        return redirect(url_for("login"))

    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM retos_bj WHERE id = %s FOR UPDATE", (reto_id,))
            reto = cur.fetchone()

            if not reto:
                db.rollback()
                return redirect(url_for("retar_bj"))

            if reto["estado"] == "pendiente":
                if reto["retidor"] == usuario["username"] or reto["retado"] == usuario["username"]:
                    cur.execute(
                        "UPDATE usuarios SET perikoins = perikoins + %s WHERE username = %s",
                        (reto["apuesta"], reto["retidor"])
                    )
                    cur.execute(
                        "UPDATE retos_bj SET estado='cancelado', terminado_en=NOW() WHERE id=%s",
                        (reto_id,)
                    )
                    db.commit()
                else:
                    db.rollback()
            else:
                db.rollback()

    except Exception as e:
        db.rollback()
        print("Error cancelar reto: " + str(e))

    return redirect(url_for("retar_bj"))


@app.route("/pvp-bj/<int:reto_id>", methods=["GET", "POST"])
def pvp_bj(reto_id):
    usuario = usuario_actual()
    if not usuario:
        return redirect(url_for("login"))

    db = get_db()
    mensaje = ""
    resultado = None
    victoria = False

    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM retos_bj WHERE id = %s", (reto_id,))
            reto = cur.fetchone()

            if not reto:
                return redirect(url_for("retar_bj"))

            if usuario["username"] not in (reto["retidor"], reto["retado"]):
                return redirect(url_for("retar_bj"))

            mano_j1 = reto["mano_j1"] or []
            mano_j2 = reto["mano_j2"] or []
            v1 = valor_blackjack(mano_j1)
            v2 = valor_blackjack(mano_j2)

            # If game already finished
            if reto["estado"] in ("gano_j1", "gano_j2", "empate", "cancelado"):
                resultado = (
                    reto["retidor"] + ": " + " ".join(mano_j1) + " = " + str(v1) + "  |  "
                    + reto["retado"] + ": " + " ".join(mano_j2) + " = " + str(v2)
                )

                if reto["estado"] == "empate":
                    mensaje = "EMPATE. Se devolvieron las apuestas."
                elif reto["estado"] == "gano_j1":
                    ganador = reto["retidor"]
                    bj = v1 == 21 and len(mano_j1) == 2
                    premio = reto["apuesta"] * (3 if bj else 2)
                    if ganador == usuario["username"]:
                        victoria = True
                        mensaje = "GANASTE! +" + str(premio) + " P" + (" BLACKJACK!" if bj else "")
                    else:
                        mensaje = ganador + " GANO. Perdiste " + str(reto["apuesta"]) + " P."
                elif reto["estado"] == "gano_j2":
                    ganador = reto["retado"]
                    bj = v2 == 21 and len(mano_j2) == 2
                    premio = reto["apuesta"] * (3 if bj else 2)
                    if ganador == usuario["username"]:
                        victoria = True
                        mensaje = "GANASTE! +" + str(premio) + " P" + (" BLACKJACK!" if bj else "")
                    else:
                        mensaje = ganador + " GANO. Perdiste " + str(reto["apuesta"]) + " P."
                else:
                    mensaje = "Reto cancelado."

                terminado = True
                es_mi_turno = False

                return render_template_string(
                    HTML_PVP_BJ,
                    usuario=usuario,
                    reto=reto,
                    resultado=resultado,
                    mensaje=mensaje,
                    victoria=victoria,
                    terminado=terminado,
                    es_mi_turno=es_mi_turno,
                    cartas_j1=" ".join(mano_j1),
                    cartas_j2=" ".join(mano_j2),
                    valor_j1=v1,
                    valor_j2=v2,
                    estado_j1="standing",
                    estado_j2="standing",
                    texto_j1="Finalizado",
                    texto_j2="Finalizado"
                )

            # Game in progress
            soy_j1 = usuario["username"] == reto["retidor"]
            mi_campo = "j1" if soy_j1 else "j2"
            otro_campo = "j2" if soy_j1 else "j1"

            if request.method == "POST" and reto["estado"] == "jugando":
                accion = request.form.get("accion", "")
                es_mi_turno = reto["turno"] == mi_campo

                if es_mi_turno and accion in ("pedir", "plantarse"):
                    cur.execute("SELECT * FROM retos_bj WHERE id = %s FOR UPDATE", (reto_id,))
                    reto = cur.fetchone()

                    if accion == "pedir":
                        import json as _json
                        mazo_data = reto["mazo"]
                        if isinstance(mazo_data, str):
                            mazo = _json.loads(mazo_data)
                        else:
                            mazo = list(mazo_data)
                        carta = mazo.pop()

                        mano_actual = list(mano_j1 if mi_campo == "j1" else mano_j2) + [carta]
                        v_actual = valor_blackjack(mano_actual)

                        cur.execute(
                            "UPDATE retos_bj SET mano_" + mi_campo + " = array_append(mano_" + mi_campo + ", %s), mazo = %s::jsonb WHERE id = %s",
                            (carta, _json.dumps(mazo), reto_id)
                        )

                        if v_actual >= 21:
                            cur.execute(
                                "UPDATE retos_bj SET plantado_" + mi_campo + " = TRUE, turno = %s WHERE id = %s",
                                (otro_campo, reto_id)
                            )
                        else:
                            cur.execute(
                                "UPDATE retos_bj SET turno = %s WHERE id = %s",
                                (otro_campo, reto_id)
                            )

                    elif accion == "plantarse":
                        cur.execute(
                            "UPDATE retos_bj SET plantado_" + mi_campo + " = TRUE, turno = %s WHERE id = %s",
                            (otro_campo, reto_id)
                        )

                    db.commit()

                    # Reload reto after action
                    cur.execute("SELECT * FROM retos_bj WHERE id = %s", (reto_id,))
                    reto = cur.fetchone()
                    mano_j1 = reto["mano_j1"] or []
                    mano_j2 = reto["mano_j2"] or []
                    v1 = valor_blackjack(mano_j1)
                    v2 = valor_blackjack(mano_j2)

                    # Check if both stood
                    if reto["plantado_j1"] and reto["plantado_j2"]:
                        resolver_pvp_bj(reto_id, conn=db)
                        # Reload after resolution
                        cur.execute("SELECT * FROM retos_bj WHERE id = %s", (reto_id,))
                        reto = cur.fetchone()

            # Display current state
            mano_j1 = reto["mano_j1"] or []
            mano_j2 = reto["mano_j2"] or []
            v1 = valor_blackjack(mano_j1)
            v2 = valor_blackjack(mano_j2)

            soy_j1 = usuario["username"] == reto["retidor"]
            mi_campo = "j1" if soy_j1 else "j2"
            es_mi_turno = reto["turno"] == mi_campo and reto["estado"] == "jugando"
            terminado = reto["estado"] != "jugando"

            def estado_jugador(plantado, valor, es_turno):
                if plantado:
                    return "standing", "PLANTADO"
                if valor > 21:
                    return "busted", "SE PASO!"
                if es_turno:
                    return "turn", "JUGANDO..."
                return "", "ESPERANDO"

            e1, t1 = estado_jugador(reto["plantado_j1"], v1, reto["turno"] == "j1")
            e2, t2 = estado_jugador(reto["plantado_j2"], v2, reto["turno"] == "j2")

    except Exception as e:
        db.rollback()
        print("Error pvp_bj: " + str(e))
        mensaje = "Error: " + str(e)
        e1 = t1 = ""
        e2 = t2 = ""
        mano_j1 = []
        mano_j2 = []
        v1 = 0
        v2 = 0
        terminado = False
        es_mi_turno = False
        reto = {"retidor": "?", "retado": "?", "apuesta": 0, "id": reto_id}

    return render_template_string(
        HTML_PVP_BJ,
        usuario=usuario,
        reto=reto,
        resultado=resultado,
        mensaje=mensaje,
        victoria=victoria,
        terminado=terminado,
        es_mi_turno=es_mi_turno,
        cartas_j1=" ".join(mano_j1),
        cartas_j2=" ".join(mano_j2),
        valor_j1=v1,
        valor_j2=v2,
        estado_j1=e1,
        estado_j2=e2,
        texto_j1=t1,
        texto_j2=t2
    )




@app.errorhandler(Exception)
def manejar_error(error):
    print("ERROR:", error)

    return render_template_string(
        CSS + """

        <div class="arcade-box">

        <h1>⚠️ ERROR</h1>

        <div class="msg">
        Ocurrio un error en el servidor.
        <br><br>
        Intenta nuevamente.
        </div>

        <a class="btn" href="/menu">
        VOLVER AL MENU
        </a>

        </div>

        </body>
        </html>
        """
    ), 500


init_db()


if __name__ == "__main__":
    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
