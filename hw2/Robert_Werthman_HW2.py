'''
Robert Werthman
CSCI 5502
Homework 2
'''

#Assignment based on http://www.nasdaq.com/quotes/
#Feel free to use any libraries. 
#Make sure that the output format is perfect as mentioned in the problem.
#Also check the second row of the download dataset.
#If it follows a different format, avoid it or remove it.

import argparse
import csv
import math

def ReadInAttributeFromCSV(fileName, attribute):
    '''
    Opens and reads in data from a csv file

    Input:
        fileName: the file path to the file with the values to be read in
        attribute: the column of the file the values should be read in from
    Output:
        a list of the values for the attribute given as input

    Source: https://pymotw.com/2/csv/
    Source: https://docs.python.org/2/library/csv.html
    Source: https://stackoverflow.com/questions/2184955/test-if-a-variable-is-a-list-or-tuple
    '''

    attributeValues = []
    f = open(fileName, 'r')
    # Create a csv reader that stores the each column of the first line of the file
    # as keys and then the rest of the lines of each column as values for those keys
    reader = csv.DictReader(f)
    for row in reader:
        if attribute in row:
            value = float(row[attribute])
            attributeValues.append(value)
    f.close()
    return attributeValues

def Mean(data):
    '''
    Input:
        data: list of floating point values 

    Output:
        Return the average/mean of the list of floating point values
    '''
    return (sum(data)/len(data))

def StandardDeviation(data, mean):
    '''
    Computes the standard deviation of the data with the
    mean of that data

    Input:
        data: list of floating point values
        mean: average/mean of the list of floating point values
    Output:
        Returns the standard deviation of all the floating point values in the list

    Source: https://en.wikipedia.org/wiki/Standard_deviation
    '''
    deviations = []
    for x in data:
        x = (x - mean)**2
        deviations.append(x)
    variance = sum(deviations)/len(deviations)
    return math.sqrt(variance)


def Min_Max(values):
    '''
    Computes the min max normalization of a floating point value

    Input:
        values: list of floating point values to normalize
    Output:
        list of tuples where first element in tuple is original value
        and second element in tuple is min_max normalization of original value

    '''
    originalAndNormalizedValues = []
    minValue = min(values)
    maxValue = max(values)
    for value in values:
        normalizedValue = (value - minValue)/(maxValue - minValue)
        originalAndNormalizedValues.append((value,normalizedValue))
    return originalAndNormalizedValues

def Z_Score(values):
    '''
    Computes the z score normalization of a floating point value

    Input:
        values: list of floating point values to normalize
    Output:
        list of tuples where first element in tuple is original value
        and second element in tuple is min_max normalization of original value
    '''
    originalAndNormalizedValues = []
    mean = Mean(values)
    standardDeviation = StandardDeviation(values,mean)
    for value in values:
        normalizedValue = (value - mean)/standardDeviation
        originalAndNormalizedValues.append((value,normalizedValue))
    return originalAndNormalizedValues

def normalization ( fileName , normalizationType , attribute):
    '''
    Input Parameters:
        fileName: The comma seperated file that must be considered for the normalization
        attribute: The attribute for which you are performing the normalization
        normalizationType: The type of normalization you are performing
    Output:
        For each line in the input file, print the original "attribute" value and "normalized" value seperated by <TAB> 
    '''
    values = ReadInAttributeFromCSV(fileName, attribute)
    if normalizationType == 'z_score':
        values = Z_Score(values)
    elif normalizationType == 'min_max':
        values = Min_Max(values)

    for value in values:
        print '{0}\t{1}'.format(value[0],value[1])

def correlation ( attribute1 , fileName1 , attribute2, fileName2 ):
    '''
    Input Parameters:
        attribute1: The attribute you want to consider from file1
        attribute2: The attribute you want to consider from file2
        fileName1: The comma seperated file1
        fileName2: The comma seperated file2
        
    Output:
        Print the correlation coefficient 
    '''
    correlationCoefficient = 0.0
    A = ReadInAttributeFromCSV(fileName1, attribute1)
    B = ReadInAttributeFromCSV(fileName2, attribute2)
    n = len(A)
    AMean = Mean(A)
    BMean = Mean(B)
    AStandardDeviation = StandardDeviation(A, AMean)
    BStandardDeviation = StandardDeviation(B, BMean)

    for ai, bi in  zip(A,B):
        correlationCoefficient += (ai - AMean)*(bi - BMean)

    try:
        correlationCoefficient = correlationCoefficient/(n*AStandardDeviation*BStandardDeviation)
        print correlationCoefficient
    except ZeroDivisionError:
        print 'Cannot calculate the correlation coefficient because one of the standard deviations is zero.'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data Mining HW2')
    parser.add_argument('-f1', type=str,
                            help="Location of filename1. Use only f1 when working with only one file.",
                            required=True)
    parser.add_argument("-f2", type=str, 
                            help="Location of filename2. To be used only when there are two files to be compared.",
                            required=False)
    parser.add_argument("-n", type=str, 
                            help="Type of Normalization. Select either min_max or z_score",
                            choices=['min_max','z_score'],
                            required=False)
    parser.add_argument("-a1", type=str, 
                            help="Type of Attribute for filename1. Select either open or high or low or close/last or volume",
                            choices=['open','high','low','close','volume'],
                            required=False)
    parser.add_argument("-a2", type=str, 
                            help="Type of Attribute for filename2. Select either open or high or low or close/last or volume",
                            choices=['open','high','low','close','volume'],
                            required=False)



    args = parser.parse_args()

    if ( args.n and args.a1 ):
        normalization( args.f1 , args.n , args.a1)
    elif ( args.f2 and args.a1 and args.a2):
        correlation ( args.a1 , args.f1 , args.a2 , args.f2 )
    else:
        print "Kindly provide input of the following form:\nDMPythonHW2.py -f1 <filename1> -a1 <attribute> -n <normalizationType> \nDMPythonHW2.py -f1 <filename1> -a1 <attribute> -f2 <filename2> -a2 <attribute>"
