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
# extraChitchat = mg.findConfig(53)
TriggerPhrases = Triggers['tigger']
TriggerCats = Triggers['answers']

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

def sendQuicks(sender, mess, quicks):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
      "recipient": {"id": sender},
      "message": {"text": mess,
      "quick_replies":[{
                     "content_type":"text",
                     "title":x,
                     "payload":x
                   } for x in quicks]}
    }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendLocation(sender, mess):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
  "recipient":{
    "id":sender
  },
  "message":{
    "text":mess,
    "quick_replies":[
      {
        "content_type":"location",
      }
    ]
  }
 }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendButton(sender, mess, buttons):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps(    {
      "recipient":{
        "id":sender
      },
      "message":{
        "attachment":{
          "type":"template",
          "payload":{
            "template_type":"button",
            "text":mess,
            "buttons":[x for x in buttons]
          }
        }
      }
    }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendTexts(sender, mess):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
      "recipient": {"id": sender},
      "message": {"text": mess.encode('utf-8')}
    }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendQuicksImage(sender, mess, quicks):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
      "recipient": {"id": sender},
      "message": {"text": mess,
      "quick_replies":[{
                     "content_type":"text",
                     "title":x[0],
                     "payload":x[0],
                     "image_url":x[1]
                   } for x in quicks]}
    }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendTemplate(sender, buttons):
    print(buttons)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
  "recipient":{
    "id":sender
  },
  "message":{
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"generic",
        "elements":buttons
      }
    }
  }
 }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendImage(sender, url):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
  "recipient":{
    "id":sender
  },
  "message":{
    "attachment":{
      "type":"image",
      "payload":{
        "url":url
      }
    }
  }
 }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendFile(sender, url):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
  "recipient":{
    "id":sender
  },
  "message":{
    "attachment":{
      "type":"file",
      "payload":{
        "url":url
      }
    }
  }
 }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendVideo(sender, url):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
  "recipient":{
    "id":sender
  },
  "message":{
    "attachment":{
      "type":"video",
      "payload":{
        "url":url
      }
    }
  }
    }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def sendAudio(sender, url):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps({
  "recipient":{
    "id":sender
  },
  "message":{
    "attachment":{
      "type":"audio",
      "payload":{
        "url":url
      }
    }
  }
  }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
    	print r.text

def semdMess(sender,mess):
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": mess}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def openBrowser(sender, loc):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": PAT},
    data=json.dumps(      {
      "recipient":{
        "id":sender
      },
      "message":{
        "attachment":{
          "type":"template",
          "payload":{
            "template_type":"generic",
            "elements":[
              {
                "title":"Via onderstaande link kunt u de kaart bekijken.",
                "buttons":[
                  {
                    "type":"web_url",
                    "url":"http://onlinepublisher.nl/Chatbot/voorbeeld_wgp_events.html?loc="+loc,
                    "title":"Bekijk de kaart",
                    "webview_height_ratio":"tall"
                  }
                ]
              }
            ]
          }
        }
      }
    }),
    headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print r.text

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

def presentMeal(token, recipient, data,n):
    Ingredient = data['data']['Ingredient']
    meals = mg.findRightProduct(Ingredient)[:n]
    meals = [x for x in meals if x not in data['presented']]
    print(meals)
    meal = meals[0]
    postdashbot('bot',(recipient,'meal: '+ meal['titel'], data['message-id']) )
    data['presented'].append(meal)
    typing('off', PAT, recipient)
    sendTemplate(recipient, ['''{
        "title":'''+ meal['titel']+ ''',
        "item_url":'''+ meal['afbeelding']+ ''',
        "image_url":'''+ meal['afbeelding']+ ''',
        "buttons":[
          {
            "type":"web_url",
            "url": "http://www.lidl.nl/nl/index.htm",
            "title":"Bekijk het recept!"
          }
        ]
      }'''])
    sendTemplate(recipient, ['''{
        "title":'''+ meal['titel']+ ''',
        "item_url":'''+ meal['afbeelding']+ ''',
        "image_url":'''+ meal['afbeelding']+ ''',
        "buttons":[
          {
            "type":"web_url",
            "url": "http://www.lidl.nl/nl/index.htm",
            "title":"Bekijk het recept!"
          }]}'''])
    mg.updateUser(recipient, data)

def findToken(recipient, data, text):
  data['session'] = 'GreenOrange-session-' + str(datetime.datetime.now()).replace(" ", '')
  oldToken = data['token']
  Stage = data['Stage']
  if Stage == 'Welkom':
    #   data['type'] = text
      if text == 'Een gang':
          data['type'] = 'gang'
          NextStage = TokenStages[TokenStages.index(Stage)+1]
          data['Stage'] = NextStage
          mg.updateUser(recipient, data)
          send_message(PAT, recipient, 'gang', data)
      elif text == 'Een menu':
          data['type'] = 'menu'
          NextStage = TokenStages[TokenStages.index(Stage)+1]
        #   data['token'] = 'personality'
        #   data['chitchat'].append(data['token'])
          data['Stage'] = NextStage
          mg.updateUser(recipient, data)
          send_message(PAT, recipient, 'menu', data)
  elif Stage == 'Keuzes':
      if not all(k in data['data'] for k in ['Ingredient']):
          data['token'] = random.choice(allValues(Tokens[Stage]))
          while get_keys(Tokens, data['token'])[-1] in data['data']:
              data['token'] = random.choice(allValues(Tokens[Stage]))
          data['starter'] = get_keys(Tokens, data['token'])[-1]
          mg.updateUser(recipient, data)
          send_message(PAT, recipient, data['starter'], data)
      else:
          NextStage = TokenStages[TokenStages.index(Stage)+1]
          data['Stage'] = NextStage
          response = {}
          mg.updateUser(recipient, data)
          send_message(PAT, recipient, 'presentatie', data)
  elif Stage == 'Presentatie':
      NextStage = TokenStages[TokenStages.index(Stage)+1]
      data['Stage'] = NextStage
      response = {}
      mg.updateUser(recipient, data)
      send_message(PAT, recipient, 'chitchat', data)
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
    return data

""" FUNCTIONS TO RECEIVE AND SEND MESSAGES

below the receive and send functions can be found.

"""

@app.route('/', methods=['POST'])
def handle_messages():
  payload = request.get_data()
  print(payload)
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
                    sendTexts(recipient,'Oke! Toch bedankt voor het fijne gesprek en veel plezier tijdens pakjesavond!')
                    data['dolog'] = 'end'
                    mg.updateUser(recipient, data)
        else:
            data = mg.findUser(sender)
            print(mid, data['message-id'])
            if mid != data['message-id']:
                data['messagenumber'] +=1
                if data['messagenumber'] > data['messagenumberresponse']+2:
                    pass
                elif findword(message):
                    typing('on', PAT, sender)
                    time.sleep(1.5)
                    typing('off', PAT, sender)
                    message = 'Wij houden hier niet zo van schelden. Zou je hier alsjeblieft mee willen stoppen!.'
                    data['text'].append(('bot',message))
                    data['oldmessage'] = message
                    postdashbot('bot',(sender,message, data['message-id']) )
                    typing('off', PAT, sender)
                    sendTexts(recipient,message)
                    time.sleep(1.5)
                    message = 'Wil je nu verder met het zoeken van een leuk cadeau?'
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
                    message = 'Wil je nu verder met het zoeken van een leuk cadeau?'
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
                        log = {}
                        if 'Feedback' in data['data']:
                            log['feedback']= (data['data']['Feedback'])
                        else:
                            log['feedback']= ('0')
                        if data['data']:
                            log['data']= (data['data'])
                        if data['meals']:
                            log['meals']=(data['meals'])
                        if data['text']:
                            log['text'] = data['text']
                        log['id'] = sender
                        mg.logging(log)
                        data['Stage'] = TokenStages[0]
                        data['text'] = []
                        if len (data['chitchat']) > 3:
                            data['chitchat'] = []
                        data['dolog'] = ''
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
          "recipient": {"id": 1363695020339691},
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
          "recipient": {"id": 1363695020339691},
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
  if data['dolog'] == 'end':
      print('done')
  elif data['Stage'] == 'Welkom':
    if text == 'Een gang' or text == 'Een menu':
        findToken(recipient, data, text)
    else:
        message = random.choice(startmessage)
        message = message[0] + data['info']['first_name']+ message[1]
        data = messageSend(recipient,message, token,data)
        sendTexts(recipient, message)
        message = 'Bent u op zoek naar een volledig menu of een gang?'
        data = messageSend(recipient,message, token,data)
        quicks = ['Een gang', 'Een menu']
        sendQuicks(recipient, message, quicks)
        mg.updateUser(recipient, data)
  elif data['Stage'] == 'Gangen' and data['type'] == 'menu':
      if text == 'menu':
          message = 'We kunnen u een menu van 4 of minder gangen aanbevelen! Hoeveel gangen wilt u?'
          data = messageSend(recipient,message, token,data)
          quicks = ['1','2','3','4']
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif text.isdigit():
          text == int(text)
          if text == 2:
              message = 'Wilt u een voor- of een nagerecht?'
              data = messageSend(recipient,message, token,data)
              quicks = ['Voorgerecht','Nagerecht']
              sendQuicks(recipient, message, quicks)
              mg.updateUser(recipient, data)
          elif text == 4:
              data['gangen'] = ['Amuse', 'Voorgerecht', 'Hoofdgerecht', 'Nagerecht']
              mg.updateUser(recipient, data)
              findToken(recipient, data, text)
          elif text == 3:
              data['gangen'] = ['Voorgerecht', 'Hoofdgerecht', 'Nagerecht']
              mg.updateUser(recipient, data)
              findToken(recipient, data, text)
          elif text == 1:
              data['gangen'] = ['Hoofdgerecht']
              mg.updateUser(recipient, data)
              findToken(recipient, data, text)
      elif text == 'Voorgerecht':
          data['gangen'] = ['Voorgerecht', 'Hoofdgerecht']
          mg.updateUser(recipient, data)
          findToken(recipient, data, text)
      elif text == 'Nagerecht':
          data['gangen'] = ['Hoofdgerecht', 'Nagerecht']
          mg.updateUser(recipient, data)
          findToken(recipient, data, text)
  elif data['Stage'] == 'Gangen' and data['type'] == 'gang':
      if text == 'gang':
          message = 'Welke gang moet u nog aanvullen?'
          data = messageSend(recipient,message, token,data)
          quicks = ['Amuse', 'Voorgerecht', 'Hoofdgerecht', 'Nagerecht']
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif text in ['Amuse', 'Voorgerecht', 'Hoofdgerecht', 'Nagerecht']:
          data['gangen']= [text]
          mg.updateUser(recipient, data)
          findToken(recipient, data, text)
  elif data['Stage'] == 'Presentatie':
      if text == 'presentatie':
          presentMeal(token, recipient, data,8)
          message = 'Is dit wat u zoekt?'
          data = messageSend(recipient,message, token,data)
          quicks = ['Ja', 'Nee']
          time.sleep(1.5)
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif text == 'Ja':
          findToken(recipient, data, text)
      elif text == 'Nee':
          presentMeal(token, recipient, data,8)
          message = 'Is dit wat u zoekt?'
          data = messageSend(recipient,message, token,data)
          quicks = ['Ja', 'Nee']
          time.sleep(1.5)
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
  elif data['Stage'] =='Chitchat':
      if text == 'chitchat':
          message = random.choice(Chitchat)
          data['chitchat'].append(message)
          data = messageSend(recipient,message, token,data)
          quicks = ['Ja', 'Nee']
          sendQuicks(recipient, message, quicks)
          mg.updateUser(recipient, data)
      elif data['oldmessage'] == data['chitchat'][-1]:
          index = Chitchat.index(data['oldmessage'])
          if index == 0:
              if text == 'Ja':
                  message = 'Het is ook al bijna zover!'
              elif text == 'Nee':
                  message = 'Oke, hopelijk komt het snel!'
              data = messageSend(recipient,message, token,data)
              sendTexts(recipient, message)
              mg.updateUser(recipient, data)
              findToken(recipient, data, text)
          elif index == 1:
              if isEten(text):
                  message = 'Dat klinkt lekker!'
              else:
                  message = 'Dat ken ik nog niet'
              data = messageSend(recipient,message, token,data)
              sendTexts(recipient, message)
              mg.updateUser(recipient, data)
              findToken(recipient, data, text)
          elif index == 2:
              if text == 'Ja':
                  message = 'Ik vind dat altijd zo gezellig!'
              elif text == 'Nee':
                  message = 'Je moet er nog wel 1 kopen hoor!'
              data = messageSend(recipient,message, token,data)
              sendTexts(recipient, message)
              mg.updateUser(recipient, data)
              findToken(recipient, data, text)
  elif data['Stage'] == 'Afscheid':
      message = random.choice(responsemessage)
      data = messageSend(recipient,message, token,data)
      sendTexts(recipient, message)
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
