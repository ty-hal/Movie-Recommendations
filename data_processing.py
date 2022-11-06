import pandas as pd # Python library for data analysis and data frame
import numpy as np # Numerical Python library for linear algebra and computations
import nltk
from nltk.stem.snowball import SnowballStemmer #educes words to their word stems that affixes to suffixes and prefixes
pd.set_option('display.max_columns', None) # code to display all columns
import warnings
warnings.filterwarnings('ignore') # To prevent kernel from showing any warning

df = pd.read_csv('input/movies.csv') #Read the CSV file
df.drop_duplicates(inplace=True) #Remove duplicate entries
df.drop_duplicates(subset=['title','release_date'], inplace=True) #Remove duplicate movies (same title AND release date)
#659,978 movies left at this point

new_df = df[df.vote_count >= 10].reset_index() #Remove movies with less than 10 vote counts (can be adjusted)
new_df.fillna('', inplace=True) #Replace NaN values with ''
index = new_df[(new_df['overview']=='') & (new_df['genres'] == '')].index #Find indices of movies with blank overviews (plots) and genres
new_df.drop(index, inplace=True) #Remove these movies
#64,560 movies left at this point (vote count filter removes a lot)

#Genres, keywords, and credits delimiters are '-' so change it to ' '
new_df['genres'] = new_df['genres'].apply(lambda x: ' '.join(x.split('-')))
new_df['keywords'] = new_df['keywords'].apply(lambda x: ' '.join(x.split('-')))
new_df['credits'] = new_df['credits'].apply(lambda x: ' '.join(x.replace(' ', '').split('-')[:5]))
new_df['title_no_spaces'] = new_df['title'].str.replace('[^a-zA-Z0-9]', '') #Add a column called "title_no_spaces" that is the alphanumeric title of the movie (remove non-important characters)

new_df['info'] = new_df['overview'] + ' ' + new_df['keywords'] #Add a column called "info" that stores the overview (plot) and keywords (used for comparing plots between movies)
stemmer = SnowballStemmer("english")
def stem(words):
    output = []
    for item in words.split():
        output.append(stemmer.stem(item))
    return ' '.join(output)

new_df['info'] = new_df['info'].apply(stem)
new_df['info'] = new_df['info'].str.replace('[^\w\s]','') #Remove punctuation

new_df['genres'] = new_df['genres'].apply(stem)
new_df['genres'] = new_df['genres'].str.replace('[^\w\s]','') #Remove punctuation


new_df.drop(columns=['index', 'production_companies', 'budget', 'revenue', 'status', 'backdrop_path', 'vote_count', 'recommendations'], inplace = True) #Remove columns we don't need to save space
new_df.to_csv('input/processed_movies.csv', index = False) #Save to CSV file
