import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ======================
# Funções auxiliares
# ======================
def primeira_casa(num):
    """Extrai o primeiro dígito de um número"""
    num = str(num).replace(".", "").replace(",", "").strip()
    for c in num:
        if c.isdigit() and c != "0":
            return int(c)
    return None

def distribuicao_benford():
    """Distribuição esperada pela Lei de Benford"""
    return [np.log10(1 + 1/d) for d in range(1, 10)]

def aplicar_lei_benford(dados):
    """Aplica a Lei de Benford a uma série de valores"""
    primeiros_digitos = dados.apply(primeira_casa).dropna()
    contagem = primeiros_digitos.value_counts().sort_index()
    proporcao = contagem / contagem.sum()
    return proporcao

# ======================
# Streamlit App
# ======================
st.title("🔎 Detecção de Anomalias - Lei de Benford")

# Exemplo: Lendo de CSV local (sem upload do usuário)
# Coloque seu arquivo na pasta `data/`
try:
    df = pd.read_csv("despesasPorOrgao.csv", sep=";", decimal=",")
    st.success("✅ Dados carregados de 'data/despesasPorOrgao.csv'")
except:
    st.warning("⚠️ CSV não encontrado. Usando dados fictícios para demonstração.")
    np.random.seed(42)
    df = pd.DataFrame({
        "Orgão": [f"Orgão {i}" for i in range(1, 51)],
        "Valor": np.random.lognormal(mean=10, sigma=1, size=50)  # simula valores financeiros
    })

st.subheader("📊 Amostra dos Dados")
st.dataframe(df.head())

# Selecionar coluna numérica
colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
coluna_valores = st.selectbox("Selecione a coluna para aplicar a Lei de Benford:", colunas_numericas)

# Aplicar Lei de Benford
proporcao_observada = aplicar_lei_benford(df[coluna_valores])
proporcao_esperada = distribuicao_benford()

# Mostrar tabela
st.subheader("📋 Distribuição Observada x Esperada")
resultado = pd.DataFrame({
    "Dígito": range(1, 10),
    "Observado (%)": (proporcao_observada.reindex(range(1,10), fill_value=0) * 100).round(2),
    "Esperado (%)": (np.array(proporcao_esperada) * 100).round(2)
})
st.dataframe(resultado)

# Gráfico comparativo
st.subheader("📈 Comparação Gráfica")
fig, ax = plt.subplots()
ax.bar(resultado["Dígito"] - 0.2, resultado["Observado (%)"], width=0.4, label="Observado")
ax.bar(resultado["Dígito"] + 0.2, resultado["Esperado (%)"], width=0.4, label="Benford")
ax.set_xlabel("Primeiro Dígito")
ax.set_ylabel("Frequência (%)")
ax.legend()
st.pyplot(fig)
