# -*- coding: utf-8 -*-
"""Time Series Forecasting of AEP Energy Consumption Using XGBoost.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16C01t9zwGXnpJv4IOilz04XzrKMQoQH2
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import xgboost as xgb
from sklearn.metrics import mean_squared_error
color_pal = sns.color_palette()
plt.style.use('fivethirtyeight')

df = pd.read_csv('/content/AEP_hourly.csv')
df =df.set_index('Datetime')
df.index=pd.to_datetime(df.index)

df.head()

df.tail()

df.describe()

df.plot(style='.',
        figsize=(15, 5),
        color=color_pal[2],
        title='PJME Energy use in MW')
plt.show()



"""## TRAIN/TEST SPLIT"""

train = df.loc[df.index < '01-01-2015']
test = df.loc[df.index >= '01-01-2015']

fig, ax = plt.subplots(figsize=(15, 5))
train.plot(ax=ax, label = 'Training set',title='Data Train/Test Split')
test.plot(ax=ax, label = 'Test Set')
ax.axvline('01-01-2015', color ='black', ls='--')
ax.legend(['Training Set','Test Set'])
plt.show()

df.loc[(df.index > '01-01-2010') & (df.index < '01-08-2010' )].plot()

"""## FEATURE CREATION"""

df.index.hour

def create_features(df):

    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['quarter'] = df.index.quarter
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    return df

df = create_features(df)

"""## VISUALIZE OUR FEATURE /TARGET RELATIONSHIP

"""

print(df.columns)

fig, ax = plt.subplots(figsize=(18,8))
sns.boxplot(data=df, x='hour', y ='AEP_MW', palette ='rainbow')
ax.set_title('MW by Hour')
plt.show()

fig, ax = plt.subplots(figsize=(18,8))
sns.boxplot(data=df, x='month', y ='AEP_MW', palette ='Greens')
ax.set_title('MW by Month')
plt.show()

"""## CREATE A MODEL

"""

train = create_features(train)
test =  create_features(test)
FEATURES = ['hour', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear']
TARGET = 'AEP_MW'

X_train = train[FEATURES]
y_train = train[TARGET]

X_test = test[FEATURES]
y_test = test[TARGET]

!pip install -U xgboost

import xgboost
print(xgboost.__version__)

reg = xgb.XGBRegressor(n_estimators=1000,early_stopping_rounds=50, learning_rate=0.001)

reg.fit(X_train, y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=100
)

"""## FEATURE IMPORTANCE

"""

fi = pd.DataFrame(data=reg.feature_importances_,
             index=reg.feature_names_in_,
             columns=['importance'])
fi.sort_values('importance').plot(kind='barh', title ='Feature Importance')
plt.show()

"""## FORECAST ON TEST"""

test['prediction'] = reg.predict(X_test)

df.columns

print(type(test))
print(test.head())

print(f"X_test shape: {X_test.shape}")
print(f"test shape: {test.shape}")

df = df.merge(test[['prediction']], how='left', left_index=True, right_index=True)
ax = df[['AEP_MW']].plot(figsize=(15, 5))
df['prediction'].plot(ax=ax, style='.')
plt.legend(['truth data', 'predictions'])
ax.set_title('raw data and prediction')
plt.show()

score = np.sqrt(mean_squared_error(test['AEP_MW'], test['prediction']))
print(f'RMSE Score on test set:{score:0.2f}')

"""## CALCULATE ERROR

LOOK AT THE BEST AND WORST PREDICTED KEYS
"""

test['error'] = np.abs(test[TARGET] - test['prediction'])
test['date']=test.index.date
test.groupby('date')['error'].mean().sort_values(ascending=False).head(5)

test['error'] = np.abs(test[TARGET] - test['prediction'])
test['date']=test.index.date
test.groupby('date')['error'].mean().sort_values(ascending=True).head(5)

#next steps
add more features (weather forecast, holidays)
more robust cross validation