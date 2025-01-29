#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('pip install scikit-surprise')


# import library

# In[ ]:


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, average_precision_score
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy
import numpy as np


# load data

# In[ ]:


file_path = "steam.csv"
data = pd.read_csv(file_path)

file1_path = "steam_desc.csv"
data_desc = pd.read_csv(file1_path)


# data preprocessing

# In[ ]:


cek = data.isnull().sum()
print(cek)
print(data)

cek1 = data_desc.isnull().sum()
print(cek1)
print(data_desc)


# cek data yang hilang dalam steam.csv

# In[ ]:


missing_publishers = data[data['publisher'].isnull()]
print(missing_publishers[['name', 'publisher']])

missing_dev = data[data['developer'].isnull()]
print(missing_dev[['name', 'developer']])


# Menggabungkan deskripsi dari data steam_desc.csv ke dalam 1 dataframe yang sama

# In[ ]:


print(data_desc.columns)
print(data.columns)


# In[ ]:


# Merge dengan data_desc
data = data.merge(data_desc[['steam_appid', 'short_description']],
                  left_on='appid', right_on='steam_appid', how='left')

# Pastikan steam_appid sama dengan appid
data['steam_appid'] = data['appid']

# Hapus steam_appid dari data_desc jika tidak diperlukan
data.drop(columns=['steam_appid'], inplace=True)

# Cek hasilnya
print(data.columns)
print(data[['appid', 'short_description']].head())


# feature engineering

# In[ ]:


data = data[['name', 'positive_ratings', 'negative_ratings', 'average_playtime', 'genres', 'categories', 'price', 'owners', 'platforms',
             'steamspy_tags', 'short_description']]

print(data.isnull())

# filter data untuk memastikan game yang diseleksi
data = data[(data['positive_ratings'] + data['negative_ratings'] >= 100) & (data['average_playtime'] > 0)]

# buat variable baru untuk formula satisfaction score
data['satisfaction_score'] = (data['positive_ratings'] / (data['positive_ratings'] + data['negative_ratings'])) * data['average_playtime']


# Model 1 - TF-IDF + Cosine Similarity

# In[ ]:


# prompt: buatkan code Content-Based Filtering (CBF)  lagi dengan fitur yang berbeda

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy
import numpy as np

get_ipython().system('pip install scikit-surprise')

# Load data
file_path = "steam.csv"
data = pd.read_csv(file_path)

# Feature Engineering (enhanced)
data = data[['name', 'positive_ratings', 'negative_ratings', 'average_playtime', 'genres', 'categories', 'owners']]

# Data Cleaning
data = data.dropna()  # Remove rows with missing values
data['owners'] = data['owners'].astype(str).str.replace(',', '').str.replace('-', ' ').str.split().str[0].fillna(0).astype(int)
data = data[(data['positive_ratings'] + data['negative_ratings'] >= 100) & (data['average_playtime'] > 0) & (data['owners'] > 0)]

# Calculate a more nuanced satisfaction score
data['satisfaction_score'] = ((data['positive_ratings'] / (data['positive_ratings'] + data['negative_ratings'])) * 0.6 +
                             (data['average_playtime'] / data['average_playtime'].max()) * 0.4) * np.log1p(data['owners'])

# Content-Based Filtering (CBF) with enhanced features
def content_based_filtering(data, game_name, top_n=10):
    data['text_features'] = data['name'] + ' ' + data['genres'] + ' ' + data['categories']

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['text_features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    indices = pd.Series(data.index, index=data['name']).drop_duplicates()

    if game_name not in indices:
        return f"Game '{game_name}' not found in dataset."

    idx = indices[game_name]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n + 1]  # Exclude the game itself

    game_indices = [i[0] for i in sim_scores]
    return data.iloc[game_indices][['name', 'genres', 'categories', 'owners']]


# Example Usage
example_game_name = "Team Fortress Classic"  # Example game name

# Content-Based Filtering
print("Content-Based Filtering Recommendations:")
cbf_results = content_based_filtering(data, example_game_name)
cbf_results


# # **experiment 1**

# In[ ]:


# prompt: dari code line [89] diatas lakukan experiment kepada code  bagian Content-Based Filtering  dengan ubah fitur yang digunakan selain name, genres, categories

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy
import numpy as np

# Load data (assuming 'steam.csv' is in the same directory)
file_path = "steam.csv"
data = pd.read_csv(file_path)

# Feature Engineering (enhanced)
data = data[['name', 'positive_ratings', 'negative_ratings', 'average_playtime', 'genres', 'categories', 'owners', 'platforms']]

# Data Cleaning (handling missing values and data type conversion)
data = data.dropna()  # Remove rows with missing values
data['owners'] = data['owners'].astype(str).str.replace(',', '').str.replace('-', ' ').str.split().str[0].fillna(0).astype(int)
data = data[(data['positive_ratings'] + data['negative_ratings'] >= 100) & (data['average_playtime'] > 0) & (data['owners'] > 0)]

# Calculate a more nuanced satisfaction score
data['satisfaction_score'] = ((data['positive_ratings'] / (data['positive_ratings'] + data['negative_ratings'])) * 0.6 +
                             (data['average_playtime'] / data['average_playtime'].max()) * 0.4) * np.log1p(data['owners'])

# Content-Based Filtering (CBF) with MODIFIED features
def content_based_filtering(data, game_name, top_n=10):
    # MODIFIED: Using 'genres', 'categories', and 'platforms'
    data['text_features'] = data['genres'] + ' ' + data['categories'] + ' ' + data['platforms']  # Combine relevant features

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['text_features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    indices = pd.Series(data.index, index=data['name']).drop_duplicates()

    if game_name not in indices:
        return f"Game '{game_name}' not found in dataset."

    idx = indices[game_name]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n + 1]  # Exclude the game itself

    game_indices = [i[0] for i in sim_scores]
    # MODIFIED: Returning additional relevant features
    return data.iloc[game_indices][['name', 'genres', 'categories', 'platforms', 'owners']]


# Example Usage
example_game_name = "Ricochet"  # Example game name

# Content-Based Filtering
print("Content-Based Filtering Recommendations:")
cbf_results = content_based_filtering(data, example_game_name)
cbf_results


# # **experiment 2**

# In[ ]:


# prompt: dari code line [93] diatas lakukan experiment kepada code  bagian Content-Based Filtering  dengan ubah fitur yang digunakan selain fitur ini : genres, categories, platforms, price

# Content-Based Filtering (CBF) with MODIFIED features
def content_based_filtering(data, game_name, top_n=10):
    # MODIFIED: Using 'owners', 'platforms', and 'average_playtime'
    # Convert average_playtime to string for concatenation
    data['average_playtime'] = data['average_playtime'].astype(str)
    data['text_features'] = data['owners'].astype(str) + ' ' + data['platforms'] + ' ' + data['average_playtime']  # Combine relevant features

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['text_features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    indices = pd.Series(data.index, index=data['name']).drop_duplicates()

    if game_name not in indices:
        return f"Game '{game_name}' not found in dataset."

    idx = indices[game_name]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n + 1]  # Exclude the game itself

    game_indices = [i[0] for i in sim_scores]
    # MODIFIED: Returning additional relevant features
    return data.iloc[game_indices][['name', 'owners', 'platforms', 'average_playtime']]


# Example Usage
example_game_name = "Day of Defeat"  # Example game name

# Content-Based Filtering
print("Content-Based Filtering Recommendations:")
cbf_results = content_based_filtering(data, example_game_name)
cbf_results


# Model 2. Count Vectorizer + Cosine Similarity

# Experiment 1 : Genre, kategori, dan deskripsi

# In[ ]:


data['combined_features'] = data['genres'] + ' ' + data['categories'] + ' ' + data['short_description']

vectorizer = CountVectorizer(stop_words='english')
count_matrix = vectorizer.fit_transform(data['combined_features'])
cosine_sim = cosine_similarity(count_matrix, count_matrix)

# menerima input untuk menrekomendasi game
def get_game_recommendations(game_name, cosine_sim=cosine_sim):
    try:
        idx = data.index[data['name'] == game_name].tolist()[0]
    except IndexError:
        return f"Game '{game_name}' tidak ditemukan, pastikan nama game sudah benar."

    sim_scores = list(enumerate(cosine_sim[idx]))

    # Mengurutkan game berdasarkan skor kesamaan (dari yang paling mirip)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Mengambil 5 game teratas selain game itu sendiri
    sim_scores = sim_scores[1:6]

    # Mendapatkan indeks game yang relevan
    game_indices = [i[0] for i in sim_scores]

    # Mengembalikan nama game yang direkomendasikan
    return data['name'].iloc[game_indices]

recommended_games = get_game_recommendations('Counter-Strike')
print(recommended_games)


# Experiment 2 : Genre, kategori, steamspy tag, dan deskripsi

# In[ ]:


data['combined_features'] = data['genres'] + ' ' + data['categories'] + ' ' + data['steamspy_tags'] + ' ' + data['short_description']

vectorizer = CountVectorizer(stop_words='english')
count_matrix = vectorizer.fit_transform(data['combined_features'])
cosine_sim = cosine_similarity(count_matrix, count_matrix)

# menerima input untuk menrekomendasi game
def get_game_recommendations(game_name, cosine_sim=cosine_sim):
    try:
        idx = data.index[data['name'] == game_name].tolist()[0]
    except IndexError:
        return f"Game '{game_name}' tidak ditemukan, pastikan nama game sudah benar."

    sim_scores = list(enumerate(cosine_sim[idx]))

    # Mengurutkan game berdasarkan skor kesamaan (dari yang paling mirip)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Mengambil 5 game teratas selain game itu sendiri
    sim_scores = sim_scores[1:6]

    # Mendapatkan indeks game yang relevan
    game_indices = [i[0] for i in sim_scores]

    # Mengembalikan nama game yang direkomendasikan
    return data['name'].iloc[game_indices]

recommended_games = get_game_recommendations('Counter-Strike')
print(recommended_games)


# Experiment 3 : Genre dan deskripsi

# In[ ]:


data['combined_features'] = data['genres'] + ' ' + data['short_description']

vectorizer = CountVectorizer(stop_words='english')
count_matrix = vectorizer.fit_transform(data['combined_features'])
cosine_sim = cosine_similarity(count_matrix, count_matrix)

# menerima input untuk menrekomendasi game
def get_game_recommendations(game_name, cosine_sim=cosine_sim):
    try:
        idx = data.index[data['name'] == game_name].tolist()[0]
    except IndexError:
        return f"Game '{game_name}' tidak ditemukan, pastikan nama game sudah benar."

    sim_scores = list(enumerate(cosine_sim[idx]))

    # Mengurutkan game berdasarkan skor kesamaan (dari yang paling mirip)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Mengambil 5 game teratas selain game itu sendiri
    sim_scores = sim_scores[1:6]

    # Mendapatkan indeks game yang relevan
    game_indices = [i[0] for i in sim_scores]

    # Mengembalikan nama game yang direkomendasikan
    return data['name'].iloc[game_indices]

recommended_games = get_game_recommendations('Counter-Strike')
print(recommended_games)


# Experiment 4 : Genre dan kategori

# In[ ]:


data['combined_features'] = data['genres'] + ' ' + data['categories']

vectorizer = CountVectorizer(stop_words='english')
count_matrix = vectorizer.fit_transform(data['combined_features'])
cosine_sim = cosine_similarity(count_matrix, count_matrix)

# menerima input untuk menrekomendasi game
def get_game_recommendations(game_name, cosine_sim=cosine_sim):
    try:
        idx = data.index[data['name'] == game_name].tolist()[0]
    except IndexError:
        return f"Game '{game_name}' tidak ditemukan, pastikan nama game sudah benar."

    sim_scores = list(enumerate(cosine_sim[idx]))

    # Mengurutkan game berdasarkan skor kesamaan (dari yang paling mirip)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Mengambil 5 game teratas selain game itu sendiri
    sim_scores = sim_scores[1:6]

    # Mendapatkan indeks game yang relevan
    game_indices = [i[0] for i in sim_scores]

    # Mengembalikan nama game yang direkomendasikan
    return data['name'].iloc[game_indices]

recommended_games = get_game_recommendations('Counter-Strike')
print(recommended_games)

