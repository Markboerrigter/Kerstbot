import networkx as nx
from pymongo import MongoClient
import datetime
from difflib import SequenceMatcher

from stringscore import liquidmetal
import random
import numpy as np
client = MongoClient('mongodb://go:go1234@95.85.15.38:27017/toys')
db = client.kerstbot

now = datetime.datetime.now()
d = now.isoformat()
# db.speelgoed.create_index( [( 'title', "text"), ('description', "text"), ('description_extended', "text"), ('brand', "text")], weights={
#         'title': 3,
#         'brand': 2,
#         'description': 2,
#         'description_extended': 1
#     })

def getConvos():
    catalogus = db.conversations
    results = catalogus.find({})
    return(list(results))

def getUsers():
    catalogus = db.users
    results = catalogus.find({})
    return(list(results))

def logging(log):
    try:
        catalogus = db.conversations
        catalogus.insert(log)
        return 'done'
    except Exception, e:
        return 'Not found user because ',e

def printgraph(mGraph):
    ##pos=nx.spring_layout(mGraph)
    ##colors=range(20)
    ##nx.draw(mGraph,pos,node_color='#A0CBE2',edge_color='#A0CBE5',width=10,edge_cmap=plt.cm.Blues,with_labels=False)

    plt.figure(1, figsize=(8, 8))
    # layout graphs with positions using graphviz neato

    # color nodes the same in each connected subgraph
    C = nx.connected_component_subgraphs(mGraph)
    for g in C:
        c = [random.random()] * nx.number_of_nodes(g)  # random color...
        nx.draw_spectral(g,
                       node_size=80,
                       node_color=c,
                       vmin=0.0,
                       vmax=1.0,
                       with_labels=False
                       )
    plt.show()
    return 0

def addConfig(dict, name, number):
    try:
        catalogus = db.configs
        catalogus.insert({name: dict, 'number': number})
        return 'done'
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

def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]
# print(updateUser(1042410335857237, information))

# add data regarding usage of user in channel
# define the payload now the example of a complete watson personality is being stored
#
# @app.route('/user/add/positive/<artnr>/<pamount>')
def addPositive(artnr, pamount):
    try:
        catalogus = db.speelgoed
        catalogus.update_one(
            {'article_number':int(artnr)},
            {'$set': {'updated': d}, '$inc': {'posScore':int(pamount)}}
        )
        return 'Added ' + pamount + ' positive point(s) to article :' + artnr
    except Exception, e:
        return 'Not found an article'

# add data regarding usage of user in channel
# define the payload now the example of a complete watson personality is being stored
#
# @app.route('/user/add/positive/<artnr>')
# note this function works with one negative point extracted each time used
def addDislike(artnr):
    try:
        catalogus = db.speelgoed
        catalogus.update_one(
            {'article_number':int(artnr)},
            {'$set': {'updated': d}, '$inc': {'negScore':1}}
        )
        return 'Extracted 1 dislike point to article :' + artnr
    except Exception, e:
        return 'Not found an article'

# add data regarding usage of user in channel
# define the payload now the example of a complete watson personality is being stored
#
# @app.route('/user/add/score/<ref>')
def addUserScore(ref, pers, text, prod, feedback):
    try:
        user = db.users
        user.insert({
        'facebook_id': ref, # facebook id gebruiken
        'personality': pers,
        'qa': text,
        'products': prod,
        'feedback': feedback
        })
        return 'Added ' + ref
    except Exception, e:
        return 'Not found an user'

# # finding one unique toy by article number [title, brand, price, age, gender, page]
# @app.route('/article/number/<artnr>')
def findArticle(artnr):
    try:
        catalogus = db.speelgoed
        toy = catalogus.find_one({'article_number':int(artnr)})
        # return str(toy['price'])
        return 'The article you found: ' + toy['title'] + ', ' + toy['brand'] + ', ' + str(toy['price']) + ', ' + toy['age'] + ', ' + toy['gender'] +', ' + str(toy['page']) + '<br>'
    except Exception, e:
        return 'Not found an article'


# getting all articles based on title (regex part of string not case sensitive)
# @app.route('/articles/title/<the_query>')
def findArticlesTitle(the_query,y):
    try:
        catalogus = db.speelgoed
        results = list(catalogus.find({"$text": {'$search': the_query } } ,{ 'score': { "$meta": "textScore" } }).sort( [( 'score', { "$meta": "textScore" } )] ))
        # for x in results:
        #     print(x['score'])
        results = [x for x in results if x['score'] > y]
        return list(results)
    except Exception, e:
        return 'Not found',e


def score(x,y):
    return float(levenshtein(x,y)/float((len(x)+len(y))/2))

def findRightProduct(Ingredient):
    ideaQuery = findArticlesTitleAndDescription(Ingredient)
    titleQuery = findArticlesTitle(Ingredient,3)
    allProducts = ideaQuery + titleQuery
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
# x = findRightProduct(u'jongen', [u'15', u'30'], '2.5', [u'Razende racers en stoere stuurders', u'Rocksterren en stijliconen'], u'', 18)
#
# for y in x :
#     print(y['title'])

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
