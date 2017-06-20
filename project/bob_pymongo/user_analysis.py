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
  
Notes about data:

  1. All of the user_ids in the users collection are contained in the reviews
    collection.
  2. The number of business_ids found in the reviews collection is 77079 but 
    the number of business_ids found in the businesses collection is 77445.  
    This means not all businesses have reviews.
  
Hypotheses:

  1. How many users have traveled? 
    - Look to see if user has reviewed a business in multiple locations.  If 
      they review a business it is assumed they have been there.
      
    - ('Highest number of states a user has been to', 8)
    - ('Lowest number of states a user has been to', 1)
    - ('Total number of users', 552339)
    - ('Total number of users who have traveled', 28413)
      
  2. Can we figure out a user's home?
    - Look at location where the user has reviewed the most business.
    
    
  3. How many users gave multiple reviews for the same business?
  
  4. Do users who travel have the most reviews?
  
  5. Have any users reviewed a business in different states on the same day?
    
  
'''


import math
import numpy as np
from scipy.stats import chisquare
from pymongo import MongoClient

import matplotlib.pyplot as plt


def NumberOfUsersWhoHaveTraveled(db):
  users = db.user
  reviews = db.review
  businesses = db.business
  
  user_ids = []
  users = users.find()
#   users = users.find().sort([('user_id', -1)]).limit(10)
  
  print ('Going through users...')
  for user in users:
    user_ids.append(user['user_id'])  
  print ('Done with users.')
  
  userid_and_businessid_from_reviews = {}
#   business_ids = {}
  reviews = reviews.find()
#   reviews = reviews.find().sort([('user_id', -1)]).limit(10)
    
  print ('Going through reviews...')  
  for review in reviews:
    
#     if review['business_id'] not in business_ids:
#       business_ids[review['business_id']] = 0
      
    if review['user_id'] not in userid_and_businessid_from_reviews:
      userid_and_businessid_from_reviews[review['user_id']] = [review['business_id']]
    else:
      userid_and_businessid_from_reviews[review['user_id']].append(review['business_id'])
  print ('Done with reviews.')
      
  # Check if all of the users ids from the users collection are contained in
  # business collection 
#   print (sorted(user_ids) == sorted(userid_and_businessid_from_review.keys()))
  
  businessid_and_state = {}
  businesses = businesses.find()
  
  print ('Going through businesses...')
  for business in businesses:
    if business['business_id'] not in businessid_and_state:
      businessid_and_state[business['business_id']] = [business['state']]
  print ('Done with businesses.')
  
  # Check if all of the businesses ids from the reviews collection are contained
  # in the business collection
#   print ('Comparing the lists of business ids...')
#   print sorted(business_ids.keys()) == sorted(businessid_and_state.keys())
#   print len(business_ids.keys()), len(businessid_and_state.keys())

  userid_and_states = {}
  
  print ('Matching user_ids with states they have traveled to...')
  for user_id, business_ids in userid_and_businessid_from_reviews.items():
    userid_and_states[user_id] = []
    for business_id in business_ids:
      if businessid_and_state[business_id] not in userid_and_states[user_id]:
        userid_and_states[user_id].append(businessid_and_state[business_id])
  print ('Done matching user_ids with states.')
  
  userid_and_states_count = []
  for states in userid_and_states.values():
    userid_and_states_count.append(len(states))
     
  
  print ('Highest number of states a user has been to', max(userid_and_states_count))
  print ('Lowest number of states a user has been to', min(userid_and_states_count))
  
  print ('Total number of users', len(userid_and_states_count))
  print ('Total number of users who have traveled', len([x for x in userid_and_states_count if x > 1]))


def main():
  # Create a connection to the mongodb process
  # on default port of 27017 and localhost
  client = MongoClient()

  
  # Assign the yelpmining database to a variable
  db = client.yelpmining
 
  NumberOfUsersWhoHaveTraveled(db)


if __name__ == '__main__':
  main()