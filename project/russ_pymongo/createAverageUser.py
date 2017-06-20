#this script jsut averages out attributes of both elite users and normal users
#The goal of this is to test our bayes classifier with these average users to see how it classifies them

import json
#for generating graphs
import matplotlib.pyplot as plt
from pymongo import MongoClient #NOTE: example of fascade dp -- don't need all features of pymongo
#Mongo stores objects in bson format, need this to print
from bson import json_util

# put all elite users in a dict
def collectElite(connection, numberOfUsers):
  #query only for elite users, setting greater than 0 forces a year to exist in return query
  #31,461 users are 'elite' or were at one time or another
  users = connection.user.find({ 'elite': { '$exists': True, '$gt': 0 } }, timeout = True).limit(numberOfUsers);#timeout == False = keep curser open until program stops
  print("number of elites in cursor: " + str(users.count(with_limit_and_skip = True))) #include the limit parameter that has been set above
  return (users);
  
# put all non-elite users in a dict
def collectNormal(connection, numberOfUsers):
  #520,000 normal users in db 
  users = connection.user.find({ 'elite': { '$exists': True}, '$where' : 'this.elite.length < 1' }, timeout = True).limit(numberOfUsers);
  print("number of normals in cursor: " + str(users.count(with_limit_and_skip = True))) 
  return (users);

def average(sumOf, total):
    return(sumOf/total)

#collect averages for this kind of user
def createNormal(users):
    #compliments are pretty varied and numerous -- we could explore this but not necessary at this time
    #If go this route -- hash the type of compliment and count/divide -- not sure if these affect elite status or not
    numberOfReviews = 0;
    averageStars = 0;
    numberOfFriends = 0;
    numberOfFans = 0;
    funnyVotes = 0;
    coolVotes = 0;
    usefulVotes = 0;
    total = users.count(with_limit_and_skip = True)
    
    for user in users:
        numberOfReviews += user.get('review_count');
        averageStars += user.get('average_stars');
        numberOfFriends += len(user.get('friends'));
        numberOfFans += user.get('fans');
        usefulVotes += user.get('votes').get('useful');
        coolVotes += user.get('votes').get('cool');
        funnyVotes += user.get('votes').get('funny')
        
    numberOfReviews = average(numberOfReviews, total);
    averageStars = average(averageStars, total);
    numberOfFriends = average(numberOfFriends, total);
    numberOfFans = average(numberOfFans, total);
    usefulVotes = average(usefulVotes, total);
    coolVotes = average(coolVotes, total);
    funnyVotes = average(funnyVotes, total);
    
    print("number of reviews: " + str(numberOfReviews) + ", avg stars: " + str(averageStars) + ", Number of Friends: "+ str(numberOfFriends) +", Number of Fans: " + str(numberOfFans)
          + ", cool votes: " + str(coolVotes) + ", useful votes: " + str(usefulVotes) + ", funny votes: " + str(funnyVotes))
    

def main():
    #Number ofusers to analyze -- set to 0 to return all results in database
    analyze = 0;
    # Create a connection to the mongodb process
    # on default port of 27017 and localhost
    client = MongoClient();
    # Assign the yelpmining database to a variable
    db = client.yelpdb;
    #Collect elite users from db for all elite relevant functions
    eliteUsers = collectElite(db, analyze);
    #collect normal users
    normalUsers = collectNormal(db, analyze);
    
    createNormal(eliteUsers);
    createNormal(normalUsers);
    
    #close connection
    client.close();

if __name__ == '__main__':
  main()