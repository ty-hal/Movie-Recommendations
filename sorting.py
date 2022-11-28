def initializeSort(df, similarMovies, typeToSort):
    listToSort = []
    # 'Rating', 'Release Date', 'Popularity', 'Runtime', 'Most Similar'
    key = {'Rating' : 'vote_average', 'Release Date' : 'release_date', 'Popularity' : 'popularity', 'Runtime' : 'runtime'}
    for idx, item in similarMovies:
        if (typeToSort == 'Most Similar'):
            listToSort.append([df.iloc[idx]["index"], item, df.iloc[idx][key[typeToSort]]])
        else:
            listToSort.append([df.iloc[idx]["index"], item])
    print(listToSort)
    return listToSort

