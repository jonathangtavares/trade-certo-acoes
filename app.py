
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Trade Certo Ações")
st.title("Trade Certo Ações")

st.markdown("Esta aplicação analisa ações da B3 com base em critérios de variação, volume e número mínimo de operações.")

# Entradas do usuário
variacao_pct = st.number_input("Variação negativa mínima (%)", value=2.0, min_value=0.1)
volume_minimo = st.number_input("Volume diário mínimo", value=1000000, step=100000)
trades_minimos = st.number_input("Número mínimo de operações", value=10, step=1)

if st.button("Atualizar Dados"):
    ativos_b3 = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "B3SA3.SA", "BBAS3.SA", "ABEV3.SA",
        "WEGE3.SA", "MGLU3.SA", "PETR3.SA", "RENT3.SA", "LREN3.SA", "BBDC4.SA"
    ]

    fim = datetime.now() - timedelta(days=1)
    inicio = fim - timedelta(days=90)
    resultados = []

    for ticker in ativos_b3:
        try:
            df = yf.download(ticker, start=inicio.strftime("%Y-%m-%d"), end=fim.strftime("%Y-%m-%d"))
            df.dropna(inplace=True)
            df = df[df['Volume'] >= volume_minimo]
            df.reset_index(inplace=True)
            operacoes, vitorias, derrotas = 0, 0, 0

            for i in range(1, len(df)):
                fechamento_ant = df.loc[i - 1, 'Close']
                variacao = fechamento_ant - (fechamento_ant * (variacao_pct / 100))
                if df.loc[i, 'Low'] <= variacao:
                    operacoes += 1
                    fechamento_dia = df.loc[i, 'Close']
                    if fechamento_dia > variacao:
                        vitorias += 1
                    else:
                        derrotas += 1

            if operacoes >= trades_minimos:
                taxa_sucesso = (vitorias / operacoes) * 100 if operacoes else 0
                resultados.append({
                    "Ativo": ticker.replace(".SA", ""),
                    "Operações": operacoes,
                    "Com Lucro": vitorias,
                    "Com Prejuízo": derrotas,
                    "Taxa de Sucesso (%)": round(taxa_sucesso, 2)
                })
        except Exception as e:
            st.warning(f"Erro ao processar {ticker}: {e}")

    df_resultado = pd.DataFrame(resultados)
    st.subheader("Resultados da Análise")
    st.dataframe(df_resultado)
