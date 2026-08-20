import streamlit as st
import os
import time
import glob
import re
from gtts import gTTS
from PIL import Image

# 1. Configuración de la página
st.set_page_config(
    page_title="Lector de Voz IA",
    page_icon="🎙️",
    layout="centered"
)

# Crear directorio temporal si no existe
os.makedirs("temp", exist_ok=True)

# 2. Barra lateral (Sidebar)
with st.sidebar:
    st.subheader("⚙️ Configuración de Audio")
    
    option_lang = st.selectbox(
        "Idioma / Acento",
        ("Español (Latinoamérica)", "Español (España)", "English (US)", "English (UK)")
    )
    
    lang_config = {
        "Español (Latinoamérica)": ("es", "com.mx"),
        "Español (España)": ("es", "es"),
        "English (US)": ("en", "com"),
        "English (UK)": ("en", "co.uk")
    }
    lg, tld_code = lang_config[option_lang]

    slow_speed = st.checkbox("Modo lento", value=False)

# 3. Encabezado e Imagen
st.title("🎙️ Generador de Audio con IA")

header_image_path = 'gTTS_header.png'
if os.path.exists(header_image_path):
    image = Image.open(header_image_path)
    st.image(image, use_container_width=True)

# Texto principal creativo
texto_cool = (
    "Bienvenido al futuro de la síntesis de voz. "
    "Hoy las palabras ya no solo se leen en pantallas, cobran vida en ondas de sonido digitales. "
    "Desde podcasts automatizados hasta interfaces del metaverso, "
    "la inteligencia artificial transforma las ideas escritas en experiencias auditivas únicas. "
    "¿Qué historia vas a crear hoy?"
)

st.markdown("### ⚡ Texto de muestra")
st.info(texto_cool)

# Cargar archivo .txt externo
uploaded_file = st.file_uploader("O carga un archivo de texto (.txt)", type=["txt"])
file_text = ""
if uploaded_file is not None:
    try:
        file_text = uploaded_file.read().decode("utf-8")
        st.success("Archivo cargado con éxito.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

# Manejo de estado de la sesión
if "user_text" not in st.session_state:
    st.session_state["user_text"] = ""

display_text = file_text if file_text else st.session_state["user_text"]

# Área de texto
text = st.text_area("Copia o escribe tu texto aquí:", value=display_text, height=160, placeholder="Escribe algo épico...")

if st.button("🚀 Cargar texto de ejemplo"):
    st.session_state["user_text"] = texto_cool
    st.rerun()

if text:
    st.caption(f"Caracteres: {len(text)}")

# Función para síntesis de voz
def text_to_speech(text_input, lang, tld, slow):
    try:
        tts = gTTS(text=text_input, lang=lang, tld=tld, slow=slow)
        clean_name = re.sub(r'[^\w\s]', '', text_input[:15]).strip().replace(" ", "_")
        my_file_name = clean_name if clean_name else "audio"
        file_path = f"temp/{my_file_name}.mp3"
        tts.save(file_path)
        return file_path
    except Exception as e:
        st.error(f"Error al generar audio: {e}")
        return None

# Procesar y reproducir audio
if st.button("🔊 Generar Voz"):
    if not text.strip():
        st.warning("Escribe o carga un texto primero.")
    else:
        with st.spinner("Procesando audio..."):
            audio_path = text_to_speech(text, lg, tld_code, slow_speed)
            
            if audio_path:
                with open(audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                
                st.markdown("### 🎧 Reproductor:")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)

                st.download_button(
                    label="📥 Descargar MP3",
                    data=audio_bytes,
                    file_name="voz_ia.mp3",
                    mime="audio/mp3"
                )

# Limpieza de archivos antiguos
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
