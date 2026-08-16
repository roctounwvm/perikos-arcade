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
    justify-content:center;
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

</style>
</head>
<body>
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


def usuario_actual():
    if "user" not in session:
        return None

    return obtener_usuario(session["user"])


HTML_MENU = CSS + """

<div class="arcade-box">

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
</div>

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

<a class="btn" href="/juego/dados">
1. DADOS
</a>

<a class="btn" href="/juego/ruleta">
2. RULETA ROYALE
</a>

<a class="btn" href="/juego/cartas">
3. MAYOR O MENOR
</a>

<a class="btn" href="/juego/moneda">
4. CARA O CRUZ
</a>

<a class="btn" href="/juego/slots">
5. TRAGAPERRAS 8-BITS
</a>

<a class="btn" href="/juego/derby">
6. CARRERA DE PERIKOS
</a>

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

    return render_template_string(
        HTML_MENU,
        usuario=usuario,
        avatar=avatar,
        regalo=regalo,
        color_estilo=color_estilo,
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
            nuevo_saldo = saldo + (apuesta * multiplicador)
            mensaje = mensaje_gana
        else:
            nuevo_saldo = saldo - apuesta
            mensaje = mensaje_pierde

        cur.execute(
            """
            UPDATE usuarios
            SET perikoins = %s
            WHERE username = %s
            """,
            (
                nuevo_saldo,
                usuario["username"]
            )
        )

    db.commit()

    return ganado, mensaje


HTML_JUEGO = CSS + """

<div class="arcade-box">

<h1>{{ titulo }}</h1>

<div class="badge">
SALDO: {{ usuario.perikoins }} P
</div>

{% if visual %}
<div class="game-icon">
{{ visual }}
</div>
{% endif %}

{% if resultado %}
<div class="win">
RESULTADO:<br><br>
{{ resultado }}
</div>
{% endif %}

{% if mensaje %}

{% if victoria %}
<div class="win">
✨ {{ mensaje }} ✨
</div>
{% else %}
<div class="msg">
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

{% for cantidad in [10,50,100,250,500,1000] %}

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
        resultado = random.randint(1, 13)

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

        resultado = f"{r1} {r2} {r3}"

        if r1 == r2 == r3:
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
        victoria=victoria
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

<label>ELIGE CORREDOR</label>

<select name="corredor" required>

{% for valor,texto in opciones %}

<option value="{{ valor }}">
{{ texto }}
</option>

{% endfor %}

</select>

<label>SELECCIONA TU APUESTA</label>

<div class="grid">

{% for cantidad in [10,50,100,250,500,1000] %}

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

{% if carrera %}

<div class="race">

<div class="race-title">
🏁 ¡QUE COMIENCE LA CARRERA! 🏁
</div>

{% for corredor,data in carrera.items() %}

<div
class="racer {% if corredor == ganador %}winner{% endif %}"
data-score="{{ data.score }}"
>

<div class="racer-name">
{{ data.icon }} {{ data.nombre }}
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

<div id="raceResult" class="race-result">
🏆 ¡{{ carrera[ganador].nombre|upper }} GANÓ! 🏆
</div>

</div>

<script>

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

    if request.method == "POST":
        apuesta = calcular_apuesta_monto(
            request.form.get("apuesta"),
            usuario["perikoins"]
        )

        corredor_elegido = request.form.get("corredor")

        if corredor_elegido not in corredores:
            mensaje = "Corredor invalido."

        elif apuesta <= 0:
            mensaje = "Apuesta invalida."

        elif apuesta > usuario["perikoins"]:
            mensaje = "No tienes suficientes Perikoins."

        else:
            scores = {
                "ROJO": random.randint(30, 100),
                "VERDE": random.randint(25, 100),
                "AZUL": random.randint(20, 100),
                "DORADO": random.randint(10, 100)
            }

            ganador = max(
                scores,
                key=scores.get
            )

            cuotas = {
                "ROJO": 2,
                "VERDE": 3,
                "AZUL": 4,
                "DORADO": 8
            }

            carrera = {}

            for nombre, datos in corredores.items():
                carrera[nombre] = {
                    **datos,
                    "score": scores[nombre]
                }

            if corredor_elegido == ganador:
                mult = cuotas[corredor_elegido]
                ganancia = apuesta * mult

                mensaje = (
                    f"🏆 GANO EL {corredores[ganador]['nombre']}! "
                    f"Ganaste {ganancia} Perikoins "
                    f"(x{mult})!"
                )

                victoria, mensaje = procesar_apuesta(
                    usuario,
                    apuesta,
                    True,
                    mult,
                    mensaje,
                    ""
                )

            else:
                mensaje = (
                    f"GANO EL {corredores[ganador]['nombre']}. "
                    f"Tu corredor perdió. "
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
        mensaje=mensaje,
        victoria=victoria
    )


HTML_TIENDA = CSS + """

<div class="arcade-box">

<h1>TIENDA DE COFRES</h1>

<div class="badge">
SALDO: {{ usuario.perikoins }} P
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
<!-- COLORES DE MAQUINA -->
<!-- ============================= -->

<div
class="chest"
style="border-color:#ff00ff;"
>

<h2 style="color:#ff00ff;font-size:10px;">
🎰 COLORES DE LA MAQUINA
</h2>

<p
style="
font-size:7px;
color:#aaa;
line-height:1.8;
"
>
🔥 FUEGO<br>
❄️ HIELO<br>
🌈 NEON<br>
🌌 GALAXIA<br>
👑 DIVINO<br>
<br>
Estos colores son exclusivos
de la maquina.
</p>

<div
style="
font-size:7px;
color:#ff00ff;
margin-top:10px;
"
>
🔒 PROXIMAMENTE
</div>

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

    return render_template_string(
        HTML_TIENDA,
        usuario=usuario,
        nuevo=nuevo,
        mensaje=mensaje,
        colores_tienda=colores_tienda,
        colores_desbloqueados=colores_desbloqueados
    )

HTML_PERFIL = CSS + """

<div class="arcade-box">

<h1>MI PERFIL</h1>

<div class="badge">
{{ avatar.icon }}
<br>
{{ avatar.nombre }}
</div>

<p style="font-size:8px">
AVATARES:
{{ desbloqueados|length }}/50
</p>

<div class="avatar-grid">

{% for aid,item in avatares.items() %}

{% set tiene = aid in desbloqueados %}

<form method="POST">

<input
type="hidden"
name="avatar_id"
value="{{ aid }}"
>

<button
class="avatar-item
{% if aid == usuario.avatar_activo %}active{% endif %}
{% if not tiene %}locked{% endif %}"
type="submit"
{% if not tiene %}disabled{% endif %}
>

<div style="font-size:20px">
{% if tiene %}
{{ item.icon }}
{% else %}
🔒
{% endif %}
</div>

<div style="color:{{ item.color }}">
{{ item.rareza }}
</div>

</button>

</form>

{% endfor %}

</div>

<a class="link" href="/menu">
< VOLVER
</a>

</div>

</body>
</html>
"""


@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    desbloqueados = cargar_avatares(
        usuario["avatares_desbloqueados"]
    )

    if request.method == "POST":
        try:
            avatar_id = int(
                request.form.get("avatar_id", 1)
            )
        except ValueError:
            avatar_id = 1

        if (
            avatar_id in AVATARES_DB
            and avatar_id in desbloqueados
        ):
            db = get_db()

            with db.cursor() as cur:
                cur.execute(
                    """
                    UPDATE usuarios
                    SET avatar_activo = %s
                    WHERE username = %s
                    """,
                    (
                        avatar_id,
                        usuario["username"]
                    )
                )

            db.commit()

            usuario = obtener_usuario(
                session["user"]
            )

    avatar = AVATARES_DB.get(
        usuario["avatar_activo"],
        AVATARES_DB[1]
    )

    return render_template_string(
        HTML_PERFIL,
        usuario=usuario,
        avatares=AVATARES_DB,
        desbloqueados=desbloqueados,
        avatar=avatar
    )


HTML_RANKING = CSS + """

<div class="arcade-box">

<h1>TOP 50 JUGADORES</h1>

<div style="max-height:350px;overflow:auto">

<table>

<tr>
<th>POS</th>
<th>JUGADOR</th>
<th>PERIKOINS</th>
</tr>

{% for pos,j in jugadores %}

<tr>

<td>{{ pos }}</td>

<td>
{{ j.avatar.icon }}
{{ j.username }}
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
                avatar_activo
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
            "avatar": avatar
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

<h1 style="color:#ff0055">
PANEL ADMIN PERIKO
</h1>

<div class="badge">
👑 ADMINISTRADOR SUPREMO
</div>

{% if mensaje %}
<div class="msg">
{{ mensaje }}
</div>
{% endif %}


<!-- ============================= -->
<!-- REGALAR PERIKOINS -->
<!-- ============================= -->

<div class="chest">

<h2 style="color:#00ffcc;font-size:10px;">
🎁 REGALAR PERIKOINS
</h2>

<p style="font-size:7px;color:#aaa;line-height:1.7;">
Envía Perikoins directamente a cualquier jugador.
</p>

<form method="POST" action="/admin">

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


<!-- ============================= -->
<!-- ELIMINAR CUENTA -->
<!-- ============================= -->

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


<!-- ============================= -->
<!-- INFORMACION DEL PANEL -->
<!-- ============================= -->

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

@app.route("/admin", methods=["GET", "POST"])
def admin():
    usuario = usuario_actual()

    if not usuario:
        return redirect(url_for("login"))

    if usuario["username"].lower() != "periko":
        return redirect(url_for("menu"))

    mensaje = ""

    if request.method == "POST":
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

    return render_template_string(
        HTML_ADMIN,
        mensaje=mensaje
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
            mensaje="Debes indicar un usuario."
        )

    if destino.lower() == "periko":
        return render_template_string(
            HTML_ADMIN,
            mensaje="No puedes eliminar la cuenta PERIKO."
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
        mensaje=mensaje
    )

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
