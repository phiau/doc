#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import sqrt

# A dictionary of movie critics and their ratings of a small(存储他们对几部电影的评价的哈希表)
# set of movies
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                         'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5, 'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                            'The Night Listener': 4.5, 'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


def shared_items_fn(prefs, person1, person2):
    return {item: 1 for item in prefs[person1] if item in prefs[person2]}


# euclidean distance between two people
# 两人的欧式距离
def sim_distance(prefs, person1, person2):
    '''
    Calculates euclidean distance between two people
    by comparing their shared item scores.
    计算两人共有项的欧氏距离
    '''
    shared_items = shared_items_fn(prefs, person1, person2)

    if len(shared_items) == 0:
        return 0

    sum_of_squares = sum([(prefs[person1][item] - prefs[person2][item]) ** 2
                          for item in prefs[person1]
                          if item in prefs[person2]])
    return 1 / (1 + sum_of_squares)


def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = shared_items_fn(prefs, p1, p2)

    # if they are no ratings in common, return 0
    if len(si) == 0:
        return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0:
        return 0

    r = num / den

    return r


def top_matches(prefs, person, n=5, similarity_fn=sim_pearson):
    '''
    Calculates n top similar matches for person.
    计算用户相似度（口味相近）的排名
    '''
    scores = [(similarity_fn(prefs, person, other), other)
              for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[:n]


def get_recommendations(prefs, person, similarity_fn=sim_pearson):
    '''
    Generates an orderded list of similar items for person.
    为用户生成一个相似（口味相近）物品（这里指电影）有序列表
    '''
    totals = {}
    similarity_sums = {}

    for other_person in prefs:
        if other_person != person:
            similarity = similarity_fn(prefs, person, other_person)

            if similarity > 0:
                for item in prefs[other_person]:
                    if item not in prefs[person] or prefs[person][item] == 0:
                        totals.setdefault(item, 0)
                        # accumulate movie score times similarity...
                        totals[item] += prefs[other_person][item] * similarity
                        similarity_sums.setdefault(item, 0)
                        # ... and accumulate the total similarity as well ...
                        similarity_sums[item] += similarity

    # ... so we can normalize the final score here!
    rankings = [(total / similarity_sums[item], item)
                for item, total in totals.items()]

    rankings.sort()
    rankings.reverse()
    return rankings


def transform_prefs(prefs):
    '''
    Transforms user based preferences into item based
    preferences ie. {'User': {'item': 3.5, 'item2': 5.0}}
    is turned into {'item': {'User': 3.5'}, 'item2':
    {'User': 5.0}. Useful when trying to get similar items
    instead of similar users.
    把人的基本偏好转成物品的偏好。当试图获取相似物品（而不是相似口味的人）就会变得有用。
    '''
    results = {}
    for person in prefs:
        for item in prefs[person]:
            results.setdefault(item, {})
            results[item][person] = prefs[person][item]

    return results


def calculate_similar_items(prefs, n=10):
    '''
    Generates a list of items along with n top matched similar items and their similarity score.
    生成一个列表，包含与其他物品的相似程度
    '''

    result = {}

    item_prefs = transform_prefs(prefs)
    c = 0
    for item in item_prefs:
        c += 1
        if c % 100 == 0:
            print "%d / %d" % (c, len(item_prefs))

        scores = top_matches(item_prefs, item, n, sim_distance)
        # use sim_distance, because pearsonr will
        # have problems with divide by 0 and introduce nan's
        result[item] = scores
    return result


def get_recommended_items(prefs, itemMatch, user):
    '''
    Generates a list of recommended items for a user
    based on user preferences (prefs[user]) as well
    as a list of similar items.
    根据用户喜好，推荐类似的物品列表
    '''
    user_ratings = prefs[user]
    scores = {}
    total_similar = {}

    for (item, rating) in user_ratings.items():
        for (similarity, item2) in itemMatch[item]:
            if item2 not in user_ratings:
                scores.setdefault(item2, 0)
                scores[item2] += similarity * rating

                total_similar.setdefault(item2, 0)
                total_similar[item2] += similarity

    rankings = [(score / total_similar[item], item) for item, score in scores.items()]

    rankings.sort()
    rankings.reverse()
    return rankings


def loadMovieLens(path='/data/movielens'):
    # Get movie titles
    movies = {}
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    # Load data
    prefs = {}
    for line in open(path + '/u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    return prefs


if __name__ == '__main__':
    # print(sim_pearson(critics, 'Toby', 'Lisa Rose'))
    # print(top_matches(critics, 'Toby'))
    # print(get_recommendations(critics, 'Toby'))
    # print(calculate_similar_items(critics, 3))
    # print(get_recommended_items(critics, calculate_similar_items(critics), 'Toby'))
    # print('Toby')
    prefs = loadMovieLens('./ml-100k')
    # print(prefs['87'])
    # print(get_recommendations(prefs, '87')[0:30])
    itemsim = calculate_similar_items(prefs, n=50)

    get_recommended_items(prefs, itemsim, '87')[0:30]
    # print(itemsim)
