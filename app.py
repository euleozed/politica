import streamlit as st
import pandas as pd
from babel.numbers import format_currency
from streamlit.web.cli import main
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards





st.set_page_config(page_title='Emendas Parlamentares', page_icon=None, layout="centered", initial_sidebar_state="auto")
st.markdown('# App de Emendas Parlamentares')
st.text("O presente aplicativo tem como objetivo resumir valores de emendas parlamentares.")
st.text("Os dados podem ser acessados no Portal da Transparência:")
st.link_button("Portal da Transparência - Site - Download", url='https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares')
                   

df = pd.read_csv('Emendas.csv', sep = ";", encoding = "latin1")
df.info()


def substituir_virgula_por_ponto(valor):
    return float(valor.replace(',', '.'))



df['Valor Empenhado'] = df['Valor Empenhado'].apply(substituir_virgula_por_ponto)
df['Valor Liquidado'] = df['Valor Liquidado'].apply(substituir_virgula_por_ponto)
df['Valor Pago'] = df['Valor Pago'].apply(substituir_virgula_por_ponto)
df['Valor Restos A Pagar Inscritos'] = df['Valor Restos A Pagar Inscritos'].apply(substituir_virgula_por_ponto)
df['Valor Restos A Pagar Cancelados'] = df['Valor Restos A Pagar Cancelados'].apply(substituir_virgula_por_ponto)
df['Valor Restos A Pagar Pagos'] = df['Valor Restos A Pagar Pagos'].apply(substituir_virgula_por_ponto)
df.info()

st.divider()

# Selectbox para o nome do deputado
nome_options = df['Nome do Autor da Emenda'].sort_values().unique()
nome = st.selectbox("Selecione o Nome do Parlamentar", options=nome_options, index=None, placeholder="")

# Filtrando os dados pelo nome do deputado selecionado
df_filtered = df[df['Nome do Autor da Emenda'] == nome]

# Lista de cidades, incluindo a opção "TODOS"
cidade_list = ["TODOS"] + df_filtered['Localidade do gasto'].sort_values().unique().tolist()
cidade = st.selectbox("Cidade", options=cidade_list, index=0, placeholder="")

# Filtragem dos dados de acordo com a seleção de cidade
if cidade == "TODOS":
    df_selection = df_filtered  # Mostra o DataFrame completo filtrado pelo deputado
else:
    df_selection = df_filtered[df_filtered['Localidade do gasto'] == cidade]  # Filtra também pela cidade

# Calculando o valor total empenhado
valor_empenhado = df_selection['Valor Empenhado'].sum()

# ## widget mes
# widget_mes_hom = st.sidebar.multiselect(
#     "Mês da Homologação:",
#     options=df_homologados['mes_homologacao'].sort_values().unique(),
#     default=df_homologados['mes_homologacao'].unique()
# )


# ## dataframe selection
# df_selection = df_homologados.query("ano_homologacao == @widget_ano_hom & mes_homologacao == @widget_mes_hom")

df_selection.info()

col1, col2 = st.columns(2)
# col1
def format_currency_value(value):
    return format_currency(value, 'BRL', locale='pt_BR')
valor_empenhado_f = format_currency_value(valor_empenhado)

if cidade == "TODOS":
    st.metric("Valor Total Empenhado:", value=valor_empenhado_f)
else:
    st.metric("Valor Total Empenhado na Localidade:", value=valor_empenhado_f)
style_metric_cards(background_color= 'rainbow')

# Funções
# Função para formatar valores no padrão brasileiro
def format_brl(val):
    if isinstance(val, (int, float)):
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return val

valor_empenhado_cidade = df_selection.groupby(['Localidade do gasto']).agg(Valor=('Valor Empenhado', 'sum')).sort_values(by='Valor', ascending=False)
valor_empenhado_cidade_formated = valor_empenhado_cidade.applymap(format_brl)
st.subheader("Total Empenhado por Localidade")
st.dataframe(valor_empenhado_cidade_formated, width=1000)

funcao = df_selection.groupby('Nome Função').agg(Valor=('Valor Empenhado', 'sum')).sort_values(by='Valor', ascending=False).reset_index()
funcao_formated = funcao.applymap(format_brl)
st.subheader("Total Empenhado por Área")
st.dataframe(funcao_formated, width=1000, hide_index=True)

valor_empenhado_cidade_funcao = df_selection.groupby(['Localidade do gasto', 'Nome Função']).agg(Valor=('Valor Empenhado', 'sum')).sort_values(by='Valor', ascending=False)
valor_empenhado_cidade_funcao_formated = valor_empenhado_cidade_funcao.applymap(format_brl)
st.subheader("Total Empenhado por Localidade e Área")
st.dataframe(valor_empenhado_cidade_funcao_formated, width=1000)

valor_empenhado_ano = df_selection.groupby('Ano da Emenda').agg(Valor=('Valor Empenhado', 'sum')).reset_index()
fig1 = px.bar(valor_empenhado_ano, x='Ano da Emenda', y="Valor", text_auto="Valor")
fig1.update_layout(
            showlegend=False,
            xaxis_title='Ano',
            yaxis_title='Valor',
            xaxis=dict(
                tickformat='d',
                tickmode='linear',
            ))
fig1.update_traces(texttemplate="%{y:.3s}")
fig1.update_yaxes(tickprefix="R$", ticksuffix="M")  # Prefixo e sufixo
st.subheader('Valores Empenhados por Ano')
st.write(fig1)


