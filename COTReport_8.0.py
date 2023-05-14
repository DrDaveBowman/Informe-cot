import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime, date
import datetime as dt

class COTAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = pd.read_csv(file_path, low_memory=False)
        self.__display_settings()
        self.create_additional_columns()

    # --------------------------------------- #
    #           BASIC METHODS                  #
    # --------------------------------------- #

    def __display_settings(self):
        pd.options.display.width = None
        pd.options.display.max_columns = None
        pd.set_option('display.max_rows', 10000)
        pd.set_option('display.max_columns', 10000)

    def create_additional_columns(self):

        # Adding Non-Commercial Data:
        self.data["Posiciones Netas NC"] = self.data["NC Long"] - self.data["NC Short"]
        self.data["% Largos NC"] = self.data["NC Long"] / (self.data["NC Long"] + self.data["NC Short"]) * 100
        self.data["% Cortos NC"] = self.data["NC Short"] / (self.data["NC Long"] + self.data["NC Short"]) * 100
        self.data["% Diferencial NC"] = self.data["% Largos NC"] - self.data["% Cortos NC"]
        self.data["% Largos NC"] = self.data["% Largos NC"].apply(lambda x: "{:.2f}%".format(x))
        self.data["% Cortos NC"] = self.data["% Cortos NC"].apply(lambda x: "{:.2f}%".format(x))
        self.data["% Diferencial NC"] = self.data["% Diferencial NC"].apply(lambda x: "{:.2f}%".format(x))

        # Adding Commercial Data:
        self.data["Posiciones Netas Com"] = self.data["Com Long"] - self.data["Com Short"]
        self.data["% Largos Com"] = self.data["Com Long"] / (self.data["Com Long"] + self.data["Com Short"]) * 100
        self.data["% Cortos Com"] = self.data["Com Short"] / (self.data["Com Long"] + self.data["Com Short"]) * 100
        self.data["% Diferencial Com"] = self.data["% Largos Com"] - self.data["% Cortos Com"]
        self.data["% Largos Com"] = self.data["% Largos Com"].apply(lambda x: "{:.2f}%".format(x))
        self.data["% Cortos Com"] = self.data["% Cortos Com"].apply(lambda x: "{:.2f}%".format(x))
        self.data["% Diferencial Com"] = self.data["% Diferencial Com"].apply(lambda x: "{:.2f}%".format(x))

        # Adding Retail Data:
        self.data["Posiciones Netas Retail"] = self.data["Retail Long"] - self.data["Retail Short"]
        self.data["% Largos Retail"] = self.data["Retail Long"] / (
                    self.data["Retail Long"] + self.data["Retail Short"]) * 100
        self.data["% Cortos Retail"] = self.data["Retail Short"] / (
                    self.data["Retail Long"] + self.data["Retail Short"]) * 100
        self.data["% Diferencial Retail"] = self.data["% Largos Retail"] - self.data["% Cortos Retail"]
        self.data["% Largos Retail"] = self.data["% Largos Retail"].apply(lambda x: "{:.2f}%".format(x))
        self.data["% Cortos Retail"] = self.data["% Cortos Retail"].apply(lambda x: "{:.2f}%".format(x))
        self.data["% Diferencial Retail"] = self.data["% Diferencial Retail"].apply(lambda x: "{:.2f}%".format(x))

        # --------------------------------------- #
        #            COMMERCIALS INDEX            #
        # --------------------------------------- #

        # Calculate the lowest value of "Posiciones Netas Com" of the previous 156 values
        self.data["Lowest Com"] = self.data["Posiciones Netas Com"].rolling(window=156).min()

        # Calculate the highest value of "Posiciones Netas Com" of the previous 156 values
        self.data["Highest Com"] = self.data["Posiciones Netas Com"].rolling(window=156).max()

        # Calculate the "Índice Com" using the formula provided
        self.data["Índice Com"] = ((self.data["Posiciones Netas Com"] - self.data["Lowest Com"]) /
                                   (self.data["Highest Com"] - self.data["Lowest Com"])) * 100
        self.data["Índice Com"] = self.data["Índice Com"].apply(lambda x: "{:.2f}%".format(x))

        # --------------------------------------- #
        #        OPEN INTEREST STOCHASTIC         #
        # --------------------------------------- #

        # Calculate the lowest value of "OI" of the previous 156 values
        self.data["Lowest OI"] = self.data["OI"].rolling(window=156).min()

        # Calculate the highest value of "OI" of the previous 156 values
        self.data["Highest OI"] = self.data["OI"].rolling(window=156).max()

        # Calculate the "ÍndiceOI" using the formula provided
        self.data["Índice OI"] = ((self.data["OI"] - self.data["Lowest OI"]) /
                                   (self.data["Highest OI"] - self.data["Lowest OI"])) * 100
        self.data["Índice OI"] = self.data["Índice OI"].apply(lambda x: "{:.2f}%".format(x))

        # print(self.data.columns)
        # print(self.data[['OI', "Lowest OI" , "Highest OI", "Índice OI"]])

        # --------------------------------------- #
        #     COM LONG/SHORTS / OPEN INTEREST     #
        # --------------------------------------- #

        self.data["CL/OI"] = (self.data["Com Long"] / self.data["OI"]) * 100
        self.data["CL/OI"] = self.data["CL/OI"].apply(lambda x: "{:.2f}%".format(x))

        self.data["CS/OI"] = (self.data["Com Short"] / self.data["OI"]) * 100
        self.data["CS/OI"] = self.data["CS/OI"].apply(lambda x: "{:.2f}%".format(x))

        print(self.data[['CS/OI', "CL/OI" , "Com Short", "OI", "Com Long"]])

    def plot_data_one_graph(self, start_date=None, end_date=None):
        # Set default start and end dates if not provided
        if start_date is None:
            start_date = pd.to_datetime(self.data['Fecha']).min()
        else:
            start_date = datetime.combine(start_date, datetime.min.time())

        if end_date is None:
            end_date = pd.to_datetime(self.data['Fecha']).max()
        else:
            end_date = datetime.combine(end_date, datetime.min.time())

        # Filter data based on start and end dates
        mask = (
                (pd.to_datetime(self.data['Fecha']) >= start_date) &
                (pd.to_datetime(self.data['Fecha']) <= end_date)
        )
        filtered_data = self.data.loc[mask]

        # Convert dates to "dd-MMM-yy" format
        formatted_dates = pd.to_datetime(filtered_data['Fecha']).dt.strftime('%d %b %y')

        # Create traces
        trace1 = go.Scatter(
            x=formatted_dates,
            y=filtered_data['Cierre'],
            mode='lines',
            name='Cierre',
            yaxis='y2',
            line=dict(color='#F5B14C')
        )

        trace2 = go.Scatter(
            x=formatted_dates,
            y=filtered_data['Posiciones Netas NC'],
            mode='lines',
            name='No Comerciales - Diferencial Largos/Cortos',
            line=dict(color='#47DBCD')
        )

        trace3 = go.Scatter(
            x=formatted_dates,
            y=filtered_data['Posiciones Netas Com'],
            mode='lines',
            name='Comerciales - Diferencial Largos/Cortos',
            line=dict(color='#8C54FF')
        )

        # Set layout options
        layout = go.Layout(
            title='Análisis Informe COT',
            xaxis=dict(title='Fecha'),
            yaxis=dict(title='Datos COT'),
            yaxis2=dict(title='Cierre', overlaying='y', side='right'),
            hovermode='x'
        )

        # Create figure and add traces to it
        fig_data = [trace1, trace2, trace3]
        fig = go.Figure(data=fig_data, layout=layout)

        return fig

def main():
    # Load data
    current_directory = os.path.dirname(os.path.abspath(__file__))
    cleaned_data = os.path.join(current_directory, 'Datos Informe COT.csv')

    cot_analyzer = COTAnalyzer(cleaned_data)

    # Create and run the Streamlit app
    st.title('Informe COT para Fernando')

    # Get user input for date range
    default_start_date = dt.date(2004, 1, 1)  # Default start date is January 1st, 2010
    start_date = st.date_input('Start Date', default_start_date)
    end_date = st.date_input('End Date')

    # Plot data
    fig = cot_analyzer.plot_data_one_graph(start_date, end_date)
    fig.update_layout(height=600, width=1000)  # Adjust chart size
    st.plotly_chart(fig)


if __name__ == '__main__':
    main()
