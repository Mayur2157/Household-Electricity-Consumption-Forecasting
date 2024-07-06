from flask import Flask, render_template, request, jsonify
from statsmodels.tsa.arima.model import ARIMAResults
import pandas as pd
import numpy as np

model = ARIMAResults.load('Module 1 ARIMA/arima_model.pkl')

df = pd.read_csv('Module 1 ARIMA/household_power_consumption_days.csv', parse_dates=['datetime'], index_col='datetime')

app = Flask(__name__)

def preprocess_data(data):
    df = pd.DataFrame(data)
    df.columns = ['Global_active_power']
    df['Global_active_power'] = pd.to_numeric(df['Global_active_power'])
    df.index = pd.to_datetime(df.index)
    df = df.resample('D').sum().fillna(0)
    return df

@app.route('/past_data')
def get_past_data():
    return jsonify(df.tail(7).to_dict(orient="list"))

@app.route('/summary')
def get_summary():
    total_consumption = df['Global_active_power'].sum()
    average_daily_consumption = df['Global_active_power'].mean()
    peak_usage_time = df['Global_active_power'].idxmax().strftime('%Y-%m-%d %H:%M:%S')

    summary = {
        'total_consumption': total_consumption,
        'average_daily_consumption': average_daily_consumption,
        'peak_usage_time': peak_usage_time
    }
    return jsonify(summary)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        past_data = df['Global_active_power'].values
        weeks = int(request.json.get('weeks', 1))
        forecast = model.forecast(steps=7 * weeks)
        
        forecast_dict = {"Global_active_power": forecast.tolist()}
        
        appliance_breakdown = {
            "Fridge": (forecast * np.random.uniform(0.1, 0.2)).tolist(),
            "AC": (forecast * np.random.uniform(0.25, 0.35)).tolist(),
            "Lights": (forecast * np.random.uniform(0.05, 0.15)).tolist()
        }
        
        return jsonify({'forecast': forecast_dict, 'appliance_breakdown': appliance_breakdown})
    except Exception as e:
        print("Error occurred during prediction:", str(e))
        return jsonify({'error': 'An error occurred during prediction. Please try again later.'}), 500

@app.route('/historical_data')
def historical_data():
    historical_data = df.to_dict(orient='list')
    return jsonify(historical_data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
