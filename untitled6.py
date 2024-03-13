# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-SLm_YWPdjClCud-GvSbxhIfAVqNhKJa

# **Problem Statement**
**You are provided with the data of 145k wikipedia pages for 550 days and daily view count for each of them. Your clients belong to different regions and need data on how their ads will perform on pages in different languages.**
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Importing data
train = pd.read_csv("https://drive.usercontent.google.com/download?id=1qQkymAitU6l2pSe702rDUhQpoP8MUZXl&export=download&authuser=0&confirm=t&uuid=898b27ba-48ce-43aa-a177-e10abef9797b&at=APZUnTUq2ay4M2qKJ9Jvyiex28lp:1708138813180")

train.head()

"""# **EDA**"""

train.info()

train.shape

train.isnull().sum()

# Count of Null values over tha days
days = [d for d in range(1,len(train.columns))]
plt.figure(figsize = (10,7))
plt.xlabel("Day")
plt.ylabel("Null values")
plt.plot(days, train.isnull().sum()[1:])

# Dropping wikipages/rows, in which >300 values are missed
train = train.dropna(how = 'all')
train = train.dropna(thresh = 300)

train.shape

#Replacing Null values by 0
train = train.fillna(0)

train.isnull().sum()

df = train.copy()

"""**Data Formmating**
Page format--> SPECIFIC NAME.wikipedia.org_ACCESS TYPE_ACCESS ORIGIN
--->Separating it into Language, access type & access origin
"""

# Data formating
import re
def lang(Page):
  val = re.search('[A-Za-z]{2}.wikipedia.org_',Page)
  if val:
    return val[0][0:2]

  return 'no_lang'

df['Language'] = df['Page'].apply(lambda x: lang(str(x)))

df["Language"].value_counts()

sns.countplot(data = df, x = "Language", palette = 'Set1')

df.groupby('Language').count()

#Mean number of clicks for each language on each day
df_language = df.groupby("Language").mean().transpose()

df_language.head()

df_language.reset_index(inplace = True)
df_language.set_index('index', inplace = True)

df_language.plot(figsize = (12,7))
plt.ylabel("views per page")

"""# **Checking stationarity**"""

from statsmodels.tsa.stattools import adfuller

def df_test(x):
  result = adfuller(x)
  print('ADF Statististics:%f'%result[0])
  print('p_value: %f'%result[1])

total_view = df_language.copy()
df_test(total_view['en'])

"""* Since P > 5%, series is not stationary

**Making it stationary**
"""

ts = total_view['en']

total_view['en']

"""# **Removing trend & seasonality**"""

total_view = df_language.copy()

ts = total_view["en"]

"""# **Time Series Decomposition**"""

from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm

tsn = pd.Series(total_view['en'],index = total_view.index)

decomposition = sm.tsa.seasonal_decompose(tsn, model = "additive", period = 10)

decomposition.plot()
plt.show()

"""# New Section

# **Removing seasonality & trend using defferencing**
"""

ts_diff = ts - ts.shift(1)
plt.plot(ts_diff)
plt.show()

ts_diff.dropna(inplace = True)
df_test(ts_diff)

"""**Now P value is 0, it is stationaryt**

> Indented block

# **Auto correlation & Partial Autocorrelation Plots**
"""

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
acf = plot_acf(ts_diff,lags = 20)
pacf = plot_pacf(ts_diff, lags = 20)

"""**From above plots, concluded that seasonality is 7**

**Train Test Split**
"""

train = ts[:-30]
test = ts[-30:]

"""# **ARIMA model**

**Performance Metrics**
"""

from sklearn.metrics import mean_squared_error as mse, mean_absolute_error as mae, mean_absolute_percentage_error as mape

def performance(actual, predicted):
  print("MAE:", round(mae(actual, predicted),3))
  print("RMSE:", round(mse(actual, predicted)**0.5,3))
  print("MAPE:", round(mape(actual, predicted),3))

from statsmodels.tsa.arima.model import ARIMA
from pandas import DataFrame

model=ARIMA(ts, order = (4,1,3))
model_fit = model.fit()

from statsmodels.graphics.tsaplots import plot_predict

plot_predict(model_fit,dynamic = False)
plt.show()

"""**Multistep forecasting**"""

model = ARIMA(train, order = (4,1,3))
fitted = model.fit()

fc = fitted.forecast(30, alpha = 0.02)

# Pandas series
fc_series = pd.Series(fc, index = test.index)

# Plot
plt.figure(figsize = (12,10), dpi = 100)

plt.plot(train, label = "Training")
plt.plot(test, label = "Testing")
plt.plot(fc_series, label = "Forecasting")

plt.title("forecast Vs Actual")
plt.legend(loc = "upper left", fontsize = 8)

"""**Performance of ARIMA**"""

performance(test, fc)

"""# **SARIMAX**"""

!gdown https://drive.google.com/file/d/19qvuu7E8yD63o4WkOdy_lLFSrZlZPpuE/view?usp=drive_link    #1H9054 - eVP9IdANPOb1XwX7Nd2r_Sjf1u

#exog = pd.read_csv(raise"https://drive.google.com/file/d/19qvuu7E8yD63o4WkOdy_lLFSrZlZPpuE/view?usp=drive_link")

#exog = pd.read_csv('view?usp=drive_link')

exog_df = pd.read_csv("https://drive.google.com/uc?id=19qvuu7E8yD63o4WkOdy_lLFSrZlZPpuE")

exog_df.head()

exog = exog_df['Exog'].to_numpy()

import statsmodels.api as sm

model = sm.tsa.statespace.SARIMAX(train, order = (4,1,3), seasonal_order = (1,1,1,7), exog = exog[:-30])
results = model.fit()

fc = results.forecast(30, exog = pd.DataFrame(exog[-30:]))

# Pandas series
fc_series = pd.Series(fc)

# Plot
plt.figure(figsize = (12,10), dpi = 100)

train.index = train.index.astype('datetime64[ns]')
test.index = test.index.astype('datetime64[ns]')

plt.plot(train, label = "Training")
plt.plot(test, label = "Testing")
plt.plot(fc_series, label = "Forecasting")

plt.title("forecast Vs Actual")
plt.legend(loc = "upper left", fontsize = 8)

"""**Performance of SARIMAX**"""

performance(test, fc)