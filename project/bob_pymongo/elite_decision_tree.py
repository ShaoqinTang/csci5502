import nltk
from pymongo import MongoClient
import matplotlib.pyplot as plt

def GetEliteUsers(db, number_of_users):
  # Maximum number of elite users
  if(number_of_users > 31461):
      number_of_users = 31461
  users = db.user
  users = users.find({'elite': {'$exists':True},'$where' : 'this.elite.length > 0'}).limit(number_of_users)
  return users

def GetNormalUsers(db, number_of_users):
  # Maximum number of normal users
  if(number_of_users > 520878):
    number_of_users = 520878
  users = db.user
  users = users.find({'elite': {'$exists':True},'$where' : 'this.elite.length < 1'}).limit(number_of_users)
  return users

def CreateTrainingSet(elite_users, normal_users, features_used):
#   print ('Creating training set.')
  training_set = []
  # allocate 90% of elite users for the training set
  i = 28315
  # Go through elite users
  while i > 0:
    features = {}
    elite_user = elite_users.next()
    if 'friends' in features_used:
      features['friends'] = len(elite_user['friends'])
    if 'useful_votes' in features_used:
      features['useful_votes'] = elite_user['votes'].get('useful')
    if 'funny_votes' in features_used:
      features['funny_votes'] = elite_user['votes'].get('funny')
    if 'cool_votes' in features_used:
      features['cool_votes'] = elite_user['votes'].get('cool')
    if 'average_stars' in features_used:
      features['average_stars'] = elite_user['average_stars']
    if 'fans' in features_used:
      features['fans'] = elite_user['fans']
    if 'review_count' in features_used:
      features['review_count'] = elite_user['review_count']
    training_set.append((features, True))
    i -= 1
  # allocate 90% of normal users for the training set
  j = 468791
  # Go through normal users
  while j > 0:
    features = {}
    normal_user = normal_users.next()
    if 'friends' in features_used:
      features['friends'] = len(normal_user['friends'])
    if 'useful_votes' in features_used:
      features['useful_votes'] = normal_user['votes'].get('useful')
    if 'funny_votes' in features_used:
      features['funny_votes'] = normal_user['votes'].get('funny')
    if 'cool_votes' in features_used:
      features['cool_votes'] = normal_user['votes'].get('cool')
    if 'average_stars' in features_used:
      features['average_stars'] = normal_user['average_stars']
    if 'fans' in features_used:
      features['fans'] = normal_user['fans']
    if 'review_count' in features_used:
      features['review_count'] = normal_user['review_count']
    training_set.append((features, False))
    j -= 1
#   print ('Training set created.')
  print ('Training set sample:', training_set[0])
  return training_set, normal_users, elite_users

def CreateTestSet(normal_users, elite_users, features_used):
  test_set = []
  try:
    # Add normal users to the test set
    while True:
      features = {}
      normal_user = normal_users.next()
      if 'friends' in features_used:
        features['friends'] = len(normal_user['friends'])
      if 'useful_votes' in features_used:
        features['useful_votes'] =normal_user['votes'].get('useful')
      if 'funny_votes' in features_used:
        features['funny_votes'] = normal_user['votes'].get('funny')
      if 'cool_votes' in features_used:
        features['cool_votes'] = normal_user['votes'].get('cool')
      if 'average_stars' in features_used:
        features['average_stars'] = normal_user['average_stars']
      if 'fans' in features_used:
        features['fans'] = normal_user['fans']
      if 'review_count' in features_used:
        features['review_count'] = normal_user['review_count']
      test_set.append((features, False))
  except StopIteration:
    pass
  try:
    # Add elite users to the test set
    while True:
      features = {}
      elite_user = elite_users.next()
      if 'friends' in features_used:
        features['friends'] = len(elite_user['friends'])
      if 'useful_votes' in features_used:
        features['useful_votes'] = elite_user['votes'].get('useful')
      if 'funny_votes' in features_used:
        features['funny_votes'] = elite_user['votes'].get('funny')
      if 'cool_votes' in features_used:
        features['cool_votes'] = elite_user['votes'].get('cool')
      if 'average_stars' in features_used:
        features['average_stars'] = elite_user['average_stars']
      if 'fans' in features_used:
        features['fans'] = elite_user['fans']
      if 'review_count' in features_used:
        features['review_count'] = elite_user['review_count']
      test_set.append((features, True))
  except StopIteration:
    pass
  print ('Test set sample:', test_set[0])
  return test_set

def FindDecisionTreeAccuracy(): 
  client = MongoClient()
  db = client.yelpmining
    
  number_of_users = 1000000
  normal_users = GetNormalUsers(db, number_of_users)
  elite_users = GetEliteUsers(db, number_of_users)
  features = [
            'review_count',
            'fans',
            'average_stars',
            'friends',
            'cool_votes',
            'useful_votes',
            'funny_votes'
            ]
  
  for original_feature in features:
    features_used = []
    features_used.append(original_feature)
    # Create a new list of features without the original feature
    nofeature = list(features)
    nofeature.remove(original_feature)
    print ('Original feature', original_feature)
    print ('Remaining features', nofeature)
    print ('Features used', features_used)
    training_set, normal_users, elite_users = CreateTrainingSet(elite_users, normal_users, features_used)
    test_set = CreateTestSet(normal_users, elite_users, features_used)
    print ('Training set and test set are correct size', (len(training_set)+len(test_set)) == 552339)
    classifier = nltk.DecisionTreeClassifier.train(training_set)
    features_used_classification_accuracy = nltk.classify.accuracy(classifier, test_set)
    print ('{0}\t{1}'.format(features_used, features_used_classification_accuracy))
    
    for feature in nofeature:
      # Reset elite and normal users
      elite_users.rewind()
      normal_users.rewind()
      features_used.append(feature)
      print ('Features used', features_used)
      training_set, normal_users, elite_users = CreateTrainingSet(elite_users, normal_users, features_used)
      test_set = CreateTestSet(normal_users, elite_users, features_used)
      print ('Training set and test set are correct size', (len(training_set)+len(test_set)) == 552339)
      classifier = nltk.DecisionTreeClassifier.train(training_set)
      features_used_classification_accuracy = nltk.classify.accuracy(classifier, test_set)
      print ('{0}\t{1}'.format(features_used, features_used_classification_accuracy))
      
    # Reset elite and normal users
    elite_users.rewind()
    normal_users.rewind() 

def main():
  GraphDecisionTreeAccuracy()
  
                    
  
def GraphDecisionTreeAccuracy():
  x = [1,2,3,4,5,6,7] # Number of features
  fans = [0.96612532362899, 0.9618344105878732, 0.9505911321130484,
          0.9508627088878026, 0.9512791266090924, 0.9505187116397805, 0.9505549218764144]
  review_count = [0.9668676334799848, 0.9618344105878732, 0.9505911321130484,
                  0.9508627088878026, 0.9512791266090924, 0.9505187116397805, 0.9505549218764144]
  average_stars = [0.9432404540763674, 0.952437854181377, 0.9505911321130484,
                   0.9508627088878026, 0.9512791266090924, 0.9505187116397805, 0.9505549218764144]
  friends = [0.9492694584759112, 0.9537052124635634, 0.9529629026125686,
             0.9508627088878026, 0.9512791266090924, 0.9505187116397805, 0.9505549218764144]
  cool_votes = [0.9679539405790016, 0.9500660836818569, 0.9503919758115619,
                0.9510799703076059, 0.9512791266090924, 0.9505187116397805, 0.9505549218764144]
  useful_votes = [0.9655821700794814, 0.9498126120254196, 0.9497220864338348,
                  0.950373870693245, 0.9505368167580975, 0.9505187116397805, 0.9505549218764144]
  funny_votes = [0.9633552405264968, 0.9473684210526315, 0.9466080060833197,
                 0.9473684210526315, 0.9474951568808502, 0.9502109246283924, 0.9505549218764144]
  colors = ['red', 'blue', 'green', 'magenta', 'cyan', 'yellow', 'black']
  ls = '--'
  
  plt.figure(figsize=(20,12))
  plt.plot(x, fans, marker='o', label='fans', linestyle=ls, color=colors[0], linewidth=2)
  for i, value in enumerate(fans):
    plt.annotate('%0.4f' % (value), (x[i], fans[i]), weight='bold')
  
  plt.plot(x, review_count, marker='o', label='review_count', linestyle=ls, color=colors[1], linewidth=2)
  for i, value in enumerate(review_count):
    plt.annotate('%0.4f' % (value), (x[i], review_count[i]), weight='bold')
    
  plt.plot(x, average_stars, marker='o', label='average_stars', linestyle=ls, color=colors[2], linewidth=2)
  for i, value in enumerate(average_stars):
    plt.annotate('%0.4f' % (value), (x[i], average_stars[i]), weight='bold')
    
  plt.plot(x, friends, marker='o', label='friends', linestyle=ls, color=colors[3], linewidth=2)
  for i, value in enumerate(friends):
    plt.annotate('%0.4f' % (value), (x[i], friends[i]), weight='bold')
  
  plt.plot(x, cool_votes, marker='o', label='cool_votes', linestyle=ls, color=colors[4], linewidth=2)
  for i, value in enumerate(cool_votes):
    plt.annotate('%0.4f' % (value), (x[i], cool_votes[i]), weight='bold')
    
  plt.plot(x, useful_votes, marker='o', label='useful_votes', linestyle=ls, color=colors[5], linewidth=2)
  for i, value in enumerate(useful_votes):
    plt.annotate('%0.4f' % (value), (x[i], useful_votes[i]), weight='bold')
    
  plt.plot(x, funny_votes, marker='o', label='funny_votes', linestyle=ls, color=colors[6], linewidth=2)
  for i, value in enumerate(funny_votes):
    plt.annotate('%0.4f' % (value), (x[i], funny_votes[i]), weight='bold')
  
  plt.legend()
  plt.grid(True)
  plt.xlim(xmin=0, xmax=8)
  plt.xlabel('Number of Features')
  plt.ylabel('Classifier Accuracy')
  plt.title('Accuracy of the Decision Tree classifier as more features are added.')
  plt.savefig('results/decision_tree_overall_accuracy.png', dpi=300)


if __name__ == '__main__':
    main()