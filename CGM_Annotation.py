#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import base64
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import plotly.graph_objs as go
from datetime import datetime


# In[ ]:


app = dash.Dash(__name__)

server = app.server

fig = go.Figure()
fig.update_layout(height = 700, width = 1200, title='Click points on the line to annotate and re-click to undo', title_font=dict(size=20), title_x=0.5, title_y=0.95)
fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="CGM", line=dict(color='black', width=3)))  # Line color and width modified

fig.add_trace(go.Scatter(x=[], y=[], mode="markers", name="Label", showlegend=False, marker=dict(symbol='circle', color='blue', size=10)))  # Marker size modified

fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="Start meal",
                         showlegend=True, marker=dict(symbol='circle', color='red', size=10)))  # Marker size and color modified for Start meal
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="Peak",
                         showlegend=True, marker=dict(symbol='circle', color='blue', size=10)))  # Marker size and color modified for Peak
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="Certainty: Yes",
                         showlegend=True, marker=dict(symbol='circle', color='black', size=10)))  # Marker size and color modified for Certainty: Yes
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="Certainty: No",
                         showlegend=True, marker=dict(symbol='circle-open', color='black', size=10)))  # Marker size and color modified for Certainty: No

fig.update_xaxes(title='Timestamp', rangeslider=dict(visible=True), title_font=dict(size=20))  # Add rangeslider for scrolling
fig.update_yaxes(title='Glucose level', title_font=dict(size=20))
fig.update_layout(uirevision='constant')
fig.data[1].x = []
fig.data[1].y = []



# Update marker properties for the rangeslider
fig.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True,
        ),
        rangeselector=dict(
            buttons=[]
        ),
    ),
)
instructions_text = '''
    Here are the instructions for using this program:
    
    Step 1: Upload first CGM file with at leaast one column of timestamps and another with glucose values. Choose corresponding columns from dropdown options.
    
    Step 2: (Optional) Upload second file with automated or predetermined points from your first file with a column titled 'Timestamp', another titled 'Glucose'
    and another titled 'Label' containing the labels 'Start meal' or 'Peak' 
    
    Step 3: Adjust the slider below plot to view the desired range of the plot. 
    
    Step 4: Annotate points by clicking points on the line! Use Label and Certainty dropdowns to determine labels. Reclick on points to remove them.
    
    Step 5: When you finish annotationg, enter a file name and click save file! 
    
    Enjoy using the program!
'''

# Callback to show/hide instructions text
@app.callback(
    dash.dependencies.Output('instructions', 'style'),
    dash.dependencies.Input('instructions-button', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_instructions(n_clicks):
    if n_clicks % 2 == 1:
        return {'display': 'block'}  # Show the instructions Div
    else:
        return {'display': 'none'}   # Hide the instructions Div


params = ['Timestamp', 'Glucose', 'Label', 'Certainty']

@app.callback(
    Output('upload-data', 'style'),
    Output('upload-data-2', 'style'),
    Input('plot', 'clickData'),
    prevent_initial_call=True
)
def hide_upload_options(click_data):
    if click_data is not None:
        # If points are plotted, hide the upload options
        return {'display': 'none'}, {'display': 'none'}
    else:
        # If no points are plotted, keep the upload options visible
        return {'width': '300px', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'}, {'width': '300px', 'height': '60px',
                'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px'}


app.layout = html.Div([
    html.H1("CGM Annotation", style={'text-align': 'center'}),
    
    # Add the instructions button
    html.Button('Instructions', id='instructions-button', n_clicks=0, style={'margin': '10px'}),

    # Add a Div to display the instructions text as Markdown
    dcc.Markdown(id='instructions', children=instructions_text, style={'display': 'none'}),


    dcc.Upload(
        id='upload-data',
        children=html.Div(['Upload First CGM ', html.A('File')]),
        style={
            'width': '300px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),

    dcc.Upload(
        id='upload-data-2',
        children=html.Div(['Upload Second File ', html.A('(Optional)')]),
        style={
            'width': '300px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),

    html.Div(id='overlay-output'),

    html.Div(id='column-dropdowns'),

    html.Div([
        html.Label('Label:'),
        dcc.Dropdown(
            id='label-dropdown',
            options=[
                {'label': 'Start meal', 'value': 'Start meal'},
                {'label': 'Peak', 'value': 'peak'}
            ],
            value='Start meal'
        )
    ]),

    html.Div([
        html.Label('Certainty:'),
        dcc.Dropdown(
            id='certainty-dropdown',
            options=[
                {'label': 'Yes', 'value': 'yes'},
                {'label': 'No', 'value': 'no'}
            ],
            value='yes'
        )
    ]),

        dcc.Graph(id='plot', figure=fig, config={'doubleClick': False, 'scrollZoom': False}),
    html.Div(id='output'),

    dash_table.DataTable(
        id='table',
        columns=[{'id': p, 'name': p} for p in params],
        data=[],
        editable=True
    ),

    html.Div([
        html.Button('Save File', id='save-button', n_clicks=0, style={'margin': '10px'}),
        dcc.Input(
            id='filename-input',
            type='text',
            placeholder='Enter file name...',
            style={'margin': '10px'}
        )
    ]),

    dcc.Download(id='download-data')
])

labels = []
certainty = []
counter = []

@app.callback(
    Output('column-dropdowns', 'children'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)

def create_dropdowns_from_excel(excel_file):
    content_type, content_string = excel_file.split(',')
    decoded = base64.b64decode(content_string)

    df = pd.read_excel(decoded)
    column_options = [{'label': col, 'value': col} for col in df.columns]

    return [
        html.Label('Select timestamp column:'),
        dcc.Dropdown(
            id='timestamp-column',
            options=column_options
        ),

        html.Label('Select glucose column:'),
        dcc.Dropdown(
            id='glucose-column',
            options=column_options
        )
    ]

@app.callback(
    [Output('plot', 'figure'), Output('table', 'data')],
    [Input('upload-data', 'contents'), Input('upload-data-2', 'contents'), Input('plot', 'clickData'), Input('timestamp-column', 'value'), Input('glucose-column', 'value')],
    [State('plot', 'figure'), State('label-dropdown', 'value'), State('certainty-dropdown', 'value')],
    prevent_initial_call=True
)
def plot_points_from_excel(excel_file, excel_file_2, clk_data, timestamp_col, glucose_col, figure, label_value, certainty_value):
    global labels, certainty, counter

    content_type, content_string = excel_file.split(',')
    decoded = base64.b64decode(content_string)
    
    df = pd.read_excel(decoded)

    pre_x_values = df[timestamp_col].tolist()
    x_values = pd.to_datetime(pre_x_values).strftime('%Y-%m-%d %H:%M')
    y_values = df[glucose_col].round().astype(int)
    num_points_to_show = 96
    initial_start_date = df.iloc[0, 0]
    initial_end_date = df.iloc[num_points_to_show - 1, 0]
    fig.update_xaxes(range=[initial_start_date, initial_end_date])
    fig['data'][0]['x'] = [xs for xs in x_values]
    fig['data'][0]['y'] = [ys for ys in y_values]
    
    if excel_file_2 is not None and len(counter) < 2:
        content_type_2, content_string_2 = excel_file_2.split(',')
        decoded_2 = base64.b64decode(content_string_2)
        df_2 = pd.read_excel(decoded_2)
        pre_x_values_2 = df_2['Timestamp'].tolist()
        x_values_2 = pd.to_datetime(pre_x_values_2).strftime('%Y-%m-%d %H:%M')
        y_values_2 = df_2['Glucose'].round().astype(int)
        fig['data'][1]['x'] = [xs for xs in x_values_2] 
        fig['data'][1]['y'] = [ys for ys in y_values_2]
        labels = df_2['Label'].tolist()
        certainty = ['yes' for _ in x_values_2]
        counter.append(1)
        
        fig['data'][1]['x'] = tuple(fig['data'][1]['x'])
        fig['data'][1]['y'] = tuple(fig['data'][1]['y'])
    
    if clk_data is not None:
        point = clk_data['points'][0]
        x_val = point['x']
        y_val = point['y']
        
        clicked_points = list(zip(list(fig['data'][1]['x']), list(fig['data'][1]['y'])))  # Convert tuple to a list
        
        if (x_val, y_val) in clicked_points:
            # If the point exists, remove it
            index = clicked_points.index((x_val, y_val))
            clicked_points.pop(index)
            labels.pop(index)
            certainty.pop(index)
            fig['data'][1]['x'] = [p[0] for p in clicked_points]  # Update x values
            fig['data'][1]['y'] = [p[1] for p in clicked_points]  # Update y values
        else:
            # If the point doesn't exist, add it
            clicked_points.append((x_val, y_val))
            fig['data'][1]['x'], fig['data'][1]['y'] = zip(*clicked_points)  # Convert back to tuple format
            labels.append(label_value)
            certainty.append(certainty_value)
            
        fig.update_layout(uirevision='constant')
        
    # Determine color based on selected label
    color = ['red' if lab_val == 'Start meal' else 'blue' for lab_val in labels]

    # Determine marker symbol based on selected certainty
    marker_symbol = ['circle' if cer_val == 'yes' else 'circle-open' for cer_val in certainty]

    # Update the markers for all clicked points
    fig['data'][1]['marker']['symbol'] = marker_symbol
    fig['data'][1]['marker']['color'] = color

    #output = html.Div(f"Clicked Point: x={fig['data'][1]['x']}, y={fig['data'][1]['y']}, label={labels}, certainty={certainty}")
        
        
    if len(fig['data'][1]['x']) > 0:
        df2 = pd.DataFrame({
            'Timestamp': fig['data'][1]['x'],
            'Glucose': fig['data'][1]['y'],
            'Label': labels,
            'Certainty': certainty
        })
    else:
        df2 = pd.DataFrame({
            'Timestamp': [],
            'Glucose': [],
            'Label': [],
            'Certainty': []
        })
            
    return fig, df2.to_dict('records')

@app.callback(
    Output("download-data", "data"),
    [Input("save-button", "n_clicks")],
    [State('table', 'data'), State('filename-input', 'value')],
    prevent_initial_call=True
)
def save_file(n_clicks, table_data, file_name):
    if n_clicks < 1 or file_name is None:
        return None
    else:
        df = pd.DataFrame(table_data)
        df_sorted = df.sort_values(by='Timestamp')
        return dcc.send_data_frame(df_sorted.to_excel, f"{file_name}.xlsx", index=False)


# In[ ]:


if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




