import gspread
from datetime import timedelta
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import plotly.io as pio

# === 1. Conectar ao Google Sheets ===
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', scope) #Gerar arquivo credenciais.json no google cloud
client = gspread.authorize(creds)

# Nome ou ID da planilha
spreadsheet_id = "ID da SpreadSheet aqui"  # o ID da URL da planilha
sheet = client.open_by_key(spreadsheet_id).sheet1

# === 2. Obter os dados ===
headers = ['TAREFAS', 'DATA INICIO', 'DATA DE TÉRMINO', 'DURAÇÃO', 'RESPONSÁVEL', 'DESCRIÇÃO'] #colunas esperadas, se estivar utilizando uma tabela diferente é necessário modificar, o mesmo para as informações abaixo
data = sheet.get_all_records(expected_headers=headers) 
df = pd.DataFrame(data)

# Mostrar colunas reais
print(df.columns)

# Converter datas
df['DATA INICIO'] = pd.to_datetime(df['DATA INICIO'], dayfirst=True) 
df['DATA DE TÉRMINO'] = pd.to_datetime(df['DATA DE TÉRMINO'], dayfirst=True)

# Criar uma coluna que une tarefa + responsável para tooltip
ordem_tarefas = df['TAREFAS'].tolist()
df['TAREFAS'] = pd.Categorical(df['TAREFAS'], categories=ordem_tarefas, ordered=True)

# Criar gráfico de Gantt
fig = px.timeline(
    df,
    x_start='DATA INICIO',
    x_end='DATA DE TÉRMINO',
    y='TAREFAS',
    color='RESPONSÁVEL',
    hover_name='TAREFAS',
    hover_data={'DATA INICIO': True, 'DATA DE TÉRMINO': True, 'DURAÇÃO': True, 'DESCRIÇÃO': True, 'RESPONSÁVEL': False},
    title='Cronograma de Tarefas - Projeto',
    labels={'TAREFAS': 'Tarefas', 'RESPONSÁVEL': 'Responsável'}
)

# Inverter eixo Y para ordem cronológica
fig.update_yaxes(categoryorder='array', categoryarray=ordem_tarefas, autorange='reversed')

fig.update_xaxes(
    tickformat="%d/%m",
    showgrid=True,          # Linhas verticais
    gridcolor="lightgray",
    gridwidth=1,
    linecolor="black",
    mirror=True
)

# Formata eixo Y
fig.update_yaxes(
    showgrid=True,          # Linhas horizontais
    gridcolor="lightgray",
    gridwidth=1,
    linecolor="black",
    mirror=True
)

#layout 800x1700
fig.update_layout(
    height=800,
    width=1700,
    margin=dict(l=80, r=80, t=80, b=80),
    plot_bgcolor="white"
)

#layout personalizado
fig.update_yaxes(autorange="reversed")
for _, row in df.iterrows():
    tarefa = row['TAREFAS']
    data_inicio = row['DATA INICIO']
    data_termino = row['DATA DE TÉRMINO']

    data_inicio_str = data_inicio.strftime("%d/%m")
    data_termino_str = data_termino.strftime("%d/%m")

    # Caixinha ANTES da barra (data de início)
    fig.add_annotation(
        x=data_inicio - timedelta(days=1),  # 1 dia antes
        y=tarefa,
        text=data_inicio_str,
        showarrow=False,
        xanchor='right',
        yanchor='middle',
        font=dict(size=10, color="black"),
        bgcolor='white',
        bordercolor='gray',
        borderwidth=1,
        opacity=0.8
    )

    # Caixinha DEPOIS da barra (data de término)
    fig.add_annotation(
        x=data_termino + timedelta(days=1),  # 1 dia depois
        y=tarefa,
        text=data_termino_str,
        showarrow=False,
        xanchor='left',
        yanchor='middle',
        font=dict(size=10, color="black"),
        bgcolor='white',
        bordercolor='gray',
        borderwidth=1,
        opacity=0.8
    )
# Mostrar gráfico
pio.renderers.default = 'browser'
fig.show()
