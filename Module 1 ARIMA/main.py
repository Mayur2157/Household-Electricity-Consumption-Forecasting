import pickle
from math import sqrt
from numpy import split, array
from pandas import read_csv
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot
from statsmodels.tsa.arima.model import ARIMA

def split_dataset(data):
    train, test = data[1:-328], data[-328:-6]
    train = array(split(train, len(train)/7))
    test = array(split(test, len(test)/7))
    return train, test

def evaluate_forecasts(actual, predicted):
    scores = []
    for i in range(actual.shape[1]):
        mse = mean_squared_error(actual[:, i], predicted[:, i])
        rmse = sqrt(mse)
        scores.append(rmse)
    s = 0
    for row in range(actual.shape[0]):
        for col in range(actual.shape[1]):
            s += (actual[row, col] - predicted[row, col])**2
    score = sqrt(s / (actual.shape[0] * actual.shape[1]))
    return score, scores

def summarize_scores(name, score, scores):
    s_scores = ', '.join(['%.1f' % s for s in scores])
    print('%s: [%.3f] %s' % (name, score, s_scores))

def evaluate_model(model_func, train, test):
    history = [x for x in train]
    predictions = []
    for i in range(len(test)):
        yhat_sequence = model_func(history)
        predictions.append(yhat_sequence)
        history.append(test[i, :])
    predictions = array(predictions)
    score, scores = evaluate_forecasts(test[:, :, 0], predictions)
    return score, scores

def to_series(data):
    series = [week[:, 0] for week in data]
    series = array(series).flatten()
    return series

def arima_forecast(history):
    series = to_series(history)
    model = ARIMA(series, order=(7,0,0))
    model_fit = model.fit()
    with open('arima_model.pkl', 'wb') as model_file:
        pickle.dump(model_fit, model_file)
    yhat = model_fit.predict(len(series), len(series)+6)
    return yhat

dataset = read_csv('household_power_consumption_days.csv', header=0, infer_datetime_format=True, parse_dates=['datetime'], index_col=['datetime'])
train, test = split_dataset(dataset.values)
models = {'arima': arima_forecast}
days = ['sun', 'mon', 'tue', 'wed', 'thr', 'fri', 'sat']
for name, func in models.items():
    score, scores = evaluate_model(func, train, test)
    summarize_scores(name, score, scores)
    pyplot.plot(days, scores, marker='o', label=name)
pyplot.legend()
pyplot.show()
