import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import dcc, html, Dash

GenData = pd.read_csv("GeneralEsportData.csv")
HistData = pd.read_csv("HistoricalEsportData.csv")

# Change Year variable to date format
HistData['Date'] = pd.to_datetime(HistData['Date'], format='%Y/%m/%d')

# Add timely variables for plotting
HistData['Year'] = HistData['Date'].dt.year
HistData['Month'] = HistData['Date'].dt.month

# Clean up Genre variable in GenData
GenData['Genre'] = GenData['Genre'].str.replace(' Game', '')
GenData['Genre'].replace({
    'Multiplayer Online Battle Arena': 'MOBA',
    'Role-Playing': 'RPG',
    'Third-Person Shooter': 'TPS',
    'First-Person Shooter': 'FPS'
}, inplace=True)

# Print unique genres in GenData
print(GenData['Genre'].unique())

top_5_games = GenData.sort_values(by='TotalEarnings', ascending=False).iloc[:5]
game_names = top_5_games['Game'].apply(
    lambda x: 'CS:GO' if x == 'Counter-Strike: Global Offensive' else ('LoL' if x == 'League of Legends' else x))

# Filter HistData to only include the top 5 games
filtered_data = HistData[HistData['Game'].isin(top_5_games['Game'])]

# Format date column
filtered_data['Date'] = pd.to_datetime(filtered_data['Date'], format='%m/%d/%Y')

# Create subplots
fig1 = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.04)

# Add traces for each game
for i in range(len(game_names)):
    game_data = filtered_data[filtered_data['Game'] == top_5_games.iloc[i]['Game']]
    fig1.add_trace(go.Scatter(x=game_data['Date'], y=game_data['Earnings'], name=game_names.iloc[i], fill='tozeroy',
                              line=dict(width=2)), row=i + 1, col=1)

# Update layout
fig1.update_layout(title='Prize Pool Evolution',
                   xaxis_title='',
                   yaxis=dict(title='In thousands of dollars'),
                   height=500,
                   xaxis=dict(tickformat='%Y'),
                   template=dict(layout=dict(paper_bgcolor='rgb(240, 240, 240)', plot_bgcolor='rgb(240, 240, 240)')),
                   font=dict(family='Arial', size=12))

fig1.update_traces(line=dict(width=2), fillcolor='lightblue', hovertemplate='Earnings: %{y:.2f}')
fig1.update_layout(legend_title_text='', legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1),
                   template='ggplot2',
                   margin=dict(l=0, r=10, t=100, b=0, pad=0))

# Create the scatter plot
fig2 = px.scatter(GenData, x='ReleaseDate', y='TotalEarnings', color='Genre', size='TotalTournaments',
                  hover_name='Game', hover_data=['Game'], size_max=40)
fig2.update_traces(textposition='top center')

# Add pointers to the top 5 earners
top_earnings = GenData.sort_values(by='TotalEarnings', ascending=False).iloc[:5]
for i, game in enumerate(top_earnings['Game']):
    earnings = top_earnings['TotalEarnings'].iloc[i]
    Release_Date = top_earnings['ReleaseDate'].iloc[i]
    fig2.add_annotation(x=Release_Date, y=earnings, text=game,
                        showarrow=True, arrowhead=0, ax=-10, ay=15)

# Customize the layout
fig2.update_layout(title='Total revenue vs release date',
                   xaxis_title='ReleaseDate',
                   yaxis_title='Total Earnings (millions of dollars)',
                   height=500,
                   template='ggplot2',
                   font=dict(family='Arial', size=12))

# Plotting Earnings per year
HistData["Year"] = pd.DatetimeIndex(HistData['Date']).year

# Create two separate traces for the data before and after 2020
trace_1 = go.Bar(
    x=HistData[HistData['Year'] < 2020].groupby('Year')['Earnings'].sum().index,
    y=HistData[HistData['Year'] < 2020].groupby('Year')['Earnings'].sum() / 1E6,
    name='Before 2020'
)

trace_2 = go.Bar(
    x=HistData[HistData['Year'] >= 2020].groupby('Year')['Earnings'].sum().index,
    y=HistData[HistData['Year'] >= 2020].groupby('Year')['Earnings'].sum() / 1E6,
    name='After 2020'
)

fig3 = go.Figure(data=[trace_1, trace_2])

# Create the layout and figure
fig3.layout = go.Layout(
    title='Total revenue per year',
    yaxis=dict(title='In millions of dollars'),
    xaxis=dict(title='Year'),
    barmode='group',
    font=dict(family='Arial', size=12),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    margin=dict(l=50, r=50, t=80, b=50),
    template='ggplot2',
    height=500
)

# Calculate total tournaments per year
tournaments_per_year = HistData.groupby('Year')['Tournaments'].sum().reset_index()

# Add a column to distinguish 2020 data
tournaments_per_year['Condition'] = tournaments_per_year['Year'].apply(lambda x: True if x == 2020 else False)

# Create bar chart
fig4 = go.Figure()
fig4.add_trace(go.Bar(x=tournaments_per_year['Year'], y=tournaments_per_year['Tournaments'],
                      marker=dict(color=tournaments_per_year['Condition'].map({True: 'lightblue', False: 'lightblue'})),
                      text=tournaments_per_year['Tournaments'], textposition='outside',
                      textfont=dict(size=10)))
fig4.update_layout(title='Total Tournaments per year', xaxis_title='Year',
                   yaxis_title='', xaxis=dict(tickvals=[98, 99] + list(range(2000, 2023)),
                                              ticktext=['98', '99'] + list(range(2000, 2023)),
                                              tickangle=0),
                   height=500, template='ggplot2',
                   margin=dict(l=50, r=50, t=100, b=50), plot_bgcolor='rgb(240, 240, 240)',
                   annotations=[dict(x=0.5, y=-0.5, showarrow=False,
                                     xref='paper', yref='paper', font=dict(size=12))])

# Set up the Dash app
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Innovation and Disruption: A History of Gaming Industry Changes'),
    html.P(
        children="This dashboard shows the evolution of the gaming industry over the year including aspects of Total "
                 "revenue, Tournaments, Price award",
        className="header-description"),
    html.Div([
        dcc.Graph(
            id='graph-3',
            figure=fig3,
            style={'display': 'inline-block', 'width': '50%', 'height': '50%'}
        ),
        dcc.Graph(
            id='graph-2',
            figure=fig2,
            style={'display': 'inline-block', 'width': '50%', 'height': '50%'}
        ),
    ]),

    dcc.Graph(
        id='graph-1',
        figure=fig1,
        style={'display': 'inline-block', 'width': '50%', 'height': '50%'}
    ),
    dcc.Graph(
        id='graph-4',
        figure=fig4,
        style={'display': 'inline-block', 'width': '50%', 'height': '50%'},
    ),
], style={'backgroundColor': '#FFBE11'})

if __name__ == '__main__':
    app.run_server(debug=True)
