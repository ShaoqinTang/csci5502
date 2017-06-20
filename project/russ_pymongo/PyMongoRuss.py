#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Database name for Russ: 
  yelpdb

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
'''
import json
import difflib #for computing delta of 2 strings
from pymongo import MongoClient
#Mongo stores objects in bson format, need this to print
from bson import json_util

# put all elite users in a dict
def collectElite(connection):
  #query only for elite users, setting greater than 0 forces a year to exist in return query
  #31,461 users are 'elite' or were at one time or another
  users = connection.user.find({ 'elite': { '$exists': True , '$gt': 0 } }, timeout=True);#false = keep curser open until program stops
  return (users);

# put all elite users in a dict -- SOME ELITE USERS ONLY WROTE A SINGLE REVIEW
def collectReviews(connection, users):
  
  #Array of cursors pertaining to elite users
  cursorArray = []
  
  for user in users:
    userid = user.get('user_id');
    reviews = connection.review.find({ 'user_id': userid});
    cursorArray.append(reviews);
  
  #So far only way to grab individuals reviews for comparisons -- just show first 2 elems
  for rev in cursorArray:
    for text in rev:
      print('User: ' + text.get('user_id') + ': ' + text.get('text') + '\n');
    rev.rewind();
  
  #be kind, rewind
  users.rewind();
  
  return (cursorArray);

# find input users elite friends
def findEliteFriends(users):
  #hash table to store elite friend relations
  eliteHash = {};
  totalEliteFriends = 0;

  # Query the first two users in the user collection
  #users = db.user.find()[0:2]

  #hash users
  for user in users:	
    #format the data for printing
    #print (json.dumps(user, sort_keys=True, indent=4, default=json_util.default))
    #Get the user specific data by key
    userid = (user.get('user_id'));
    #hash user -- user initially has 0 other elite friends
    eliteHash[userid] = 0;
	
  #rewind cursor for next query
  users.rewind();
  
  #find elite friends of users
  for user in users:
    #check for hashed users
    friends = (user.get('friends'));
    #Look for friends in hashtable of this user
    for i in friends:
       #if friend exists in hash table--they are elite--update hash val
       if i in eliteHash:
          userid = (user.get('user_id'));
          eliteHash[userid] += 1;
  
  #search hash table for average number of elite friends the elite have
  for key in eliteHash.keys():
     totalEliteFriends += eliteHash[key];
  
  #be kind, rewind
  users.rewind();
  
  return (totalEliteFriends/len(eliteHash));

# separate review text into a list
def getWords(text):
    return (text.split())

#ensure collectReviews() is working correctly, check one users reviews for discrepencies
def checkIndividualsReviews(connection, uid):
    #f = open('suspicious.txt', 'a');
    
    listoflists = []#to store all reviews as lists of text
    listofreviewids = []
    suspiciousreviews = []
    reviews = connection.review.find({ 'user_id': uid});
    
    #Check size of cursor -- if < 2 then stop 
    if(reviews.count() < 2):
        print("not enough reviews from this user to assess!")
        return;
    
    #start comparing reviews from this user
    else:
        for rev in reviews:
            #print(rev.get('text'));
            #note if want to just compare individual chars in a hash then just do listOne = list(rev.get('text'))
            listOne = list(getWords(rev.get('text')))
            listofreviewids.append(getWords(rev.get('business_id')))
            #idea -- list of lists or figure out how to cursor over everything
            listoflists.append(listOne)#just get into form that's easy ot work with
        #start comparing
        for i, dataOne in enumerate (listoflists):
            #Start at next position in array
            for dataTwo in (listoflists[i+1:]):
                #Return a measure of the sequences’ similarity as a float in the range [0, 1] -- if measure high enough do the more expensive ratio() function for more accurate measurement
                s = difflib.SequenceMatcher(None, dataOne, dataTwo) 
                if(s.quick_ratio() > .8):
                    print("!.!.!.!\n")

                    try:
                        suspiciousreviews.append(listofreviewids[i]);
                        suspiciousreviews.append(listofreviewids[i + 1]);
                        #f.write(uid + "\n FIRST: \n" + " ".join(dataOne) + "\n SECOND: \n" + " ".join(dataTwo) + "\n\n\n")
                        
                    except UnicodeEncodeError:
                        print("Can't write to file for some goddamn reason: USER IS" + uid + "\n");
                        #Skip past unicode issues -- might be using a foreign language not recognized by ascii
                        pass
        print("done getting reviews");
    
    #Halt writing    
    #f.close();
    
    return (suspiciousreviews);
     
# check user reviews for similarities
#runs about 16 hours -- started at 3pm prev. day ended at 7pm day after:
def reviewSimilarities(connection, users):
    for user in users:
        checkIndividualsReviews(connection, user.get("user_id"))
    return;

#remove duplicate data
def cleanDuplicateSuspicious():
    f = open('./textResults/suspiciousUsers.txt', 'r');
    found = False;
    original = f.readlines();
    f.close();
    
    clean = [];
    
    for user in original:
        for check in clean:
            if(user == check):
                found = True;
        #user not yet in array
        if(found == False):
            clean.append(user);
        found = False;
        
    #write cleaned data to new file
    f2 = open('clean.txt','a');
    for u in clean:
        f2.write(u);
                
    f2.close();
    
#pull reviews of suspicious user and write to file
def getSuspiciousReviews(connection):
    f = open('./textResults/clean.txt','r');
    f2 = open('temp.txt','a');
    users = f.readlines();
    
    print("getting this users reviews general: ");
    
    for user in users:
        f2.write("\n\n<<<<<<<<<<<<< user: " + user + " >>>>>>>>>>>>>>>>>" + "\n");
        #get business_ids of suspicious reviews
        suspiciousreviews = checkIndividualsReviews(connection, user.strip());#grab business id's of suspicious reviews
        #pull all reviews from this user
        reviews = connection.review.find({ 'user_id': user.strip()});
        for rev in reviews:
            try:
                for k in suspiciousreviews:
                    #got a suspicious review!
                    if(rev.get('business_id') == (''.join(k))):
                        votes = rev.get('votes');
                        f2.write("\nDATE:\n" + rev.get('date') + "\nBID:\n" + rev.get('business_id') + "\nTEXT:\n" + rev.get('text') 
                                + "\nVOTES\n" + "funny: " + str(votes.get('funny')) + " useful: " + str(votes.get('useful')) 
                                + " cool: " + str(votes.get('cool')) + "\n\n");
                        #prevent repeat reviews by removing element from suspiciousreviews
                        suspiciousreviews.remove(k);
                        break;#leave the loop
                        
            except UnicodeEncodeError:
                print("oh no! unicode error!");
                pass;
    f.close();
    f2.close();

#pull reviews and check business locations against review BID's
def businessReviewLocations(connection):
    cityHash = {};
    print("getting business locations (cities)");
    #suspicion -- same 5 cities so just hash results and check the numbers in the table after 
    business = connection.business.find();
    for rev in business:
        city = (rev.get('state'));
        #if in hash update -- else add 1 to count
        if(city not in cityHash):
            cityHash[city] = 1;
        
        else: 
            cityHash[city] += 1;
    
    #output results
    for key, value in cityHash.items():
        print("City: " + key + "; number of businesses: " + str(value));

def reviewsWrittentoReviewsInDB(connection, user):
  #check number of reviews this user wrote: example user: 18kPq7GPye-YQ3LyKyAZPw
  
  reviews = connection.review.find({ 'user_id': user});
  reviewsWritten = connection.user.find({ 'user_id': user});
  
  print("this user has: " + str(reviews.count()) + " reviews stored in the db")
  
  for j in reviewsWritten:
      print ("This user has written: " + str(j.get('review_count')) + " reviews")
      
def main():
  # Create a connection to the mongodb process
  # on default port of 27017 and localhost
  client = MongoClient();
  # Assign the yelpmining database to a variable
  db = client.yelpdb;
  #Collect elite users from db for all elite relevant functions
  users = collectElite(db);
  
  #Average number of fellow elite friends an elite has:
  print("The Average number of Elite friends to have: ",findEliteFriends(users));
  
  #reviewSimilarities(db, users);
  #collectReviews(db, users);
  #getSuspiciousReviews(db);
  #businessReviewLocations(db);
  #reviewsWrittentoReviewsInDB(db,'18kPq7GPye-YQ3LyKyAZPw')
  
  #close connection
  client.close();

if __name__ == '__main__':
  main()