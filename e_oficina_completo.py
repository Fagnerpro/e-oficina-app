
import streamlit as st
import sqlite3
from fpdf import FPDF
import os
from datetime import datetime

st.set_page_config(page_title="E-OFICINA - Diagnóstico e Orçamento", layout="centered")

# Banco de dados local
conn = sqlite3.connect("e_oficina.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS atendimentos (    id INTEGER PRIMARY KEY AUTOINCREMENT,    cliente TEXT,    telefone TEXT,    modelo TEXT,    ano INTEGER,    km INTEGER,    sintomas TEXT,    diagnostico TEXT,    data_atendimento TEXT)")
conn.commit()

# Interface do usuário
st.title("🔧 E-OFICINA")
st.subheader("Módulo 1: Diagnóstico Assistido e Orçamento Inteligente")

st.markdown("### 📋 Cadastro do Cliente e Veículo")
cliente = st.text_input("Nome do Cliente")
telefone = st.text_input("Telefone de Contato")
modelo = st.text_input("Modelo do Veículo")
ano = st.number_input("Ano do Veículo", min_value=1990, max_value=2030, step=1)
km = st.number_input("Quilometragem Atual (km)", min_value=0)
sintomas = st.text_area("Descreva os sintomas observados ou relatados pelo cliente")

# Diagnóstico simulado
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
    pdf.ln(10)
    for chave, valor in dados.items():
        pdf.multi_cell(0, 10, f"{chave}: {valor}")
    nome_arquivo = f"orcamento_{dados['Cliente'].replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# Botão de gerar orçamento
if st.button("Gerar Orçamento e Salvar"):
    if cliente and modelo and sintomas:
        data = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO atendimentos (cliente, telefone, modelo, ano, km, sintomas, diagnostico, data_atendimento) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (cliente, telefone, modelo, ano, km, sintomas, diagnostico, data))
        conn.commit()

        dados = {
            "Cliente": cliente,
            "Telefone": telefone,
            "Veículo": f"{modelo} - {ano}",
            "KM Atual": km,
            "Sintomas": sintomas,
            "Diagnóstico": diagnostico,
            "Data": data
        }

        arquivo_pdf = gerar_pdf(dados)
        with open(arquivo_pdf, "rb") as file:
            st.download_button("📄 Baixar Orçamento em PDF", file.read(), file_name=arquivo_pdf, mime="application/pdf")
        os.remove(arquivo_pdf)
    else:
        st.error("Preencha todos os campos obrigatórios para gerar o orçamento.")
