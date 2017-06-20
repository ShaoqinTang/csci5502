#!/usr/bin/env python3

'''
Database name for Ian: 
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

1) Create a scatterplot for number of reviews by user to investigate outliers

'''
import math
import matplotlib
import numpy as np
from pymongo import MongoClient
#Mongo stores objects in bson format, need this to print
from bson import json_util
from matplotlib import pyplot as plt

def getEliteUsers(db):
	print ('Getting elite users.')
	users = db.user
	users = users.find({
	    'elite': {'$exists':True},
	    '$where' : 'this.elite.length > 0'
	})
	print ('Done getting elite users.')
	
	return users
  
def getNonEliteUsers(db):
    users = db.user
    users = users.find({
        'elite': {'$exists':True},
        '$where' : 'this.elite.length < 1'
    })
  
    return users
    
def avgStarsBoxPlot(db):
	#users = getEliteUsers(db)
	users = getNonEliteUsers(db)
	avgStars = []
	print("Getting avg stars")
	for user in users:
		avgStars.append(user.get('average_stars'))
	print(avgStars)
	print("Creating box plot")
	plt.boxplot(avgStars)
	plt.title("User Average Stars")
	plt.show()
    
def avgStarsScatterPlot(db):
	#users = getEliteUsers(db)
	users = getNonEliteUsers(db)
	avgStars = []
	user_count = []
	count = 0
	print("Getting average stars")
	for user in users:
		count += 1
		user_count.append(count)
		avgStars.append(user.get('average_stars'))
	print(avgStars)
	print("Creating scatter plot")
	plt.scatter(user_count, avgStars)
	plt.xlim(xmin=0,xmax=len(user_count))
	plt.ylim(ymin=0)
	plt.xlabel("Number of Users")
	plt.ylabel("Average Stars")
	plt.title("Average Stars per User")
	plt.show()
    
def friendsBoxPlot(db):
	#users = getEliteUsers(db)
	users = getNonEliteUsers(db)
	friends = []
	print("Getting friend count")
	for user in users:
		friends.append(len(user.get('friends')))
	print(friends)
	print("Creating box plot")
	plt.boxplot(friends, widths=0.7)
	plt.yscale('log')
	plt.ylim(ymin=0)
	plt.title("User Friends Count")
	plt.show()
    
def friendsScatterPlot(db):
	#change this line to see elite vs non-elite
	#users = getEliteUsers(db)
	users = getNonEliteUsers(db)
	friend_count = []
	user_count = []
	count = 0
	print("Getting friend count")
	for user in users:
		count += 1
		user_count.append(count)
		friend_count.append(len(user.get('friends')))
	print("Finished getting friends")
	print("Creating scatter plot")
	plt.scatter(user_count, friend_count)
	plt.xlim(xmin=0, xmax=len(user_count))
	plt.ylim(ymin=0)
	plt.xlabel("Number of Users")
	plt.ylabel("Number of Friends")
	plt.title("Number of Friends for Users")
	print("Finished creating plot")
	plt.show()
	
def reviewCountBoxPlot(db):
	users = getNonEliteUsers(db)
	review_counts = []
	print("Getting review counts")
	for user in users:
		review_counts.append(user.get('review_count'))
	print(review_counts)
	print("Creating Box Plot")
	plt.boxplot(review_counts, widths=0.7)
	plt.yscale('log')
	plt.ylim(ymin=0)
	plt.title("User Reivew Counts")
	plt.show()
  
def reviewCountScatterPlot(db):
	users = getNonEliteUsers(db)
	review_counts = []
	user_counts = []
	count = 0
	print("Getting review counts")
	for user in users:
		count += 1
		user_counts.append(count)
		review_counts.append([user['review_count']])
	print("Finished getting review counts")
	print("Creating plot")
	plt.scatter(user_counts, review_counts)
	plt.xlim(xmin=0, xmax=len(user_counts))
	plt.ylim(ymin=0)
	plt.xlabel("Number of Users")
	plt.ylabel("Number of Reviews")
	plt.title("Reviews for Non-Elite Users")
	print("Finished creating plot")
	plt.show()

def eliteReviewCountScatterPlot(db):
	elite_users = getEliteUsers(db)
	review_counts = []
	user_counts = []
	count = 0
	print("Getting review counts")
	for user in elite_users:
		count += 1
		user_counts.append(count)
		review_counts.append([user['review_count']])
	print("Finished getting review counts")
	print("Creating plot")
	plt.scatter(user_counts, review_counts)
	plt.xlim(xmin=0, xmax=len(user_counts))
	plt.ylim(ymin = 0)
	plt.xlabel("Number of Elite Users")
	plt.ylabel("Number of Reviews")
	plt.title("Reviews per Elite User")
	print("Finished creating plot")
	plt.show()


def main():
	# Create a connection to the mongodb process
	# on default port of 27017 and localhost
	client = MongoClient()
	db = client.yelpmining
	
	#eliteReviewCountScatterPlot(db)
	#reviewCountScatterPlot(db)
	#friendsScatterPlot(db)
	friendsBoxPlot(db)
	#reviewCountBoxPlot(db)
	#avgStarsScatterPlot(db)
	#avgStarsBoxPlot(db)
	
if __name__ == '__main__':
    main()
