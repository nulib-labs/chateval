import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import json
from chateval.helpers import get_token, confirm_login, get_answer, get_answers, format_answer, format_error


@patch('chateval.helpers.webdriver.Chrome')
@patch('chateval.helpers.WebDriverWait')
def test_get_token(mock_webdriverwait, mock_chrome):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_element = MagicMock()
    mock_element.text = json.dumps({'token': 'fake_token'})
    mock_webdriverwait.return_value.until.return_value = mock_element

    token = get_token()
    assert token == 'fake_token'


@patch('chateval.helpers.requests.get')
def test_confirm_login(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {'isLoggedIn': True, 'sub': 'test_user'}
    mock_get.return_value = mock_response

    with patch('chateval.helpers.os.getenv', side_effect=lambda key: 'test_profile' if key == 'AWS_PROFILE' else None):
        message = confirm_login('fake_token')
        assert message == "You are logged in as test_user using test_profile"


@patch('chateval.helpers.requests.post')
def test_get_answer(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'answer': 'test_answer', 'context': 'test_context'}
    mock_post.return_value = mock_response
    response = get_answer('test_question', 'fake_token', with_context=True)
    assert response.equals(pd.Series(['test_answer', 'test_context']))

    response = get_answer('test_question', 'fake_token', with_context=False)
    assert response == 'test_answer'


def test_format_answer():
    response = {'answer': 'test_answer', 'context': 'test_context'}
    result = format_answer(response, with_context=True)
    assert result.equals(pd.Series(['test_answer', 'test_context']))

    result = format_answer(response, with_context=False)
    assert result == 'test_answer'


def test_format_error():
    result = format_error(with_context=True)
    assert result.equals(pd.Series(['--ERROR--', '--ERROR--']))

    result = format_error(with_context=False)
    assert result == '--ERROR--'


@patch('chateval.helpers.get_answer')
def test_get_answers(mock_get_answer):
    mock_get_answer.return_value = 'test_answer'
    questions = pd.DataFrame({'question': ['test_question']})
    token = 'fake_token'

    result = get_answers(questions, token, with_context=False)
    assert result['answer'].iloc[0] == 'test_answer'
