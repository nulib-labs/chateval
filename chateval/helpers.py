import pandas as pd
import os
import random
import json, requests
import io
from datetime import datetime
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


# for development purposes. But should this just be hardcoded in the cli?
load_dotenv('.env')
DC_API_WHOAMI = "https://api.dc.library.northwestern.edu/api/v2/auth/whoami"
DC_CHAT_URL = os.getenv('DC_CHAT_URL')

def get_token():
    driver = webdriver.Chrome()
    driver.get("https://api.dc.library.northwestern.edu/api/v2/auth/login?goto=https://api.dc.library.northwestern.edu/api/v2/auth/token")
    token = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.TAG_NAME, "pre")))
    return json.loads(token.text).get('token')
 
def confirm_login(token):
    """ Sanity check on login"""
    whoami_response = requests.get(DC_API_WHOAMI, params=None, headers={'Authorization': 'Bearer ' + token})
    if whoami_response.json().get('isLoggedIn') and os.getenv('AWS_PROFILE'):
        message = f"You are logged in as {whoami_response.json().get('sub')} using {os.getenv('AWS_PROFILE')}" 
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
    print(f"Asking question: {question} ")
    
    try:
        response = requests.post(url, json.dumps(body), headers=header)
        response.raise_for_status()
        print(f"Response: {response.status_code}")
        if response.status_code != 200:
            print('Status:', response.status_code, response.reason)
            return format_error(with_context)
        response_json = response.json()
        return format_answer(response_json, with_context)
    except Exception as err:
        print(f"Other error occurred: {err}")
        return format_error(with_context)
    
def get_answers(questions, token, with_context=False):
    if with_context:
       questions[['answer', 'context']] = questions['question'].apply(lambda x:get_answer(x, token, with_context))
    else:
        questions['answer'] = questions['question'].apply(lambda x:get_answer(x, token, with_context))
    print("Done")
    return questions

