'''
Starting database:
  mongod --dbpath data/db

Database name: 
  yelpmining

Collections already imported into database:
  business
  checkin
  review
  tip
  user


Start database:
  mongod --dbpath <path to data directory>

Stop database:
  Control-C in terminal where database was started 



Hypotheses:

  1. Does the number of attributes given by a business correlate to the number of stars a business has?
    - correlation coefficient = -0.112212854391, negatively correlated, the fewer the attributes
      the more stars a business has

  2. Does the number of reviews for a business correlate to the number of stars a business has?
    - correlation coefficient = 0.0193920014996, positively correlated, as number of reviews
      increase so does the number of stars
  
  3. Does the state a business is in correlate to the number of stars a business has?
    - chi-square = 
    
  4. What states have the most 5-star reviews?
    NV 3319, AZ 5872
    
  5. What states have the most 1-star reviews?
    AZ 479, NV 273
    
  6. What states have the most total reviews?
  NV 1063584, AZ 913588, NC 146513
  
'''
import math
import numpy as np
from scipy.stats import chisquare
from pymongo import MongoClient
import matplotlib.pyplot as plt


def Mean(data):
    return (sum(data)/len(data))


def StandardDeviation(data, mean):
    deviations = []
    for x in data:
        x = (x - mean)**2
        deviations.append(x)
    variance = sum(deviations)/len(deviations)
    return math.sqrt(variance)


def CorrelationCoefficient(A, B):
  correlation_coefficient = 0.0
  n = len(A)
  A_mean = Mean(A)
  B_mean = Mean(B)
  A_standard_deviation = StandardDeviation(A, A_mean)
  B_standard_deviation = StandardDeviation(B, B_mean)
  for a_i, b_i in zip(A,B):
    correlation_coefficient += (a_i-A_mean)*(b_i-B_mean)
  correlation_coefficient = correlation_coefficient/(n*A_standard_deviation*B_standard_deviation)
  return correlation_coefficient


def ExpectedFrequency(A, B):
  expected_freqency = {}
  joint_events = [(a_i, b_i) for a_i, b_i in zip(A,B)]
  n = len(joint_events)
  A_counts = {}
  B_counts = {}
  for a_i in A:
    if a_i not in A_counts:
      A_counts[a_i] = A.count(a_i)
  for b_i in B:
    if b_i not in B_counts:
      B_counts[b_i] = B.count(b_i)
  for event in joint_events:
    if event not in expected_freqency:
      expected_freqency[event] = (A_counts[event[0]]*B_counts[event[1]])/(n*1.0)
  return expected_freqency


def ObservedFreqency(A, B):
  observed_freqency = {}
  joint_events = [(a_i, b_i) for a_i, b_i in zip(A,B)]
  for event in joint_events:
    if event not in observed_freqency:
      observed_freqency[event] = joint_events.count(event)  
  return observed_freqency
  

def ChiSquare(A, B, observed_frequency, expected_frequency):
  chi_square = 0.0
  for event in observed_frequency:
    chi_square += ((observed_frequency[event]-expected_frequency[event])**2/expected_frequency[event])
  return chi_square  


def CorrelationBetweenBusinessStarsAndNumberAttributes(businesses):
  cursor = businesses.find({'$and': [{'stars': {'$ne': ''}},
                                     {'attributes': {'$ne': ''}}]})
  A = []
  B = []
  for business in cursor:
    A.append(business['stars'])
    B.append(len(business['attributes']))
  print ('Correlation between stars and the number of attributes for a business', CorrelationCoefficient(A, B))


def CorrelationBetweenBusinessStarsAndNumberReviews(businesses):
  cursor = businesses.find({'$and': [{'stars': {'$ne': ''}},
                                     {'review_count': {'$ne': ''}}]})
  A = []
  B = []
  for business in cursor:
    A.append(business['stars'])
    B.append(business['review_count'])
  print ('Correlation between stars and the number of reviews for a business', CorrelationCoefficient(A, B)) 
  x = np.array(A)
  y = np.array(B)
  # fit with np.polyfit
  m, b = np.polyfit(x, y, 1)
  a, = plt.plot(x,y,'.')
  b, = plt.plot(x, m*x + b, '-')
  plt.title('Correlation between stars and the number of reviews for a business')
  plt.xlabel('Number of stars per business')
  plt.ylabel('Number of reviews per business')
  plt.ylim(0,200)
  plt.legend([a,b], ['Businesses', 'Best fit line'])
  plt.savefig('results/correlation_businessstars_and_numreviews.png', dpi=300)


def CorrelationBetweenBusinessStarsAndState(businesses):
  cursor = businesses.find({'$and': [{'stars': {'$ne': ''}},
                                     {'state': {'$ne': ''}}]})
  A = []
  B = []
  for business in cursor:
    A.append(business['stars'])
    B.append(business['state'])  
  expected_frequency = ExpectedFrequency(A, B)
  observed_frequency = ObservedFreqency(A, B)
  print ('chi square', ChiSquare(A, B, observed_frequency, expected_frequency))
  print ('degrees of freedom', (len(set(A))-1)*(len(set(B))-1))
  scipy_expected = []
  scipy_observed = []
  for event in expected_frequency:
    scipy_expected.append(expected_frequency[event])
    scipy_observed.append(observed_frequency[event])
  chi_square, _ = chisquare(scipy_observed, scipy_expected)
  print ('scipy chi square', chi_square)
  

def StatesWithMostNStarReviews(businesses, n):
  cursor = businesses.find({'stars': n})
  
  A = []
  B = []
  
  for business in cursor:
    A.append(business['stars'])
    B.append(business['state'])
#     print business['stars'], business['state'], business['city']
  observed_frequency = ObservedFreqency(A, B)
  mean = Mean(observed_frequency.values())
  
  for event in observed_frequency:
    if observed_frequency[event] > mean:
      print (event[1], observed_frequency[event])

def StatesWithMostReviews(businesses):
  cursor = businesses.aggregate([{'$group': {'_id': '$state',
                                           'totalReviews': {'$sum': '$review_count'}}},
                               {'$sort' : {'totalReviews': -1}},
                               {'$limit': 3}])
  for business in cursor:
    print (business['_id'], business['totalReviews'])
  

def GetLatLongOfBusinesses(businesses):
  latitudes = []
  longitudes = []
  cursor = businesses.find()
  for business in cursor:
    latitudes.append(business['latitude'])
    longitudes.append(business['longitude'])
  return latitudes, longitudes


def main():
  # Create a connection to the mongodb process
  # on default port of 27017 and localhost
  client = MongoClient()

  
  # Assign the yelpmining database to a variable
  db = client.yelpmining
 
  businesses = db.business
  
#   CorrelationBetweenBusinessStarsAndNumberAttributes(businesses)
  CorrelationBetweenBusinessStarsAndNumberReviews(businesses)
#   CorrelationBetweenBusinessStarsAndState(businesses)

#   print ('States with most 5 star reviews.')
#   StatesWithMostNStarReviews(businesses, 5)

#   print ('States with most 1 star reviews.')
#   StatesWithMostNStarReviews(businesses, 1)

#   print ('States with most total reviews.')
#   StatesWithMostReviews(businesses)


if __name__ == '__main__':
  main()