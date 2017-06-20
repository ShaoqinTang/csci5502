#!/usr/bin/env python3

'''
Database name for Vikas: 
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

1) Analyse credit card acceptance rate by business and see if that affects it's review.

'''
import json
import math;
from pymongo import MongoClient
#Mongo stores objects in bson format, need this to print
from bson import json_util


def find_card_accept_rate(reviews):
  count = 0;
  num_reviews = 0;
  accepts_cards = 0;
  no_cards = 0;
  for review in reviews:
    num_reviews += review.get('review_count')
    count += 1;
    attribute = review.get('attributes');
    if (attribute['Accepts Credit Cards'] == True):
      accepts_cards += 1;
    elif (attribute['Accepts Credit Cards'] == False):
      no_cards += 1;

  print("Average number of reviews a business gets = ", math.ceil(num_reviews/count))
  print("Percentage that accepts cards = ", math.ceil((accepts_cards/ (accepts_cards + no_cards)) * 100)); 

def main():
  # Create a connection to the mongodb process
  # on default port of 27017 and localhost
  client = MongoClient()
  db = client.yelpmining
 
  low = 1;
  high = 2;
  while high <= 5:
    print("Stars : ", low, "-", high)
    find_card_accept_rate(db.business.find(
      { "$and" : 
        [ {"stars" : 
            {"$gte": low, "$lte": high}
          }, 
          {"attributes.Accepts Credit Cards" : {"$exists" : "true"}}
        ]
      }, 
      {"review_count" : "true",  "attributes.Accepts Credit Cards": 1, "_id": 0}));
    low += 1;
    high += 1;

  #close connection
  client.close();

if __name__ == '__main__':
  main()