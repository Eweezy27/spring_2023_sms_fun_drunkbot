import yaml
from flask import request, g
from flask_json import FlaskJSON, JsonError, json_response, as_json
from os.path import exists


from tools.logging import logger
from things.actors import actor


import random
import json
import pickle

yml_configs = {}
BODY_MSGS = []
with open('config.yml', 'r') as yml_file:
    yml_configs = yaml.safe_load(yml_file)

CORPUS = {}

with open('chatbot_corpus.json', 'r') as myfile:
    CORPUS = json.loads(myfile.read())


def handle_request():
    convo = {}
    logger.debug(request.form)

    act = None
    if exists( f"users/{request.form['From']}.pkl") :
        with open(f"users/{request.form['From']}.pkl", 'rb') as p:
            act = pickle.load(p) 
    else:
        act= actor(request.form['From'])

    act.save_msg(request.form['Body'])
    logger.debug(act.prev_msgs)
    

    with open(f"users/{request.form['From']}.pkl", 'wb') as p:
        pickle.dump(act,p)

    response = random.choice(CORPUS['random']['random'])

    nateNum = "+17609200710"
    userNum = request.form['From']
    sent_input = str(request.form['Body']).lower()

    if userNum in convo and convo[userNum]['last_message_from'] == 'nateNum':
        return json_response(status = 'ok')
    
    if sent_input in CORPUS['input']:
        response = random.choice(CORPUS['input'][sent_input])
        message = g.sms_client.messages.create(
            body=response,
            from_=yml_configs['twillio']['phone_number'],
            to=userNum)
    else:
        ##userNum = request.form['From']
        message = g.sms_client.messages.create(
            body = 'answer this please:"{}"'.format(sent_input),
            from_ = yml_configs['twillio']['phone_number'],
            to = nateNum)
        
        ##response = ''
        ##print(response)
        ##while response == '':
        response_recieved = False
        while not response_recieved:
            messages = g.sms_client.messages.list(from_ = nateNum, to = userNum)
            for m in messages:
                if m.body:
                    ##if m.from_ == nateNum and response_expected:
                    response = m.body
                    print(response)
                    

                    CORPUS['input'][sent_input] = [response]
                    with open('chatbot_corpus.json', 'w') as myfile:
                        myfile.write(json.dumps(CORPUS, indent=4 ))
                        
                    logger.debug(response)
        
                    message = g.sms_client.messages.create(
                        body=response,
                        from_=yml_configs['twillio']['phone_number'],
                        to=userNum)
                    
                    response_recieved = True
                    break
        if userNum not in convo:
            convo[userNum] = {'last_message_from': 'chatbot'}

        convo[userNum]['last_message_from'] = 'nateNum'
                    
        return json_response( status = "ok" )
