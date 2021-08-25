import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import webbrowser


df = pd.read_csv('https://raw.githubusercontent.com/colmr/vis_class/master/FakeAccomodationDetails.csv')

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server


color = {'B & B': '#e48900',
         'Hotel': '#5aa469',
         'Self Catering': '#8ab6d6',
         'Hostel':'#f8a1d1',
         'Camping':'#2978b5'}

def update_bar(df):
    fig = go.Figure()
    for type in df['Type'].unique():
        df_by_Type = df[df['Type']==type]
        df_by_Type.sort_values('Capacity',inplace=True)
        fig.add_trace(go.Histogram({
                              'x':df_by_Type['Capacity'],
                              'y':df_by_Type['AddressRegion'],
                              'orientation':'h',
                              'name':type,
                              'marker':{'color':color[type]},
                              # 'cumulative':{'enabled':True,'direction':'decreasing'}
                              # 'histfunc':'count'
        }))

    fig.update_layout(barmode='stack',height=900)
    fig.update_yaxes(categoryorder='category descending')
    fig.update_xaxes(title_text='Total Accommodations')

    return fig

def update_map(df):
    traces = []

    for type in df['Type'].unique():
        df_by_Type = df[df['Type']==type]
        traces.append(go.Scattermapbox(
        lat=df_by_Type['Latitude'],
        lon=df_by_Type['Longitude'],
        mode='markers',
        customdata=df.loc[:, ['Type','Telephone','Url']],
        hovertemplate="<b>%{text}</b><br><br>" +"Type: %{customdata[0]}<br>" +"Telephone: %{customdata[1]}<br>"+ "<extra></extra>",
        showlegend=True,
        marker=go.scattermapbox.Marker(
                size=10,
                color=color[type]
                ),
        text=df['Name'],
        name = type
        ))

    return {'data': traces,
             'layout': go.Layout(hovermode='closest',
              height= 900,
              mapbox=dict(
                  accesstoken='pk.eyJ1IjoidGVjaGNvdWciLCJhIjoiY2tubHNvdHQ0MGtydzJwbW9mbnM0MWFwayJ9.RD-w9fF-rCw4RqSjwbfDVA',
                  bearing=0,
             center=go.layout.mapbox.Center(
                        lat=53.350140,
                        lon=-6.266155
                ),
            pitch=0,
            zoom=6
        ))}


app.layout = dbc.Container([
        html.Div([
          html.H1(['Exploring Irish Accommodations'],style={'text-align':'center'}),
          html.Hr()
        ]),
        dbc.Row(
            [
                dbc.Col(
                    [
                     html.Label(['Select Region'],style={'font-weight':'bold'}),
                     dcc.Dropdown(id='region-dropdown',
                                  options=[{'label':i,'value':i} for i in df['AddressRegion'].unique()],
                                  multi= True

                     )
                    ]
                ),
                dbc.Col(
                    [
                     html.Label(['Select Popularity'],style={'font-weight':'bold'}),
                     dcc.Dropdown(id='popularity-dropdown',
                                  options=[{'label':i,'value':i} for i in df['Popularity'].unique()],
                                  multi= True
                     )
                    ]
                ),
                dbc.Col(
                    [
                    html.Div(
                            [
                            dbc.Button('Submit', id='submit-button', color='primary', className='mr-1')
                            ],style={'margin-top':'30px'}
                    )
                    ]
                )

            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                [
                  html.Div([
                  dcc.Graph(id = 'graph',figure=update_map(df))
                  ])
                ],md=8
               ),
               dbc.Col(
               [
                  html.Div([
                  dcc.Graph(id = 'graph-1',figure=update_bar(df))
                  ])
               ],md=4
               ),
               dbc.Col(
                       [
                       html.Div(id='hidden-div')
                       ],style={'display':'none'}
               )
            ]
        ),
],fluid=True)

@app.callback([Output('graph','figure'),Output('graph-1','figure')],
             [Input('submit-button','n_clicks')],
             [State('region-dropdown','value')],
             [State('popularity-dropdown','value')])

def update_graph(n_clicks,region,popularity):
    fig = go.Figure()
    frames = []
    traces = []
    for region_name in region:
        for popular in popularity:
            frames.append(df[(df['AddressRegion']==region_name) & (df['Popularity']==int(popular))])
    df_filtered = pd.concat(frames,ignore_index=True)
    return [update_map(df_filtered), update_bar(df_filtered)]


@app.callback(
              Output('hidden-div','children'),
              Input('graph','clickData')

)
def click_data(data):
    if data:
        list1 = data['points']
        list_customdata = list1[0]['customdata']
        link = list_customdata[2]
        if link is not None:
            return webbrowser.open(link)
    return ""


if __name__ == '__main__':
    app.run_server()
