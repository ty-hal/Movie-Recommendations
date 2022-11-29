def initializeSort(df, similarMovies, typeToSort):
    listToSort = []
    key = {'Rating' : 'vote_average', 'Release Date' : 'release_date', 'Popularity' : 'popularity', 'Runtime' : 'runtime'}
    sim_scores = sorted(similarMovies, key=lambda x: x[1], reverse=True) # Sort the movies based on the similarity scores
    sim_scores = sim_scores[1:100] # Get the scores of the 50 most similar movies
    for item in sim_scores:
        index = item[0]
        similarityValue = item[1][0]
        if (typeToSort == 'Most Similar'):
            listToSort.append([index, similarityValue])
        else:
            sortValue = list(df.loc[df["index"] == index][key[typeToSort]])[0]
            listToSort.append([index, similarityValue, sortValue])
    return listToSort

def quickSort(listToSort, typeToSort):
    sortedList = []
    #sort the third (2nd index) elements of listToSort (a list of lists), which is either rating, release date, popularity, or runtime
    #I think you're going to have to do a separate case for release date because I think its like YYYY-MM-DD (not a number)
    return sortedList

def mergeSort(listToSort, typeToSort):
    sortedList = []
    return sortedList




