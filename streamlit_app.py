import streamlit as st
import pandas as pd
import requests

def coletar_parametros_sisagua(
    uf='RS',
    limit=1000,
    codigo_ibge=None,
    tipo_da_forma_de_abastecimento=None,
    ano=None,
    mes=None,
    parametro=None
):
    url = 'https://apidadosabertos.saude.gov.br/sisagua/vigilancia-parametros-basicos'
    headers = {'accept': 'application/json'}
    offset = 0
    todos_dados = []

    while True:
        params = {
            'uf': uf,
            'limit': limit,
            'offset': offset
        }

        if codigo_ibge:
            params['codigo_ibge'] = codigo_ibge
        if tipo_da_forma_de_abastecimento:
            params['tipo_da_forma_de_abastecimento'] = tipo_da_forma_de_abastecimento
        if ano:
            params['ano'] = ano
        if mes:
            params['mes'] = mes
        if parametro:
            params['parametro'] = parametro

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            st.error(f'Erro na requisição: {response.status_code}')
            break

        dados_json = response.json()
        parametros = dados_json.get('parametros', [])

        if not parametros:
            break

        todos_dados.extend(parametros)
        offset += limit

    return pd.DataFrame(todos_dados)


# ---------- INTERFACE STREAMLIT ----------
st.title("Consulta SISAGUA - Vigilância de Parâmetros Básicos")

# Filtros
uf = st.selectbox("UF", ["RS", "SC", "PR", "SP", "MG", "RJ"], index=0)
codigo_ibge = st.text_input("Código IBGE do Município (opcional)")
forma_abastecimento = st.text_input("Tipo da forma de abastecimento (opcional)")
ano = st.number_input("Ano de referência (opcional)", min_value=2000, max_value=2030, step=1, format="%d")
mes = st.number_input("Mês de referência (opcional)", min_value=1, max_value=12, step=1, format="%d")
parametro = st.selectbox("Parâmetro básico (opcional)", options =  ['Turbidez (uT)', 'Fluoreto (mg/L)', 'Cloro residual livre (mg/L)', 
       'Cor Aparente (uH)', 'Dióxido de Cloro (mg/L)',
       'Cloro residual combinado (mg/L)', 'pH', 'Coliformes totais',
       'Escherichia coli', 'Bactérias Heterotróficas'], index = None)

# Botão para buscar
if st.button("Buscar dados"):
    with st.spinner("Coletando dados..."):
        df = coletar_parametros_sisagua(
            uf=uf,
            codigo_ibge=codigo_ibge if codigo_ibge else None,
            tipo_da_forma_de_abastecimento=forma_abastecimento if forma_abastecimento else None,
            ano=int(ano) if ano else None,
            mes=int(mes) if mes else None,
            parametro=parametro if parametro else None
        )
        df = df[['regional_de_saude', 'municipio',
       'numero_da_amostra', 'motivo_da_coleta',
       'tipo_da_forma_de_abastecimento', 'codigo_forma_de_abastecimento',
       'nome_da_forma_de_abastecimento', 'ano', 'mes',
       'data_da_coleta',
       'procedencia_da_coleta',
       'ponto_de_coleta', 'descricao_do_local', 'zona', 
       'area','local', 'latitude', 'longitude', 'parametro',
       'resultado','providencia']].reset_index(drop=True)
    if not df.empty:
        st.success(f"{len(df)} registros encontrados.")
        st.dataframe(df, hide_index = True)
        st.download_button("Baixar como CSV", df.to_csv(index=False).encode('utf-8'), file_name="dados_sisagua.csv", mime='text/csv')
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
