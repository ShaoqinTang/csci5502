#!/usr/bin/env python3
'''
This script for naive bayes algorithm

Database name for Russ: 
  yelpdb

Collections already imported into database:
  business
  checkin
  review
  tip
  user
'''
import json
import nltk
#for generating graphs
import matplotlib.pyplot as plt
from pymongo import MongoClient #NOTE: example of fascade dp -- don't need all features of pymongo
#Mongo stores objects in bson format, need this to print
from bson import json_util


# put all elite users in a dict
def collectElite(connection, numberOfUsers):
  #query only for elite users, setting greater than 0 forces a year to exist in return query
  #31,461 users are 'elite' or were at one time or another
  #bounds checking
  if(numberOfUsers > 31461):
      numberOfUsers = 31461;
      
  users = connection.user.find({ 'elite': { '$exists': True, '$gt': 0 } }, timeout = True).limit(numberOfUsers);#timeout == False = keep curser open until program stops
  print("number of elites in cursor: " + str(users.count(with_limit_and_skip = True))) #include the limit parameter that has been set above
  return (users);
  
# put all non-elite users in a dict
def collectNormal(connection, numberOfUsers):
  #520,000 normal users in db 
  users = connection.user.find({ 'elite': { '$exists': True}, '$where' : 'this.elite.length < 1' }, timeout = True).limit(numberOfUsers);
  print("number of normals in cursor: " + str(users.count(with_limit_and_skip = True))) 
  return (users);

#usersFrom is the int position in the Cursor from which to start collecting users (ideally not one's in the training set)
def collectNormalTestSet(connection, usersFrom, numberOfUsers, users):
  #users = connection.user.find({ 'elite': { '$exists': True}, '$where' : 'this.elite.length < 1' }, timeout = True)[usersFrom:usersFrom + numberOfUsers];
  subset = users[usersFrom:numberOfUsers];
  return (subset);
  
#Runtime: O(n+m)
def createTrainingSet(eliteUsers, normalUsers):
  training_set = [];
  i = 0;
  j = 0;
  eliteLimit = eliteUsers.count(with_limit_and_skip = True);#pass limits here to speed up process
  normalLimit = normalUsers.count(with_limit_and_skip = True);#speed up
  
  
  #first add elite users
  while i < eliteLimit:
  #True and False are labels attached to training set data -- classifier will attempt to select the appropriate label based on new input
    eliteUser = eliteUsers.next()
    training_set.append(({#'average_stars': eliteUser['average_stars'],
                          'review_count': eliteUser['review_count'],
                          #'friends': len(eliteUser['friends']),
                          #'fans': eliteUser['fans'],
                          #'cool_votes': eliteUser['votes'].get('cool'),
                          #'useful_votes': eliteUser['votes'].get('useful'),
                          #'funny_votes': eliteUser['votes'].get('funny')
                          },
                           True))
    i += 1
    
  #Then add normal users (total may be different
  while j < normalLimit:
    normalUser = normalUsers.next()
    training_set.append(({#'average_stars': normalUser['average_stars'],
                          'review_count': normalUser['review_count'],
                          #'friends': len(normalUser['friends']),
                          #'fans': normalUser['fans'],
                          #'cool_votes': normalUser['votes'].get('cool'),
                          #'useful_votes': normalUser['votes'].get('useful'),
                          #'funny_votes': normalUser['votes'].get('funny')
                          },
                           False))
    j += 1
  
  #print (training_set) 
  
  return(training_set); 

#get uids of users
def getUIDS(users):
    uid = [];
    for user in users:
        uid.append(user['user_id']);
    return (uid);

#elite Status is to be either True or False as input
def createTestSet(users, eliteStatus):
    ts = [];
    for user in users:
        ts.append(({'average_stars': user['average_stars'],
                    'review_count': user['review_count'],
                    'friends': len(user['friends']),
                    'fans': user['fans'],
                    'cool_votes': user['votes'].get('cool'),
                    'useful_votes': user['votes'].get('useful'),
                    'funny_votes': user['votes'].get('funny')
                    },
                    eliteStatus))
    #be kind rewind                
    users.rewind();
    return(ts);

#pull reviews for this user
def reviews(connection, user):
    reviews = [];
    review = connection.review.find({'user_id':user});
    for r in review:
        reviews.append(r['text']);

    return reviews;

def main():
  '''
  #Number ofusers to analyze -- set to 0 to return all results in database
  analyze = 1;
  #array to store potential elite users -- i.e. misclassified normal users
  potential = [];
  # Create a connection to the mongodb process
  # on default port of 27017 and localhost
  client = MongoClient();
  # Assign the yelpmining database to a variable
  db = client.yelpdb;
  #Collect elite users from db for all elite relevant functions
  eliteUsers = collectElite(db, analyze);
  #collect normal users
  normalUsers = collectNormal(db, analyze);
  
  #create the training set for naive bayes
  ts = createTrainingSet(eliteUsers, normalUsers);
  #create a classifier
  classifier = nltk.NaiveBayesClassifier.train(ts)
  #classify the most average user:
  print (classifier.classify({'average_stars': 3.8, 'review_count': 240, 'friends': 57, 'fans': 15, 'cool_votes': 394, 'useful_votes': 616, 'funny_votes':337 })) # Should be true
  print (classifier.classify({'average_stars': 3.7, 'review_count': 14, 'friends': 3, 'fans': 0, 'cool_votes': 5, 'useful_votes': 16, 'funny_votes':5})) # Should be false
  #create a test set :First is a hardcoded example
  #test_set = [({'average_stars': 3.8, 'review_count': 240, 'friends': 57, 'fans': 15, 'cool_votes': 394, 'useful_votes': 616, 'funny_votes':337 }, True),
  #           (({'average_stars': 3.7, 'review_count': 14, 'friends': 3, 'fans': 0, 'cool_votes': 5, 'useful_votes': 16, 'funny_votes':5}, False))]
  
  #idea: create subset of users (cursor) and see how well the classifier holds up to this new set i.e. create a large test set
  user_set = collectNormalTestSet(db,225, 275,ts);#change 500 to analyze + 1 if want to check users that have not been predicted
  #test_set = createTestSet(user_set, False);
  #new way
  test_set = user_set;
  #grab the uids of users that should be considered for elite:
  #uids = getUIDS(user_set);
  
  print (nltk.classify.accuracy(classifier, test_set)) # Should be 100% accurate
  #try to classify some points
  #print (classifier.labels())
  
  #new idea -- try to find normal users going for elite status i.e. is they get misclassified then there's a good chance they're trying to become elite
  #TODO: store associated user ids somewhere for later access
  for i,data in enumerate(test_set):
      singleTest = [];
      singleTest.append(data);
      if((nltk.classify.accuracy(classifier, singleTest)) < 1):
          potential.append(uids[i]);
  
  #Normal users that are potentially becomming elite
  #get some of these users reviews and check google to see if they have become elite
  review = reviews(db, potential[4]);
  for r in review:
      print(r + "\n\n***********\n");
  print("user_id: "+potential[4]); 
  '''
  #pyplot graph creation below this line
  #single features
  #plot results of classifier -- TEST SET WAS 50% elite and %50 normal users -- 55000 profiles total because with large data sets you SHOULD test 10% of data set
  #title = 'Accuracy of Single Features'
  #labels = ['average_stars', 'review_count', 'friends', 'fans', 'cool_votes', 'useful_votes','funny_votes'];
  #x = [1,2,3,4,5,6,7];
  #y = [0.5104, 0.81778, 0.6317, 0.787, 0.8325, 0.8186, 0.7902];
  
  #double Features -- show best pairings to rate on (i.e. average_stars and x's best rating only (ignore rest))
  #plot results of classifier -- TEST SET WAS 50% elite and %50 normal users -- 55000 profiles total because with large data sets you SHOULD test 10% of data set
  #title = 'Accuracy of Feature Pairs'
  #labels = ['average_stars\ncool_votes', 'review_count\ncool_votes', 'friends\nreview_count', 'fans\nreview_count', 'cool_votes\nreview_count', 'useful_votes\nreview_count','funny_votes\nreview_count'];
  #x = [1,2,3,4,5,6,7];
  #y = [0.89, 0.92, 0.89, 0.91, 0.92, 0.918, 0.912];
  
  #best 3 Features
  #title = 'Accuracy of Three Features'
  #labels = ['average_stars\ncool_votes\nreview_count', 'review_count\ncool_votes\naverage_stars', 'friends\nreview_count\ncool_votes', 'fans\nreview_count\ncool_votes', 'cool_votes\nreview_count\naverage_stars', 'useful_votes\nreview_count\ncool_votes','funny_votes\nreview_count\ncool_votes'];
  #x = [1,2,3,4,5,6,7];
  #y = [0.937, 0.937, 0.929, 0.929, 0.937, 0.934, 0.93];
  
  #best 4 Features
  #title = 'Accuracy of Four Features'
  #labels = ['average_stars\ncool_votes\nreview_count\nuseful_vote', 'review_count\ncool_votes\naverage_stars\nuseful_vote', 'friends\nreview_count\ncool_votes\nuseful_vote', 'fans\nreview_count\ncool_votes\naverage_stars', 'cool_votes\nreview_count\naverage_stars\nuseful_vote', 'useful_votes\nreview_count\ncool_votes\naverage_stars','funny_votes\nreview_count\ncool_votes\naverage_stars'];
  #x = [1,2,3,4,5,6,7];
  #y = [0.941, 0.941, 0.939, 0.937, 0.941, 0.941, 0.937];
  
  #best 5 Features
  #title = 'Accuracy of Five Features'
  #labels = ['average_stars\ncool_votes\nreview_count\nuseful_vote\nfriends', 'review_count\ncool_votes\naverage_stars\nuseful_vote\nfriends', 'friends\nreview_count\ncool_votes\nuseful_vote\naverage_stars', 'fans\nreview_count\ncool_votes\naverage_stars\nuseful_vote', 'cool_votes\nreview_count\naverage_stars\nuseful_vote\nfriends', 'useful_votes\nreview_count\ncool_votes\naverage_stars\nfriends','funny_votes\nreview_count\ncool_votes\naverage_stars\nuseful'];
  #x = [1,2,3,4,5,6,7];
  #y = [0.943, 0.943, 0.943, 0.942, 0.943, 0.943, 0.94];
  
  #best 6 Features
  #title = 'Accuracy of Five Features'
  #labels = ['average_stars\ncool_votes\nreview_count\nuseful_vote\nfriends\nfans', 'review_count\ncool_votes\naverage_stars\nuseful_vote\nfriends\nfans', 'friends\nreview_count\ncool_votes\nuseful_vote\naverage_stars\nfans', 'fans\nreview_count\ncool_votes\naverage_stars\nuseful_vote\nfriends', 'cool_votes\nreview_count\naverage_stars\nuseful_vote\nfriends\nfans', 'useful_votes\nreview_count\ncool_votes\naverage_stars\nfriends\nfans','funny_votes\nreview_count\ncool_votes\naverage_stars\nuseful\nfriends'];
  #x = [1,2,3,4,5,6,7];
  #y = [0.943,0.943,0.943,0.943,0.943,0.943,0.942];
  
  #best 7 Features
  title = 'Accuracy of Five Features'
  labels = ['average_stars\ncool_votes\nreview_count\nuseful_vote\nfriends\nfans\nfun', 'review_count\ncool_votes\naverage_stars\nuseful_vote\nfriends\nfans\nfun', 'friends\nreview_count\ncool_votes\nuseful_vote\naverage_stars\nfans\nfun', 'fans\nreview_count\ncool_votes\naverage_stars\nuseful_vote\nfriends\nfun', 'cool_votes\nreview_count\naverage_stars\nuseful_vote\nfriends\nfans\nfun', 'useful_votes\nreview_count\ncool_votes\naverage_stars\nfriends\nfans\nfun','funny_votes\nreview_count\ncool_votes\naverage_stars\nuseful\nfriends\nfans'];
  x = [1,2,3,4,5,6,7];
  y = [0.942,0.942,0.942,0.942,0.942,0.942,0.942];
  
  '''
  #training accuracy as more labels are added
  title = 'Accuracy of Naive Bayes as Features Added'
  #labels = ['average_stars\ncool_votes\nreview_count\nuseful_vote\nfriends\nfans\nfun', 'review_count\ncool_votes\naverage_stars\nuseful_vote\nfriends\nfans\nfun', 'friends\nreview_count\ncool_votes\nuseful_vote\naverage_stars\nfans\nfun', 'fans\nreview_count\ncool_votes\naverage_stars\nuseful_vote\nfriends\nfun', 'cool_votes\nreview_count\naverage_stars\nuseful_vote\nfriends\nfans\nfun', 'useful_votes\nreview_count\ncool_votes\naverage_stars\nfriends\nfans\nfun','funny_votes\nreview_count\ncool_votes\naverage_stars\nuseful\nfriends\nfans'];
  x = [1,2,3,4,5,6,7];#number of labels
  avg_stars = [0.5104, 0.89,0.937,0.941,0.943,0.943,0.942];#y values for avg number of stars
  review_count = [0.81778, 0.92, 0.937, 0.941, 0.943, 0.943, 0.942];
  friends = [0.6137,0.89,0.929,0.939,0.943,0.943,0.942];
  fans = [0.787,0.91,0.929,0.937,0.943,0.943,0.942];
  cool = [0.8325,0.92,0.937,0.941,0.943,0.943,0.942];
  useful = [0.8186,0.918,0.934,0.941,0.943,0.943,0.942];
  funny = [0.7902,0.912,0.93,0.937,0.94,0.942,0.942];
  '''
  
  #colors for line graph (trends)
  colors = ['red','blue', 'green', 'orange', 'purple', 'pink', 'black'];
  #lineStyle
  ls = '--';
  plt.figure(figsize=(25,20))#set window size
  plt.title(title, fontweight='bold')
  plt.grid(True)
  plt.plot(x, y, 'ro')
  for i, txt in enumerate(y):
    plt.annotate(txt, (x[i],y[i]))
  '''
  #avg_stars
  plt.plot(x, avg_stars, 'ro', label='average_stars',linestyle=ls, color=colors[0], linewidth=3)
  #annotate the points with actual values
  for i, txt in enumerate(avg_stars):
    plt.annotate(txt, (x[i],avg_stars[i]))
    
  #review Count
  plt.plot(x, review_count, 'ro', label='review_count',linestyle=ls, color=colors[1], linewidth=3)
  #annotate the points with actual values
  for i, txt in enumerate(review_count):
    plt.annotate(txt, (x[i],review_count[i]))
    
  #friends
  plt.plot(x, friends, 'ro', label='friends',linestyle=ls, color=colors[2], linewidth=3)
  #annotate the points with actual values
  for i, txt in enumerate(friends):
    plt.annotate(txt, (x[i],friends[i]))
    
  #fans
  plt.plot(x, fans, 'ro', label='fans', linestyle=ls, color=colors[3], linewidth=3)
  #annotate the points with actual values
  for i, txt in enumerate(fans):
    plt.annotate(txt, (x[i],fans[i]))
    
  #cool
  plt.plot(x, cool, 'ro', label='cool_votes', linestyle=ls, color=colors[4], linewidth=3)
  #annotate the points with actual values
  for i, txt in enumerate(cool):
    plt.annotate(txt, (x[i],cool[i]))
    
  #useful
  plt.plot(x, useful, 'ro', label='useful_votes', linestyle=ls, color=colors[5], linewidth=3)
  #annotate the points with actual values
  for i, txt in enumerate(useful):
    plt.annotate(txt, (x[i],useful[i]))
    
  #funny
  plt.plot(x, funny, 'ro', label='funny_votes', linestyle=ls, color=colors[6], linewidth=3)
  #annotate the points with actual values
  for i, txt in enumerate(funny):
    plt.annotate(txt, (x[i],funny[i]))
  '''
  plt.xticks(x, labels, rotation='vertical', fontweight='bold')
  # Pad margins so that markers don't get clipped by the axes
  plt.margins(0.2)
  # Tweak spacing to prevent clipping of tick-labels
  plt.subplots_adjust(bottom=0.15);
  plt.xlabel('Number of Features');
  plt.ylabel('Accuracy of Test Set');
  plt.legend();
  #plt.show();
  plt.savefig("./Documents/graphs/seven_label_accuracy.png",dpi=300)
  plt.close();
  
  #close connection
  #client.close();

if __name__ == '__main__':
  main()