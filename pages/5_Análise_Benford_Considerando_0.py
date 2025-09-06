import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


st.title("📊 Análise com a Lei de Benford")

df = pd.read_csv('despesasPorOrgao.csv', 
                    sep=';', # nforma que o separador de colunas no arquivo é ; (ponto e vírgula), e não a vírgula padrão ,.
                    engine='python') #Pede para o Pandas usar o “motor de leitura” em Python puro.

st.write(df)

# Remover espaços e substituir vírgula por ponto
valores = df['Valor Empenhado'].dropna().astype(str)
valores = valores.str.replace(' ', '', regex=False)  # remove espaços
valores = valores.str.replace('.', '', regex=False)  # remove separador de milhar
valores = valores.str.replace(',', '.', regex=False) # substitui vírgula decimal

# Tratar sinais negativos ou inválidos
valores = valores.str.replace('-', '', regex=False)  # opcional: ignora sinais negativos

# Converter para float
valores = pd.to_numeric(valores, errors='coerce')  # valores inválidos viram NaN
valores = valores.dropna()  # remove NaN
valores = valores[valores > 0]  # mantém apenas positivos


# Extrair o primeiro dígito
primeiro_digito = valores.astype(str).str.replace('.', '').str.replace(',', '').str[0].astype(int)

# Contar frequência dos dígitos
frequencia = primeiro_digito.value_counts().sort_index()
frequencia_percent = frequencia / frequencia.sum() * 100

# Frequência esperada pela Lei de Benford
benford = {1:30.10, 2:17.61, 3:12.49, 4:9.69, 5:7.92, 6:6.69, 7:5.80, 8:5.12, 9:4.59}

fig, ax = plt.subplots(figsize=(6,3))
ax.bar(frequencia_percent.index, frequencia_percent.values, alpha=0.7, label='Dados reais')
ax.plot(list(benford.keys()), list(benford.values()), color='red', marker='o', linestyle='dashed', label='Lei de Benford')
ax.set_xlabel('Primeiro dígito')
ax.set_ylabel('Porcentagem (%)')
ax.set_title('Lei de Benford - Valor Empenhado')
ax.legend()

st.pyplot(fig)

st.markdown('''
#### Coluna escolhida: Valor Empenhado

Porque são valores financeiros positivos e contínuos, adequados para Benford.

''')


st.markdown('''
#### Comparação com a Lei de Benford:

Barras azuis → frequência real dos dígitos

Linha vermelha → frequência teórica da Lei de Benford

''')