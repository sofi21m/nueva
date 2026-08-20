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
    page_title="Conversión de Texto a Audio",
    page_icon="🎙️",
    layout="centered"
)

# Crear directorio temporal si no existe
os.makedirs("temp", exist_ok=True)

# 2. Barra lateral (Sidebar)
with st.sidebar:
    st.subheader("Configuración")
    st.write("Escribe y/o selecciona texto para ser escuchado.")
    
    option_lang = st.selectbox(
        "Selecciona el lenguaje",
        ("Español", "English")
    )
    lg = 'es' if option_lang == "Español" else 'en'

# 3. Encabezado e Imagen
st.title("Conversión de Texto a Audio")

# Cargar la nueva imagen fot2.jpg
if os.path.exists('fot2.jpg'):
    image = Image.open('fot2.jpg')
    st.image(image, width=350)
else:
    st.warning("No se encontró la imagen 'fot2.jpg' en el directorio.")

# Texto de la fábula
fabula_texto = (
    "¡Ay! -dijo el ratón-. El mundo se hace cada día más pequeño. "
    "Al principio era tan grande que le tenía miedo. Corría y corría y por cierto que me alegraba "
    "ver esos muros, a diestra y siniestra, en la distancia. Pero esas paredes se estrechan tan rápido "
    "que me encuentro en el último cuarto y ahí en el rincón está la trampa sobre la cual debo pasar. "
    "Todo lo que debes hacer es cambiar de rumbo dijo el gato... y se lo comió. "
    "Franz Kafka."
)

st.subheader("Una pequeña Fábula.")
st.write(fabula_texto)

# Inicializar la variable de texto en la sesión
if "user_text" not in st.session_state:
    st.session_state["user_text"] = ""

# Funcionalidad: Botón para copiar la fábula al área de texto automáticamente
if st.button("📋 Usar el texto de la fábula"):
    st.session_state["user_text"] = fabula_texto

# Entrada de texto del usuario
st.markdown("Quieres escucharlo?, copia o escribe el texto abajo:")
text = st.text_area("Ingrese El texto a escuchar.", value=st.session_state["user_text"], height=120)

# Función de conversión de texto a voz
def text_to_speech(text_input, lang):
    tts = gTTS(text=text_input, lang=lang)
    # Generar un nombre de archivo seguro eliminando caracteres especiales
    clean_name = re.sub(r'[^\w\s]', '', text_input[:15]).strip().replace(" ", "_")
    my_file_name = clean_name if clean_name else "audio"
    file_path = f"temp/{my_file_name}.mp3"
    tts.save(file_path)
    return file_path

# Botón principal para generar el audio
if st.button("Convertir a Audio"):
    if not text.strip():
        st.warning("Por favor, ingresa algún texto.")
    else:
        audio_path = text_to_speech(text, lg)
        
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        st.markdown("## Tú audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        # Enlace para descargar el archivo MP3
        bin_str = base64.b64encode(audio_bytes).decode()
        download_href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="audio.mp3">Descargar Audio File</a>'
        st.markdown(download_href, unsafe_allow_html=True)

# Mantenimiento: Elimina archivos creados hace más de N días
def remove_files(n_days):
    mp3_files = glob.glob("temp/*.mp3")
    if mp3_files:
        now = time.time()
        n_seconds = n_days * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < (now - n_seconds):
                try:
                    os.remove(f)
                except Exception:
                    pass

remove_files(7)
