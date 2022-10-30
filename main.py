import pandas as pd # Python library for data analysis and data frame
import numpy as np # Numerical Python library for linear algebra and computations
pd.set_option('display.max_columns', None) # code to display all columns
# Visualisation libraries
import matplotlib.pyplot as plt
import seaborn as sns
# libraries for text processing
import nltk
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# to display images
from skimage import io
# to save the required files
import pickle
import warnings
warnings.filterwarnings('ignore') # To prevent kernel from showing any warning

df = pd.read_csv('input/movies.csv')
df.drop_duplicates(inplace=True) #Remove duplicate values
df.drop_duplicates(subset=['title','release_date'], inplace=True) #Remove duplicate movies (same title and release date)
#659,978 movies left at this point
df1 = df[df.vote_count >= 10].reset_index() #Remove movies with less than 20 vote counts
df1.fillna('', inplace=True) #Replace the NaN with ''
index = df1[df1['overview']==''].index #Finding index with blank overview
df1.drop(index, inplace=True) #Drop blank overview movies
#64,560 movies left at this point (vote count filter removes a lot)
#Genres, keywords, and credits delimiters are '-' so change it to ' '
df1['genres'] = df1['genres'].apply(lambda x: ' '.join(x.split('-')))
df1['keywords'] = df1['keywords'].apply(lambda x: ' '.join(x.split('-')))
df1['credits'] = df1['credits'].apply(lambda x: ' '.join(x.replace(' ', '').split('-')[:5]))
df1.to_csv('input/processed_data.csv')