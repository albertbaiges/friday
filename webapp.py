import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

app.layout = html.Div(
    children = [
        dcc.Textarea(id = "keyword"), 
        dcc.Textarea(id = "n_tweets"),
        html.Button('Submit', id='submit', n_clicks=0),
        html.Div(
            id = "spam_holder"
        )
    ]
)

@app.callback(
    Output(component_id = "spam_holder", component_property = "children"), # Display spam counter
    [
        Input(component_id = "submit", component_property  = "n_clicks") 
    
    ],
    [
        State(component_id = "keyword", component_property  = "value"),
        State(component_id = "n_tweets", component_property  = "value")
    ]
)
def performAnalisis(n_clicksButton, keyword, n_tweets):
    if n_clicksButton == 0:
        raise dash.exceptions.PreventUpdate
    print(keyword, n_tweets)
    return html.H1('You have entered: \n{}'.format(keyword))

if __name__ == '__main__':
    app.run_server(debug=False)