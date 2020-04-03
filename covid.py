import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
from urllib.request import urlopen
import json

def main():
    df = pd.read_csv('~/Desktop/louisiana-covid19/covid-19-data/us-counties.csv')
    # df['fips'] = df['fips'].fillna(0)
    df = df[~df['fips'].isna()] ## let's just drop N/As
    df['fips'] = df['fips'].apply(lambda x: int(x))
    stateDF = df[df['state'] == 'Louisiana']
    caddoDF = stateDF[stateDF['county'] == 'Caddo']
    # print(caddoDF[['date','county','state','cases','deaths']])

    ## Make graphs
    drillDownChartBuilder(caddoDF)
    stateCaseVizualizer(stateDF,200)
    stateContinuousCaseVizualizer(stateDF,20,["green",'yellow','orange',"red"])
    stateContinuousCaseVizualizer(df,50,['#313695','#74add1','#e0f3f8','#fee090','#f46d43','#a50026'])
    caddoLineChart(caddoDF)

def caddoLineChart(caddoDF):
    currentParish = caddoDF['county'].iloc[[0][0]]
    # fig = px.line(caddoDF, x="date", y="cases", color='county') ## only showed one at a time, so we went from df-wide style to df-long style
    df_long=pd.melt(caddoDF, id_vars=['date'], value_vars=['cases', 'deaths'])
    fig = px.line(df_long, x='date', y='value', color='variable',text='value').update_traces(textposition='top left',textfont_size=12).for_each_trace(lambda t: t.update(name=t.name[9:].capitalize())) 
                #.update_traces(mode='lines+markers').for_each_trace(lambda t: t.update(name=t.name.replace("=",": ")))
    fig.update_layout(
        title="{} Parish Cases and Deaths Overtime".format(currentParish),
        xaxis_title='Date',
        yaxis_title='Number of People',
        ## If I want to disable Automargins
        # width=1500,
        # height=1300,
        font=dict(
            family="Helvetica, monospace",
            size=18,
            color="#7f7f7f")
    )
    fig.show()

def drillDownChartBuilder(df):
    mostRecentDate = df['date'].iloc[[-1][0]]
    currentParish = df['county'].iloc[[0][0]]
    fig1 = go.Figure(data=[\
        go.Bar(name='Cases',x=df['date'],y=df['cases'],text=df['cases'], textposition = 'auto'),
        go.Bar(name='Deaths', x=df['date'],y=df['deaths'],text=df['deaths'], textposition = 'auto')])
    fig1.update_layout(
        title = '{} Parish Statistics as of {}'.format(currentParish, mostRecentDate),
        xaxis_title='Date',
        yaxis_title='Number of People',
        ## If I want to disable Automargins
        # width=1500,
        # height=1300,
        font=dict(
            family="Helvetica, monospace",
            size=18,
            color="#7f7f7f")
    )
    # fig1.update_yaxes(tick0=0, dtick=5) ## five-unit increments per y-axis tick
    fig1.update_layout(barmode='group')
    fig1.show()

def stateCaseVizualizer(df,maxValue):
    ## For colorscale help: https://react-colorscales.getforge.io/
    colorscale = ["#d6f9cf","#b8e5b0","#9ad291","#7cbf76","#5cad66", "#359c57", "#17884c", "#177345",
                "#185f3c","#194a2e", "#163720", "#112414"] # Create a colorscale
    ## Static bins
    # States = ['LA', 'TX', 'MS'] # Specify states of interest > show adjacent states to tell your story, even if they don't contain any data!
    States = ['LA']

    values = df['cases'].tolist() # Read in the values contained within your file
    fips = df['fips'].tolist() # Read in FIPS Codes
    endpts = list(np.linspace(0, maxValue, len(colorscale) - 1)) # Identify a suitable range for your data

    fig = ff.create_choropleth(
        fips=fips, values=values, colorscale=colorscale, show_state_data=True, 
        scope=States, # Define your scope
        font=dict(
            family="Helvetica, monospace",
            size=18,
            color="#7f7f7f"),
        binning_endpoints=endpts, # If your values is a list of numbers, you can bin your values into half-open intervals
        county_outline={'color': 'rgb(15, 15, 55)', 'width': 0.5}, # Customize borders    
        state_outline={'color': 'rgb(15, 15, 55)', 'width': 1}, # Specify your state borders
        legend_title='Number of Cases', title='COVID-19 Cases by Parish'
    )
    fig.show()

def stateContinuousCaseVizualizer(df,bucketValue,colorscalePassed):
    ### Continuous
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    # fig = go.Figure(go.Choroplethmapbox(geojson=counties,locations=df.fips,colorscale='Viridis',zmin=0,zmax=50,z=df.cases)) ## Viridis = dark is good here?
    fig = go.Figure(go.Choroplethmapbox(geojson=counties,locations=df.fips,colorscale=colorscalePassed,zmin=0,zmax=bucketValue,z=df.cases))
    fig.update_layout(mapbox_style='carto-positron',mapbox_center={'lat':30.9843,'lon':-91.9623},mapbox_zoom=5)
    fig.update_layout(margin={'r':0,'t':0,'l':1,'b':0})

    fig.show()

if __name__ == '__main__':
    main()