import requests
import json
import os
PAT = os.environ['PAT']
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
    buttons = [str(x) for x in buttons]
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
                "elements": [x for x in buttons]
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
