import streamlit as st
import os
import time
import glob
import base64
import re
from gtts import gTTS
from PIL import Image

# 1. Configuración de la página
st.set_page_config(
    page_title="Lector de Texto a Voz",
    page_icon="🎙️",
    layout="centered"
)

# Estilos visuales
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .story-card {
            background-color: #f9f9f9;
            padding: 18px;
            border-radius: 10px;
            border-left: 5px solid #4CAF50;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Crear directorio temporal para guardar audios
os.makedirs("temp", exist_ok=True)

# 2. Barra Lateral (Sidebar)
with st.sidebar:
    st.header("⚙️ Configuración")
    option_lang = st.selectbox(
        "Selecciona el idioma",
        ("Español", "English")
    )
    lg = 'es' if option_lang == "Español" else 'en'
    
    st.divider()
    st.info("Escribe o carga texto en el área principal para escucharlo.")

# 3. Encabezado e Imagen
st.title("🎙️ Conversión de Texto a Voz")

# Carga de la nueva imagen fot2.jpg
image_path = 'fot2.jpg'
if os.path.exists(image_path):
    image = Image.open(image_path)
    st.image(image, use_container_width=True)

# Fábula de muestra
fabula_texto = (
    "¡Ay! -dijo el ratón-. El mundo se hace cada día más pequeño. "
    "Al principio era tan grande que le tenía miedo. Corría y corría y por cierto que me alegraba "
    "ver esos muros, a diestra y siniestra, en la distancia. Pero esas paredes se estrechan tan rápido "
    "que me encuentro en el último cuarto y ahí en el rincón está la trampa sobre la cual debo pasar. "
    "Todo lo que debes hacer es cambiar de rumbo dijo el gato... y se lo comió.\n\n— Franz Kafka"
)

st.markdown("### 📖 Texto de ejemplo")
st.markdown(f'<div class="story-card">{fabula_texto}</div>', unsafe_allow_html=True)

# Inicializar estado para el texto
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

# Botón para cargar la fábula directamente
if st.button("📋 Usar el texto de la fábula arriba"):
    st.session_state["input_text"] = fabula_texto

# Entrada de texto del usuario
text = st.text_area(
    "Ingresa el texto a escuchar:", 
    value=st.session_state["input_text"], 
    height=140, 
    placeholder="Escribe o pega tu texto aquí...",
    key="text_area_input"
)

# Función para convertir texto a voz
def text_to_speech(input_text, lang):
    tts = gTTS(text=input_text, lang=lang)
    clean_name = re.sub(r'[^\w\s]', '', input_text[:15]).strip().replace(" ", "_")
    file_name = clean_name if clean_name else "audio"
    file_path = f"temp/{file_name}.mp3"
    tts.save(file_path)
    return file_path

# Botón para generar audio
if st.button("🔊 Convertir a Audio", key="convert_btn"):
    if not text.strip():
        st.warning("Por favor, ingresa algún texto para convertir.")
    else:
        with st.spinner("Generando archivo de audio..."):
            audio_path = text_to_speech(text, lg)
            
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            
            st.success("¡Audio generado con éxito!")
            st.audio(audio_bytes, format="audio/mp3")

            # Botón de descarga
            b64_audio = base64.b64encode(audio_bytes).decode()
            download_html = f'''
                <a href="data:file/mp3;base64,{b64_audio}" download="audio.mp3" style="
                    display: inline-block;
                    padding: 0.6em 1.2em;
                    color: white;
                    background-color: #008CBA;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                    text-align: center;">
                    📥 Descargar Archivo MP3
                </a>
            '''
            st.markdown(download_html, unsafe_allow_html=True)

# Limpieza de archivos temporales antiguos
def remove_files(n_days_old):
    mp3_files = glob.glob("temp/*.mp3")
    now = time.time()
    cutoff_time = n_days_old * 86400
    for file in mp3_files:
        if os.stat(file).st_mtime < (now - cutoff_time):
            try:
                os.remove(file)
            except Exception:
                pass

remove_files(7)
