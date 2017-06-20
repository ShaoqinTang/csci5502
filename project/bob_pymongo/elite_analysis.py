"""
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
  
  
Hypotheses

1. Where do elite users lives?  Do elite users tend to travel?
  - Total number of elite users who travel = 8003
  - Highest number of states a user has been to 7
  - Avg number of states visisted by an elite user is 1

2. Are they friends with a lot of elite users from the same city?

3. Is there a correlation between the number of reviews a user writes and 
   a user being elite?

4. Can we find any fake reviews based on check-in time and when reviews are
   written?
   
5. Do any elite users write multiple reviews for the same business?
  - Highest number of reviews written for the same business by a single user: 29
  - Number of users who have written multiple reviews for the same business: 4805

6. What are some interesting things about the number of reviews users have given?
  - Minimum number of reviews given by a single user: 1
  - Maximum number of reviews given by a single user: 10320
  - Average number of reviews given by a single user: 240
  - Number of elite users: 31,461
  
  
7. Naive Bayes
  Class Labels: Yes or No for elite user
  Features: review_count, average_stars
  
Sources: http://www.nltk.org/book/ch06.html

"""
from pymongo import MongoClient
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import itertools
import collections
from scipy.cluster.vq import kmeans2

def GetEliteUsers(db):
  """Return any user who has been elite
  """
  
  print ('Getting elite users.')
  users = db.user
  users = users.find({
                      'elite': {'$exists':True},
                      '$where' : 'this.elite.length > 0'
  })
  print ('Done getting elite users.')
  
  return users

def GetNonEliteUsers(db):
  """Return any user who has been elite
  """
  
  users = db.user
  users = users.find({
                      'elite': {'$exists':True},
                      '$where' : 'this.elite.length < 1'
  })
  
  return users


def NumberOfEliteUsersWhoHaveTraveled(db):
  users = GetEliteUsers(db)
  reviews = db.review
  businesses = db.business  
  
  userid_and_businessid_from_reviews = {}
  reviews = reviews.find()
  
  businessid_and_state = {}
  businesses = businesses.find()
  
  userid_and_states = {}
  userid_and_states_count = []
  
  print ('Getting all user ids...')
  for user in users:
    userid_and_businessid_from_reviews[user['user_id']] = []
  print ('Done with users.')
    
  print ('Associating user ids with all business ids reviews have been written for...')  
  for review in reviews:
    if review['user_id'] in userid_and_businessid_from_reviews:
      userid_and_businessid_from_reviews[review['user_id']].append(review['business_id'])
  print ('Done with reviews.')
  
  # Create one giant list of the business ids form each user id
  business_ids = list(itertools.chain(*userid_and_businessid_from_reviews.values()))
  for business_id in business_ids:
    businessid_and_state[business_id] = ''
  
  print ('Associating business ids with the state business is located in...')
  for business in businesses:
    if business['business_id'] in businessid_and_state:
      businessid_and_state[business['business_id']] = business['state']
  print ('Done with businesses.')
  
  print ('Matching user ids with states they have written reviews about businesses in...')
  for user_id, business_ids in userid_and_businessid_from_reviews.items():
    userid_and_states[user_id] = []
    for business_id in business_ids:
      if businessid_and_state[business_id] not in userid_and_states[user_id]:
        userid_and_states[user_id].append(businessid_and_state[business_id])
  print ('Done matching user ids with states.')
  
  for states in userid_and_states.values():
    userid_and_states_count.append(len(states))
     
  
#   print 'Highest number of states a user has been to', max(userid_and_states_count)
#   print 'Lowest number of states a user has been to', min(userid_and_states_count)
#   print 'Number of users', len(userid_and_states_count)
#   print 'Total number of users who have traveled', len([x for x in userid_and_states_count if x > 1])
#   print 'Average number of states a user has been to', sum(userid_and_states_count)/len(userid_and_states_count)
  
  PlotEliteUsersAndStatesVisited(userid_and_states_count)
  
def NumberOfNonEliteUsersWhoHaveTraveled(db):
  users = GetNonEliteUsers(db)
  reviews = db.review
  businesses = db.business  
  
  userid_and_businessid_from_reviews = {}
  reviews = reviews.find()
  
  businessid_and_state = {}
  businesses = businesses.find()
  
  userid_and_states = {}
  userid_and_states_count = []
  
  print ('Getting all user ids...')
  for user in users:
    userid_and_businessid_from_reviews[user['user_id']] = []
  print ('Done with users.')
    
  print ('Associating user ids with all business ids reviews have been written for...')  
  for review in reviews:
    if review['user_id'] in userid_and_businessid_from_reviews:
      userid_and_businessid_from_reviews[review['user_id']].append(review['business_id'])
  print ('Done with reviews.')
  
  # Create one giant list of the business ids form each user id
  business_ids = list(itertools.chain(*userid_and_businessid_from_reviews.values()))
  for business_id in business_ids:
    businessid_and_state[business_id] = ''
  
  print ('Associating business ids with the state business is located in...')
  for business in businesses:
    if business['business_id'] in businessid_and_state:
      businessid_and_state[business['business_id']] = business['state']
  print ('Done with businesses.')
  
  print ('Matching user ids with states they have written reviews about businesses in...')
  for user_id, business_ids in userid_and_businessid_from_reviews.items():
    userid_and_states[user_id] = []
    for business_id in business_ids:
      if businessid_and_state[business_id] not in userid_and_states[user_id]:
        userid_and_states[user_id].append(businessid_and_state[business_id])
  print ('Done matching user ids with states.')
  
  for states in userid_and_states.values():
    userid_and_states_count.append(len(states))
    
  PlotNonEliteUsersAndStatesVisited(userid_and_states_count)
    
def PlotNonEliteUsersAndStatesVisited(userid_and_states_count):
  number_of_bins = 8
  histogram_range = (0,8)
  plt.hist(userid_and_states_count,bins=number_of_bins,range=histogram_range)
  plt.xlabel('Number of States Visited')
  plt.ylabel('Frequency')
  plt.title('Histogram of the number of states visited by non elite users')
  
  plt.savefig('results/distribution_of_states_visited_by_non_elite_users.png', dpi=300)
  plt.close()
  
def PlotEliteUsersAndStatesVisited(userid_and_states_count):
  number_of_bins = 8
  histogram_range = (0,8)
  plt.hist(userid_and_states_count,bins=number_of_bins,range=histogram_range)
  plt.xlabel('Number of States Visited')
  plt.ylabel('Frequency')
  plt.title('Histogram of the number of states visited by elite users')
  
  plt.savefig('results/distribution_of_states_visited_by_elite_users.png', dpi=300)
  plt.close()
  
  
def MultipleReviewsWrittenForSameBusiness(db):
  users = GetEliteUsers(db)
  reviews = db.review.find()
  
  userid_and_businessid_from_reviews = {}
  
  for user in users:
    userid_and_businessid_from_reviews[user['user_id']] = []
    
  for review in reviews:
    if review['user_id'] in userid_and_businessid_from_reviews:
      userid_and_businessid_from_reviews[review['user_id']].append(review['business_id'])
  
  number_of_multiple_reviews_per_business_per_user = [] 
  number_of_users_who_have_written_multiple_reviews_for_the_same_business = {}
  for user_id, business_ids in userid_and_businessid_from_reviews.items():
    c = collections.Counter(business_ids)
    for _, count in c.items():
      if count > 1:
        number_of_multiple_reviews_per_business_per_user.append(count)
        number_of_users_who_have_written_multiple_reviews_for_the_same_business[user_id] = 0
        
#   print 'Highest number of reviews written for the same business by the same user', max(number_of_multiple_reviews_per_business_per_user)
#   print 'Number of users who have written multiple reviews for the same business', len(number_of_users_who_have_written_multiple_reviews_for_the_same_business.keys())

  
def KmeansEliteUsersAndReviewLocations(db):
  userid_and_businessid_from_reviews = {}
  businessid_and_locations = {}
  
  reviews = db.review.find()
  elite_users = GetEliteUsers(db)
  businesses = db.business.find()
  
  print ('Getting all user ids...')
  for user in elite_users:
    userid_and_businessid_from_reviews[user['user_id']] = []
  print ('Done with users.')
    
  print ('Associating user ids with all business ids reviews have been written for...')  
  for review in reviews:
    if review['user_id'] in userid_and_businessid_from_reviews:
      userid_and_businessid_from_reviews[review['user_id']].append(review['business_id'])
  print ('Done with reviews.')
  
  print ('Associating user ids with latitude and longitude of businesses...')
  business_ids = list(itertools.chain(*userid_and_businessid_from_reviews.values()))
  for business_id in business_ids:
    businessid_and_locations[business_id] = []
  
  for business in businesses:
    if business['business_id'] in businessid_and_locations:
      businessid_and_locations[business['business_id']].append([business['latitude'], business['longitude']])
  print ('Done with latitude and longitude.')

  
  business_locations = list(itertools.chain(*businessid_and_locations.values()))
  centroids, labels = kmeans2(business_locations, 3)
  
  colors = ([([0.4,1,0.4],[1,0.4,0.4],[0.1,0.8,1])[i] for i in labels])
    
  lon = []
  lat = []
  for business in business_locations:
    lat.append(business[0])
    lon.append(business[1])
    
  lonc = []
  latc = []
  for centroid in centroids:
    latc.append(centroid[0])
    lonc.append(centroid[1])
  
  ax = plt.axes(projection=ccrs.PlateCarree())
  ax.stock_img()
  plt.scatter(lon, lat, c=colors)
  
  plt.scatter(lonc, latc, marker='+', c='m')
  plt.title('K-means 3-centroid clustering of elite user review locations.')
  plt.savefig('results/cluster_elite_user_review_locations.png', dpi=300)
  plt.close()
  
def KmeansNormalUsersAndReviewLocations(db):
  userid_and_businessid_from_reviews = {}
  businessid_and_locations = {}
  
  reviews = db.review.find()
  normal_users = GetNonEliteUsers(db)
  businesses = db.business.find()
  
  print ('Getting all user ids...')
  for user in normal_users:
    userid_and_businessid_from_reviews[user['user_id']] = []
  print ('Done with users.')
    
  print ('Associating user ids with all business ids reviews have been written for...')  
  for review in reviews:
    if review['user_id'] in userid_and_businessid_from_reviews:
      userid_and_businessid_from_reviews[review['user_id']].append(review['business_id'])
  print ('Done with reviews.')
  
  print ('Associating user ids with latitude and longitude of businesses...')
  business_ids = list(itertools.chain(*userid_and_businessid_from_reviews.values()))
  for business_id in business_ids:
    businessid_and_locations[business_id] = []
  
  for business in businesses:
    if business['business_id'] in businessid_and_locations:
      businessid_and_locations[business['business_id']].append([business['latitude'], business['longitude']])
  print ('Done with latitude and longitude.')

  
  business_locations = list(itertools.chain(*businessid_and_locations.values()))
  centroids, labels = kmeans2(business_locations, 3)
  
  colors = ([([0.4,1,0.4],[1,0.4,0.4],[0.1,0.8,1])[i] for i in labels])
    
  lon = []
  lat = []
  for business in business_locations:
    lat.append(business[0])
    lon.append(business[1])
    
  lonc = []
  latc = []
  for centroid in centroids:
    latc.append(centroid[0])
    lonc.append(centroid[1])
  
  ax = plt.axes(projection=ccrs.PlateCarree())
  ax.stock_img()
  plt.scatter(lon, lat, c=colors)
  
  plt.scatter(lonc, latc, marker='+', c='m')
  plt.title('K-means 3-centroid clustering of normal user review locations.')
  plt.savefig('results/cluster_normal_user_review_locations.png', dpi=300)
  plt.close()
  
  
def main():
  # Create a connection to the mongodb process
  # on default port of 27017 and localhost
  client = MongoClient()

  # Assign the yelpmining database to a variable
  db = client.yelpmining

#   KmeansNormalUsersAndReviewLocations(db)
#   KmeansEliteUsersAndReviewLocations(db)
  
  NumberOfNonEliteUsersWhoHaveTraveled(db)
#   MultipleReviewsWrittenForSameBusiness(db)
#   NumberOfEliteUsersWhoHaveTraveled(db)
#   PlotEliteUsersAndNumberOfReviewsHistogram(elite_users)
#   elite_users.rewind()
#   InterestingThingsAboutNumberOfReviews(elite_users)
  

if __name__ == '__main__':
    main()