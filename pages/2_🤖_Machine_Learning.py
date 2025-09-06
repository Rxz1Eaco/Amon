import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

st.title("📊 Análise com a Lei de Benford + Regressão Logística")

# Carregar CSV
df = pd.read_csv('despesasPorOrgao.csv', sep=';', engine='python')
st.write(df)

# Limpeza de dados financeiros
valores = df['Valor Empenhado'].dropna().astype(str)
valores = valores.str.replace(' ', '', regex=False)
valores = valores.str.replace('.', '', regex=False)
valores = valores.str.replace(',', '.', regex=False)
valores = valores.str.replace('-', '', regex=False)

# Converter em float
valores = pd.to_numeric(valores, errors='coerce')
valores = valores.dropna()
valores = valores[valores > 0]

# Extrair primeiro dígito
primeiro_digito = valores.astype(str).str.replace('.', '').str[0].astype(int)

# Frequência observada
freq = primeiro_digito.value_counts(normalize=True).sort_index()

# Frequência esperada Benford
benford = np.array([30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]) / 100
observado = np.array([freq.get(i,0) for i in range(1,10)])

# Criar features = diferenças entre observado e esperado
X_base = np.abs(observado - benford).reshape(1,-1)

# 🔹 Criar dataset maior
X_normais = np.repeat(X_base, 20, axis=0)   # 20 exemplos "normais"
y_normais = np.zeros(20)

X_anomalias = np.repeat(X_base*3, 20, axis=0)  # 20 exemplos "fraudados"
y_anomalias = np.ones(20)

# Concatenar dataset
X_fake = np.vstack([X_normais, X_anomalias])
y_fake = np.concatenate([y_normais, y_anomalias])

# Dividir em treino/teste (garantindo estratificação para ter as 2 classes)
X_train, X_test, y_train, y_test = train_test_split(
    X_fake, y_fake, test_size=0.3, random_state=42, stratify=y_fake
)

# Treinar modelo
modelo = LogisticRegression()
modelo.fit(X_train, y_train)

# Predição
y_pred = modelo.predict(X_test)

# Mostrar gráfico
st.subheader("📈 Comparação Lei de Benford")
fig, ax = plt.subplots(figsize=(10,6))
ax.bar(range(1,10), observado*100, alpha=0.7, label='Dados reais')
ax.plot(range(1,10), benford*100, color='red', marker='o', linestyle='dashed', label='Lei de Benford')
ax.set_xlabel('Primeiro dígito')
ax.set_ylabel('Porcentagem (%)')
ax.set_title('Lei de Benford - Valor Empenhado')
ax.legend()
st.pyplot(fig)

# Resultados da classificação
st.subheader("🤖 Classificação com Regressão Logística")
st.write("Relatório de Classificação:")
st.text(classification_report(y_test, y_pred))

st.write("Matriz de Confusão:")
st.write(confusion_matrix(y_test, y_pred))
