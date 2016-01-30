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
	Input:
		fileName:
		attribute:
	Output:
		a list of the values for the attribute given as input

	Source: https://pymotw.com/2/csv/
	Source: https://docs.python.org/2/library/csv.html
	'''
	if attribute not in ['open','high','low','close', 'last','volume']:
		return 1

	attributeValues = []
	f = open(fileName, 'r')
	reader = csv.DictReader(f)
	for row in reader:
		value = float(row[attribute])
		attributeValues.append(value)
	f.close()
	return attributeValues

def Mean(data):
    '''
    Input:
        data:

    Output:
        Return the average/mean of a list of floats
    '''
    return (sum(data)/len(data))

def StandardDeviation(data, mean):
    '''
    Input:
        data:
        mean:
    Output:


    Computes the standard deviation of the data with the
    mean of that data

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
    Input:
        values:
    '''
    originalAndNormalizedValues = []
    minValue = min(values)
    maxValue = max(values)
    for value in values:
        normalizedValue = (value - minValue)/(maxValue - minValue)
        originalAndNormalizedValues.append((value,normalizedValue))
    return originalAndNormalizedValues

def Z_Score(values):
    pass

def normalization ( fileName , attribute, normalizationType ):
    '''
    Input Parameters:
        fileName: The comma seperated file that must be considered for the normalization
        attribute: The attribute for which you are performing the normalization
        normalizationType: The type of normalization you are performing
    Output:
        For each line in the input file, print the original "attribute" value and "normalized" value seperated by <TAB> 
    '''
    #TODO: Write code given the Input / Output Paramters.

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
    #TODO: Write code given the Input / Output Paramters.

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
                            choices=['open','high','low','close/last','volume'],
                            required=False)
    parser.add_argument("-a2", type=str, 
                            help="Type of Attribute for filename2. Select either open or high or low or close/last or volume",
                            choices=['open','high','low','close/last','volume'],
                            required=False)



    args = parser.parse_args()

    if ( args.n and args.a1 ):
        normalization( args.f1 , args.n , args.a1 )
    elif ( args.f2 and args.a1 and args.a2):
        correlation ( args.a1 , args.f1 , args.a2 , args.f2 )
    else:
        print "Kindly provide input of the following form:\nDMPythonHW2.py -f1 <filename1> -a1 <attribute> -n <normalizationType> \nDMPythonHW2.py -f1 <filename1> -a1 <attribute> -f2 <filename2> -a2 <attribute>"
