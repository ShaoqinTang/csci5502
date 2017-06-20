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

1) Analyze multiple reviews by same user of a business:

Elite:
Total number of elite users:  31461
Total number of elite users with duplicate count: 4805
Max duplicate reviews by an elite user: 210
15% of the elite users had duplicate reviews.

Non Elite:
Total number of users:  520878
Total number of users with duplicate count 27808
Max duplicate reviews by an non-elite user:  228
5% of the non-elite users had duplicate reviews.


2) Tip distribution of Elite User vs Non Elite User:

Max tips by a elite user: 1162
Number of Elite User that gave tips: 10595

3) Like distribution of Elite User vs Non Elite User:

Max likes for a elite user review: 83
Number of Elite Users that had likes: 18812

4) Chronological distribution of reviews:

Number of business elite users that had atleast 1 review in first 5 reviews: 48152
Total number of business' 77079
Percentage of all business where elite user's reviews featured in first 5 reviews: 62.5

5) Number of reviews/year by elite user.

Elite:
{2004: 8, 2005: 501, 2006: 2742, 2007: 10232, 2008: 23375, 2009: 32592,
2010: 56390, 2011: 75884, 2012: 81986, 2013: 91421, 2014: 85474, 2015: 84031}

Non Elite:
{2004: 3, 2005: 187, 2006: 1439, 2007: 7327, 2008: 21552, 2009: 40133,
2010: 81683, 2011: 135366, 2012: 165005, 2013: 245602, 2014: 404085, 2015: 578171}

6) Review count of elite users


'''
import json
import math
import operator
import matplotlib
import datetime
import numpy as np
from pymongo import MongoClient
# Mongo stores objects in bson format, need this to print
from bson import json_util
from matplotlib import pyplot
from operator import itemgetter

'''
Return elite user ids
'''
def elite_userids(db):
    user_ids = db.user.find(
        {'elite':
         {'$exists': True, '$gt': 0}
         },
        {"user_id": 1, "_id": 0})
    return user_ids


'''
Return non-elite user ids
'''
def non_elite_userids(db):
    user_ids = db.user.find(
        {'elite': []
         },
        {"user_id": 1, "_id": 0})
    return user_ids


'''
Return distinct business ids in review schema.
'''
def distinct_business_ids(db):
    business_ids = db.review.distinct("business_id")
    return business_ids

'''
Analyze multiple reviews by same user of a business
'''


def elite_multiple_reviews_same_business(db):
    find_multiple_reviews(db, elite_userids(db), 'elite_user')
    find_multiple_reviews(db, non_elite_userids(db), 'non_elite_user')

'''
Find duplicate reviews and plot
'''
def find_multiple_reviews(db, user_ids, label):
    user_hash = {}
    user_duplicate_count = {}
    # initialize dictionaries
    for user_id in user_ids:
        user_hash[user_id.get("user_id")] = []
        user_duplicate_count[user_id.get("user_id")] = 0

    # Get business id and user id for all the reviews.
    review_ids = db.review.find(
        {},
        {"business_id": 1, "user_id": 1, "_id": 0})

    count_dup_review_users = 0
    for review_id in review_ids:
        user = review_id.get("user_id")
        business = review_id.get("business_id")
        if user in user_hash.keys():
            if business in user_hash[user]:
                user_duplicate_count[user] += 1
                if user_duplicate_count[user] == 1:
                    count_dup_review_users += 1
            user_hash[user].append(business)

    print("total number of users: ", len(user_hash))
    print("total number of users with duplicate count", count_dup_review_users)
    print("max reviews: ", user_duplicate_count[
          max(user_duplicate_count, key=user_duplicate_count.get)])
    pyplot.bar(
        range(
            len(user_duplicate_count)),
        user_duplicate_count.values(),
        align='center')
    pyplot.xticks(
        range(
            len(user_duplicate_count)),
        user_duplicate_count.keys())
    pyplot.savefig(label + "_multiple_reviews.png")
    pyplot.close()

'''
Analyze number of tips by an user and
        number of likes given to an user
'''
def user_tips_likes_distribution(db):
    elite_user_tips, elite_user_likes = find_user_tips_likes_distribution(
        db, elite_userids(db), 'elite_user')
    non_elite_user_tips, non_elite_user_likes = find_user_tips_likes_distribution(
        db, non_elite_userids(db), 'non_elite_user')

    # plot graph for "tips"
    max_tips = elite_user_tips[max(elite_user_tips, key=elite_user_tips.get)]
    min_tips = elite_user_tips[min(elite_user_tips, key=elite_user_tips.get)]
    # 1) Using hard coded value of 15 instead of max_tips as
    # frequency is very low after 15.
    # 2) Ignore 0 tips as that doesn't give us any information.
    # So, use 1 instead of min_tips which is 0
    interval = 1
    bins = [x for x in range(1, 15, interval)]
    listoflists = []
    listoflists.append(list(elite_user_tips.values()))
    listoflists.append(list(non_elite_user_tips.values()))
    pyplot.hist(
        listoflists,
        bins,
        histtype='bar',
        rwidth=0.6,
        label=[
            'elite',
            'non-elite'])
    pyplot.xlabel('Tips')
    pyplot.ylabel('Number of users')
    pyplot.legend(loc='upper right')
    pyplot.savefig('../graphs/' + "user_tips.png")
    pyplot.close()

    # Plot graph for "likes"
    max_likes = elite_user_likes[
        max(elite_user_likes, key=elite_user_likes.get)]
    min_likes = elite_user_likes[
        min(elite_user_likes, key=elite_user_likes.get)]
    interval = 1
    bins = [x for x in range(1, 6, interval)]
    print(bins)
    listoflists = []
    listoflists.append(list(elite_user_likes.values()))
    listoflists.append(list(non_elite_user_likes.values()))
    pyplot.hist(
        listoflists,
        bins,
        histtype='bar',
        rwidth=0.6,
        label=[
            'elite',
            'non-elite'])
    pyplot.xlabel('Likes')
    pyplot.ylabel('Number of users')
    pyplot.legend(loc='upper right')
    pyplot.savefig('../graphs/' + "user_likes.png")
    pyplot.close()


def find_user_tips_likes_distribution(db, user_ids, label):
    user_like_hash = {}
    user_tip_hash = {}
    for user_id in user_ids:
        user_like_hash[user_id.get("user_id")] = 0
        user_tip_hash[user_id.get("user_id")] = 0

    tips = db.tip.find({}, {"likes": 1, "user_id": 1, "_id": 0})

    user_tip_count = 0
    user_like_count = 0
    for tip in tips:
        user = tip.get("user_id")
        if user in user_tip_hash.keys():
            user_tip_hash[user] += 1
            user_like_hash[user] += tip.get("likes")
            if user_tip_hash[user] == 1:
                user_tip_count += 1
            if user_like_hash[user] == 1:
                user_like_count += 1

    print("Number of " + label + " users that gave tips", user_tip_count)
    print("Number of " + label + " users that got likes", user_like_count)

    return user_tip_hash, user_like_hash


'''
Find the position of reviews posted by elite users
This function takes a few minutes to execute as there are 2225213 reviews to
sort through. This time could be improved by indexing on (business id, date)
'''
def elite_reviews_position(db):
    businesss = distinct_business_ids(db)
    business_ids = {}
    for business_id in businesss:
        business_ids[business_id] = []

    review_ids = db.review.find(
        {}, {"business_id": 1, "user_id": 1, "date": 1, "_id": 0})
    review_position = 0
    # Collect user id and dates for each business
    for review_id in review_ids:
        user = review_id.get("user_id")
        bus_id = review_id.get("business_id")
        date = datetime.datetime.strptime(review_id.get("date"), "%Y-%m-%d")
        business_ids[bus_id].append([user, date])

    # Collect elite user ids in a list
    elite_user_ids = elite_userids(db)
    elite_users = []
    for user_id in elite_user_ids:
        elite_users.append(user_id.get("user_id"))

    position_list = []
    # sort the reviews by date and find position of elite member
    for bus_id, val in business_ids.items():
        if val:
            sortedList = sorted(val, key=itemgetter(1))
            position = 1
            for values in sortedList:
                user = values[0]
                if user in elite_users:
                    position_list.append(position)
                    break
                position = position + 1

    # count the business that had an elite user review in first 5 reviews.
    count = 0
    for position in position_list:
        if (position <= 5):
            count += 1

    print('''Number of business elite users that had atleast 1 review in first
            5 reviews''', count)
    print("Total number of business'", len(business_ids))

    # plot a histogram with position frequency
    max_pos = max(position_list)
    min_pos = min(position_list)
    interval = 1
    # hard coding max range to 15 as after that frequency is very low.
    bins = [x for x in range(1, 15, interval)]
    pyplot.hist(position_list, bins, histtype='bar', rwidth=0.6)
    pyplot.xlabel('Position (Chronological)')
    pyplot.ylabel('Review count')
    pyplot.title('Position of reviews by elite users')
    pyplot.savefig('../graphs/' + 'elite_users_position.png')
    pyplot.close()


'''
Number of reviews/year for elite users in review database
'''
def user_reviews_per_year(db):
    elite_user_ids = elite_userids(db)
    elite_users = {}
    for user_id in elite_user_ids:
        elite_users[user_id.get("user_id")] = []
    elite_yearly_reviews = {}
    user_yearly_reviews = {}
    review_ids = db.review.find(
        {}, {"date": 1, "user_id": 1, "_id": 0})
    for review_id in review_ids:
        user = review_id.get("user_id")
        # Get the 4 digit year
        year = (int)(review_id.get("date").split('-')[0])
        # add to user dictionary.
        if year in user_yearly_reviews.keys():
            user_yearly_reviews[year] += 1
        else:
            user_yearly_reviews[year] = 1
        # add to elite dictionary.
        if user in elite_users.keys():
            if year in elite_yearly_reviews.keys():
                elite_yearly_reviews[year] += 1
            else:
                elite_yearly_reviews[year] = 1

    print(elite_yearly_reviews)

    # get array of year values for pyplot
    years = []
    for key in elite_yearly_reviews.keys():
        years.append(key)
    print("keys = ", years)
    N = len(years)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35
    p1 = pyplot.bar(
        ind,
        elite_yearly_reviews.values(),
        width=width,
        color='blue')
    p2 = pyplot.bar(
        ind,
        user_yearly_reviews.values(),
        width=width,
        color='green',
        bottom=elite_yearly_reviews.values())
    pyplot.xticks(ind + width / 2., years)
    pyplot.xlabel('Year')
    pyplot.ylabel('Number of users')
    pyplot.title('Distribution of reviews per year')
    pyplot.legend((p1[0], p2[0]), ('Elite Users', 'All Users'), loc=2)
    pyplot.savefig('../graphs/' + 'user_per_year_review_analysis.png')
    pyplot.close()

'''
Review distribution for elite users in review database
'''
def user_review_distribution(db):
    elite_reviews = find_user_reviews(db, elite_userids(db), 2015)
    non_elite_reviews = find_user_reviews(db, non_elite_userids(db), 2015)

    listoflists = []
    listoflists.append(list(elite_reviews.values()))
    listoflists.append(list(non_elite_reviews.values()))
    plot_user_reviews(listoflists, 10, 50, 5)
    plot_user_reviews(listoflists, 50, 200, 10)


def plot_user_reviews(review_list, low, high, interval):
    bins = [x for x in range(low, high, interval)]
    pyplot.hist(
        review_list,
        bins,
        histtype='bar',
        rwidth=0.6,
        label=[
            'elite',
            'non-elite'])
    pyplot.xlabel('Reviews')
    pyplot.ylabel('Number of users')
    pyplot.title('Frequency of reviews in 2015')
    pyplot.legend(loc='upper right')
    pyplot.savefig(
        '../graphs/' +
        'user_review_distribution_' +
        str(low) +
        '_' +
        str(high) +
        '.png')
    pyplot.close()

'''
Find the number of reviews by users per year or over the years.
'''
def find_user_reviews(db, userids, year=0):
    users = {}
    for userid in userids:
        users[userid.get("user_id")] = 0

    review_ids = db.review.find(
        {},
        {"date": 1, "user_id": 1, "_id": 0})

    for review_id in review_ids:
        review_year = (int)(review_id.get("date").split('-')[0])
        if year == 0 or review_year == year:
            user = review_id.get("user_id")
            if user in users.keys():
                users[user] += 1

    min_reviews = users[min(users, key=users.get)]
    max_reviews = users[max(users, key=users.get)]
    print("min reviews: ", min_reviews)
    print("max reviews: ", max_reviews)
    return users


def main():
    # Create a connection to the mongodb process
    # on default port of 27017 and localhost
    client = MongoClient()
    db = client.yelpmining

    # Data Mining algorithms. Some of them
    # take considerable time. So, avoid
    # runing all at once.

    # elite_multiple_reviews_same_business(db)
    # user_tips_likes_distribution(db)
    # elite_reviews_position(db)
    # elite_duplicate_business_reviews(db)
    # user_reviews_per_year(db)
    user_review_distribution(db)

    # close connection
    client.close()

if __name__ == '__main__':
    main()
