import pandas as pd
import os
import random
import json
import requests
import io
from datetime import datetime
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from tqdm import tqdm
import time
from botocore.config import Config
import boto3
import importlib.resources as pkg_resources

# for development purposes. But should this just be hardcoded in the cli?
load_dotenv('.env')
DC_API_WHOAMI = "https://api.dc.library.northwestern.edu/api/v2/auth/whoami"
DC_CHAT_URL = os.getenv('DC_CHAT_URL')


def get_token():
    driver = webdriver.Chrome()
    driver.get("https://api.dc.library.northwestern.edu/api/v2/auth/login?goto=https://api.dc.library.northwestern.edu/api/v2/auth/token")
    token = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.TAG_NAME, "pre")))
    return json.loads(token.text).get('token')


def confirm_login(token):
    """ Sanity check on login"""
    whoami_response = requests.get(DC_API_WHOAMI, params=None, headers={
                                   'Authorization': 'Bearer ' + token})
    if whoami_response.json().get('isLoggedIn') and os.getenv('AWS_PROFILE'):
        message = f"You are logged in as {whoami_response.json().get('sub')} using {
            os.getenv('AWS_PROFILE')}"
    else:
        message = "check that you're logged in and your aws profile is set "
    return message


def format_answer(response, with_context=False):
    if with_context:
        return pd.Series([response['answer'], response['context']])
    else:
        return response['answer']


def format_error(with_context=False):
    if with_context:
        return pd.Series(["--ERROR--", "--ERROR--"])
    else:
        return "--ERROR--"


def get_answer(question, token, with_context=False):
    url = DC_CHAT_URL
    header = {'Content-Type': 'application/json'}

    body = {
        'message': 'chat',
        'auth': token,
        'ref': 'DEV-TEAM-TEST-' + str(random.random()),
        "question": question
    }

    try:
        response = requests.post(url, json.dumps(body), headers=header)
        response.raise_for_status()
        if response.status_code != 200:
            print('Status:', response.status_code, response.reason)
            return format_error(with_context)
        response_json = response.json()
        return format_answer(response_json, with_context)
    except Exception as err:
        print(f"Other error occurred: {err}")
        return format_error(with_context)


def get_answers(questions, token, with_context=False):
    tqdm.pandas()
    if with_context:
        questions[['answer', 'context']] = questions['question'].progress_apply(
            lambda x: get_answer(x, token, with_context))
    else:
        questions['answer'] = questions['question'].progress_apply(
            lambda x: get_answer(x, token, with_context))
    return questions


def ask_claude(messages, system="", DEBUG=False, model_version="haiku"):
    '''
    Send a prompt to Bedrock, and return the response.  Debug is used to see exactly what is being sent to and from Bedrock.
    messages can be an array of role/message pairs, or a string.
    '''
    session_cache = {}
    MAX_ATTEMPTS = 3
    raw_prompt_text = str(messages)

    my_config = Config(
        connect_timeout=60*3,
        read_timeout=60*3,
    )
    bedrock = boto3.client(service_name='bedrock-runtime', config=my_config)
    bedrock_service = boto3.client(service_name='bedrock', config=my_config)

    if type(messages) == str:
        messages = [{"role": "user", "content": messages}]

    promt_json = {
        "system": system,
        "messages": messages,
        "max_tokens": 3000,
        "temperature": 0.7,
        "anthropic_version": "",
        "top_k": 250,
        "top_p": 0.7,
        "stop_sequences": ["\n\nHuman:"]
    }

    if DEBUG:
        print("sending:\nSystem:\n", system,
              "\nMessages:\n", "\n".join(messages))
    models = {
        "opus": 'anthropic.claude-3-opus-20240229-v1:0',
        "sonnet": 'anthropic.claude-3-5-sonne-20240620-v1:0',
        "haiku": 'anthropic.claude-3-haiku-20240307-v1:0'
    }

    modelId = models.get(model_version, "error")

    if raw_prompt_text in session_cache:
        return [raw_prompt_text, session_cache[raw_prompt_text]]
    attempt = 1
    while True:
        try:
            response = bedrock.invoke_model(body=json.dumps(
                promt_json), modelId=modelId, accept='application/json', contentType='application/json')
            response_body = json.loads(response.get('body').read())
            results = response_body.get("content")[0].get("text")
            if DEBUG:
                print("Recieved:", results)
            break
        except Exception as e:
            print("Error with calling Bedrock: "+str(e))
            attempt += 1
            if attempt > MAX_ATTEMPTS:
                print("Max attempts reached!")
                results = str(e)
                break
            else:  # retry in 10 seconds
                time.sleep(10)
    session_cache[raw_prompt_text] = results
    return (raw_prompt_text, results)


def score_answers(question_answers, model):
    '''
    ask our LLM to score each of the generated answers.
    '''
    # Load the template from the package
    with pkg_resources.open_text('chateval', 'scoring_prompt_template.txt') as file:
        scoring_prompt_template = file.read()
   
    prompts = []
    results = []
    for question in question_answers:  
        print(f"Scoring: {question['question']}...")
        scoring_prompt = scoring_prompt_template.format(**question)
        prompts.append(scoring_prompt)
        p, s = ask_claude(scoring_prompt, model)
        results.append([s.split(',')])
    return results # ask_claude_threaded(prompts, model)

def score_answer(question_answer, model):
    '''
    ask our LLM to score each of the generated answers.
    '''
    # Load the template from the package
    with pkg_resources.open_text('chateval', 'scoring_prompt_template.txt') as file:
        scoring_prompt_template = file.read()
        
    print(f"Scoring: {question_answer['question']}...")
    scoring_prompt = scoring_prompt_template.format(**question_answer)
    p, s = ask_claude(scoring_prompt, model)
    
    return pd.Series(s.split(',')[:3], index=['oq','score','reason']) # ask_claude_threaded(prompts, model)


def score_answers_df(question_answers_df, model):
    '''
    ask our LLM to score each of the generated answers.
    '''
    # Load the template from the package
    with pkg_resources.open_text('chateval', 'scoring_prompt_template.txt') as file:
        scoring_prompt_template = file.read()
    
    df = question_answers_df.copy()
    df[['oq','score','reason']]=df.apply(lambda x: score_answer(x, model), axis=1, result_type='expand')
    return df# ask_claude_threaded(prompts, model)


def test_answers():
    return [{"question": "What is the capital of France?", "ground_truth": "Paris", "answer": "Paris"},
            {"question": "What is the capital of Germany?", "ground_truth": "Berlin", "answer": "Berlin"},
            {"question": "What is the capital of Italy?", "ground_truth": "Rome", "answer": "Rome, my love"}]
    

