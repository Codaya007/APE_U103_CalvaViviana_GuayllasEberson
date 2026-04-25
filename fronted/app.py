import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="Analizador de Autómatas", layout="wide")

# Configuración de Contenidos por Autómata
AFND_META = {
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

AFD_META = {
    "Transacción Bancaria": {
        "id": "transaccion",
        "sigma": "{ A, C, L }",
        "desc": "Transacción Bancaria (A: Autenticar, C: Capturar, L: Liquidar)",
        "img": "transaccionBancaria.png",
        "trans": ["δ(q0,A)=q_aut", "δ(q_aut,C)=q_cap", "δ(q_cap,L)=q_com"]
    },
    "Smart Lock": {
        "id": "smartlock",
        "sigma": "{ ok, bad }",
        "desc": "Cerradura Inteligente (ok: clave correcta, bad: clave incorrecta)",
        "img": "smartlock.png",
        "trans": ["δ(q0,ok)=q_open", "δ(q0,bad)=q1", "δ(q1,ok)=q_open", "δ(q1,bad)=q2", "δ(q2,ok)=q_open", "δ(q2,bad)=q_block", "δ(q_block,bad)=q_block", "δ(q_block,ok)=q_block"]
    },
    "Logística": {
        "id": "logistica",
        "sigma": "{ emp, env, ent, dev, can }",
        "desc": "Flujo de Logística (emp: empaquetar, env: enviar, ent: entregar, dev: devolver, can: cancelar)",
        "img": "logistica.png",
        "trans": ["δ(q_cre,emp)=q_emp", "δ(q_cre,can)=q_can", "δ(q_emp,env)=q_env", "δ(q_emp,can)=q_can", "δ(q_env,ent)=q_ent", "δ(q_ent,dev)=q_dev"]
    }
}

# --- Sidebar ---
st.sidebar.title("Configuración")
categoria = st.sidebar.radio("Categoría:", ["Autómatas Finitos Deterministas (AFD)", "Autómatas Finitos No Deterministas (AFND)"])

if categoria == "Autómatas Finitos Deterministas (AFD)":
    meta_dict = AFD_META
    endpoint = "evaluate_dfa"
else:
    meta_dict = AFND_META
    endpoint = "evaluate"

selected_name = st.sidebar.selectbox("Selecciona el Ejercicio:", list(meta_dict.keys()))
meta = meta_dict[selected_name]

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
        st.image(img_path, caption=f"Modelo para {selected_name}")
    else:
        st.warning(f"No hay diagrama disponible para este modelo (falta imagen: '{meta['img']}')")

st.divider()

# --- Ejecución ---
st.subheader(" Ejecución y Pruebas")
raw_input = st.text_input("Ingresa la secuencia (ej: H, S, S, C):", placeholder="Usa comas para separar")

if st.button("Evaluar Cadena", type="primary"):
    seq = [s.strip() for s in raw_input.split(",") if s.strip()]
    if categoria == "Autómatas Finitos No Deterministas (AFND)":
        seq = [s.upper() for s in seq] # Los AFND usaban mayúsculas en el código original
    try:
        res = requests.post(f"http://localhost:8000/{endpoint}", 
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