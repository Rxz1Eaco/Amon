import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ===============================
# Funções auxiliares
# ===============================
def primeira_casa(n):
    """Extrai o primeiro dígito de um número positivo."""
    while n >= 10:
        n //= 10
    return n

def distribuicao_benford():
    """Distribuição teórica da Lei de Benford (1 a 9)."""
    return {d: np.log10(1 + 1/d) for d in range(1, 10)}

# ===============================
# Streamlit App
# ===============================
st.set_page_config(page_title="Análise Lei de Benford", layout="wide")

st.title("🔎 Detecção de Anomalias - Lei de Benford")
st.write("Este painel aplica a Lei de Benford em dados financeiros para verificar possíveis inconsistências.")

# Carregar automaticamente os dados (sem upload)
DATA_PATH = "despesasPorOrgao.csv"
df = pd.read_csv(DATA_PATH, sep=";", decimal=",")  

# Mostrar preview dos dados
st.subheader("📊 Amostra dos Dados")
st.dataframe(df.head())

# Selecionar coluna numérica para aplicar Benford
colunas_numericas = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
coluna_valores = st.selectbox("Selecione a coluna para análise:", colunas_numericas)

# Extrair primeiros dígitos
valores = df[coluna_valores].dropna().astype(float)
valores = valores[valores > 0]  # só positivos
primeiros_digitos = valores.astype(str).str.replace(".", "").str.strip().str[0].astype(int)

# Frequência real
freq_real = primeiros_digitos.value_counts(normalize=True).sort_index()

# Frequência esperada (Benford)
freq_benford = pd.Series(distribuicao_benford())

# ===============================
# Exibir resultados
# ===============================
st.subheader("📈 Comparação com a Lei de Benford")

fig, ax = plt.subplots(figsize=(8, 5), facecolor="black")  # fundo da figura
ax.set_facecolor("black")  # fundo da área do gráfico

ax.bar(freq_real.index, freq_real.values, alpha=0.7, label="Dados Reais")
ax.plot(freq_benford.index, freq_benford.values, "ro-", label="Benford (Teórico)")

ax.set_xlabel("Primeiro Dígito", color="white")
ax.set_ylabel("Frequência Relativa", color="white")

# Deixar ticks e legendas em branco também
ax.tick_params(colors="white")
ax.legend(facecolor="black", edgecolor="white", labelcolor="white")

st.pyplot(fig)


# Mostrar tabela comparativa
st.subheader("📋 Frequências Comparativas")
comparacao = pd.DataFrame({
    "Frequência Real": freq_real,
    "Frequência Benford": freq_benford
}).fillna(0)

st.dataframe(comparacao)

# Conclusão simples
st.subheader("📌 Conclusão Automática")
desvio = abs(comparacao["Frequência Real"] - comparacao["Frequência Benford"]).mean()
if desvio < 0.01:
    st.success("✅ Os dados seguem bem a Lei de Benford (sem indícios fortes de anomalias).")
elif desvio < 0.03:
    st.warning("⚠️ Os dados apresentam pequenas divergências da Lei de Benford.")
else:
    st.error("🚨 Possível anomalia detectada! Os dados se desviam significativamente da Lei de Benford.")
