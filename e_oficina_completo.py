
import streamlit as st
import sqlite3
from fpdf import FPDF
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="E-OFICINA - Diagnóstico e Orçamento", page_icon="favicon.ico", layout="centered")

# Banco de dados SQLite local
conn = sqlite3.connect("e_oficina.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS atendimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    telefone TEXT,
    marca TEXT,
    modelo TEXT,
    ano_fabricacao INTEGER,
    ano_modelo INTEGER,
    km INTEGER,
    sintomas TEXT,
    diagnostico TEXT,
    data_atendimento TEXT
)
""")
conn.commit()

# Base de marcas e modelos
modelos_por_marca = {
    "BYD": ["Dolphin", "Yuan Plus", "Song Plus", "Tan EV", "Seal"],
    "Volvo": ["XC40 Recharge", "C40 Recharge"],
    "BMW": ["iX3", "i3", "iX", "i4"],
    "Renault": ["Kwid E-Tech", "Zoe"],
    "Fiat": ["500e"],
    "Nissan": ["Leaf"],
    "Chevrolet": ["Bolt EV", "Bolt EUV"],
    "Peugeot": ["e-208"],
    "Mercedes-Benz": ["EQB", "EQE", "EQS"],
    "GWM (Ora)": ["Ora 03", "Haval H6 Plug-in"],
    "JAC Motors": ["E-JS1", "iEV40", "iEV330P"],
    "Audi": ["e-tron", "Q4 e-tron", "RS e-tron GT"],
    "Porsche": ["Taycan"],
    "Tesla": ["Model 3", "Model Y"]
}

# Interface do usuário
st.image("logo_resized.png", width=250)
st.title("🔧 E-OFICINA")
st.subheader("Módulo 1: Diagnóstico Assistido e Orçamento Inteligente")

with st.form("formulario_oficina"):
    st.markdown("### 📋 Dados do Atendimento")
    cliente = st.text_input("Nome do Cliente*", max_chars=100)
    telefone = st.text_input("Telefone de Contato*", max_chars=20)

    marca = st.selectbox("Marca do Veículo*", options=list(modelos_por_marca.keys()))
    modelo = st.selectbox("Modelo do Veículo*", options=modelos_por_marca[marca])

    col1, col2 = st.columns(2)
    with col1:
        ano_fabricacao = st.number_input("Ano de Fabricação*", min_value=1990, max_value=2030, step=1)
    with col2:
        ano_modelo = st.number_input("Ano do Modelo*", min_value=1990, max_value=2031, step=1)

    km = st.number_input("Quilometragem Atual (km)*", min_value=0)
    sintomas = st.text_area("Descreva os sintomas relatados ou observados*", height=100)

    enviar = st.form_submit_button("Gerar Orçamento e Salvar")

# Diagnóstico automático simulado
diagnostico = ""
if sintomas:
    diagnostico = "Falha no inversor de potência. Verificar módulo eletrônico e cabos de alimentação."

# Função para gerar PDF
def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Orçamento Técnico - E-OFICINA", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(8)
    for chave, valor in dados.items():
        pdf.multi_cell(0, 10, f"{chave}: {valor}")
    nome_arquivo = f"orcamento_{dados['Cliente'].replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# Processamento ao enviar
if 'enviar' in locals() and enviar:
    if cliente and telefone and modelo and sintomas:
        data = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("""
            INSERT INTO atendimentos (
                cliente, telefone, marca, modelo, ano_fabricacao,
                ano_modelo, km, sintomas, diagnostico, data_atendimento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente, telefone, marca, modelo, ano_fabricacao, ano_modelo, km, sintomas, diagnostico, data))
        conn.commit()

        dados = {
            "Cliente": cliente,
            "Telefone": telefone,
            "Marca": marca,
            "Modelo": modelo,
            "Ano de Fabricação": ano_fabricacao,
            "Ano do Modelo": ano_modelo,
            "KM Atual": km,
            "Sintomas": sintomas,
            "Diagnóstico": diagnostico,
            "Data do Atendimento": data
        }

        arquivo_pdf = gerar_pdf(dados)
        with open(arquivo_pdf, "rb") as file:
            st.success("✅ Orçamento gerado com sucesso!")
            st.download_button("📄 Baixar PDF", file.read(), file_name=arquivo_pdf, mime="application/pdf")
        os.remove(arquivo_pdf)
    else:
        st.error("⚠️ Preencha todos os campos obrigatórios antes de gerar o orçamento.")
