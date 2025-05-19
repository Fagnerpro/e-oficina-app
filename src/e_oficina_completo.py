import streamlit as st
import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

st.set_page_config(page_title="E-OFICINA - Diagnóstico Assistido", page_icon="favicon.ico", layout="centered")

# Banco de dados SQLite
conn = sqlite3.connect("e_oficina.db")
c = conn.cursor()

# Tabela de atendimentos
c.execute("""
CREATE TABLE IF NOT EXISTS atendimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    telefone TEXT,
    marca TEXT,
    modelo TEXT,
    ano_fabricacao INTEGER,
    km INTEGER,
    sintomas TEXT,
    diagnostico TEXT,
    localizacao TEXT,
    data_atendimento TEXT
)
""")

# Tabela de oficinas (nova)
c.execute("""
CREATE TABLE IF NOT EXISTS oficinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cidade TEXT,
    especialidade TEXT
)
""")
conn.commit()

# Dados simulados de oficinas
oficinas_data = [
    ("Oficina Elétrica Goiânia", "Goiânia", "Baterias, Inversores"),
    ("EletroCar São Paulo", "São Paulo", "Softwares, Suspensão"),
    ("Volts Rio", "Rio de Janeiro", "Carregamento, Motores")
]
c.executemany("INSERT OR IGNORE INTO oficinas (nome, cidade, especialidade) VALUES (?, ?, ?)", oficinas_data)
conn.commit()

# Modelos por marca
modelos_por_marca = {
    "BYD": ["Dolphin", "Yuan Plus", "Song Plus"],
    "Tesla": ["Model 3", "Model Y"],
    "Nissan": ["Leaf"],
    "Chevrolet": ["Bolt EV"],
    "Renault": ["Zoe"],
    "BMW": ["i4"]
}

# Dados simulados para regressão
dados_falhas = pd.DataFrame([
    {"marca": "BYD", "modelo": "Dolphin", "ano_fabricacao": 2022, "km": 30000, "falha": "Bateria", "probabilidade": 0.7},
    {"marca": "BYD", "modelo": "Yuan Plus", "ano_fabricacao": 2023, "km": 20000, "falha": "Inversor", "probabilidade": 0.6},
    {"marca": "Tesla", "modelo": "Model 3", "ano_fabricacao": 2021, "km": 50000, "falha": "Piloto Automático", "probabilidade": 0.8},
    {"marca": "Tesla", "modelo": "Model Y", "ano_fabricacao": 2022, "km": 40000, "falha": "Touchscreen", "probabilidade": 0.7},
    {"marca": "Nissan", "modelo": "Leaf", "ano_fabricacao": 2019, "km": 80000, "falha": "Bateria", "probabilidade": 0.9},
    {"marca": "Chevrolet", "modelo": "Bolt EV", "ano_fabricacao": 2020, "km": 60000, "falha": "Bateria", "probabilidade": 0.8}
])

# Treinar modelo de regressão
le_marca = LabelEncoder()
le_modelo = LabelEncoder()
le_falha = LabelEncoder()
dados_falhas["marca_encoded"] = le_marca.fit_transform(dados_falhas["marca"])
dados_falhas["modelo_encoded"] = le_modelo.fit_transform(dados_falhas["modelo"])
dados_falhas["falha_encoded"] = le_falha.fit_transform(dados_falhas["falha"])

X = dados_falhas[["marca_encoded", "modelo_encoded", "ano_fabricacao", "km"]]
y = dados_falhas["probabilidade"]
modelo = RandomForestRegressor(n_estimators=100, random_state=42)
modelo.fit(X, y)

# Interface Streamlit
st.title("🔧 E-OFICINA")
st.subheader("Módulo 1: Diagnóstico Assistido para Clientes")

with st.form("formulario_cliente"):
    st.markdown("### 📋 Dados do Cliente e Veículo")
    cliente = st.text_input("Nome do Cliente*", max_chars=100)
    telefone = st.text_input("Telefone de Contato*", max_chars=20)
    localizacao = st.text_input("Cidade ou CEP*", max_chars=50)

    marca = st.selectbox("Marca do Veículo*", options=list(modelos_por_marca.keys()))
    modelo = st.selectbox("Modelo do Veículo*", options=modelos_por_marca[marca])

    col1, col2 = st.columns(2)
    with col1:
        ano_fabricacao = st.number_input("Ano de Fabricação*", min_value=1990, max_value=2030, step=1)
    with col2:
        km = st.number_input("Quilometragem Atual (km)*", min_value=0)

    sintomas = st.text_area("Descreva os sintomas relatados*", height=100)
    enviar = st.form_submit_button("Analisar Falha")

# Função para prever falha
def prever_falha(marca, modelo, ano_fabricacao, km):
    try:
        marca_enc = le_marca.transform([marca])[0]
        modelo_enc = le_modelo.transform([modelo])[0]
        entrada = [[marca_enc, modelo_enc, ano_fabricacao, km]]
        probabilidade = modelo.predict(entrada)[0]
        falha_idx = dados_falhas.iloc[entrada[0][1]]["falha_encoded"]
        falha = le_falha.inverse_transform([falha_idx])[0]
        return falha, probabilidade
    except:
        return "Falha desconhecida", 0.0

# Função para buscar oficinas
def buscar_oficinas(localizacao, falha):
    c.execute("SELECT nome, cidade, especialidade FROM oficinas WHERE cidade LIKE ? AND especialidade LIKE ?",
              (f"%{localizacao}%", f"%{falha}%"))
    return c.fetchall()

if enviar:
    if cliente and telefone and localizacao and marca and modelo and sintomas:
        data = datetime.now().strftime("%Y-%m-%d %H:%M")
        falha, probabilidade = prever_falha(marca, modelo, ano_fabricacao, km)
        diagnostico = f"Possível falha: {falha} (Probabilidade: {probabilidade:.0%})"

        # Salvar no banco
        c.execute("""
            INSERT INTO atendimentos (
                cliente, telefone, marca, modelo, ano_fabricacao, km, sintomas, diagnostico, localizacao, data_atendimento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente, telefone, marca, modelo, ano_fabricacao, km, sintomas, diagnostico, localizacao, data))
        conn.commit()

        # Exibir diagnóstico
        st.success("✅ Análise concluída!")
        st.markdown(f"**Diagnóstico:** {diagnostico}")

        # Buscar e exibir oficinas
        oficinas = buscar_oficinas(localizacao, falha)
        if oficinas:
            st.markdown("### 🔧 Oficinas Recomendadas")
            for oficina in oficinas:
                st.write(f"- **{oficina[0]}** ({oficina[1]}): Especializada em {oficina[2]}")
        else:
            st.warning("⚠️ Nenhuma oficina encontrada na sua região. Tente outra cidade.")
    else:
        st.error("⚠️ Preencha todos os campos obrigatórios.")