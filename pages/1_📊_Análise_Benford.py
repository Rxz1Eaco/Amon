import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


st.title("📊 Análise com a Lei de Benford")

# Leitura dos dados
df = pd.read_csv('despesasPorOrgao.csv', 
                    sep=';', 
                    engine='python')

st.write(df)

# --- Pré-processamento dos valores ---
valores = df['Valor Empenhado'].dropna().astype(str)
valores = valores.str.replace(' ', '', regex=False)   # remove espaços
valores = valores.str.replace('.', '', regex=False)   # remove separador de milhar
valores = valores.str.replace(',', '.', regex=False)  # substitui vírgula decimal
valores = valores.str.replace('-', '', regex=False)   # remove negativos

# Converter para float e manter só positivos
valores = pd.to_numeric(valores, errors='coerce')
valores = valores.dropna()
valores = valores[valores > 0]

# --- Extração do primeiro dígito ---
primeiro_digito = valores.astype(str).str.replace('.', '').str.replace(',', '').str[0].astype(int)

primeiro_digito = primeiro_digito[primeiro_digito != 0] # Remover zeros iniciais (Lei de Benford não considera 0)

# Frequência observada (forçando todos os dígitos de 1 a 9)
frequencia = primeiro_digito.value_counts().sort_index()
frequencia = frequencia.reindex(range(1,10), fill_value=0)  # adiciona dígitos faltantes
frequencia_percent = frequencia / frequencia.sum() * 100

# Frequência teórica (Benford)
benford = {1:30.1, 2:17.6, 3:12.5, 4:9.7, 5:7.9, 6:6.7, 7:5.8, 8:5.1, 9:4.6}

# --- Plotagem ---
# --- Plotagem ---
fig, ax = plt.subplots(figsize=(6,3),facecolor="black")  # fundo da figura
ax.set_facecolor("black")  # fundo da área do gráfico

bars = ax.bar(frequencia_percent.index, frequencia_percent.values, alpha=0.7, label='Dados reais')
ax.plot(list(benford.keys()), list(benford.values()), 
        color='green', marker='o', linestyle='dashed', label='Lei de Benford')

# Adicionar valores em cima de cada barra
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 0.5, 
            f'{height:.1f}%', ha='center', va='bottom', fontsize=8, color="white")

ax.set_xticks(range(1,10))  # garante que o eixo x vai de 1 a 9
ax.set_xlabel('Primeiro dígito', color="white")
ax.set_ylabel('Porcentagem (%)', color="white")
ax.set_title('Lei de Benford - Valor Empenhado', color="white")
ax.tick_params(colors="white")
ax.legend(facecolor="black", edgecolor="white", labelcolor="white")

st.pyplot(fig)

st.markdown('''
#### Coluna escolhida: Valor Empenhado

✔ Valores financeiros positivos e contínuos.  ''')

st.markdown('''
#### Comparação com a Lei de Benford:

- **Barras azuis** → frequência real dos dígitos  
- **Linha verde** → frequência teórica esperada  
''')


st.subheader("📋 Frequências Comparativas")
# --- DataFrame comparativo ---
comparacao = pd.DataFrame({
    "Dígito": range(1,10),
    "Frequência Observada (%)": frequencia_percent.values.round(2),
    "Frequência Benford (%)": [benford[d] for d in range(1,10)]
})

comparacao['Diferença Frequência'] = comparacao['Frequência Benford (%)'] - comparacao['Frequência Observada (%)']

st.dataframe(comparacao, use_container_width=True)

st.markdown("""
#### 📌 Cálculo do MAD (Mean Absolute Deviation)

O **MAD** mede a média das diferenças absolutas entre a frequência observada e a frequência teórica da Lei de Benford. Quanto maior o MAD, mais os dados se desviam da Lei de Benford.

**Fórmula:**

$$
MAD = \\frac{1}{n} \\sum_{i=1}^{n} |O_i - E_i|
$$

- \\(O_i\\) → Frequência observada do dígito \\(i\\) (%)
- \\(E_i\\) → Frequência esperada pelo Benford do dígito \\(i\\) (%)
- \\(n = 9\\) dígitos (1 a 9)
""")

st.write('')
# Cálculo do MAD

mad = comparacao['Diferença Frequência'].abs().mean()
# Exibição do MAD
st.markdown(f"**MAD {mad:.2f}**%")

# Interpretação usando if
if mad < 0.6:
    st.success("✅ Excelente aderência à Lei de Benford: os dados parecem confiáveis.")
elif mad < 1.5:
    st.warning("⚠️ Boa aderência, mas há pequenas divergências nos dígitos.")
elif mad < 3:
    st.warning("⚠️ Atenção: divergências significativas nos dígitos, revisar os dados.")
else:
    st.error("❌ Possível anomalia ou fraude nos dados, investigar imediatamente!")

