 E-OFICINA - Módulo 1: Diagnóstico Assistido e Orçamento Inteligente

Este é o primeiro módulo da plataforma **E-OFICINA**, focado em oficinas que realizam atendimento a veículos elétricos. O módulo permite:

- Cadastro de cliente e veículo
- Registro de sintomas observados
- Diagnóstico assistido (simulado)
- Geração de orçamento em PDF
- Armazenamento local em SQLite

## 🚀 Como executar

1. Instale as dependências:
```
pip install -r requirements.txt
```

2. Execute o app localmente com Streamlit:
```
streamlit run e_oficina_completo.py
```

## 📦 Publicação no Streamlit Cloud

Para publicar no Streamlit Cloud:

1. Envie os arquivos `e_oficina_completo.py`, `requirements.txt` e `README.md` para um repositório GitHub.
2. Acesse: [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Conecte seu GitHub e selecione o repositório.
4. Escolha `e_oficina_completo.py` como arquivo principal e clique em "Deploy".
