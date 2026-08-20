import streamlit as st
import os
import time
import glob
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

# 2. Barra lateral (Sidebar) con controles mejorados
with st.sidebar:
    st.subheader("⚙️ Configuración del Audio")
    
    option_lang = st.selectbox(
        "Idioma / Acento",
        ("Español (Latinoamérica)", "Español (España)", "English (US)", "English (UK)")
    )
    
    # Mapeo de idioma y acento (tld)
    lang_config = {
        "Español (Latinoamérica)": ("es", "com.mx"),
        "Español (España)": ("es", "es"),
        "English (US)": ("en", "com"),
        "English (UK)": ("en", "co.uk")
    }
    lg, tld_code = lang_config[option_lang]

    # Control de velocidad
    slow_speed = st.checkbox("Hablar despacio", value=False)

# 3. Encabezado e Imagen
st.title("🎙️ Conversión de Texto a Audio")

if os.path.exists('fot2.jpg'):
    image = Image.open('fot2.jpg')
    st.image(image, width=350)
else:
    st.warning("No se encontró la imagen 'fot2.jpg' en el directorio.")

# Texto de ejemplo
fabula_texto = (
    "¡Ay! -dijo el ratón-. El mundo se hace cada día más pequeño. "
    "Al principio era tan grande que le tenía miedo. Corría y corría y por cierto que me alegraba "
    "ver esos muros, a diestra y siniestra, en la distancia. Pero esas paredes se estrechan tan rápido "
    "que me encuentro en el último cuarto y ahí en el rincón está la trampa sobre la cual debo pasar. "
    "Todo lo que debes hacer es cambiar de rumbo dijo el gato... y se lo comió. "
    "Franz Kafka."
)

st.subheader("📖 Una pequeña Fábula")
st.write(fabula_texto)

# Cargar archivo de texto externo
uploaded_file = st.file_uploader("O sube un archivo de texto (.txt)", type=["txt"])
file_text = ""
if uploaded_file is not None:
    file_text = uploaded_file.read().decode("utf-8")

# Inicializar la variable de texto en la sesión
if "user_text" not in st.session_state:
    st.session_state["user_text"] = ""

if st.button("📋 Usar el texto de la fábula"):
    st.session_state["user_text"] = fabula_texto

# Determinar el valor del texto a mostrar
current_text = file_text if file_text else st.session_state["user_text"]

st.markdown("### ✍️ Texto a convertir:")
text = st.text_area("Ingrese el texto a escuchar:", value=current_text, height=130)

# Mostrar contador de caracteres
if text:
    st.caption(f"Número de caracteres: {len(text)}")

# Función de conversión de texto a voz con tld y velocidad
def text_to_speech(text_input, lang, tld, slow):
    tts = gTTS(text=text_input, lang=lang, tld=tld, slow=slow)
    clean_name = re.sub(r'[^\w\s]', '', text_input[:15]).strip().replace(" ", "_")
    my_file_name = clean_name if clean_name else "audio"
    file_path = f"temp/{my_file_name}.mp3"
    tts.save(file_path)
    return file_path

# Botón principal para generar el audio
if st.button("🔊 Convertir a Audio"):
    if not text.strip():
        st.warning("Por favor, ingresa o sube algún texto.")
    else:
        with st.spinner("Generando audio..."):
            audio_path = text_to_speech(text, lg, tld_code, slow_speed)
            
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            
            st.markdown("## Tú audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            # Botón nativo de descarga de Streamlit
            st.download_button(
                label="📥 Descargar Audio MP3",
                data=audio_bytes,
                file_name="audio.mp3",
                mime="audio/mp3"
            )

# Mantenimiento de archivos temporales
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
