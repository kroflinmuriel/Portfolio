
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import pandas as pd
import requests
import plotly.express as px
from dash.dependencies import Input, Output
import scipy.stats as stats
import plotly.graph_objects as go
import statsmodels.api as sm
from datetime import datetime


# Fetch data from  the API
response = requests.get('http://127.0.0.1:5000/api/sales')
if response.status_code == 200:
    df = pd.DataFrame(response.json())  # Convert JSON response to DataFrame
else:
    df = pd.DataFrame()  # Empty DataFrame if something goes wrong

df['saledate'] = pd.to_datetime(df['saledate'])  # Convert to datetime
df['month'] = df['saledate'].dt.to_period('M')  # Extract year-month
items_sold_by_month = df.groupby('month')['itemssold'].sum().reset_index()  # Aggregate
items_sold_by_month['month'] = items_sold_by_month['month'].astype(str)
# Aggregate items sold by day
items_sold_by_day = df.groupby('saledate')['itemssold'].sum().reset_index()
items_sold_by_region = df.groupby('region')['itemssold'].sum().reset_index()
# Apply LOWESS smoothing
lowess = sm.nonparametric.lowess(
    items_sold_by_day['itemssold'], 
    items_sold_by_day['saledate'].map(lambda x: x.toordinal()), 
    frac=0.3  # Adjust this for more or less smoothing
)

# Convert LOWESS results to DataFrame
lowess_df = pd.DataFrame(lowess, columns=['saledate_ordinal', 'smoothed'])
lowess_df['saledate'] = lowess_df['saledate_ordinal'].apply(lambda x: datetime.fromordinal(int(x)))

total_days = df['saledate'].nunique()
total_sales = df['itemssold'].sum()
total_products = df['productid'].nunique()

# Find most popular product (by items sold)
most_popular_product = df.groupby('productid')['itemssold'].sum().idxmax()

# Find day with highest sales
day_with_highest_sales = df.groupby('saledate')['itemssold'].sum().idxmax()

# Create Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define About Card content
about_card = """
Welcome ladies and gentlemen! Enjoy these super interesting graphs
"""

# Layout of the app
app.layout = html.Div([
    html.H1("Sales Dashboard by Sehee, Kirsten and Muri",
            style={'backgroundColor': 'gray', 'color': 'white', 'padding': '10px', 'marginBottom': '20px'}),
    
    # Dropdown Menu with About the Team inside a box
     # Welcome message dropdown
    html.Div(
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Welcome Message", header=True),  # Header for dropdown
                dbc.DropdownMenuItem(about_card, id="about-card-content")
            ],
            nav=True,
            in_navbar=True,
            label="Welcome Message",  # Title of the dropdown
            right=True,  # Aligns the dropdown to the right
        ),
        style={
        'border': '2px solid #808080',  # Grey border around the dropdown box
        'borderRadius': '8px',  # Rounded corners
        'padding': '10px 15px',  # Adjusted padding for content
        'margin': '20px',  # Margin around the card
        'backgroundColor': '#f8f9fa',  # Light background color for card
        'width': 'auto',  # Adjusts to fit content
        'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'  # Optional shadow for effect
    }
    ),

    # Summary statistics box (spans full width and shows statistics side by side)
    dbc.Card(
        dbc.CardBody(
            [
                html.H4("Summary Statistics", className="card-title"),

                # Use a row to display the statistics side by side
              dbc.Row([
                        dbc.Col(html.P([html.Strong(f"Total Days: "), total_days]), width=2),
                dbc.Col(html.P([html.Strong(f"Total Sales Value: "), f"{total_sales:,.0f}"]), width=3),
                dbc.Col(html.P([html.Strong(f"Total Products: "), total_products]), width=3),
                dbc.Col(html.P([html.Strong(f"Highest Sales on: "), day_with_highest_sales.strftime('%Y-%m-%d')]), width=3),
                ], justify="start"),

                
            ]
        ),
        style={
        'border': '2px solid #808080',  # Grey border around the dropdown box
        'borderRadius': '8px',  # Rounded corners
        'padding': '10px 10px',  # Adjusted padding for content
        'margin': '20px',  # Margin around the card
        'backgroundColor': '#f8f9fa',  # Light background color for card
        'width': 'auto',  # Adjusts to fit content
        'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'  # Optional shadow for effect
    }
    ),

# Items Sold by Region (Bar chart)
    html.Div([
        html.H3("Items Sold By Region"),
        dcc.Graph(
            figure=go.Figure()
            .add_trace(
                go.Bar(
                    x=items_sold_by_region['region'],
                    y=items_sold_by_day['itemssold'],
                    name="Items Sold",
                    marker_color='darkblue'  # Bars set to dark grey
                )
            )
        .update_layout(
                title="Sales by Region",
                xaxis_title="Region",
                yaxis_title="Items Sold",
                plot_bgcolor="white",  # Background set to white
                paper_bgcolor="white",  # Full graph background set to white
                font=dict(color='black')  # Text color for contrast
            )
        )
    ],
    style={
        'border': '2px solid #808080',  # Grey border around the dropdown box
        'borderRadius': '8px',  # Rounded corners
        'padding': '10px 15px',  # Adjusted padding for content
        'margin': '20px',  # Margin around the card
        'backgroundColor': '#f8f9fa',  # Light background color for card
        'width': 'auto',  # Adjusts to fit content
        'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'  # Optional shadow for effect
    }
    ),
    ## sale over time with smooth line
    html.Div(
    [
        html.H3("Sales Over Time with Smoothed Line"),
        dcc.Graph(
            figure=go.Figure()
            .add_trace(
                go.Bar(
                    x=items_sold_by_day['saledate'],
                    y=items_sold_by_day['itemssold'],
                    name="Items Sold",
                    marker_color='darkblue'  # Bars set to dark grey
                )
            )
            .add_trace(
                go.Scatter(
                    x=lowess_df['saledate'],
                    y=lowess_df['smoothed'],
                    mode='lines',
                    name='Smoothed Line',
                    line=dict(color='black', width=2, dash='solid')  # Smoothed line in black
                )
            )
            .update_layout(
                title="Sales Over Time with Smoothed Line",
                xaxis_title="Date",
                yaxis_title="Items Sold",
                plot_bgcolor="white",  # Background set to white
                paper_bgcolor="white",  # Full graph background set to white
                font=dict(color='black')  # Text color for contrast
            )
        )
    ],
    style={
        'border': '2px solid #808080',  # Grey border around the dropdown box
        'borderRadius': '8px',  # Rounded corners
        'padding': '10px 15px',  # Adjusted padding for content
        'margin': '20px',  # Margin around the card
        'backgroundColor': '#f8f9fa',  # Light background color for card
        'width': 'auto',  # Adjusts to fit content
        'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'  # Optional shadow for effect
    }
    )
])
app.run_server(debug=True)
