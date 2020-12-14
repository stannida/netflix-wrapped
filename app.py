import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_table
import plotly.graph_objects as go
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

style = {
    'background': 'white',
    'color': '#E50914',
    'fontFamily': 'Montserrat',
    'fontSize': '20px',
    'text_color': '#564d4d',
    'second_color': '#94A3BC',
    'third_color': '#C1666B'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv('viewedHistory.csv', sep=';', error_bad_lines=False, engine='python')
df['dateStr'] = pd.to_datetime(df['dateStr'], utc=True)
df_2020 = df[df['dateStr']>'2019-12-31']
df_2019 = df[df['dateStr']<'2020-01-01']
hours_2020 = df_2020.duration.sum()/3600
days_2020 = str(round(hours_2020/24, 2))

df_2020['weekDay'] = df_2020['dateStr'].dt.day_name()
df_2020['weekDayCount'] = df_2020['dateStr'].apply(lambda x: x.weekday())
df_2020['durationM'] = df_2020['duration'].apply(lambda x: x/60)
df_2020['durationH'] = df_2020['duration'].apply(lambda x: x/3600)
weekday = df_2020[['durationM', 'weekDay', 'weekDayCount']].groupby('weekDay').mean().reset_index().sort_values('weekDayCount')
weekday['isWeekend'] = weekday['weekDay'].apply(lambda x: 'yes' if x =='Saturday' or x == 'Sunday' else 'no')
weekday_plot = px.bar(weekday, x="weekDay", y="durationM", color="isWeekend", 
	title="Average number of minutes spent per day of week", labels={'durationM':'Avg. Minutes'}, height=350, width=450,
	color_discrete_map={
                "yes": style['color'], "no": style['second_color']
            })

df_2020['month'] = df_2020['dateStr'].apply(lambda x: x.month)
month = df_2020[['durationH', 'month']].groupby('month').sum().reset_index().sort_values('month')
month_plot = px.line(month, x="month", y="durationH", title='Total number of hours per month', height=350, width=850, 
	color_discrete_sequence=[style['color']], labels={'durationH':'Total hours'})

tv_series_2020 = df_2020[~df_2020['seriesTitle'].isnull()]
n_tv_shows = len(tv_series_2020['seriesTitle'].unique())
tv_series_2020 = tv_series_2020[['seriesTitle', 'durationH']].groupby('seriesTitle').sum().sort_values('durationH', ascending=False).reset_index().round({'durationH': 1})
tv_series_2020.rename(columns={'seriesTitle':'TV show', 'durationH': 'Hours'}, inplace=True)

movies_2020 = df_2020[df_2020['seriesTitle'].isnull()]
n_movies = len(movies_2020)

labels_donut = ['TV Shows', 'Movies']
values_donut = [n_tv_shows, n_movies]

donut = go.Figure(data=[go.Pie(labels=labels_donut, values=values_donut, hole=.5)])
donut.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=15,
                  marker=dict(colors=[style['color'], style['second_color']]))

with open('genres.json') as json_file: 
    genres = json.load(json_file)
genre_df = pd.DataFrame({"Genre":list(genres.keys()), "Quantity":list(genres.values())}).sort_values('Quantity')

genre = px.bar(genre_df,x="Quantity", y="Genre", orientation='h', title='Top genres for TV Shows and Movies', color_discrete_sequence=[style['color']])

# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

weekday_plot.update_layout(
    plot_bgcolor=style['background'],
    paper_bgcolor=style['background'],
    title_font_color=style['text_color'],
    font_color=style['text_color'],
    title_font_size=15,
    font_family=style['fontFamily']
)

month_plot.update_layout(
    plot_bgcolor=style['background'],
    paper_bgcolor=style['background'],
    title_font_color=style['text_color'],
    title_x=0.5,
    font_color=style['text_color'],
    title_font_size=15,
    width=800,
    xaxis = dict(
        tickmode = 'array',
        tickvals = [1,2, 3,4, 5,6, 7,8, 9,10, 11, 12],
        ticktext = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ),
    font_family=style['fontFamily']
)

donut.update_layout(legend=dict(
    yanchor="top",
    y=1.4,
    xanchor="left",
    x=0.35),
    height=450,
    width=450,
    font_family=style['fontFamily'],
    plot_bgcolor=style['background'],
    paper_bgcolor=style['background'],
    )

genre.update_layout(
    plot_bgcolor=style['background'],
    paper_bgcolor=style['background'],
    title_font_color=style['text_color'],
    font_color=style['text_color'],
    title_font_size=15,
    font_family=style['fontFamily'],
    height=500,
    width=460,
)

app.layout = html.Div(style={'backgroundColor': style['background']}, children=[
    html.H1(
        children='Netflix Wrapped',
        style={
            'textAlign': 'center',
            'color': style['color'],
            'fontFamily' :style['fontFamily'],
            'fontWeight': 600

        }
    ),
    html.Div(children=[
    html.Div(children='In 2020 you watched the total of ',style={
        'textAlign': 'right',
        'color': style['color'],
        'fontFamily' :style['fontFamily'],
        'paddingRight' : '10px',
        'fontSize' : style['fontSize'],
        'display' : 'table-cell'

    }),

    html.Div(children=str(round(hours_2020, 2)), style={
        'textAlign': 'left',
        'color': style['color'],
        'fontFamily' :style['fontFamily'],
        'fontWeight': 600,
        'fontSize' : '40px',
        'paddingRight' : '10px',
        'display' : 'table-cell'
    }),

    html.Div(children='hours', style={
        'textAlign': 'left',
        'color': style['color'],
        'fontFamily' :style['fontFamily'],
        'fontSize' : style['fontSize'],
        'display' : 'table-cell'
    })
    ], style={
    	'paddingTop' : '30px',
    	'display': 'table',
    	'margin': 'auto'
    }),

    html.Div(children=[
    html.Div(children='or ', style={
        'textAlign': 'right',
        'color': style['color'],
        'fontFamily' :style['fontFamily'],
        'paddingRight' : '10px',
        'fontSize' : style['fontSize'],
        'display' : 'table-cell'

    }),

    html.Div(children=days_2020, style={
        'textAlign': 'left',
        'color': style['color'],
        'fontFamily' :style['fontFamily'],
        'fontWeight': 600,
        'fontSize' : '40px',
        'paddingRight' : '10px',
        'display' : 'table-cell'
    }),

    html.Div(children='days', style={
        'textAlign': 'left',
        'color': style['color'],
        'fontFamily' :style['fontFamily'],
        'fontSize' : style['fontSize'],
        'display' : 'table-cell'
    })
    ], style={
    	# 'padding-top' : '30px',
    	'display': 'table',
    	'margin': 'auto'
    }),

    html.Div(children=[
    dcc.Graph(
        id='weekday',
        figure=weekday_plot,
        style={'display' : 'table-cell'}
    ),

    dcc.Graph(
        id='month',
        figure=month_plot,
        style={'display' : 'table-cell'}
    )], style={
    	'display': 'table', 'width':'1209px'
    }),

    html.Div(children='What did you watch?',style={
        'textAlign': 'center',
        'color': style['color'],
        'fontFamily' :style['fontFamily'],
        'paddingRight' : '10px',
        'fontSize' : style['fontSize'],

    }),
    html.Div(children=[
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in tv_series_2020.columns],
    data=tv_series_2020[:10].to_dict('records'),
    style_table={'display' : 'table-cell', 'width':'50%', 'paddingLeft':'50px', 'paddingTop':'70px'},
    style_cell={'textAlign': 'center', 'fontFamily' :style['fontFamily'], 'color':style['text_color'], 'border': '1px solid white' },
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 600,
        'color': style['color']
    },
    style_cell_conditional=[
        {'if': {'column_id': 'TV show'},
         'width': '230px'},
        {'if': {'column_id': 'Hours'},
         'width': '100px'},
        
    ]
    ),
    dcc.Graph(
        id='donut',
        figure=donut,
        style={'display' : 'table-cell'}
    ),
    dcc.Graph(
        id='genres',
        figure=genre,
        style={'display' : 'table-cell'}
    ),
    ]
    , style={
        'display': 'table'}
    ),
])

if __name__ == '__main__':
    app.run_server()