from flask import Flask, request
import json
import requests
import sys
from wit import Wit
# from runLogin import getIt
import random
import datetime
import talkbot as tb
import ast
import mongo as mg
from flask import g
import time
import os
import re
import traceback
from sendcode import *
# Number of presented articles

# childTypes = mg.findConfig(18)
TokenStages = mg.findConfig(19)
responsemessage = mg.findConfig(20)
presentmessage1 = mg.findConfig(21)
presentmessage3 = mg.findConfig(22)
# personalitymessages = mg.findConfig(23)
faulwords = mg.findConfig(24)
Tokens = mg.findConfig(25)
Triggers = mg.findConfig(50)
startmessage = mg.findConfig(51)
Chitchat = mg.findConfig(52)
finalResponses = mg.findConfig(53)
# extraChitchat = mg.findConfig(53)
TriggerPhrases = Triggers['tigger']
TriggerCats = Triggers['answers']

thank_quotes = ['bedankt','dank je wel', 'gaaf','dankjewel','dank je']
bye_quotes = ['bye bye','bye','later','tot ziens','doei','laters','mazzel']
stop_quotes = ['stop','exit','eind','abort','cancel']
# sentimentClassifier = pickle.load( open( "sentiment_analysis_final.p", "rb" ) )

def contains_word(w,s):
    s = re.findall(r"[\w']+|[.,!?;]", s)
    print(s)
    if w in s:
        return True
    else:
        return False

app = Flask(__name__)

dashbotAPI, PAT = os.environ['dashbotAPI'], os.environ['PAT']

""" FORMULAS ON TEXT PROCESSING

Below you find all formulas needed to preprocess and process the message,
dictionaries and other data sets.
"""


def findword(string):
    string = string.lower()
    if True in [x in faulwords for x in string.split()]:
        return True
    else:
        return False

def triggered(message, sender):
    message = message.lower()
    if message in traverse(TriggerPhrases):
        i = find(message,TriggerPhrases)
        reaction = random.choice(TriggerCats[i])
        time.sleep(1.5)
        typing('off', PAT, sender)
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": PAT},
        data=json.dumps({
          "recipient": {"id": sender},
          "message": {"text": reaction}
        }),
        headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
        	print r.text
        return True
    else: return False

def find(target,L):
    for i,lst in enumerate(L):
        for j,color in enumerate(lst):
            if color == target:
                return i
    return None

def get_keys(d,target):
    result = []
    path = []
    get_key(d,target, path, result)
    return result[0]

def traverse(o, tree_types=(list, tuple)):
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value, tree_types):
                yield subvalue
    else:
        yield o

def allValues(dictionary):
    ans = []
    for k,v in dictionary.items():
        if isinstance(v,dict):
            ans.extend(allValues(v))
        else:
            ans.append(v)
    return ans

def mergedicts(L):
    intersect = []
    for item in L[0]:
        x = [True for y in L[0:] if item in y]
        if len(x) == len(L):
            intersect.append(item)
    return intersect

def findValue(L,d):
	for x in L:
		d = d[x]
	return d

def findNo(L):
	num = L.count('Nee')
	if num == 0:
		pers = 'Extraverion'
	elif num == 1:
		pers = 'Agreebableness'
	elif num == 2:
		pers = 'Openess'
	elif num == 3:
		pers = 'Conciousness'
	elif num == 4:
		pers = 'Default'
	return pers

def get_key(d, target, path, result):
    for k, v in d.iteritems():
        path.append(k)
        if isinstance(v, dict):
            get_key(v, target, path, result)
        if v == target:
            result.append(copy(path))
        path.pop()

def replace_value_with_definition(key_to_find, definition, current_dict):
    for key in current_dict.keys():
        if key == key_to_find:
            current_dict[key] = definition
    return current_dict

def word_feats(words):
    return dict([(word, True) for word in words])

""" FORMULAS TO MAKE CALLS TO FACEBOOK/DASHBOT

below all functions that make calls to dashbot and facebook to extract
or write data can be found.

"""

def makeStartScreen(token):
  r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings",
    params={"access_token": token},
    data=json.dumps({
          "setting_type":"call_to_actions",
          "thread_state":"new_thread",
          "call_to_actions":[
            {
              "payload":"START"
            }
          ]
        }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

@app.route('/', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.challenge'):
        if not request.args.get('hub.verify_token') == 'my_voice_is_my_password_verify_me':
            return 'Verification token mismatch', 403
        return request.args['hub.challenge'], 200
    return 'Hello world', 200

def typing(opt, token, recipient):
    if opt == 'on':
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": token},
        data=json.dumps({
                    "recipient":{
                    "id":recipient
                    },
                    "sender_action":"typing_on"
                    }),
        headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
            print r.text
    if opt == 'off':
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": token},
        data=json.dumps({
                    "recipient":{
                    "id":recipient
                    },
                    "sender_action":"typing_off"
                    }),
        headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
            print r.text

def postdashbot(id, payload):
  if id == 'human':
    payload1 = json.loads(payload)
    sender = payload1['entry'][0]['messaging'][0]['sender']['id']
    data = mg.findUser(sender)
    if mg.findUser(sender):
        data['messagenumberresponse'] +=1
        mg.updateUser(sender,data)
    print('send to dashbot ')
    r = requests.post("https://tracker.dashbot.io/track?platform=facebook&v=0.7.4-rest&type=incoming&apiKey=" + dashbotAPI,
        data=payload,
        headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print r.text
  if id == 'bot':
    data = mg.findUser(payload[0])
    data['messagenumberresponse'] +=1
    mg.updateUser(payload[0], data)
    print('send botshit to dashbot ')
    r = requests.post("https://tracker.dashbot.io/track?platform=facebook&v=0.7.4-rest&type=outgoing&apiKey=" + dashbotAPI,
        data=json.dumps({"qs":{"access_token":PAT},"uri":"https://graph.facebook.com/v2.6/me/messages","json":{"message":{"text":payload[1]},"recipient":{"id":payload[0]}},"method":"POST","responseBody":{"recipient_id":payload[0],"message_id":payload[2]}}),
        headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print r.text

def getdata(id):
    json1 = requests.get('https://graph.facebook.com/v2.6/'+ id+ '?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=' + PAT).text
    d = ast.literal_eval(json1)
    return d

""" FUNCTIONS TO RETRIEVE THE REIGHT ANSWER FROM WIT.AI.

below all functions that talk with wit.ai or search for a token are found.
"""

def mergeAns(response, witToken, session_id, question):
    if 'type' in response:
        action = response['type']
        if action == 'merge':
            return tb.response('', witToken, session_id)
        else:
            return response
    else:
        return response

def getInformation(response, tekst):
    feedback = tekst
    x = 0
    out  = {}
    if feedback == '\U0001f600':
        x = '5'
    if feedback == '\U0001f60a':
        x = '4'
    if feedback == '\U0001f610':
        x = '3'
    if feedback == '\U0001f614':
        x = '2'
    if feedback == '\U0001f620':
        x = '1'
    if int(x) > 0:
        out['Feedback'] = x
        print('got feedback')
    if 'entities' in response:
        entities = response['entities']
        if 'Eten' in entities and entities['Eten'][0]['confidence'] > 0.8:
            out['Ingredient'] = entities['Eten'][0]['value']

        # if 'Feedback' in entities and entities['Feedback'][0]['confidence'] > 0.6:
        #     out['Feedback'] = entities['Feedback'][0]['value']
    return out

def findAnswer(response, question,witToken,data):
    session_id = data['session']
    information = getInformation(response,question)
    response = mergeAns(response, witToken, session_id, question)
    information.update(getInformation(response,question))
    return response,data, information

def getResponse(recipient, text, data):
  response = tb.response(text, data['token'], data['session'])
  if 'msg' not in response:
      response, data, information = findAnswer(response,text,data['token'],data)
      data['data'].update(information)
  information = getInformation(response, text)
  data['data'].update(information)
  mg.updateUser(recipient, data)
  return response, data

def getFeedback(data):
    feedback = data['data']['Feedback']
    if feedback == '\U0001f600':
        return '5'
    if feedback == '\U0001f60a':
        return '4'
    if feedback == '\U0001f610':
        return '3'
    if feedback == '\U0001f614':
        return '2'
    if feedback == '\U0001f620':
        return '1'

def presentMeal(token, recipient, data):
    data['data']['Ingredient'] = ''
    if data['ideeen']:
        meals = [x for x in data['ideeen']]
    else:
        if 'NagerechtSmaak' not in  data['data']:
            if 'technique' not in data['data']:
                meals = mg.findRightProduct(data['data']['Ingredient'], '', '', data['data']['level'], data['data']['gang'],'')
            else:
                meals = mg.findRightProduct(data['data']['Ingredient'], '', data['data']['technique'], data['data']['level'], data['data']['gang'],'')
        elif 'voorkeur' not in  data['data']:
            if 'technique' not in data['data']:
                meals = mg.findRightProduct(data['data']['Ingredient'], data['data']['NagerechtSmaak'], '', data['data']['level'], data['data']['gang'],'')
            else:
                meals = mg.findRightProduct(data['data']['Ingredient'], data['data']['NagerechtSmaak'], data['data']['technique'], data['data']['level'], data['data']['gang'],'')
        else:
            meals = mg.findRightProduct(data['data']['Ingredient'], data['data']['NagerechtSmaak'], data['data']['technique'], data['data']['level'], data['data']['gang'],data['data']['voorkeur'])
        data['ideeen'] = meals
    meals = [x for x in meals if x not in data['presented']]
    if meals:
        if isinstance(meals[0], list):
            meal1 = []
            meal2 = []
            meal3 = []
            if meals[0] and meals[1] and meals[2]:
                meal1 = meals[0][0]
                meal2 = meals[1][0]
                meal3 = meals[2][0]

                postdashbot('bot',(recipient,'meal: '+ meal1['Title']+ meal2['Title']+ meal3['Title'], data['message-id']) )
                data['presented'].extend([meal1, meal2, meal3])
                data['ideeen'][0].remove(meal1)
                data['ideeen'][1].remove(meal2)
                data['ideeen'][2].remove(meal3)
                typing('off', PAT, recipient)
                if meal1['Winkel'] == 'Jumbo':
                    pag1 = 'https://www.spotta.nl/folders/jumbo?fid=1194&startpage=' + str(meal1['Pagina'])
                else:
                    pag1 = 'https://www.spotta.nl/folders/lidl?fid=1213&startpage=' + str(meal1['Pagina'])
                if meal2['Winkel'] == 'Jumbo':
                    pag2 = 'https://www.spotta.nl/folders/jumbo?fid=1194&startpage=' + str(meal2['Pagina'])
                else:
                    pag2 = 'https://www.spotta.nl/folders/lidl?fid=1213&startpage=' + str(meal2['Pagina'])
                if meal3['Winkel'] == 'Jumbo':
                    pag3 = 'https://www.spotta.nl/folders/jumbo?fid=1194&startpage=' + str(meal3['Pagina'])
                else:
                    pag3 = 'https://www.spotta.nl/folders/lidl?fid=1213&startpage=' + str(meal3['Pagina'])
                sendTemplate(recipient, ['''
                {"title":"'''+ meal1['Title']+ '''",
                    "item_url":"'''+ pag1+ '''",
                    "image_url":"'''+ meal1['Link afbeelding']+ '''",
                    "buttons":[
                      {
                        "type":"web_url",
                        "url": "'''+ pag1+ '''",
                        "title":"Bekijk het recept!"
                      }]}''',
                  '''{
                    "title":"'''+ meal2['Title']+ '''",
                    "item_url":"'''+ pag2+ '''",
                    "image_url":"'''+ meal2['Link afbeelding']+ '''",
                    "buttons":[
                        {
                          "type":"web_url",
                          "url": "'''+ pag2+ '''",
                          "title":"Bekijk het recept!"
                        }]}''',
                    '''{
                    "title":"'''+ meal3['Title']+ '''",
                    "item_url":"'''+ pag3+ '''",
                    "image_url":"'''+ meal3['Link afbeelding']+ '''",
                    "buttons":[
                      {
                        "type":"web_url",
                        "url": "'''+ pag3+ '''",
                        "title":"Bekijk het recept!"
                      }]}'''])
                mg.updateUser(recipient, data)
            else:
                return False
        else:
            meal = meals[0]
            data['ideeen'].remove(meal)
            postdashbot('bot',(recipient,'meal: '+ meal['Title'], data['message-id']) )
            data['presented'].append(meal)
            typing('off', PAT, recipient)
            if meal['Winkel'] == 'Jumbo':
                pag = 'https://www.spotta.nl/folders/jumbo?fid=1194&startpage=' + str(meal['Pagina'])
            else:
                pag = 'https://www.spotta.nl/folders/lidl?fid=1213&startpage=' + str(meal['Pagina'])
            sendTemplate(recipient, ['''{
                "title":"'''+ meal['Title']+ '''",
                "item_url":"'''+ pag+ '''",
                "image_url":"'''+ meal['Link afbeelding']+ '''",
                "buttons":[
                  {
                    "type":"web_url",
                    "url": "'''+ pag+ '''",
                    "title":"Bekijk het recept!"
                  }]}'''])
            mg.updateUser(recipient, data)
        return True

def findToken(recipient, data, text):
  data['session'] = 'GreenOrange-session-' + str(datetime.datetime.now()).replace(" ", '')
  oldToken = data['token']
  Stage = data['Stage']
  if Stage == 'Welkom':
    #   data['data']['type'] = text
      if text == 'Een gang':
          data['data']['type'] = 'gang'
          NextStage = TokenStages[TokenStages.index(Stage)+1]
          data['Stage'] = NextStage
          mg.updateUser(recipient, data)
          send_message(PAT, recipient, 'gang', data)
      elif text == 'Een menu':
          data['data']['type'] = 'menu'
          data['data']['gang'] = ['Voorgerecht', 'Hoofdgerecht','Nagerecht']
          NextStage = TokenStages[TokenStages.index(Stage)+1]
        #   data['token'] = 'personality'
        #   data['chitchat'].append(data['token'])
          data['Stage'] = NextStage
          mg.updateUser(recipient, data)
          send_message(PAT, recipient, 'menu', data)
  elif Stage == 'Gangen':
      NextStage = TokenStages[TokenStages.index(Stage)+1]
      data['Stage'] = NextStage
      response = {}
      mg.updateUser(recipient, data)
      send_message(PAT, recipient, 'Keuze', data)
  elif Stage == 'Keuzes':
    #   if not all(k in data['data'] for k in ['Ingredient']):
    #       data['token'] = random.choice(allValues(Tokens[Stage]))
    #       while get_keys(Tokens, data['token'])[-1] in data['data']:
    #           data['token'] = random.choice(allValues(Tokens[Stage]))
    #       data['starter'] = get_keys(Tokens, data['token'])[-1]
    #       mg.updateUser(recipient, data)
    #       send_message(PAT, recipient, data['starter'], data)
    #   else:
      NextStage = TokenStages[TokenStages.index(Stage)+1]
      data['Stage'] = NextStage
      response = {}
      mg.updateUser(recipient, data)
      send_message(PAT, recipient, 'presentatie', data)
  elif Stage == 'Presentatie':
      if text == 'again':
          data['data'] = []
          data['Stage'] = 'Welkom'
          mg.updateUser(recipient, data)
          send_message(PAT, recipient, 'ta', data)
      elif text == 'end':
          NextStage = TokenStages[-1]
          data['Stage'] = NextStage
          findToken(recipient, data, text)
      else:
          NextStage = TokenStages[TokenStages.index(Stage)+1]
          data['token'] = random.choice(allValues(Tokens[NextStage]))
          if isinstance(data['token'], dict):
              data['token'] = random.choice(allValues(Tokens[NextStage]))
              data['starter'] = get_keys(Tokens, data['token'])[-1]
          data['Stage'] = NextStage
          mg.updateUser(recipient, data)
          send_message(PAT, recipient, data['starter'], data)
  elif Stage == 'Feedback':
      NextStage = TokenStages[TokenStages.index(Stage)+1]
      data['Stage'] = NextStage
      response = {}
      mg.updateUser(recipient, data)
      send_message(PAT, recipient, '', data)
  elif TokenStages.index(Stage) < len(TokenStages)-1:
      NextStage = TokenStages[TokenStages.index(Stage)+1]
      data['token'] = random.choice(allValues(Tokens[NextStage]))
      if isinstance(data['token'], dict):
          data['token'] = random.choice(allValues(Tokens[NextStage]))
          data['starter'] = get_keys(Tokens, data['token'])[-1]
      data['Stage'] = NextStage
      mg.updateUser(recipient, data)
      send_message(PAT, recipient, data['starter'], data)
  else:
      print('end of conversation')
      typing('off', PAT, recipient)
      data['dolog'] = 'end'
      response = {}
      mg.updateUser(recipient, data)

def messageSend(recipient,message, token,data):
    data['text'].append(('bot',message))
    data['oldmessage'] = message
    postdashbot('bot',(recipient,message, data['message-id']))
    typing('off', token, recipient)
    time.sleep(1)
    return data

def isFood(text):
    x = tb.response(text,"CWHC2L5AL2SCFI7IDA56Q57Y6B4EENZB", 'GreenOrange-session-' + str(datetime.datetime.now()).replace(" ", ''))
    if 'entities' in x:
        entities = x['entities']
        if 'Eten' in entities:
            return entities['Eten'][0]['confidence']
        else:
            return False
    else:
        return False


""" FUNCTIONS TO RECEIVE AND SEND MESSAGES

below the receive and send functions can be found.

"""

@app.route('/', methods=['POST'])
def handle_messages():
  payload = request.get_data()
  for sender, message, mid, recipient in messaging_events(payload) :
    try:
        print("Incoming from %s: %s" % (sender, message))
        postdashbot('human', payload)
        if not mg.findUser(sender):
            typing('on', PAT, sender)
            user_info = getdata(sender)
            data = {}
            data['info'] = user_info
            data['dolog'] = ''
            data['Stage'] = TokenStages[0]
            data['text'] = []
            data['presented'] = []
            data['message-id'] = mid
            data['chitchat'] = []
            data['trig'] = False
            data['meals'] = []
            data['ideeen'] = []
            data['oldincoming'] = message
            data['oldmessage'] = ''
            data['messagenumber'] = 1
            data['messagenumberresponse'] = 0
            data['token'] = 'blah'
            data['starter'] = ''
            data['session'] = 'GreenOrange-session-' + str(datetime.datetime.now()).replace(" ", '')
            data['data'] = {}
            mg.insertUser(sender,data)
            typing('on', PAT, sender)
            data = send_message(PAT, sender, message,data)
            mg.insertUser(sender,data)
            data['message-id'] = mid
            if data['trig']:
                if text == 'Ja':
                    send_message(PAT, sender, data['oldmessage'],data)
                else:
                    typing('on', PAT, sender)
                    time.sleep(1.5)
                    typing('off', PAT, sender)
                    sendTexts(recipient,'Oke! Toch bedankt voor het fijne gesprek en veel plezier tijdens de feestdagen!')
                    data['dolog'] = 'end'
                    mg.updateUser(recipient, data)
        else:
            data = mg.findUser(sender)
            print(mid, data['message-id'])
            if mid != data['message-id']:
                data['messagenumber'] +=1
                # if data['messagenumber'] > data['messagenumberresponse']+2:
                #     pass
                if findword(message):
                    typing('on', PAT, sender)
                    time.sleep(1.5)
                    typing('off', PAT, sender)
                    message = 'Wij houden hier niet zo van schelden. Zou je hier alsjeblieft mee willen stoppen!.'
                    data['text'].append(('bot',message))
                    data['oldmessage'] = message
                    postdashbot('bot',(sender,message, data['message-id']) )
                    typing('off', PAT, sender)
                    sendTexts(recipient,message)
                    time.sleep(1)
                    message = 'Wil je nu verder met het zoeken van een lekker gerecht'
                    data['text'].append(('bot',message))
                    data['oldmessage'] = message
                    postdashbot('bot',(sender,message, data['message-id']) )
                    typing('off', PAT, sender)
                    quicks = [ 'Ja','Nee']
                    sendQuicks(recipient,message,quicks)
                    data['trig'] = True
                    mg.updateUser(recipient, data)
                elif triggered(message, sender):
                    typing('on', PAT, sender)
                    time.sleep(1.5)
                    message = 'Wil je nu verder met het zoeken van een lekker gerecht?'
                    data['text'].append(('bot',message))
                    data['oldmessage'] = message
                    postdashbot('bot',(sender,message, data['message-id']) )
                    typing('off', PAT, sender)
                    quicks = [ 'Ja','Nee']
                    sendQuicks(recipient,message,quicks)
                    data['trig'] = True
                    mg.updateUser(recipient, data)
                elif data['trig']:
                    if text == 'Ja':
                        send_message(PAT, sender, 'triggermessage',data)
                        data['trig'] = False
                    else:
                        typing('on', PAT, sender)
                        data['trig'] = False
                        time.sleep(1.5)
                        typing('off', PAT, sender)
                        sendTexts(recipient,'Oke! Toch bedankt voor het fijne gesprek en veel plezier tijdens pakjesavond!')
                        data['dolog'] = 'end'
                        mg.updateUser(recipient, data)
                elif mid != data['message-id']:
                    typing('on', PAT, sender)
                    if data['dolog'] == 'end':
                        if message in finalResponses:
                            print('no response')
                        else:
                            log = {}
                            if 'Feedback' in data['data']:
                                log['feedback']= (data['data']['Feedback'])
                            else:
                                log['feedback']= ('0')
                            if data['info']:
                                log['info']= data['info']
                            if data['data']:
                                log['data']= (data['data'])
                            if data['presented']:
                                log['presented']=(data['presented'])
                            if data['text']:
                                log['text'] = data['text']
                            log['id'] = sender
                            mg.logging(log)
                            data['Stage'] = TokenStages[0]
                            data['text'] = []
                            if len (data['chitchat']) > 3:
                                data['chitchat'] = []
                            data['dolog'] = 'again'
                            data['meals'] = []
                            data['ideeen'] = []
                            data['trig'] = False
                            data['token'] = '2'
                            data['starter'] = ''
                            data['session'] = 'GreenOrange-session-' + str(datetime.datetime.now()).replace(" ", '')
                            data['data'] = {}
                    data['text'].append(('user',message))

                    data['message-id'] = mid
                    data['oldincoming'] = message
                    mg.updateUser(recipient, data)
                    data = send_message(PAT, sender, message,data)
            mg.updateUser(recipient, data)
    except KeyboardInterrupt as e:
        print "Caught it!"
        print(sender)
        print(e)
        data['message-id'] = mid
        data['oldincoming'] = message
        data = mg.findUser(sender)
        if isinstance(data,dict):
            data['message-id'] = mid
        else:
            data = {}
            data['message-id'] = mid
            mg.updateUser(recipient, data)
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": PAT},
        data=json.dumps({
          "recipient": {"id": 1527380337277466},
          "message": {"text": str(e)
        }}),
        headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
        	print r.text
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": PAT},
        data=json.dumps({
          "recipient": {"id": sender},
          "message": {"text": 'Sorry, daar ging even iets fout'
        }}),
        headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
        	print r.text
    except Exception as e:
        print "Caught it!"
        print(sender)
        print(e)
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info
        data = mg.findUser(sender)
        if isinstance(data,dict):
            data['message-id'] = mid
        else:
            data = {}
            data['message-id'] = mid
            mg.updateUser(recipient, data)
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": PAT},
        data=json.dumps({
          "recipient": {"id": 1527380337277466},
          "message": {"text": str(e)
        }}),
        headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
        	print r.text
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": PAT},
        data=json.dumps({
          "recipient": {"id": sender},
          "message": {"text": 'Sorry, daar ging even iets fout'
        }}),
        headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
        	print r.text
  return "ok", 200

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  if "messaging" in data["entry"][0]:
      messaging_events = data["entry"][0]["messaging"]
      for event in messaging_events:
        if "message" in event and "text" in event["message"] and 'is_echo' not in event["message"]:
          yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape'), event["message"]['mid'], event["recipient"]['id']
        if 'postback'in event:
          yield event["sender"]["id"], event["postback"]["payload"].encode('unicode_escape'), 'Postback', event["recipient"]['id']

def send_message(token, recipient, text, data):
  """Send the message text to recipient with id recipient.
  """
  print('Is it Food?: ' + str(isFood(text)))
  if data['dolog'] == 'end':
      print('done')
  elif text.lower() in thank_quotes:
            emoji = u"\U0001f44b"
            # emoji = myunicode.encode('utf-8')
            message = ':) jij ook bedankt en een prettige dag. ' + emoji
            data = messageSend(recipient,message, token,data)
            time.sleep(1)
            sendTexts(recipient, message)
  elif text.lower() in bye_quotes:
            emoji = u"\U0001f44b"
            # emoji = myunicode.encode('utf-8')
            message =  'Nog een prettige dag. ' + emoji
            data = messageSend(recipient,message, token,data)
            time.sleep(1)
            sendTexts(recipient, message)
  elif text.lower() in stop_quotes:
            emoji = u"\U0001f44b"
            # emoji = myunicode.encode('utf-8')
            message = 'Ik hoop dat alles gelukt is ' + emoji
            data = messageSend(recipient,message, token,data)
            time.sleep(1)
            sendTexts(recipient, message)
  elif data['Stage'] == 'Welkom':

    if text == 'Een gang' or text == 'Een menu':
        findToken(recipient, data, text)
    elif data['dolog'] == 'again':
        message = 'Welkom terug  ' + data['info']['first_name']+ '! Wat leuk dat je er weer bent :)'
        data = messageSend(recipient,message, token,data)
        sendTexts(recipient, message)
        message = 'Ben je op zoek naar een volledig menu, of heb je alleen inspiratie nodig voor een voor- hoofd- of nagerecht?'
        data = messageSend(recipient,message, token,data)
        quicks = ['Een gang', 'Een menu']
        sendImage(recipient, 'https://s23.postimg.org/v1hi3g6rv/IG_1gang_meergang.png')
        sendQuicks(recipient, message, quicks)
        data['dolog'] = ''
        mg.updateUser(recipient, data)
    elif text == 'ta':
        message = 'Ben je op zoek naar een volledig menu, of heb je alleen inspiratie nodig voor een voor- hoofd- of nagerecht?'
        data = messageSend(recipient,message, token,data)
        quicks = ['Een gang', 'Een menu']
        sendImage(recipient, 'https://s23.postimg.org/v1hi3g6rv/IG_1gang_meergang.png')
        sendQuicks(recipient, message, quicks)
        mg.updateUser(recipient, data)
    else:
        if data['oldmessage'] != 'Ben je op zoek naar een volledig menu, of heb je alleen inspiratie nodig voor een voor- hoofd- of nagerecht?':
            message = 'Hallo ' + data['info']['first_name']+ '! Ik ben jouw hulp in de keuken en help je graag met het uitzoeken van het perfecte menu voor het kerstdiner.'
            data = messageSend(recipient,message, token,data)
            sendTexts(recipient, message)
            message = 'Ben je op zoek naar een volledig menu, of heb je alleen inspiratie nodig voor een voor- hoofd- of nagerecht?'
            data = messageSend(recipient,message, token,data)
            quicks = ['Een gang', 'Een menu']
            sendImage(recipient, 'https://s23.postimg.org/v1hi3g6rv/IG_1gang_meergang.png')
            sendQuicks(recipient, message, quicks)
            mg.updateUser(recipient, data)
  elif data['Stage'] == 'Gangen' and data['data']['type'] == 'menu':
      if text == 'menu':
          message = 'Leuk om je te helpen bij het samenstellen van het kerstmenu. Mag ik vragen of het een vegetarisch, of een vlees/vis menu moet worden?'
          data = messageSend(recipient,message, token,data)
          quicks = ['Vlees/Vis','Vegetarisch', 'Geen voorkeur']
          sendImage(recipient, 'https://s23.postimg.org/dw0i692ob/IG_vlees_vega_01.png')
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif data['oldmessage'] == 'Leuk om je te helpen bij het samenstellen van het kerstmenu. Mag ik vragen of het een vegetarisch, of een vlees/vis menu moet worden?':
          if text == 'Vlees/Vis':
              message = 'Wil je dan vlees, vis of heb je geen voorkeur?'
              data = messageSend(recipient,message, token,data)
              quicks = ['Vis', 'Geen Voorkeur', 'Vlees']
              sendImage(recipient, 'https://s28.postimg.org/xft4djma5/IG_vis_vlees.png')
              sendImage(recipient, 'https://s28.postimg.org/ux7fcv0jx/IG_visvlees.png')
              sendQuicks(recipient, message, quicks)
              mg.updateUser(recipient, data)
          else:
              if text == 'geen voorkeur':
                  data['data']['voorkeur'] = ['Vlees', 'Vis', 'Vegetarisch']
              data['data']['voorkeur'] = text
              message = 'Ben je op zoek naar een ijsdessert of zit je meer te denken aan een taart of cake?'
              data = messageSend(recipient,message, token,data)
              quicks = ['Taart', 'Ijs']
              sendImage(recipient, 'https://s23.postimg.org/6m9a2e7uz/IG_cake_ijs.png')
              sendQuicks(recipient, message, quicks)
              mg.updateUser(recipient, data)
      elif data['oldmessage'] ==  'Wil je dan vlees, vis of heb je geen voorkeur?':
          if text == 'Geen Voorkeur':
              data['data']['voorkeur'] = ['Vis', 'Vlees']
          else:
              data['data']['voorkeur'] = text
          message = 'Ben je op zoek naar een ijsdessert of zit je meer te denken aan een taart of cake?'
          data = messageSend(recipient,message, token,data)
          quicks = ['Taart', 'IJs']
          sendImage(recipient, 'https://s23.postimg.org/6m9a2e7uz/IG_cake_ijs.png')
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif data['oldmessage'] == 'Ben je op zoek naar een ijsdessert of zit je meer te denken aan een taart of cake?':
          if text == 'Taart':
              data['data']['NagerechtSmaak'] = 'Cake'
          else:
              data['data']['NagerechtSmaak'] = text
          mg.updateUser(recipient, data)
          findToken(recipient, data, '')
      else:
          data['data']['NagerechtSmaak'] = text
          mg.updateUser(recipient, data)
          findToken(recipient, data, '')
  elif data['Stage'] == 'Gangen' and data['data']['type'] == 'gang':
      if text == 'gang':
          message = 'Voor welke gang heb je inspiratie nodig?'
          data = messageSend(recipient,message, token,data)
          sendImage(recipient, 'https://s23.postimg.org/uc3b4tvm3/IG_voor_hoofd.png')
          sendImage(recipient, 'https://s23.postimg.org/ce9e9jhor/IG_na.png')
          quicks = ['Voorgerecht', 'Hoofdgerecht', 'Nagerecht']
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif text in ['Voorgerecht', 'Hoofdgerecht']:
          data['data']['gang']= text
          message = 'Ben je op zoek naar een vegetarisch gerecht, of toch liever vlees of vis?'
          data = messageSend(recipient,message, token,data)
          sendImage(recipient, 'https://s23.postimg.org/dw0i692ob/IG_vlees_vega_01.png')
          quicks = ['Vlees', 'Vis', 'Vegetarisch']
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif text == 'Nagerecht':
          data['data']['gang']= text
          message = 'Ben je op zoek naar een ijsdessert of zit je meer te denken aan een taart of cake?'
          sendImage(recipient, 'https://s23.postimg.org/6m9a2e7uz/IG_cake_ijs.png')
          data = messageSend(recipient,message, token,data)
        #   data['data']['Nagerecht'] = text
          quicks = ['Taart', 'IJs']
        #   sendImage(Keuze gebruiker (visueel): vegetarisch of vlees/vis)
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif data['oldmessage'] == 'Ben je op zoek naar een ijsdessert of zit je meer te denken aan een taart of cake?':
          if text == 'Taart':
              data['data']['NagerechtSmaak'] = 'Cake'
          else:
              data['data']['NagerechtSmaak'] = text
          mg.updateUser(recipient, data)
          findToken(recipient, data, text)
      elif data['oldmessage'] == 'Ben je op zoek naar een vegetarisch gerecht, of toch liever vlees of vis?':
          data['data']['voorkeur'] = text
          mg.updateUser(recipient, data)
          findToken(recipient, data, text)
      elif text not in ['Voorgerecht', 'Hoofdgerecht', 'Nagerecht']:
          message = 'Wil je alsjeblieft de knoppen gebruiken? \nVoor welke gang heb je inspiratie nodig?'
          data = messageSend(recipient,message, token,data)
          sendImage(recipient, 'https://s23.postimg.org/uc3b4tvm3/IG_voor_hoofd.png')
          sendImage(recipient, 'https://s23.postimg.org/ce9e9jhor/IG_na.png')
          quicks = ['Voorgerecht', 'Hoofdgerecht', 'Nagerecht']
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
  elif data['Stage'] == 'Keuzes':
      if text == 'Keuze':
          message = 'Vind jij jezelf een echte sterrenchef of hou je het liever wat eenvoudiger?'
          data = messageSend(recipient,message, token,data)
          sendImage(recipient, 'https://s23.postimg.org/70am1zryj/IG_chef_amateur.png')
          quicks = ['Sterrenchef','Amateur']
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif data['oldmessage'] == 'Vind jij jezelf een echte sterrenchef of hou je het liever wat eenvoudiger?':
          data['data']['level'] = text
          if data['data']['gang'] != 'Nagerecht':
              message = 'En voor wat betreft de manier van bereiden, waar gaat je voorkeur dan naar uit?'
              data = messageSend(recipient,message, token,data)
              sendImage(recipient, 'https://s23.postimg.org/ehjth7hhn/IG_grill_oven.png')
              sendImage(recipient, 'https://s23.postimg.org/78iytm64r/IG_wok.png')
              quicks = ['Grillen', 'Oven', 'Bakken']
              sendQuicks(recipient, message, quicks)
              mg.updateUser(recipient, data)
          else:
              message = 'Ik weet genoeg! Ik ga voor je op zoek. Ben zo terug!'
              data = messageSend(recipient,message, token,data)
              sendTexts(recipient, message)
            #   message = 'Heb je bepaalde ingredienten in gedachten die je wil gebruiken?'
            #   data = messageSend(recipient,message, token,data)
            #   quicks = ['Ja', 'Nee']
            # #   sendImage(Keuze gebruiker (visueel): vegetarisch of vlees/vis)
            #   sendQuicks(recipient, message, quicks)
              mg.updateUser(recipient, data)
              findToken(recipient, data, text)
      elif data['oldmessage'] == 'En voor wat betreft de manier van bereiden, waar gaat je voorkeur dan naar uit?':

          data['data']['technique'] = text
          message = 'Ik weet genoeg! Ik ga voor je op zoek. Ben zo terug!'
          data = messageSend(recipient,message, token,data)
          sendTexts(recipient, message)
        #   message = 'Heb je bepaalde ingredienten in gedachten die je wil gebruiken?'
        #   data = messageSend(recipient,message, token,data)
        #   quicks = ['Ja', 'Nee']
        # #   sendImage(Keuze gebruiker (visueel): vegetarisch of vlees/vis)
        #   sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
          findToken(recipient, data, text)

    #   elif data['oldmessage'] == 'Heb je bepaalde ingredienten in gedachten die je wil gebruiken?':
    #       if text.lower() == 'nee':
    #           data['data']['Ingredient'] = ''
    #           message = 'Oke dan ga ik voor je zoeken, ben zo terug!'
    #           data = messageSend(recipient,message, token,data)
    #           sendTexts(recipient, message)
    #           mg.updateUser(recipient, data)
    #           findToken(recipient, data, text)
    #       else:
    #           message = 'Wat zijn je ideeen dan?'
    #           data = messageSend(recipient,message, token,data)
    #           sendTexts(recipient, message)
    #           mg.updateUser(recipient, data)
    #   elif data['oldmessage'] == 'Wat zijn je ideeen dan?':
    #       data['data']['Ingredient'] = text
    #       message = 'Ik weet genoeg! Ik ga voor je op zoek. Ben zo terug!'
    #       data = messageSend(recipient,message, token,data)
    #       sendTexts(recipient, message)
    #       mg.updateUser(recipient, data)
    #       findToken(recipient, data, text)
  elif data['Stage'] == 'Presentatie':
      if text == 'presentatie':
          if presentMeal(token, recipient, data):
              message = 'Lijkt dit je lekker?'
              data = messageSend(recipient,message, token,data)
              quicks = ['Ja', 'Nee']
              sendQuicks(recipient, message, quicks)
              mg.updateUser(recipient, data)
          else:
              message = 'Voor deze voorkeuren hebben we geen andere keuzes. \nWil je het opnieuw proberen?'
              data = messageSend(recipient,message, token,data)
              quicks = ['Ja', 'Nee']
              sendQuicks(recipient, message, quicks)
              mg.updateUser(recipient, data)

      elif data['oldmessage'] == 'We hebben helaas niks gevonden dat aan uw wensen voldoet \nWilt u het opnieuw proberen?':
          if text == 'Ja':
              print('again')
              findToken(recipient, data, 'again')
          elif text == 'Nee':
              message = 'Voor meer inspiratie kun je onderstaande folders bekijken.'
              data = messageSend(recipient,message, token,data)
              quicks = [
          {
            "type":"web_url",
            "url":"https://www.spotta.nl/folders/lidl?fid=1213",
            "title":"Lidl folder"
          },
          {
            "type":"web_url",
            "url":"https://www.spotta.nl/folders/jumbo?fid=1194",
            "title":"Jumbo folder"
          }
        ]
              sendButton(recipient, message, quicks)
              mg.updateUser(recipient, data)
              findToken(recipient, data, 'ending')
      elif text == 'Ja':
          if data['oldmessage'] == 'Mooi zo! Fijn dat ik je heb kunnen helpen! Wil je misschien nog meer suggesties?':
            message = 'Bedankt voor je reactie. Ik ga even op zoek naar nieuwe ideeen. Momentje..'
            data = messageSend(recipient,message, token,data)
            sendTexts(recipient, message)
            if presentMeal(token, recipient, data):
                message = 'Lijkt dit je lekker?'
                data = messageSend(recipient,message, token,data)
                quicks = ['Ja', 'Nee']
                sendQuicks(recipient, message, quicks)
                mg.updateUser(recipient, data)
            else:
                message = 'We hebben helaas niks gevonden dat aan uw wensen wilt voldoen \n Wilt u het opnieuw proberen?'
                data = messageSend(recipient,message, token,data)
                quicks = ['Ja', 'Nee']
                sendQuicks(recipient, message, quicks)
                mg.updateUser(recipient, data)
          else:
              message = 'Mooi zo! Fijn dat ik je heb kunnen helpen! Wil je misschien nog meer suggesties?'
              data = messageSend(recipient,message, token,data)
              quicks = ['Ja', 'Nee']
              sendQuicks(recipient, message,quicks)
              mg.updateUser(recipient, data)
            #   findToken(recipient, data, '')
      elif text == 'Nee':
          if data['oldmessage'] == 'Mooi zo! Fijn dat ik je heb kunnen helpen! Wil je misschien nog meer suggesties?':
              message = 'Heb je nog tips nodig voor wat betreft de wijn bij het diner? Neem eens een kijkje in onze folder!'
              data = messageSend(recipient,message, token,data)
              buttons = [{
                          "type":"web_url",
                          "url":"https://www.spotta.nl/folders/lidl?fid=1213&startpage=85",
                          "title":"De wijn folder"
                        }
                      ]
              sendButton(recipient, message, buttons)
              mg.updateUser(recipient, data)
              findToken(recipient, data, '')
          elif data['oldmessage'] == 'We hebben helaas niks gevonden dat aan uw wensen wilt voldoen \n Wilt u het opnieuw proberen?':
              findToken(recipient, data, '')
          else:
              message = 'Bedankt voor je reactie. Ik ga even op zoek naar nieuwe ideeen. Momentje..'
              data = messageSend(recipient,message, token,data)
              sendTexts(recipient, message)
              if presentMeal(token, recipient, data):
                  message = 'Lijkt dit je lekker?'
                  data = messageSend(recipient,message, token,data)
                  quicks = ['Ja', 'Nee']
                  sendQuicks(recipient, message, quicks)
                  mg.updateUser(recipient, data)
              else:
                  message = 'We hebben helaas niks gevonden dat aan uw wensen wilt voldoen \n Wilt u het opnieuw proberen?'
                  data = messageSend(recipient,message, token,data)
                  quicks = ['Ja', 'Nee']
                  sendQuicks(recipient, message, quicks)
                  mg.updateUser(recipient, data)
      elif data['oldmessage'] == 'Mooi zo! Fijn dat ik je heb kunnen helpen! Heb je nog tips nodig voor wat betreft de wijn bij het diner? Neem eens een kijkje in onze folder!':
          findToken(recipient, data, '')
      else:
          message = 'Wil je nog meer suggesties?'
          data = messageSend(recipient,message, token,data)
          quicks = ['Ja', 'Nee']
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
        #   findToken(recipient, data, '')
  # elif data['Stage'] =='Chitchat':
  #     if text == 'chitchat':
  #         message = random.choice(Chitchat)
  #         data['chitchat'].append(message)
  #         data = messageSend(recipient,message, token,data)
  #         quicks = ['Ja', 'Nee']
  #         sendQuicks(recipient, message, quicks)
  #         mg.updateUser(recipient, data)
  #     elif data['oldmessage'] == data['chitchat'][-1]:
  #         index = Chitchat.index(data['oldmessage'])
  #         if index == 0:
  #             if text == 'Ja':
  #                 message = 'Het is ook al bijna zover!'
  #             elif text == 'Nee':
  #                 message = 'Oke, hopelijk komt het snel!'
  #             data = messageSend(recipient,message, token,data)
  #             sendTexts(recipient, message)
  #             mg.updateUser(recipient, data)
  #             findToken(recipient, data, text)
  #         elif index == 1:
  #             if isEten(text):
  #                 message = 'Dat klinkt lekker!'
  #             else:
  #                 message = 'Dat ken ik nog niet'
  #             data = messageSend(recipient,message, token,data)
  #             sendTexts(recipient, message)
  #             mg.updateUser(recipient, data)
  #             findToken(recipient, data, text)
  #         elif index == 2:
  #             if text == 'Ja':
  #                 message = 'Ik vind dat altijd zo gezellig!'
  #             elif text == 'Nee':
  #                 message = 'Je moet er nog wel 1 kopen hoor!'
  #             data = messageSend(recipient,message, token,data)
  #             sendTexts(recipient, message)
  #             mg.updateUser(recipient, data)
  #             findToken(recipient, data, text)
  #     else:
  #         findToken(recipient, data, text)
  elif data['Stage'] == 'Afscheid':
      if 'Feedback' in data['data']:
          if int(data['data']['Feedback']) > 2:
              message = 'Ik vond het ook gezellig!'
          else:
              message = 'Jammer dat je het niet zo leuk vond, ik hoop dat je wel geniet van het feest!'
          data = messageSend(recipient,message, token,data)
          sendTexts(recipient, message)
      message = 'Veel succes met de voorbereidingen en heel veel plezier bij het diner. Eet smakelijk!'
      data = messageSend(recipient,message, token,data)
      sendTexts(recipient, message)
      data['dolog'] = 'end'
      mg.updateUser(recipient, data)
  else:
    response, data = getResponse(recipient, text, data)
    if response['type'] == 'stop' or response['msg'] == data['oldmessage']:
    	findToken(recipient, data, text)
        mg.updateUser(recipient, data)
    elif 'msg' in response and response['msg'] != data['oldmessage']:
        message = response['msg'].encode('utf-8')
        data = messageSend(recipient,message, token,data)
        if 'quickreplies' in response:
            sendQuicks(recipient, message, response['quickreplies'])
    	else:
            sendTexts(recipient, message)
        mg.updateUser(recipient, data)
  return data

if __name__ == '__main__':
  # personality, sentiment = getIt()
  app.run()
