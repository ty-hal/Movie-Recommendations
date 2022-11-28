import PySimpleGUI as sg 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from skimage import io #For reading the movie images from URLs
import warnings
warnings.filterwarnings('ignore') # To prevent kernel from showing any warning

#To bypass error with loading images -- not ideal, but I couldn't find an easy fix
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

#VARS CONSTANTS:
_VARS = {'window': False,
         'fig_agg': False,
         'pltFig': False}

#Global variable
movieInput  = ""
selectedMovie = ""
plotPreference = 0
genrePreference = 0
ratingPreference = 0
popularityPreference = 0
releaseDatePreference = 0
runtimePreference = 0
castPreference = 0
sortOrder = ["Runtime", "User Rating", "Most Similar"] #etc (for formatting the top 10 similar movies)
languageReq = 'N' #Only certain language movies to show

preferences = ['plot', 'genre', 'cast']
preferences_keys = ['plotText', 'plot','genreText', 'genre', 'castText', 'cast']

sorting = ['score', 'releaseDate', 'popularity', 'runTime', 'similarity']

dateSpecifier = "" #If searched movie has multiple matches, this stores the user inputted date of the exact movie they want

def draw_figure(canvas, figure): #Draws a figure in the GUI
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
    
#Color theme of the GUI
sg.theme('BlueMono')   

#Read the processed movie data and store it as a data frame (df)
df = pd.read_csv('input/processed_movies.csv')

# ----------- Create the 2 layouts this Window will display -----------
layout1 = [[sg.Button('Reset Search'), sg.Button('Close')],
                [sg.Text('Enter a Movie You Like')],
                [sg.Input(key = 'userInput'), sg.Button('Find')],
                [sg.Text('', key = 'searchResult'), sg.Input(key = 'dateInfo', size = (15,1), visible = False), sg.Button('Enter', key = 'dateButton', visible = False)],
                [sg.Canvas(key='movieImg', background_color='#ADB6D1', visible = False)],
                [sg.Text('', key = 'preferencesDescription', visible = False)],
                [sg.Text('Plot', key = 'plotText', visible = False), sg.Combo(['1', '2', '3', '4', '5'], key='plot', visible = False), 
                        sg.Text('Genre', key = 'genreText', visible = False), sg.Combo(['1', '2', '3', '4', '5'], key='genre', visible = False), 
                        sg.Text('Main Cast', key = 'castText', visible = False), sg.Combo(['1', '2', '3', '4', '5'], key='cast', visible = False)],
                [sg.Text('', key = 'lang', visible = False), sg.Combo(['Yes', 'No'], key = 'langOptions', visible = False)],
                [sg.Button('Search for Similar Movies', key = 'go', visible = False)]]

layout2 = [[sg.Text('This is layout 2')],
           [sg.Button("YESSIR")],
           [sg.Input(key='-IN-')],
           [sg.Input(key='-IN2-')]]


# ----------- Create actual layout using Columns and a row of Buttons
layout = [[sg.Column(layout1, key='_layout1_'), sg.Column(layout2, visible=False, key='_layout2_')]]

# Create the Window
_VARS['window'] = sg.Window('Movie Recommendation GUI',
                            layout,
                            finalize=True,
                            resizable=True,
                            location=(100, 100),
                            element_justification="center")

#_VARS['window'].maximize()
figure, ax = plt.subplots()    
figure.set_size_inches(5, 4) #Changes the size of the figure (image)
canvas = _VARS['window'] ["movieImg"].Widget
figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def drawImage(idx): #Given an index (of the data frame), find the movie's poster URL and display the jpeg image
    ax.cla() #Clear the axes
    url = "https://image.tmdb.org/t/p/w500/" + df.loc[idx, "poster_path"]
    img = io.imread(fname = url) #Read the image using skimage
    ax.imshow(img) 
    ax.axis('off')
    #plt.title(selectedMovie)
    figure.set_facecolor('#ADB6D1') #Background color of the figure to match the color theme of the GUI
    figure_canvas_agg.draw()
    return figure_canvas_agg


test = False
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = _VARS['window'].read(timeout = 10)
    if event == sg.WIN_CLOSED or event == 'Close': #If user closes window or clicks cancel
        break

    elif event == 'Reset Search': #If user resets search (clear all of the elements and make some invisible so it matches the default setting)
        _VARS['window']['movieImg'].update(visible = False)
        _VARS['window']['searchResult'].update('')
        _VARS['window']['dateInfo'].update(visible = False)
        _VARS['window']['dateButton'].update(visible = False)
        _VARS['window']['preferencesDescription'].update(visible = False)
        _VARS['window']['userInput'].update('')
        _VARS['window']['lang'].update(visible = False)
        _VARS['window']['langOptions'].update(visible = False)
        _VARS['window']['go'].update(visible = False)
        selectedMovie = ""
        for item in preferences:
            _VARS['window'][item].update(value = '')

    elif event == 'dateButton': #If user enters a date to specify which movie they want if there are duplicate movies with the same user inputted name
        dateSpecifier = values['dateInfo'] #Store the date string
        newIndices = [] #Store the indices of the movies with the specific release date
        newIndices[:] = [x for x in indices if df['release_date'][x] == dateSpecifier]  #Movies that have the specified title and date
        if(len(newIndices) == 0): #If movie doesn't exist (invalid date)
            _VARS['window']['dateInfo'].update('Enter a valid date!')
        else:
            _VARS['window']['searchResult'].update('Successfully found the movie \"' + df['title'][newIndices[0]] + '\".') #There's only one match so print it
            selectedMovie = df['title'][newIndices[0]]
            try:
                _VARS['window']['movieImg'].update(visible = True)
                drawImage(newIndices[0])  #Display the image
            except:
                pass
            _VARS['window']['preferencesDescription'].update(visible = True)
            _VARS['window']['preferencesDescription'].update('Please enter your movie preferences below based on their similarity to the movie \"' + df['title'][newIndices[0]] + '\".\n1 means no preference and 5 means a significant preference.')
   
    elif event == 'Find': #If user tries to find a movie
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
                _VARS['window']['searchResult'].update('There are too many movies titled \"' + df['title'][indices[0]] + '\".\nWhat is the release date of the version you want?\n' + dates + '\nPlease enter its release date (YYYY-MM-DD):')
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
                try:
                    _VARS['window']['movieImg'].update(visible = True)
                    drawImage(idx)  #Display the image, if it fails (maybe invalid poster URL or missing poster URL in the csv file) then it doesn't draw
                except:
                    pass
                _VARS['window']['preferencesDescription'].update(visible = True)
                _VARS['window']['preferencesDescription'].update('Please enter your movie preferences below based on their similarity to the movie \"' + df['title'][idx] + '\".\n1 means no preference and 5 means a significant preference.')
            else: #No movies with the user input title
                _VARS['window']['movieImg'].update(visible = False)
                _VARS['window']['preferencesDescription'].update(visible = False)
                # _VARS['window']['lang'].update(visible = False)
                _VARS['window']['searchResult'].update('Unfortunately we cannot find the movie \"' + rawMovieInput + '\".\nPlease ensure you typed it correctly or try another movie.')
                selectedMovie = ""

    elif event == 'go' and values['langOptions'] != '': #If user completes movie info and tries to find the recommended movies
        languageReq = values['langOptions']
        print(languageReq)
        _VARS['window']['_layout1_'].update(visible = False)
        _VARS['window']['_layout2_'].update(visible = True)
        print("Searching")
    
    elif any(values[item] != '' and '1' > values[item]  or values[item] > '5' for item in preferences): #If one of the preference inputs is outside the range [1,5]
        _VARS['window']['lang'].update(visible = True)
        _VARS['window']['lang'].update('Please enter numbers between 1 and 5 for your preferences') 
        _VARS['window']['langOptions'].update(visible = False)
        _VARS['window']['go'].update(visible = False)
        test = True
    
    elif test:
        _VARS['window']['lang'].update(visible = False)
        test = False

    elif all('1' <= values[item] <= '5' for item in preferences): #If all of the prefernce inputs are inside the range [1,5]
        _VARS['window']['lang'].update(visible = True)
        _VARS['window']['lang'].update('Do you want to only find movies in the same language as \"' + selectedMovie + '\"?') 
        _VARS['window']['langOptions'].update(visible = True)
        _VARS['window']['go'].update(visible = True)
        
    for item in preferences_keys:
        _VARS['window'][item].update(visible = bool(selectedMovie))

_VARS['window'].close()