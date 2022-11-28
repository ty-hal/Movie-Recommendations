from sorting import *
import PySimpleGUI as sg 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from skimage import io #For reading the movie images from URLs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore') # To prevent kernel from showing any warning
import ssl #To bypass error with loading images -- not ideal, but I couldn't find an easy fix
ssl._create_default_https_context = ssl._create_unverified_context

def draw_image(idx): #Given an index (of the data frame), find the movie's poster URL and display the jpeg image
    ax.cla() #Clear the axes
    url = "https://image.tmdb.org/t/p/w500/" + df.loc[idx, "poster_path"]
    img = io.imread(fname = url) #Read the image using skimage
    ax.imshow(img, aspect='auto') 
    ax.axis('off')
    ax.axis('scaled')
    ax.autoscale_view('tight')
    figure.set_facecolor('#ADB6D1') #Background color of the figure to match the color theme of the GUI
    figure_canvas_agg.draw()
    return figure_canvas_agg

#Read the processed movie data and store it as a data frame (df)
df = pd.read_csv('input/processed_movies.csv')

#Similarity matrices
tfidf = TfidfVectorizer(stop_words='english')
#Calculates the similarity of each movie to an inputted movie based on the weighting of plot, genre, and cast preferences
def get_similiarity(df, title, id, langRequirement, plotPreference, genrePreference, creditPreference):
    if (langRequirement == "Yes"):
        lang = df.loc[df['title'] == title].original_language.values[0] #Find the language of the movie that is being compared
        df = df[df.original_language == lang].reset_index() #Remove movies with different language
        
    idx = df.index[df['id'] == id][0] # Get the index of the movie that matches the title

    # Calculate the similarity values of each movie for each of the three preferences
    plot_tfidf_matrix = tfidf.fit_transform(df['info'].values.astype('U')) 
    genre_tfidf_matrix = tfidf.fit_transform(df['genres'].values.astype('U'))
    cast_tfidf_matrix = tfidf.fit_transform(df['credits'].values.astype('U'))

    plot_scores = list(enumerate(cosine_similarity(plot_tfidf_matrix, plot_tfidf_matrix[idx]))) 
    genre_scores = list(enumerate(cosine_similarity(genre_tfidf_matrix, genre_tfidf_matrix[idx])))
    cast_scores = list(enumerate(cosine_similarity(cast_tfidf_matrix, cast_tfidf_matrix[idx])))

    similarity_scores = [] # Create new list to score similarity scores of all of the movies
    for idx, item in enumerate(plot_scores):
        score = plotPreference * plot_scores[idx][1] + genrePreference * genre_scores[idx][1] + creditPreference * cast_scores[idx][1]
        index = idx
        if (langRequirement == "Yes"):
            index = df.iloc[idx]["index"]
        similarity_scores.append([index, score.astype(float)])
    similarity_scores.pop(idx) # Remove the movie you inputted
    return df, similarity_scores # Return the list of [movie index in df, similarity score]

#Window and figure
_VARS = {'window': False,
         'fig_agg': False,
         'pltFig': False}

#Global variables
movieInput  = ""
selectedMovie = ""
movieID = None
plotPreference = 0
genrePreference = 0
castPreference = 0
typeToSort = ""
languageReq = "" #Only certain language movies to show
calculateSimilarities = False #Calculate similar movies
displayMovies = False #Display similar movies
similarMovies = []
dateSpecifier = "" #If searched movie has multiple matches, this stores the user inputted date of the exact movie they want

preferences = ['plot', 'genre', 'cast']
preferences_keys = ['plotText', 'plot','genreText', 'genre', 'castText', 'cast']
reset_keys = ['dateInfo', 'dateButton', 'movieImg', 'preferencesDescription', 'lang', 'langOptions', 'go']

#Color theme of the GUI
sg.theme('BlueMono') 

#Define the layouts
header = [[sg.Button('Reset Search'), sg.Button('Close')]]
movie_input = [[[sg.Text('Enter a Movie You Like')],
                [sg.Input(key = 'userInput'), sg.Button('Find')]],
                sg.Text('', key = 'searchResult'), sg.Input(key = 'dateInfo', size = (15,1), tooltip = "MM/DD/YYYY", visible = False), sg.Button('Enter', key = 'dateButton', visible = False)]
movie_image = [[sg.Canvas(key='movieImg', background_color='#ADB6D1', visible = False)]]
preference_description = [[sg.Text('', key = 'preferencesDescription', visible = False)]]
preference_inputs = [[[sg.Text('Plot', key = 'plotText', visible = False), sg.Combo(['1', '2', '3', '4', '5'], key='plot', visible = False), 
                        sg.Text('Genre', key = 'genreText', visible = False), sg.Combo(['1', '2', '3', '4', '5'], key='genre', visible = False), 
                        sg.Text('Main Cast', key = 'castText', visible = False), sg.Combo(['1', '2', '3', '4', '5'], key='cast', visible = False)]],
                    [sg.Text('', key = 'lang', visible = False), sg.Combo(['Yes', 'No'], key = 'langOptions', visible = False)]]
find_movies = [sg.Button('Search for Similar Movies', key = 'go', visible = False)]
# loading_gif = [[[sg.Text("Loading...", key = 'loading', visible = False)], [sg.Image(data = gif, key='gif', visible = False)]]]
similar_movies = [[sg.Text('Sort Similar Movies By', key = 'similarMoviesText', visible = False), sg.Combo(['Rating', 'Release Date', 'Popularity', 'Runtime', 'Most Similar'], key='sortTypes', visible = False), sg.Button('Sort', key = 'sort', visible = False)], [sg.Canvas(key='similarMovieImg', background_color='#ADB6D1', visible = False)]] 

#The window's layout
layout = [[header],
          [movie_input],
          [movie_image],
          [preference_description],
          [preference_inputs],
          [find_movies],
          [similar_movies]
         ]

# Create the Window
_VARS['window'] = sg.Window('Movie Recommendation GUI',
                            layout,
                            finalize=True,
                            resizable=True,
                            location=(100, 100),
                            element_justification="center")

#_VARS['window'].maximize()
figure, ax = plt.subplots()    
figure.set_size_inches(3, 3) #Changes the size of the figure (image)
figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
canvas = _VARS['window'] ["movieImg"].Widget
figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


#RECOMMENDED MOVIES FIGURES:
recommendedFigures, recommendedAxes = plt.subplots(2, 4, figsize=(8,10))
recommendedAxes = recommendedAxes.flatten()
recommendedFigures.subplots_adjust(left=0, bottom=0, right=1, top=0.9, wspace=0.2, hspace=0.2)
recommendedCanvas = _VARS['window'] ["similarMovieImg"].Widget
recommended_figure_canvas_agg = FigureCanvasTkAgg(recommendedFigures, recommendedCanvas)
recommended_figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

plt.rcParams["font.family"] = "Helvetica"

def recommended_draw_image(result): #Given an index (of the data frame), find the movie's poster URL and display the jpeg image
    for i, j in enumerate(result.poster_path):
        recommendedAxes[i].cla() #Clear the axes
        recommendedAxes[i].axis('off')
        url = "https://image.tmdb.org/t/p/w500/" + j
        img = io.imread(fname = url) #Read the image using skimage
        recommendedAxes[i].imshow(img, aspect='auto') 
        recommendedAxes[i].axis('scaled')
        recommendedFigures.set_facecolor('#ADB6D1') #Background color of the figure to match the color theme of the GUI
        text = result.iloc[i].title.split()
        title = text[0]
        length = 30
        for item in text[1:]:
            if (len(title) + len(item) < length):
                title += " " + item
            else:
                title += "\n" + item
                length += 30
        recommendedAxes[i].set_title(title, fontdict={'fontsize': 9}, wrap=True)
        recommendedAxes[1].autoscale_view('tight')
    recommended_figure_canvas_agg.draw()
    return recommended_figure_canvas_agg

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = _VARS['window'].read(timeout = 10)
    if calculateSimilarities == True:
        temp_df, similarMovies = get_similiarity(df, selectedMovie, movieID, languageReq, int(plotPreference), int(genrePreference), int(castPreference))
        calculateSimilarities = False #End the loop (to stop recalculating similarity)
        displayMovies = True

    if displayMovies == True:
        _VARS['window']['similarMoviesText'].update(visible = True) #Update cases to make this false later
        _VARS['window']['sortTypes'].update(visible = True) #Update cases to make this false later
        _VARS['window']['sort'].update(visible = True) #Update cases to make this false later
        
    if event == 'sort':
        typeToSort = values['sortTypes']
        #Call -- sort(temp_df, similarMovies, typeToSort)
        initializeSort(temp_df, similarMovies, typeToSort)
        
        #REMOVE THIS LATER!!!
        sim_scores = sorted(similarMovies, key=lambda x: x[1], reverse=True) # Sort the movies based on the similarity scores
        sim_scores = sim_scores[1:10] # Get the scores of the 10 most similar movies
        for item in sim_scores:
            print(df.iloc[item[0]]["title"])
        #ABOVE REMOVE
        movie_indices = [i[0] for i in sim_scores]
        result = df.iloc[movie_indices]
        try:
            _VARS['window']['similarMovieImg'].update(visible = True)
            recommended_draw_image(result)  #Display the image, if it fails (maybe invalid poster URL or missing poster URL in the csv file) then it doesn't draw
        except:
            pass
        displayMovies = False

    if event == sg.WIN_CLOSED or event == 'Close': #If user closes window or clicks cancel
        break

    elif event == 'Reset Search': #If user resets search (clear all of the elements and make some invisible so it matches the default setting)
        for item in reset_keys:
            _VARS['window'][item].update(visible = False)
        for item in preferences:
            _VARS['window'][item].update(value = '')
        _VARS['window']['searchResult'].update('')
        _VARS['window']['userInput'].update('')
        _VARS['window']['langOptions'].update('')
        selectedMovie = ""
        calculateSimilarities = False
        displayMovies = False
        movieID = None

    elif event == 'dateButton': #If user enters a date to specify which movie they want if there are duplicate movies with the same user inputted name
        dateSpecifier = values['dateInfo'] #Store the date string
        newIndices = [] #Store the indices of the movies with the specific release date
        newIndices[:] = [x for x in indices if df['release_date'][x] == dateSpecifier]  #Movies that have the specified title and date
        if(len(newIndices) == 0): #If movie doesn't exist (invalid date)
            _VARS['window']['dateInfo'].update('Enter a valid date!')
        else:
            _VARS['window']['searchResult'].update('Successfully found the movie \"' + df['title'][newIndices[0]] + '\".') #There's only one match so print it
            selectedMovie = df['title'][newIndices[0]]
            movieID = df['id'][newIndices[0]]
            try:
                _VARS['window']['movieImg'].update(visible = True)
                draw_image(newIndices[0])  #Display the image
            except:
                pass
            _VARS['window']['dateInfo'].update(visible = False)
            _VARS['window']['dateButton'].update(visible = False)
            _VARS['window']['preferencesDescription'].update(visible = True)
            _VARS['window']['preferencesDescription'].update('Please enter your movie preferences below based on their similarity to the movie \"' + df['title'][newIndices[0]] + '\".\n1 means no preference and 5 means a significant preference.')
   
    elif event == 'Find': #If user tries to find a movie
        calculateSimilarities = False
        displayMovies = False
        # _VARS['window']['gif'].update(visible = False)
        # _VARS['window']['loading'].update(visible = False)
        if values['userInput']: #If input text is NOT empty
            _VARS['window']['dateInfo'].update('')
            rawMovieInput = values['userInput'] #Store the user input movie title
            movieInput = ''.join(filter(str.isalnum, rawMovieInput)) #Filter the movie title so its just alphanumeric (a-Z and 0-9, no punctuation)
            indices = [i for i, x in enumerate([str(item).lower() for item in df['title_no_spaces']]) if x == movieInput.lower()] #List of indices of all movies with this title
            if len(indices) > 1: #If there is more than one movie with this title
                dates = ""
                selectedMovie = False
                for index, item in enumerate(indices[0:-1]):
                    dates += df['release_date'][item] + ", " #Create a string of all the release dates of the duplicate title movies
                    if ((index + 1) % 4 == 0):
                        dates += "\n"
                dates += df['release_date'][indices[-1]] 
                #All of these movies have the same title (except punctuation), but just let the movie title be the first one in the list
                _VARS['window']['searchResult'].update('There are multiple movies titled \"' + df['title'][indices[0]] + '\".\nWhat is the movie\'s release date?\n' + dates)
                _VARS['window']['dateInfo'].update(visible = True)
                _VARS['window']['dateButton'].update(visible = True)
                _VARS['window']['preferencesDescription'].update(visible = False)
                _VARS['window']['movieImg'].update(visible = False)
                for item in preferences:
                    _VARS['window'][item].update(value = '')
            elif len(indices) == 1: #If there is just one movie with this title
                idx = indices[0]
                _VARS['window']['searchResult'].update('Successfully found the movie \"' + df['title'][idx] + '\"')
                _VARS['window']['dateInfo'].update(visible = False)
                _VARS['window']['dateButton'].update(visible = False)
                selectedMovie = df['title'][idx]
                movieID = df['id'][idx]
                try:
                    _VARS['window']['movieImg'].update(visible = True)
                    draw_image(idx)  #Display the image, if it fails (maybe invalid poster URL or missing poster URL in the csv file) then it doesn't draw
                except:
                    pass
                _VARS['window']['preferencesDescription'].update(visible = True)
                _VARS['window']['preferencesDescription'].update('Please enter your movie preferences below based on their similarity to the movie \"' + df['title'][idx] + '\".\n1 means no preference and 5 means a significant preference.')
            else: #No movies with the user input title
                for item in reset_keys:
                    _VARS['window'][item].update(visible = False)
                _VARS['window']['searchResult'].update('Unfortunately we cannot find the movie \"' + rawMovieInput + '\".\nPlease ensure you typed it correctly or try another movie.')
                selectedMovie = ""
                movieID = None

    elif event == 'go' and (values['langOptions'] == 'Yes' or values['langOptions'] == 'No'): #If user completes movie info and tries to find the recommended movies
        languageReq = values['langOptions']
        calculateSimilarities = True
        displayMovies = False
        plotPreference = values['plot']
        genrePreference = values['genre']
        castPreference = values['cast']
    
    elif selectedMovie and any(values[item] != '' and '1' > values[item]  or values[item] > '5' for item in preferences): #If one of the preference inputs is outside the range [1,5]
        _VARS['window']['lang'].update(visible = True)
        _VARS['window']['lang'].update('Please enter numbers between 1 and 5 for your preferences') 
        _VARS['window']['langOptions'].update(visible = False)
        _VARS['window']['go'].update(visible = False)

    elif selectedMovie and all('1' <= values[item] <= '5' for item in preferences): #If all of the prefernce inputs are inside the range [1,5]
        _VARS['window']['lang'].update(visible = True)
        _VARS['window']['lang'].update('Do you want to only find movies in the same language as \"' + selectedMovie + '\"?') 
        _VARS['window']['langOptions'].update(visible = True)
        _VARS['window']['go'].update(visible = True)
        
    for item in preferences_keys:
        _VARS['window'][item].update(visible = bool(selectedMovie))

_VARS['window'].close()