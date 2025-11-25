import requests
import calendar
from datetime import datetime, timedelta
import plotly.graph_objects as go

def gerar_grafico(periodo):
    # Converte string MMYYYY para datas reais
    try:
        first_date = datetime.strptime(periodo, "%m%Y")
        last_day = calendar.monthrange(first_date.year, first_date.month)[1]
        last_date = first_date.replace(day=last_day)
    except ValueError:
        print("Formato inválido. Use MMYYYY")
        return None

    # Formata para API do Banco Central
    data_inicial = first_date.strftime("%m-%d-%Y")
    data_final = last_date.strftime("%m-%d-%Y")
    
    url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{data_inicial}'&@dataFinalCotacao='{data_final}'&$format=json"
    
    response = requests.get(url)
    data = response.json()
    
    if 'value' not in data or not data['value']:
        print("Sem dados para o período.")
        return None

    # Processa os dados
    datas, compras, vendas = [], [], []
    cotacoes = {datetime.strptime(x['dataHoraCotacao'], "%Y-%m-%d %H:%M:%S.%f").date(): x for x in data['value']}
    
    current = first_date.date()
    end = last_date.date()
    
    last_valid = None
    
    # Preenchimento de dias vazios (Forward Fill)
    while current <= end:
        if current in cotacoes:
            last_valid = cotacoes[current]
        
        if last_valid:
            datas.append(current)
            compras.append(last_valid['cotacaoCompra'])
            vendas.append(last_valid['cotacaoVenda'])
        
        current += timedelta(days=1)

    # Cria Gráfico Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=datas, y=compras, name='Compra', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=datas, y=vendas, name='Venda', line=dict(color='red')))
    fig.update_layout(title=f"Cotação Dólar - {periodo}", hovermode="x unified")
    
    return fig