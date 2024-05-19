import numpy as np
import pandas as pd
import datetime as dt 
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import yfinance as yf
from keras.models import load_model
import streamlit as st
from sklearn.preprocessing import MinMaxScaler 
import time

# Function to download stock data
def download_stock_data(start, end, user_ip):
    stock_data = yf.download(user_ip, start=start, end=end)
    return stock_data

# Function to display data description with a table
def display_data_description(df):
    st.subheader('Stock Price Data from Jan 2010 - Nov 2023',divider='rainbow')
    # st.write(df.describe(percentiles=[0.25, 0.75], include='all'))
    st.table(df.describe(percentiles=[0.25, 0.75], include='all'))

# Function to plot Moving Average chart
def plot_ma_chart(df, ma_values):
    st.subheader(f'Closing Price Vs Time Chart with {ma_values} days MA', divider='rainbow')
    st.caption(f"The following graph shows the Closing Price vs Time Chart with a {ma_values} Moving Average (MA), which is a graphical representation of a financial instrument's closing prices over time, accompanied by a smoothed line that represents the average closing price over the past {ma_values} days. It helps identify trends and potential reversals, aiding analysts and traders in making informed decisions based on longer-term market movements.")
    ma_list = [df.Close.rolling(ma).mean() for ma in ma_values]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.Close, color='blue', label='Closing Price')
    for i, ma in enumerate(ma_list):
        ax.plot(ma, label=f'{ma_values[i]} days MA')


    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# Function to split data into training and testing sets
def split_data(df):
    data_training = pd.DataFrame(df['Close'][0:int(len(df)*0.70)])
    data_testing = pd.DataFrame(df['Close'][int(len(df)*0.70):int(len(df))])
    return data_training, data_testing

# Function to scale data
def scale_data(data):
    Scaler = MinMaxScaler(feature_range=(0, 1))
    return Scaler.fit_transform(data), Scaler

# Function to load LSTM model
def load_lstm_model(model_path):
    return load_model(model_path)

# Function to prepare test data for LSTM model
def prepare_test_data(data_training, data_testing, Scaler):
    past_100_days = data_training.tail(100)
    final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
    input_data = Scaler.transform(final_df)
    x_test = [input_data[i-100:i] for i in range(100, input_data.shape[0])]
    y_test = [input_data[i, 0] for i in range(100, input_data.shape[0])]
    return np.array(x_test), np.array(y_test)

# Function to make predictions using the LSTM model
def make_predictions(model, x_test, Scaler):
    y_predicted = model.predict(x_test)
    scaler = Scaler.scale_
    scale_factor = 1/scaler[0]
    return y_predicted * scale_factor

# Function to plot Predictions vs Original Values
def plot_predictions_vs_original(y_test, y_predicted):
    st.subheader('Predictions Vs Original Value Plot', divider='rainbow')
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(y_test, 'g', label='Original Values')
    ax.plot(y_predicted, 'r', label='Predicted Values')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# Main Streamlit App
st.title('Stock Market Prediction Web App')
start = dt.datetime(2010, 1, 1)
end = dt.datetime(2023, 11, 30)
st.table_width = 100
user_ip = st.text_input('Enter your Stock Ticker', 'TSLA')


stock_info = yf.Ticker(user_ip).info
company_name = stock_info.get('longName', 'Company Name Not Available')
st.subheader(f'Company Name: ', divider='rainbow')
st.write(f'{company_name}')

with st.spinner('Loading libraries...'):
    time.sleep(0.1)

with st.spinner('Making table...'):
    df = download_stock_data(start, end, user_ip)
    display_data_description(df)

with st.spinner('Plotting Moving averages...'):
    time.sleep(1.5)
    plot_ma_chart(df, [100])
    plot_ma_chart(df, [100, 200])
    plot_ma_chart(df, [100, 200, 300])

with st.spinner('Preparing predictions...'):
    time.sleep(1)
    data_training, data_testing = split_data(df)
    data_training_array, Scaler = scale_data(data_training)
    x_test, y_test = prepare_test_data(data_training, data_testing, Scaler)

model = load_model('Keras_LSTM_Model.keras')
#model_path = 'Keras_LSTM_Model.keras'
#model = load_lstm_model(model_path)
#y_predicted = make_predictions(model, x_test, Scaler)

 #Testing Part
past_100_days = data_training.tail(100)
final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
input_data=Scaler.fit_transform(final_df)

x_test=[]
y_test=[]

for i in range (100, input_data.shape[0]):
    x_test.append(input_data[i-100:i])
    y_test.append(input_data[i,0])

x_test, y_test= np.array(x_test), np.array(y_test)

# Making Preditciton for the Real Time Data

y_predicted=model.predict(x_test)
scaler= Scaler.scale_
scale_factor= 1/scaler[0]
y_predicted = y_predicted * scale_factor
y_test=y_test* scale_factor
   


with st.spinner('Plotting predictions...'):
    time.sleep(2)
    #plot_predictions_vs_original(y_test, y_predicted)

    # Plotting the Predictions Vs Original Value Plot
    st.subheader(f'LSTM Predictions Vs Original Value Plot for {company_name}', divider='rainbow')
    st.caption("The Predictions vs Original Value Plot for the generated LSTM (Long Short-Term Memory) model illustrates the model's performance by comparing its predicted values against the actual/original values over a given dataset. The plot displays a blue line representing the original values and another green line representing the predicted values generated by the LSTM model. It helps visually assess how well the model captures the patterns and trends in the data, with close alignment indicating accurate predictions.")
    fig2 = plt.figure(figsize=(12,6))
    plt.plot(y_test,'b', label='Original Values')
    plt.plot(y_predicted,'g', label='Predicted Values')
    plt.xlabel=('TIME')
    plt.ylabel=('PRICE')
    plt.legend()
    st.pyplot(fig2)
