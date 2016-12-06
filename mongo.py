from pymongo import MongoClient
import datetime
import random
import numpy as np
import ast
import json
client = MongoClient('mongodb://go:go1234@95.85.15.38:27017/toys')
db = client.kerstbot

now = datetime.datetime.now()
d = now.isoformat()

def findArticlesTitle(the_query,y):
    try:
        catalogus = db.products
        results = list(catalogus.find({"$text": {'$search': the_query } } ,{ 'score': { "$meta": "textScore" } }).sort( [( 'score', { "$meta": "textScore" } )] ))
        results = [x for x in results if x['score'] > y]
        return list(results)
    except Exception, e:
        return 'Not found',e

def findArticlesTitleAndDescription(the_query):
    try:
        catalogus = db.products
        data = list(catalogus.find({'$or': [{'titel': {'$regex': '.*'+the_query+'.*','$options' : 'i'}},{'ingr1': {'$regex': '.*'+the_query+'.*','$options' : 'i'}},{'ingr2': {'$regex': '.*'+the_query+'.*','$options' : 'i'}} ]}))
        return data
    except Exception, e:
        return 'Not found'

def addProduct(inf):
    try:
        catalogus = db.products
        catalogus.insert(inf)
        return 'done'
    except Exception, e:
        return 'Not found user because ',e
# f = open('products.json','rb')
# f = f.read()
#
# f = json.loads(f)
# products = []
# for x in f:
#     addProduct(x['results'])


def score(x,y):
    return float(levenshtein(x,y)/float((len(x)+len(y))/2))

def findUser(id):
    try:
        catalogus = db.users
        ans = list(catalogus.find({'_id': id}))[0]
        outcome = ans
        return outcome
    except Exception, e:
        return None

def updateUser(id, newInformation):
    try:
        catalogus = db.users
        catalogus.update({'_id': str(id)},newInformation)
        return 'id: ' +str(id) + 'has been updated'
    except Exception, e:
        return 'Not found user',e

def insertUser(id, newInformation):
    try:
        newInformation['_id'] = str(id)
        catalogus = db.users
        catalogus.insert(newInformation)
        return 'id: ' +str(id) + 'has been updated'
    except Exception, e:
        return 'Not found user because ',e

def findConfig(x):
    try:
        catalogus = db.configs
        ans = catalogus.find({'number': x})[0]
        for x in ans:
            if x != '_id' and x != 'number':
                return ans[x]
    except Exception, e:
        return 'Not found any configuration',e

def findRightProduct(Ingredient):
    ideaQuery = findArticlesTitleAndDescription(Ingredient)
    titleQuery = findArticlesTitle(Ingredient,0.5)
    # print(ideaQuery,titleQuery)
    allProducts = ideaQuery + titleQuery
    print(len(ideaQuery))
    print(len(titleQuery))
    uniqueProducts = dict((v['_id'],v) for v in allProducts).values()
    uniqueProducts = [[x,0] for x in uniqueProducts]
    uniqueProducts = [x for x in uniqueProducts if x[0]['titel']]
    finalScore = []
    for x in uniqueProducts:
        a = 0
        if x[0] in titleQuery:
            a+=10
        else:
            a-=10
        if x[0] in ideaQuery:
            a+=2
        else:
            a-=2
        finalScore.append([x[0],a])
    finalScore = sorted(finalScore, key=lambda x: x[1])[::-1]
    return finalScore
#
# x = findRightProduct('kip')
#
# for y in x :
#
#     print(y[0]['titel'])

def printprod(L):
    for x in L:
        print(x[0]['title'], x[1])

#


'''
done> get product
done> get products
done> get product(s) by price
done> get products under and above cut
done> get product(s) by pricerange
done> get product(s) by gender
done> get product(s) by brand
done> get product(s) by age
get product(s) by category
done> get product(s) by age+pricerange+gender
get user data
get product(s) by keywords
get populartiy
get dislike
"""
#
# if __name__ == '__main__':
#     # app.run(debug=True)
#     app.run(host='0.0.0.0', debug=True)
'''
