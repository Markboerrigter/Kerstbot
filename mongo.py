import networkx as nx
from pymongo import MongoClient
import datetime
from difflib import SequenceMatcher
import kpss
from stringscore import liquidmetal
import random
import numpy as np
client = MongoClient('mongodb://go:go1234@95.85.15.38:27017/toys')
db = client.toys

err
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


# x = findArticlesTitle('e',5)
# for y in x:
#     print(y['title'])
# # getting all articles based on title and description_extended (regex part of string not case sensitive)
# @app.route('/articles/<the_query>')
def findArticlesTitleAndDescription(the_query):
    try:
        catalogus = db.speelgoed
        data = list(catalogus.find({'$or': [{'title': {'$regex': '.*'+the_query+'.*','$options' : 'i'}},{'description_extended': {'$regex': '.*'+the_query+'.*','$options' : 'i'}} ]}))
        return data
    except Exception, e:
        return 'Not found'

# getting all articles [title, brand, price, age, gender, page]
# @app.route('/articles')
def findAllArticles():
    try:
        catalogus = db.speelgoed
        results = catalogus.find({})
        return(list(results))
        # output = ''
        # for r in results:
        #     output += r['title'] + ', ' + r['brand'] + ', ' + str(r['price']) + ', ' + r['age'] + ', ' + r['gender'] +', ' + str(r['page']) + '<br>'
        # return output
    except Exception, e:
        return 'Not found'

def allToZero():
    try:
        articles = findAllArticles()
        catalogus = db.speelgoed
        for x in articles:
            catalogus.update({"article_number" :x['article_number'] },{'$set': {"posScore":0}},upsert=False,multi= True )
            catalogus.update({"article_number" :x['article_number'] },{'$set': {"negScore":0}},upsert=False,multi= True )
        print('done')
    except Exception, e:
        return 'Not found', e

# print(allToZero())
def readScore(number):
    try:
        catalogus = db.speelgoed
        toy = catalogus.find_one({'article_number':int(artnr)})
        return toy
    except Exception, e:
        return 'Not found'
# getting all articles that are aprox. price (plus and minus 15%)
# @app.route('/articles/price/<the_price>')
def findByPrice(the_price):
    try:
        the_price_low = float(the_price) - float(the_price)/6.6
        the_price_high = float(the_price)/6.6 + float(the_price)
        catalogus = db.speelgoed
        results = list(catalogus.find({'$and': [{'price': {'$lt':the_price_high}},{'price': {'$gt':the_price_low}} ]}))

        # return str(the_price_low) + ' and ' + str(the_price_high)
        return results
    except Exception, e:
        return 'Not found'

# getting all articles under 50 euro
# @app.route('/articles/under')
def findUndervalue(x):
    try:
        catalogus = db.speelgoed
        results = list(catalogus.find({'$and': [{'price': {'$lt':x}},{'price': {'$gt':0}} ]}))
        return results
        # ordered = results.sort('price')
        # output = ''
        # for r in ordered:
        #     output += r['title'] + ' - '+ str(r['price']) + '<br>'
        # return output
    except Exception, e:
        return 'Not found'

# getting all articles above 50 euro
# @app.route('/articles/above')
def findAbovevalue(the_price):
    try:
        catalogus = db.speelgoed
        results = list(catalogus.find({'price': {'$gt':the_price}}))
        return results
        # ordered = results.sort('price')
        # output = ''
        # for r in ordered:
        #     output += r['title'] + ' - '+ str(r['price']) + '<br>'
        # return output
    except Exception, e:
        return 'Not found'

# getting all articles within price range
# @app.route('/articles/price/range/<start>/<end>')
def findFromRange(start, end):
    try:
        aa = float(start)
        bb = float(end)
        catalogus = db.speelgoed
        results = list(catalogus.find({'$and': [{'price': {'$lt':bb}},{'price': {'$gt':aa}} ]}))
        return results
    except Exception, e:
        return 'Not found'

# getting all articles based on gender (Jongen / Meisje / Beide)
# @app.route('/articles/gender/<sex>')
def findArticlesGender(sex):
    try:
        catalogus = db.speelgoed
        results = list(catalogus.find({'gender': sex}))
        # ordered = results.sort('price')
        # output = ''
        # for r in ordered:
        #     output += r['title'] + ' - '+ str(r['price']) + '<br>'
        return results
    except Exception, e:
        return 'Not found'

# getting all articles based on brand (regex part of string not case sensitive)
# @app.route('/articles/brand/<the_brand>')
def findArticlesBrand(the_brand):
    try:
        catalogus = db.speelgoed
        results = catalogus.find({'brand': {'$regex': '.*'+the_brand+'.*','$options' : 'i'}})
        ordered = results.sort('price')
        output = ''
        for r in ordered:
            output += r['title'] + ' - '+ str(r['price']) + '<br>'
        return output
    except Exception, e:
        return 'Not found'

def findArticlesCategory(category):
    try:
        catalogus = db.speelgoed
        results = list(catalogus.find({'folder_category': category}))
        return results
    except Exception, e:
        return 'Not found'

def findArticlesStemming(the_query):
    try:
        catalogus = db.speelgoed
        data = list(catalogus.find({'stemming.2': {'$regex': '.*'+the_query+'.*','$options' : 'i'}}))
        return data
    except Exception, e:
        return 'Not found'

# finding one unique toy by article number [title, brand, price, age, gender, page]
# @app.route('/articles/by/age/year/<jaar>')
def findByAge(jaar):
    try:
        # append this madness dictionary regarding age
        query = [{'age': 'alle leeftijden'}]
        if jaar == '0':
            query.append({'age': 'Vanaf 0 maanden'})
            query.append({'age': '0 jaar tot 1 jaar'})
            query.append({'age': '0 jaar tot 2 jaar'})
            query.append({'age': '0 jaar tot 3 jaar'})
            query.append({'age': '0 maanden tot 3 jaar'})
            query.append({'age': '0 maanden tot 4 jaar'})
            query.append({'age': '0 maanden tot 5 jaar'})
            query.append({'age': '3 maanden tot 1 jaar'})
            query.append({'age': 'Tot 12 maanden'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '1':
            query.append({'age': '1 jaar tot 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': '1,5 jaar tot 3 jaar'})
            query.append({'age': '1,5 jaar tot 4 jaar'})
            query.append({'age': '1,5 jaar tot 5 jaar'})
            query.append({'age': '1,5 jaar tot 8 jaar'})
            query.append({'age': '1,5 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '2':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': '1 jaar tot 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 3 jaar'})
            query.append({'age': '2 jaar tot 4 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 4 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '6 maanden tot 3 jaar'})
            query.append({'age': '6 maanden tot 4 jaar'})
            query.append({'age': '10 maanden tot 3 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '3':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 4 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 4 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 4 jaar'})
            query.append({'age': '3 jaar tot 5 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 3 tot 8 jaar'})
            query.append({'age': 'Vanaf 3 tot 11 jaar'})
            query.append({'age': 'Vanaf 3 tot 12 jaar'})
            query.append({'age': 'Vanaf 3 tot 99 jaar'})
            query.append({'age': '6 maanden tot 4 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '4':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 5 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 6 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 11 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '5':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 6 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': '6 jaar tot 8 jaar'})
            query.append({'age': '6 jaar tot 10 jaar'})
            query.append({'age': '6 jaar tot 12 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '6':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '7':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '8':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '9':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '10':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '11':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '12':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '13':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '14':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '15':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '16':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '17':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        else:
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': 'vanaf 18 jaar'})
            query.append({'age': 'Vanaf 18 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})

        catalogus = db.speelgoed
        # get query dict working
        results = catalogus.find({'$or': query})
        return(list(results))
        # ordered = results.sort('price')
        # output = ''
        # for r in ordered:
        #     output += r['title'] + ' | '+ r['age'] + ' | ' + str(r['price']) +'<br>'
        # return output
    except Exception, e:
        return 'Not found an article'

def findSpecificAge(jaar):
    try:
        # append this madness dictionary regarding age
        query = []
        if jaar == '0':
            query.append({'age': 'Vanaf 0 maanden'})
            query.append({'age': '0 jaar tot 1 jaar'})
            query.append({'age': '0 jaar tot 2 jaar'})
            query.append({'age': '0 jaar tot 3 jaar'})
            query.append({'age': '0 maanden tot 3 jaar'})
            query.append({'age': '0 maanden tot 4 jaar'})
            query.append({'age': '0 maanden tot 5 jaar'})
            query.append({'age': '3 maanden tot 1 jaar'})
            query.append({'age': 'Tot 12 maanden'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '1':
            query.append({'age': '1 jaar tot 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': '1,5 jaar tot 3 jaar'})
            query.append({'age': '1,5 jaar tot 4 jaar'})
            query.append({'age': '1,5 jaar tot 5 jaar'})
            query.append({'age': '1,5 jaar tot 8 jaar'})
            query.append({'age': '1,5 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '2':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': '1 jaar tot 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 3 jaar'})
            query.append({'age': '2 jaar tot 4 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 4 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '6 maanden tot 3 jaar'})
            query.append({'age': '6 maanden tot 4 jaar'})
            query.append({'age': '10 maanden tot 3 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '3':
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 4 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 4 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 4 jaar'})
            query.append({'age': '3 jaar tot 5 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 3 tot 8 jaar'})
            query.append({'age': 'Vanaf 3 tot 11 jaar'})
            query.append({'age': 'Vanaf 3 tot 12 jaar'})
            query.append({'age': 'Vanaf 3 tot 99 jaar'})
            query.append({'age': '6 maanden tot 4 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '4':
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 5 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 6 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 11 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
        elif jaar == '5':
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 6 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': '6 jaar tot 8 jaar'})
            query.append({'age': '6 jaar tot 10 jaar'})
            query.append({'age': '6 jaar tot 12 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
        elif jaar == '6':
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
        elif jaar == '7':
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
        elif jaar == '8':
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
        elif jaar == '9':
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
        elif jaar == '10':
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
        elif jaar == '11':
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': ''})
        elif jaar == '12':
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
        elif jaar == '13':
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
        elif jaar == '14':
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
        elif jaar == '15':
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
        elif jaar == '16':
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
        elif jaar == '17':
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
        else:
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': 'vanaf 18 jaar'})
            query.append({'age': 'Vanaf 18 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})

        catalogus = db.speelgoed
        # get query dict working
        results = catalogus.find({'$or': query})
        return(list(results))
        # ordered = results.sort('price')
        # output = ''
        # for r in ordered:
        #     output += r['title'] + ' | '+ r['age'] + ' | ' + str(r['price']) +'<br>'
        # return output
    except Exception, e:
        return 'Not found an article'

def score(x,y):
    return float(levenshtein(x,y)/float((len(x)+len(y))/2))

def findRightProduct(geslacht, budget, age, category, idea,n):
    print((geslacht, budget, age, category, idea,n))
    # print(type(age))
    # print(age)
    if len(age.split(','))>1:
        age = age.split(',')[0]
    if len(age.split('.'))>1:
        age = age.split('.')[0]
    idea = idea.lower()
    idea = idea.replace('een ', '').replace('de ', '' ).replace('het ', '')
    ideaStem = ' '.join([kpss.stem(word) for word in idea.split()])
    geslachtQuery = findArticlesGender(geslacht)
    if len(budget) >1:
        budgetQuery = findFromRange(budget[0],budget[1])
    elif budget[0].isdigit():
        budgetQuery = findAbovevalue(budget[0])
    else:
        if 'meer' in budget[0].lower() or 'boven' in budget[0].lower():
            budget = [int(s) for s in budget[0].split() if s.isdigit()]

            budgetQuery = findAbovevalue(int(budget[0]))
        elif 'minder' in budget[0].lower() or 'onder' in budget[0].lower():
            budget = [int(s) for s in budget[0].split() if s.isdigit()]

            budgetQuery = findUndervalue(int(budget[0]))
        else:
            budget = [int(s) for s in budget[0].split() if s.isdigit()]

            budgetQuery = findByPrice((budget[0]))
    ageQuery = findByAge(age)
    ageSpecificQuery = findSpecificAge(age)
    if idea == '':
        ideaStem = 'jaa'
        ideaQuery = []
        titleQuery = []
        stemQuery = []
    else:
        ideaQuery = findArticlesTitleAndDescription(idea)
        stemQuery = findArticlesStemming(ideaStem)
        titleQuery = findArticlesTitle(idea,3)
    categoryQuery = [findArticlesCategory(x) for x in category]
    categoryQuery = [item for sublist in categoryQuery for item in sublist]
    # print(budgetQuery)
    allProducts = geslachtQuery + budgetQuery + ageQuery + ideaQuery + stemQuery + titleQuery + categoryQuery
    uniqueProducts = dict((v['_id'],v) for v in allProducts).values()
    uniqueProducts = [[x,0] for x in uniqueProducts]
    uniqueProducts = [x for x in uniqueProducts if x[0]['title']]
    finalScore = []
    for x in uniqueProducts:
        pos = x[0]['posScore']
        neg = x[0]['negScore']
        a = 0
        if x[0] in titleQuery:
            a+=10
        else:
            a-=10
        if x[0] in ideaQuery:
            a+=2
        else:
            a-=2
        if x[0] in stemQuery:
            a+=2
        else:
            a-=2
        if x[0] in categoryQuery:
            a+=3
        else:
            a-=3
        if x[0] in ageQuery:
            a+=3
        else:
            a-=3
        if x[0] in ageSpecificQuery:
            a+=3
        else:
            a-=3
        if x[0] in budgetQuery:
            a+=8
        else:
            a-=4
        if x[0] in geslachtQuery:
            a+=8
        else:
            a-=6
        score1 = pos-neg
        if pos>0 or neg >0:
            score1= float(score1/(pos+neg))
            if a!=0:
                a += int(score1/a)
        else:
            a+= score1
        finalScore.append([x[0],a])
    finalScore = sorted(finalScore, key=lambda x: x[1])[::-1]
    lenScores = [y for [x,y] in finalScore].count(finalScore[0][1])
    finalScore = finalScore[:max(100,lenScores)]
    if lenScores >3:
        copy = finalScore[:lenScores]
        random.shuffle(copy)
        finalScore[:lenScores] = copy
    if lenScores<30:
        lenScores = 30
    chosenProducts = finalScore[:lenScores]
    if lenScores>50:
        lenScores = 50
    chosenProducts = chosenProducts[:lenScores]
    levs = []
    for x in chosenProducts:
        for y in chosenProducts:
            if x!=y:
                levs.append([x[0]['_id'], y[0]['_id'], score(x[0]['title'], y[0]['title']) ,liquidmetal.score(x[0]['title'], y[0]['title']) ])
    final = []
    twolist1 = [[(x, y), z] for [x, y, z,s] in levs]
    twolistdict = {x: z for [x, z] in twolist1}
    twolist2 = [[x, y] for [x, y, z,s] in levs]
    twolist2 = [item for items in twolist2 for item in items]
    leftover = [item[0]['_id'] for item in chosenProducts if item[0]['_id'] not in twolist2]
    #now we make a graph consisting all cd's as nodes and possible duplicate relations as edges with the probability as weight
    mGraph = nx.Graph()
    count = 0
    for [x, y, z, s] in levs:
        if z <0.7 or s >0.5:
            count += 1
            mGraph.add_edge(x, y, weight=z)
    for item in leftover:
        mGraph.add_node(item)
    graphs = list(nx.connected_component_subgraphs(mGraph))
    l = (sorted(map(sorted, mGraph.edges())))
    a = [x for [x,y] in l]
    b = [y for [x,y] in l]
    c = a+b
    c = list(set(c))
    for x in a:
        for y in b:
            if [x,y] in l:
                if y in c:
                    c.remove(y)
    u = [x['title'] for [x,y] in chosenProducts if x['_id'] in c]
    finalScore = [x for [x,y] in chosenProducts if x['_id'] in c] + [item[0] for item in finalScore[lenScores:]]
    return finalScore[:n]
#
# x = findRightProduct(u'jongen', [u'15', u'30'], '2.5', [u'Razende racers en stoere stuurders', u'Rocksterren en stijliconen'], u'', 18)
#
# for y in x :
#     print(y['title'])

def printprod(L):
    for x in L:
        print(x[0]['title'], x[1])

# # finding one unique toy by article number [title, brand, price, age, gender, page, img_link]
# @app.route('/articles/<geslacht>/<budget>/<bedrag>/age/<jaar>')
def findByTrinity(geslacht,budget,bedrag,jaar):
    try:
        # append this madness dictionary regarding age
        query = [{'age': 'alle leeftijden'}]
        if jaar == '0':
            query.append({'age': 'Vanaf 0 maanden'})
            query.append({'age': '0 jaar tot 1 jaar'})
            query.append({'age': '0 jaar tot 2 jaar'})
            query.append({'age': '0 jaar tot 3 jaar'})
            query.append({'age': '0 maanden tot 3 jaar'})
            query.append({'age': '0 maanden tot 4 jaar'})
            query.append({'age': '0 maanden tot 5 jaar'})
            query.append({'age': '3 maanden tot 1 jaar'})
            query.append({'age': 'Tot 12 maanden'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '1':
            query.append({'age': '1 jaar tot 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': '1,5 jaar tot 3 jaar'})
            query.append({'age': '1,5 jaar tot 4 jaar'})
            query.append({'age': '1,5 jaar tot 5 jaar'})
            query.append({'age': '1,5 jaar tot 8 jaar'})
            query.append({'age': '1,5 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '2':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': '1 jaar tot 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 3 jaar'})
            query.append({'age': '2 jaar tot 4 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 4 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '6 maanden tot 3 jaar'})
            query.append({'age': '6 maanden tot 4 jaar'})
            query.append({'age': '10 maanden tot 3 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '3':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': '1 jaar tot 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 4 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 4 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 4 jaar'})
            query.append({'age': '3 jaar tot 5 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 3 tot 8 jaar'})
            query.append({'age': 'Vanaf 3 tot 11 jaar'})
            query.append({'age': 'Vanaf 3 tot 12 jaar'})
            query.append({'age': 'Vanaf 3 tot 99 jaar'})
            query.append({'age': '6 maanden tot 4 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '4':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': '1 jaar tot 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 5 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 5 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 5 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 6 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 11 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '5':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': '1 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '2,5 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 6 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 6 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': '6 jaar tot 8 jaar'})
            query.append({'age': '6 jaar tot 10 jaar'})
            query.append({'age': '6 jaar tot 12 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '6':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 7 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '7':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': '2 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 8 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 8 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '8':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '9':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': '3 jaar tot 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 10 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 10 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 10 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 10 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '10':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 11 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 11 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 11 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
        elif jaar == '11':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': '3 jaar tot 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '4 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 12 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 4 tot 12 jaar'})
            query.append({'age': 'Vanaf 5 tot 12 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 12 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 12 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '12':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '13':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 14 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': 'vanaf 7 tot 14 jaar'})
            query.append({'age': 'Vanaf 7 tot 14 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '14':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': '5 jaar tot 15 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '15':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '16':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        elif jaar == '17':
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})
        else:
            query.append({'age': 'vanaf 1 jaar'})
            query.append({'age': 'vanaf 1,5 jaar'})
            query.append({'age': 'vanaf 2 jaar'})
            query.append({'age': 'Vanaf 1 jaar'})
            query.append({'age': 'Vanaf 1,5 jaar'})
            query.append({'age': 'Vanaf 2 jaar'})
            query.append({'age': 'vanaf 3 jaar'})
            query.append({'age': 'Vanaf 3 jaar'})
            query.append({'age': 'vanaf 4 jaar'})
            query.append({'age': 'Vanaf 4 jaar'})
            query.append({'age': 'vanaf 5 jaar'})
            query.append({'age': 'Vanaf 5 jaar'})
            query.append({'age': 'vanaf 6 jaar'})
            query.append({'age': 'Vanaf 6 jaar'})
            query.append({'age': 'vanaf 7 jaar'})
            query.append({'age': 'Vanaf 7 jaar'})
            query.append({'age': 'vanaf 8 jaar'})
            query.append({'age': 'Vanaf 8 jaar'})
            query.append({'age': 'vanaf 9 jaar'})
            query.append({'age': 'Vanaf 9 jaar'})
            query.append({'age': 'vanaf 10 jaar'})
            query.append({'age': 'Vanaf 10 jaar'})
            query.append({'age': 'vanaf 12 jaar'})
            query.append({'age': 'Vanaf 12 jaar'})
            query.append({'age': 'vanaf 13 jaar'})
            query.append({'age': 'vanaf 14 jaar'})
            query.append({'age': 'vanaf 16 jaar'})
            query.append({'age': 'Vanaf 16 jaar'})
            query.append({'age': 'vanaf 18 jaar'})
            query.append({'age': 'Vanaf 18 jaar'})
            query.append({'age': '3 jaar tot 99 jaar'})
            query.append({'age': 'Vanaf 6 tot 99 jaar'})
            query.append({'age': '10 maanden tot 99 jaar'})
            query.append({'age': 'vanaf 9 tot 99 jaar'})
            query.append({'age': 'Vanaf 9 maanden'})
            query.append({'age': 'Vanaf 10 maanden'})
            query.append({'age': ''})

        query2 = ''
        if geslacht == 'jongen':
            query2 = 'Jongen'
        elif geslacht == 'meisje':
            query2 = 'Meisje'
        else:
            query2 = 'Beide'

        query3 = ''
        if budget == 'minder':
            query3 = '$lte'
        else:
            query3 = '$gte'

        catalogus = db.speelgoed
        # results = catalogus.find({ '$or': query, 'gender': query2, 'price': {query3: int(bedrag)} })
        # ordered = results.sort('price')
        #
        # output = ''
        # for r in ordered:
        #     output += r['title'] + ', ' + r['brand'] + ', ' + str(r['price']) + ', ' + r['age'] + ', ' + r['gender'] + ', ' + str(r['page']) + ', <a href="' + r['img_link'] + '">' + r['img_link'] + '</a><br>'
        # return output

        data = list(catalogus.find({ '$or': query, 'gender': query2, 'price': {query3: int(bedrag)} }))
        return data

    except Exception, e:
        return 'Not found an article'

def addImg(artnr, img):
    try:
        catalogus = db.speelgoed
        catalogus.update_one(
            {'_id': artnr},
            {'$set': {'img_link':img}}
        )
        print('finished')
        return 'doei'
    except Exception, e:
        print(e)
        return 'Not found an article'

def changeImage():
    prod = findAllArticles()
    for x in prod:
        newImage = ''
        if x['img_link'].startswith('https://ca'):
            print(x['img_link'])
            if x['retailer'] == 'intertoys':
                if x['article_number'] == 1380441:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2F'+ str(x['page']) + '-' + str(x['article_number']) +'.png&width=400&height=200'
                elif x['article_number'] in [1020822,1020814, 1020826, 1020831, 1020630, 1020314, 1020533, 1020395, 1020141]:
                    newImage = 'https://www.onlinepublisher.nl/Chatbot/intertoys/p'+ str(x['page']) + '-' + str(x['article_number'])+ ".png"
                elif x['page'] > 33:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2Fp'+ str(x['page']) + '_' + str(x['article_number']) +'.png&width=400&height=200'
                else:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2Fp'+ str(x['page']) + '-' + str(x['article_number']) +'.png&width=400&height=200'
            else:
                newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fbartsmit%2Fp'+ str(x['page']) + '_' + str(x['article_number']) +'.png&width=400&height=200'
        if x['img_link'].startswith('https://www.onl'):
            print(x['img_link'])
            if x['retailer'] == 'intertoys':
                if x['article_number'] == 1380441:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2F'+ str(x['page']) + '-' + str(x['article_number']) +'.png&width=400&height=200'
                elif x['article_number'] in [1020822,1020814, 1020826, 1020831, 1020630, 1020314, 1020533, 1020395, 1020141]:
                    newImage = 'https://www.onlinepublisher.nl/Chatbot/intertoys/p'+ str(x['page']) + '-' + str(x['article_number'])+ ".png"
                elif x['page'] > 33:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2Fp'+ str(x['page']) + '_' + str(x['article_number']) +'.png&width=400&height=200'
                else:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2Fp'+ str(x['page']) + '-' + str(x['article_number']) +'.png&width=400&height=200'
            else:
                newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fbartsmit%2Fp'+ str(x['page']) + '_' + str(x['article_number']) +'.png&width=400&height=200'
        if x['img_link'] == 'x':
            print(x['img_link'])
            if x['retailer'] == 'intertoys':
                if x['article_number'] == 1380441:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2F'+ str(x['page']) + '-' + str(x['article_number']) +'.png&width=400&height=200'
                elif x['article_number'] in [1020822,1020814, 1020826, 1020831, 1020630, 1020314, 1020533, 1020395, 1020141]:
                    newImage = 'https://www.onlinepublisher.nl/Chatbot/intertoys/p'+ str(x['page']) + '-' + str(x['article_number'])+ ".png"
                elif x['page'] > 33:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2Fp'+ str(x['page']) + '_' + str(x['article_number']) +'.png&width=400&height=200'
                else:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2Fp'+ str(x['page']) + '-' + str(x['article_number']) +'.png&width=400&height=200'
            else:
                newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fbartsmit%2Fp'+ str(x['page']) + '_' + str(x['article_number']) +'.png&width=400&height=200'
        if not x['img_link']:
            print(x['img_link'])
            if x['retailer'] == 'intertoys':
                if x['article_number'] == 1380441:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2F'+ str(x['page']) + '-' + str(x['article_number']) +'.png&width=400&height=200'
                elif x['article_number'] in [1020822,1020814, 1020826, 1020831, 1020630, 1020314, 1020533, 1020395, 1020141]:
                    newImage = 'https://www.onlinepublisher.nl/Chatbot/intertoys/p'+ str(x['page']) + '-' + str(x['article_number'])+ ".png"
                elif x['page'] > 33:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2Fp'+ str(x['page']) + '_' + str(x['article_number']) +'.png&width=400&height=200'
                else:
                    newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fintertoys%2Fp'+ str(x['page']) + '-' + str(x['article_number']) +'.png&width=400&height=200'
            else:
                newImage = 'https://cache.onlinepublisher.nl/fsicache/server?type=image&source=shares%2FChatbot%2Fbartsmit%2Fp'+ str(x['page']) + '_' + str(x['article_number']) +'.png&width=400&height=200'
        if newImage:
            print(x['title'], newImage)
            addImg(x['_id'], newImage)
    return 'done'

# changeImage()
"""



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
