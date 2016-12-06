from wit import Wit
from flask import Flask, request
import json
import requests
import sys
from wit import Wit

# from runLogin import getIt
import pickle
import random
import datetime
# import mongo as mg
import mongo as mg

import pprint


#
# import pyowm
# owm = pyowm.OWM
import datetime

def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def response(input,token, session_id):
    client = Wit(token,actions = actions)
    resp = client.converse(session_id, input, {})
    return resp

def send(request, response):
    print(response['text'])


actions = {
    'send': send,
    'first_entity_value': first_entity_value,
}
