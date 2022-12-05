from datetime import date
import random

def initializeSort(df, similarMovies, typeToSort, sortOrder):
    listToSort = []
    key = {'Rating' : 'vote_average', 'Release Date' : 'release_date', 'Popularity' : 'popularity', 'Runtime' : 'runtime'}
    sim_scores = sorted(similarMovies, key=lambda x: x[1], reverse=sortOrder) # Sort the movies based on the similarity scores
    sim_scores = sim_scores[1:64] # Get the scores of the 50 most similar movies
    for item in sim_scores:
        index = item[0]
        similarityValue = item[1][0]
        if typeToSort == 'Similarity':
            listToSort.append([index, similarityValue])
        elif typeToSort == 'Release Date':
            sortValue = list(df.loc[df["index"] == index][key[typeToSort]])[0]
            listToSort.append([index, convert_date(sortValue)])
        else:
            sortValue = list(df.loc[df["index"] == index][key[typeToSort]])[0]
            listToSort.append([index, sortValue])
    return listToSort

def convert_date (date_to_convert):
    dateDict = {
        0: 0,# Years
        1: 0,# Months
        2: 0 # Days
    }
    count = 0
    string_to_convert = ""
    # Break apart the time stamp into components
    for i, char in enumerate(date_to_convert):
        if char == "-":
            dateDict[count] = int(string_to_convert)
            string_to_convert = ""
            count += 1
        elif i == len(date_to_convert)-1:
            string_to_convert += char
            dateDict[count] = int(string_to_convert)
        else:
            string_to_convert += char
    # use datetime library to figure out how many days after the year of the first movie ever made
    d1 = date(dateDict[0], dateDict[1], dateDict[2])
    d0 = date(1888, 1, 1) # date of the first movie ever made
    delta = d1 - d0
    return delta.days


"""
Quick Sort function and helpers 
"""


def quickSort(listToSort, end, sortOrder, start):
    if start < end:
        pivot = sort(listToSort, start, end)
        quickSort(listToSort, pivot - 1, sortOrder, start)
        quickSort(listToSort, end, sortOrder, pivot + 1)
    if not sortOrder:
        listToSort.reverse()
    return listToSort

def sort(listToSort, start, end):
    pivot = listToSort[end]

    element_pointer = start - 1

    for index in range(start, end):
        if listToSort[index][1] >= pivot[1]:
            element_pointer = element_pointer + 1

            (listToSort[element_pointer], listToSort[index]) = (listToSort[index], listToSort[element_pointer])
    (listToSort[element_pointer+1], listToSort[end]) = (listToSort[end], listToSort[element_pointer + 1])

    return element_pointer + 1
"""
Merge Sort Function and helpers  
"""
def mergeSort(listToSort, end, sortOrder, start=0):
    if start < end:
        mid = start + (end - start)//2
        mergeSort(listToSort, mid, sortOrder, start)
        mergeSort(listToSort, end, sortOrder, mid+1)
        merge(listToSort, start, mid, end)
    if not sortOrder:
        listToSort.reverse()
    return listToSort

def merge(listToSort, start, mid, end):
    temp_size1 = mid - start + 1
    temp_size2 = end - mid

    # Temp Array1
    temp_array1 = [0] * temp_size1
    for index1 in range(0, temp_size1):
        temp_array1[index1] = listToSort[start + index1]

    # Temp Array2
    temp_array2 = [0] * temp_size2
    for index2 in range(0, temp_size2):
        temp_array2[index2] = listToSort[mid + 1 + index2]

    index1 = 0
    index2 = 0
    merged_index = start

    while index1 < temp_size1 and index2 < temp_size2:
        if temp_array1[index1][1] >= temp_array2[index2][1]:
            listToSort[merged_index] = temp_array1[index1]
            index1 = index1 + 1
        else:
            listToSort[merged_index] = temp_array2[index2]
            index2 = index2 + 1
        merged_index = merged_index + 1

    while index1 < temp_size1:
        listToSort[merged_index] = temp_array1[index1]
        index1 = index1 + 1
        merged_index = merged_index + 1

    while index2 < temp_size2:
        listToSort[merged_index] = temp_array2[index2]
        index2 = index2 + 1
        merged_index = merged_index + 1
    return listToSort

def getSortingTime():
    return 1 + random.random()
