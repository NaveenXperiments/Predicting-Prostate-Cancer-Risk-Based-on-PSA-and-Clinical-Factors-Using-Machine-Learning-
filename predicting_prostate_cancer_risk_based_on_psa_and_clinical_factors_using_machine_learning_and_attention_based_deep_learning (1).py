# -*- coding: utf-8 -*-
"""Predicting Prostate Cancer Risk Based on PSA  and Clinical Factors Using Machine Learning  and Attention-Based Deep Learning

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GBLMSJTKbS1bZ9wcBuraKjnMYMQbR3ck
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_rows', None)
df = pd.read_excel('/content/dataset20.xlsx', header=None)
df = pd.DataFrame([row[0].split() for row in df.values[1:]],
                 columns=['Index', 'lcavol', 'lweight', 'age', 'lbph', 'svi', 'lcp', 'gleason', 'pgg45', 'lpsa'])
df = df.astype({'Index': int,
                'lcavol': float,
                'lweight': float,
                'age': int,
                'lbph': float,
                'svi': int,
                'lcp': float,
                'gleason': int,
                'pgg45': int,
                'lpsa': float})

print(df)

df.head()

df.tail()

df.shape

df.duplicated().sum()

df.isnull().sum()

df.info()

df.describe()

df.nunique()

def classify_features(df):
    categorical_features = []
    non_categorical_features = []
    discrete_features = []
    continuous_features = []

    for column in df.columns:
        if df[column].dtype == 'object':
            if df[column].nunique() < 40:
                categorical_features.append(column)
            else:
                non_categorical_features.append(column)
        elif df[column].dtype in ['int64', 'float64']:
            if df[column].nunique() < 10:
                discrete_features.append(column)
            else:
                continuous_features.append(column)

    return categorical_features, non_categorical_features, discrete_features, continuous_features

categorical, non_categorical, discrete, continuous = classify_features(df)

print("Categorical Features:", categorical)
print("Non-Categorical Features:", non_categorical)
print("Discrete Features:", discrete)
print("Continuous Features:", continuous)

for i in discrete:
    plt.figure(figsize=(15, 6))
    ax = sns.countplot(x=i, data=df, palette='hls')
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(
            f'{height}',
            xy=(p.get_x() + p.get_width() / 2, height),
            xytext=(0, 10),  # Offset annotation 10 points above the bar
            textcoords='offset points',
            ha='center',  # Horizontal alignment
            va='center'   # Vertical alignment
        )
    plt.title(f'Distribution of {i}')
    plt.show()

plt.figure(figsize=(8, 6))
sns.boxplot(data=df, x='svi', y='lpsa', palette='Set2')
plt.title('Distribution of PSA Levels by Seminal Vesicle Invasion')
plt.xlabel('Seminal Vesicle Invasion (svi)')
plt.ylabel('PSA Level (lpsa)')
_ = plt.xticks([0, 1], ['No', 'Yes'])

import plotly.express as px

for i in discrete:
    counts = df[i].value_counts().reset_index()
    counts.columns = [i, 'count']  # Rename columns for clarity

    fig = px.pie(
        counts,
        values='count',
        names=i,
        title=f'Distribution of {i}'
    )

    fig.show()

for i in continuous:
    plt.figure(figsize=(15, 6))
    sns.histplot(data=df, x=i, bins=20, kde=True, color='cyan')  # Use sns.histplot for histogram with KDE
    plt.xticks(rotation=90)
    plt.title(f'Distribution of {i}')
    plt.xlabel(i)
    plt.ylabel("Frequency")
    plt.show()

for i in continuous:
    plt.figure(figsize=(15, 6))
    sns.boxplot(x=i, data=df, palette='hls')
    plt.xticks(rotation=90)
    plt.title(f'Boxplot of {i}')
    plt.xlabel(i)
    plt.show()

# Correlation Matrix and Heatmap
correlation_matrix = df[['lcavol', 'lbph', 'lcp', 'lweight', 'age', 'pgg45', 'lpsa']].corr()
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Correlation Matrix of Continuous Variables')
plt.show()

# Boxplot of 'lcavol' by 'gleason'
sns.boxplot(x='gleason', y='lcavol', data=df, palette='hls')
plt.title('Boxplot of lcavol by Gleason')
plt.show()

# Violin plot of 'lpsa' by 'svi'
sns.violinplot(x='svi', y='lpsa', data=df)
plt.show()

from scipy.stats import chi2_contingency
contingency_table = pd.crosstab(df['svi'], df['gleason'])

# Perform Chi-Square test
chi2, p, dof, expected = chi2_contingency(contingency_table)
print(f"Chi-Square Test result:\nChi2: {chi2}\nP-value: {p}")

sns.pairplot(df[['lcavol', 'lpsa']])
plt.show()

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score

X = df[['svi', 'age', 'lcavol']]
y = df[['lweight', 'lbph', 'lcp', 'pgg45', 'gleason', 'lpsa']]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("MSE:", mean_squared_error(y_test, y_pred))
print("R2:", r2_score(y_test, y_pred))

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score

# Cross-validation scores for Linear Regression
cv_scores = cross_val_score(model, X, y, cv=5)
print("Cross-validation scores:", cv_scores)

# Classifying based on 'lpsa'
y_class = (df['lpsa'] > df['lpsa'].median()).astype(int)

# Train-test split for classification
X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.2, random_state=42)

# Random Forest model
rf_model = RandomForestClassifier()
rf_model.fit(X_train, y_train)

# Prediction and accuracy
y_pred_class = rf_model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred_class))

from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
import pandas as pd

X_vif = add_constant(df[['lcavol', 'lweight', 'age', 'lbph', 'lcp', 'pgg45', 'gleason', 'svi']])
vif = pd.DataFrame()
vif['Features'] = X_vif.columns
vif['VIF'] = [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])]
print(vif)

import tensorflow as tf
from tensorflow.keras import layers, models

class AttentionLayer(layers.Layer):
    def __init__(self, units):
        super(AttentionLayer, self).__init__()
        self.units = units

    def build(self, input_shape):
        self.query_dense = layers.Dense(self.units)
        self.key_dense = layers.Dense(self.units)
        self.value_dense = layers.Dense(self.units)

    def call(self, inputs):
        query = self.query_dense(inputs)
        key = self.key_dense(inputs)
        value = self.value_dense(inputs)

        attention_scores = tf.matmul(query, key, transpose_b=True)
        attention_scores = attention_scores / tf.sqrt(float(self.units))

        attention_weights = tf.nn.softmax(attention_scores, axis=-1)

        output = tf.matmul(attention_weights, value)

        return output

def build_model(input_shape):
    inputs = layers.Input(shape=input_shape)
    x = layers.Dense(64, activation='relu')(inputs)
    x = AttentionLayer(64)(x)
    x = layers.Dense(32, activation='relu')(x)
    x = layers.Dense(1)(x)
    model = models.Model(inputs, x)
    return model

model = build_model((X_train.shape[1],))
model.compile(optimizer='adam', loss='mean_squared_error')

history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

plt.figure(figsize=(12, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()