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

    sent_input = str(request.form['Body']).lower()
    wordslist = nltk.word_tokenize(sent_input)
    wordslist = [w for w in wordslist if not w in stop_words]#remove stop words from text

    tagged = nltk.pos_tag(wordslist)

    stags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in tagged]#simplified tags https://stackoverflow.com/questions/5787673/python-nltk-how-to-tag-sentences-with-the-simplified-set-of-part-of-speech-tags
    #verbs = list(filter(lambda x:(x[1]=='VERB'), stags))
    #print(verbs)
    #nouns = list(filter(lambda x:x[1]=='NOUN', stags))#some verbs like fight were getting tagged as noun
    #print(nouns)
    keywords = list(filter(lambda x:x[1] == 'VERB' or x[1] == 'NOUN' or x[1] == 'ADJ', stags))
    #print(keywords)
    fkeyword = "no valid"#get first valid keyword
    for i in keywords:
        if i[0] in CORPUS['keyword']:
            fkeyword = i[0]
            break

    #print(fkeyword)
    if sent_input in CORPUS['input']:
        response = random.choice(CORPUS['input'][sent_input])
    elif fkeyword != "no valid":
        response = random.choice(CORPUS['keyword'][fkeyword])
    else:
        CORPUS['input'][sent_input] = ['Yooooooo whts uppppppp? Lets partyyyyyyyyyyy!']
        with open('chatbot_corpus.json', 'w') as myfile:
            myfile.write(json.dumps(CORPUS, indent=4 ))

    logger.debug(response)

    message = g.sms_client.messages.create(
                     body=response,
                     from_=yml_configs['twillio']['phone_number'],
                     to=request.form['From'])
    return json_response( status = "ok" )




