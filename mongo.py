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


def logging(log):
    try:
        catalogus = db.conversations
        catalogus.insert(log)
        return 'done'
    except Exception, e:
        return 'Not found user because ',e

def findArticlesTitle(the_query,y):
    try:
        catalogus = db.products
        results = list(catalogus.find({"$text": {'$search': the_query } } ,{ 'score': { "$meta": "textScore" } }).sort( [( 'score', { "$meta": "textScore" } )] ))
        return list(results)
    except Exception, e:
        return 'Not found',e

def findArticlesTitleAndDescription(the_query):
    try:
        catalogus = db.products
        data = list(catalogus.find({'$or': [{'Title': {'$regex': '.*'+the_query+'.*','$options' : 'i'}},{'Ingredienten': {'$regex': '.*'+the_query+'.*','$options' : 'i'}},{'Bereidingswijze': {'$regex': '.*'+the_query+'.*','$options' : 'i'}} ]}))
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

# file  = open('data.json', 'r+')
# file = file.read()
# data = json.loads(file)
# for x in data:
#     dat = data[x]
#     dat.update({'Title': x})
#     addProduct(dat)

# f = open('products.json','rb')
# f = f.read()
#
# f = json.loads(f)
# products = []
# for x in f:
#     addProduct(x['results'])
def findArticlesTitle(the_query):
    try:
        catalogus = db.products
        results = list(catalogus.find({"$text": {'$search': the_query } } ,{ 'score': { "$meta": "textScore" } }).sort( [( 'score', { "$meta": "textScore" } )] ))
        # results = [x for x in results if x['score'] > y]
        results = [[{i:a[i] for i in a if i!='score'},a['score']] for a in results]
        return (results)
    except Exception, e:
        return 'Not found',e

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

def findGang(gang):
    try:
        if gang == 'Voorgerecht':
            sex = 'voor'
        if gang == 'Hoofdgerecht':
            sex = 'hoofd'
        if gang == 'Nagerecht':
            sex = 'na'
        catalogus = db.products
        results = list(catalogus.find({'Gang': sex}))
        return results
    except Exception, e:
        return 'Not found'

def findDesertType(type):
    try:
        type = type.lower()
        catalogus = db.products
        results = list(catalogus.find({'Type Gerecht': type}))
        return results
    except Exception, e:
        return 'Not found'

def findVega(type):
    try:
        type = type.lower()
        catalogus = db.products
        results = list(catalogus.find({'Type Gerecht': type}))
        return results
    except Exception, e:
        return 'Not found'

def findLevel(type):
    try:
        if type == 'Amateur':
            query = [{'Moeilijkheid': 1}, {'Moeilijkheid': 2}]
        else:
            query = [{'Moeilijkheid': 2}, {'Moeilijkheid': 3}]
        catalogus = db.products
        results = list(catalogus.find({'$or': query}))
        return results
    except Exception, e:
        return 'Not found'

def find(x,L):
    return [(i, colour.index(x)) for i, colour in enumerate(L) if x in colour]

def findForGang(Ingredient, dessertKind, technique, level, gang,vega):
    gangQuery = findGang(gang)
    if gang == 'Nagerecht':
        voorkeurQuery = findDesertType(dessertKind)
        techniekQuery = ''
    else:
        voorkeurQuery = findVega(vega)
        techniekQuery = findArticlesTitle(technique)
    techniques = [x for [x,y] in techniekQuery]
    levelQuery = findLevel(level)
    ideaQuery = findArticlesTitleAndDescription(Ingredient)
    titleQuery = findArticlesTitle(Ingredient)
    ideas = [x for [x,y] in titleQuery]
    vegaQuery = findVega(vega)
    finalScore = []
    for x in gangQuery:
        a = 0
        if x in techniques:
            ind = find(x,techniekQuery)[0]
            a+=techniekQuery[ind[0]][1]
        if x in ideas:
            ind = find(x,titleQuery)[0]
            a+=titleQuery[ind[0]][1]
        if x in voorkeurQuery:
            a += 2
        if x in levelQuery:
            a += 2
        if x in ideaQuery:
            a +=2
        if x in vegaQuery:
            a += 3
        finalScore.append([x,a])
    finalScore = sorted(finalScore, key=lambda x: x[1])[::-1]
    finalScore = [x for [x,y] in finalScore]
    return finalScore

def findRightProduct(Ingredient, dessertKind, technique, level, gang,vega):
    if isinstance(gang,str):
        meals = findForGang(Ingredient, dessertKind, technique, level, gang,vega)
    else:
        meals = []
        for x in gang:
            meals.append(findForGang(Ingredient, dessertKind, technique, level, x,vega))
    return meals

# x = findRightProduct('beef', '', 'Oven', 'Amateur', 'Hoofdgerecht','Vlees')
#
# for y in x :
#     print(y['Title'])

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
