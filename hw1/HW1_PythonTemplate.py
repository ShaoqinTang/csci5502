#Assignment based on MAGIC Gamma Telescope Data Set ( http://archive.ics.uci.edu/ml/datasets/MAGIC+Gamma+Telescope )

import argparse
import sys
import numpy
import math

class dataSet:
    """
    Class to store the MAGIC Gamma Telescope Data Set
    """
    def __init__(self, location):
        with open (location, "r") as myfile:
            self.readData=myfile.readlines();

def splitData(data):
    '''
    Take each line of the data and split it into a 
    list delimited by a comma

    Creates a list of lists
    '''
    splitData = []
    for line in data:
        line = line.split(',')
        splitData.append(line)
    return splitData

def findIthData(data, ithAttribute):
    '''
    Go through the data and return a list 
    of the ith attribute for each line of the data
    '''
    ithData = []
    for line in data:
        line = line[ithAttribute-1]
        ithData.append(line)
    return ithData

def Mean(data):
    '''
    Return the average/mean of a list of floats
    '''
    return (sum(data)/len(data))

def Median(data):
    '''
    Find the medain value in the data

    Source: https://stackoverflow.com/questions/24101524/finding-median-of-list-in-python
    Source: https://en.wikipedia.org/wiki/Median
    '''
    data.sort()
    # Uneven length list
    if len(data) % 2 == 1:
        middleNumber = (len(data)-1)/2
        return data[middleNumber]
    # Even length list
    else:
        firstMiddleNumber = data[len(data)/2]
        secondMiddleNumber = data[len(data)/2 - 1]
        return (firstMiddleNumber + secondMiddleNumber)/2

def StandardDeviation(data, mean):
    '''


    Source: https://en.wikipedia.org/wiki/Standard_deviation
    '''
    deviations = []
    for x in data:
        x = (x - mean)**2
        print x
        deviations.append(x)
    variance = sum(deviations)/len(deviations)
    return math.sqrt(variance)



def calculate( data, ithAttribute):
    """
    Input Parameters:
        data: The data that is read from the file.
        ithAttribute: The ith Attribute for which the various properties must be calculated.

    Default value of 0,infinity,-infinity are assigned to all the variables as required. 
    Objective of the function is to calculate:  N (number of objects), min, max, mean, standard deviation, Q1, median, Q3, IQR
    """

    noOfObjects , minValue , maxValue , mean , standardDeviation , q1 , median , q3 ,iqr = [0,"inf","-inf",0,0,0,0,0,0]
    #TODO : Write code to assign the values to the respective variables.

    # Split each line of the data delimited by a comma into a list
    data = splitData(data)

    # set the data to a list of the the ith attribute of the data
    data = findIthData(data,ithAttribute)

    # Convert each element in the data from a string to a float
    # Source: https://stackoverflow.com/questions/3371269/call-int-function-on-every-list-element-in-python
    data = [float(x) for x in data]

    noOfObjects = len(data)
    minValue = min(data)
    maxValue = max(data)
    mean = Mean(data)
    median = Median(data)
    standardDeviation = StandardDeviation(data, mean)



    return noOfObjects , minValue , maxValue, mean, standardDeviation , q1 , median , q3 , iqr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data Mining HW1')
    parser.add_argument('--i', type=int,
                            help="ith attribute of the dataset ( limit 1 to 10 )",
                            default=5,
                            choices=set((1,2,3,4,5,6,7,8,9,10)) ,
                            required=True)
    parser.add_argument("--data", type=str, 
                            help="Location of the downloaded file",
                            default="magic04.data.txt", 
                            required=False)
    args = parser.parse_args()
    data = dataSet(args.data)

    print ','.join(map(str,calculate(data.readData,args.i)))
