import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="Analizador de Autómatas", layout="wide")

# Configuración de Contenidos por Autómata
AUT_META = {
    "E-commerce": {
        "id": "ecommerce",
        "sigma": "{ H, S, C }",
        "desc": "Patrón: HOME SEARCH+ CART",
        "img": "ecommerce.png",
        "trans": ["δ(q0,H)=q1", "δ(q1,S)=q2", "δ(q2,S)=q2", "δ(q2,C)=q3"]
    },
    "Protocolo IoT": {
        "id": "iot",
        "sigma": "{ H, T, U, C }",
        "desc": "Patrón: HDR (TEMP | HUM)* CRC",
        "img": "iot.png",
        "trans": ["δ(q0,H)=q1", "δ(q1,T)=q1", "δ(q1,U)=q1", "δ(q1,C)=q2"]
    },
    "Secuencias Genéticas": {
        "id": "genetica",
        "sigma": "{ K, G, X, F }",
        "desc": "Patrón: K G X* F",
        "img": "genetica.png",
        "trans": ["δ(q0,K)=q1", "δ(q1,G)=q2", "δ(q2,X)=q2", "δ(q2,F)=q3"]
    }
}

# --- Sidebar ---
st.sidebar.title("Configuración")
selected_name = st.sidebar.selectbox("Selecciona el Ejercicio:", list(AUT_META.keys()))
meta = AUT_META[selected_name]

# --- UI Principal ---
st.title(f"🔍 {selected_name}")
st.info(meta["desc"])

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Definición Formal")
    st.write(f"**Alfabeto (Σ):** {meta['sigma']}")
    st.write("**Transiciones:**")
    for t in meta["trans"]:
        st.code(t)

with col2:
    st.subheader("Diagrama de Transición")
    # Busca la imagen en la carpeta images/
    img_path = os.path.join(os.path.dirname(__file__), "images", meta["img"])
    if os.path.exists(img_path):
        st.image(img_path, caption=f"Modelo AFND para {selected_name}")
    else:
        st.error(f"Falta imagen: '{meta['img']}' en carpeta 'images/'")

st.divider()

# --- Ejecución ---
st.subheader(" Ejecución y Pruebas")
raw_input = st.text_input("Ingresa la secuencia (ej: H, S, S, C):", placeholder="Usa comas para separar")

if st.button("Evaluar Cadena", type="primary"):
    seq = [s.strip().upper() for s in raw_input.split(",") if s.strip()]
    try:
        res = requests.post("http://localhost:8000/evaluate", 
                            json={"automata_type": meta["id"], "sequence": seq})
        
        if res.status_code == 200:
            data = res.json()
            if data["accepted"]:
                st.success(" ¡CADENA ACEPTADA!")
            else:
                st.error(" CADENA RECHAZADA (Estado de Error)")
            
            st.table(pd.DataFrame(data["history"]))
        else:
            st.error("Error en el Backend.")
    except:
        st.error("¿El Backend está encendido? (uvicorn main:app)")