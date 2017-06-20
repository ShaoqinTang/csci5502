import nltk
import math

from nltk.classify.scikitlearn import SklearnClassifier
from pymongo import MongoClient
from sklearn.linear_model import LogisticRegression, SGDClassifier

'''
Returns elite user ids
'''
def elite_userids(db):
    user_ids = db.user.find(
        {'elite':
         {'$exists': True, '$gt': 0}
         },
        {"review_count": 1, "average_stars" : 1, 
        "fans" : 1, "friends" : 1, "votes" : 1, "_id": 0}
        )
    return user_ids


'''
Returns non-elite user ids
'''
def non_elite_userids(db):
    user_ids = db.user.find(
        {'elite': []
         },
        {"review_count": 1, "average_stars" : 1, 
        "fans" : 1, "friends" : 1, "votes" : 1, "_id": 0}     
        )
    return user_ids


'''
Returns data from yelpmining database based on range n1, n2.
'''
def get_data_set(db, n1, n2):
    elite_n = elite_userids(db)
    non_elite_n = non_elite_userids(db)
    data_set = []

    for i in range(n1, n2):
    	if i <= n1:
	        for elite in elite_n:
	            data_set.append(({'review_count': elite['review_count']}, True))
	            data_set.append(({'average_stars': elite['average_stars']}, True))
	            data_set.append(({'fans': elite['fans']}, True))
	            data_set.append(({'friends': len(elite['friends'])}, True))
	            data_set.append(({'cool_votes': elite['votes'].get('cool')}, True))
	            data_set.append(({'useful_votes': elite['votes'].get('useful')}, True))
	            data_set.append(({'funny_votes': elite['votes'].get('funny')}, True))

	        for non_elite in non_elite_n:
	            data_set.append(({'review_count': elite['review_count']}, False))
	            data_set.append(({'average_stars': elite['average_stars']}, False))
	            data_set.append(({'fans': elite['fans']}, False))
	            data_set.append(({'friends': len(elite['friends'])}, False))
	            data_set.append(({'cool_votes': elite['votes'].get('cool')}, False))
	            data_set.append(({'useful_votes': elite['votes'].get('useful')}, False))	         
	            data_set.append(({'funny_votes': elite['votes'].get('funny')}, False))

    return data_set


def main():
    # Create a connection to the mongodb process
    # on default port of 27017 and localhost
    client = MongoClient()
    db = client.yelpmining

    number_elite_users = db.user.find(
        {'elite':
         {'$exists': True, '$gt': 0}
         }
        ).count()

    # train 80%
    n = math.ceil(number_elite_users * 0.8)
    print (n)

    training_set = get_data_set(db, 0, n)
    test_set = get_data_set(db, n + 1, number_elite_users)
    # Initialize logistic regression classifier
    LogisticRegression_classifier = SklearnClassifier(
        LogisticRegression(
            C=1.0,
            class_weight=None,
            dual=False,
            fit_intercept=True,
            intercept_scaling=1,
            penalty='l2',
            random_state=None,
            tol=0.0001))

    classifier = LogisticRegression_classifier.train(training_set)
    print(nltk.classify.accuracy(classifier, test_set))

if __name__ == '__main__':
    main()
