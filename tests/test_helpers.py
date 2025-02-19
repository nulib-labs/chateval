import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from chateval.helpers import get_token, confirm_login, get_answer, get_answers, format_answer, format_error, score_answer, score_answers_df, ask_claude
import json

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
    mock_response.status_code = 200  # Set the status code to 200
    mock_response.json.return_value = {'answer': 'test_answer', 'context': 'test_context'}
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

@patch('chateval.helpers.pkg_resources.open_text')
@patch('chateval.helpers.ask_claude')
def test_score_answer(mock_ask_claude, mock_open_text):
    mock_open_text.return_value.__enter__.return_value.read.return_value = "Question: {question}\nAnswer: {answer}"
    mock_ask_claude.return_value = ("prompt", "5||Good answer")

    question_answer_df = pd.Series({'question': 'What is AI?', 'answer': 'Artificial Intelligence'})
    model = 'test_model'

    result = score_answer(question_answer_df, model)
    assert result.equals(pd.Series(['5', 'Good answer'], index=['score', 'reason']))

@patch('chateval.helpers.pkg_resources.open_text')
@patch('chateval.helpers.ask_claude')
@patch('chateval.helpers.tqdm.pandas')
def test_score_answers_df(mock_tqdm_pandas, mock_ask_claude, mock_open_text):
    mock_open_text.return_value.__enter__.return_value.read.return_value = "Question: {question}\nAnswer: {answer}"
    mock_ask_claude.return_value = ("prompt", "5||Good answer")

    question_answers_df = pd.DataFrame({
        'question': ['What is AI?', 'What is ML?'],
        'answer': ['Artificial Intelligence', 'Machine Learning']
    })
    model = 'test_model'

    result = score_answers_df(question_answers_df, model)
    expected = pd.DataFrame({
        'question': ['What is AI?', 'What is ML?'],
        'answer': ['Artificial Intelligence', 'Machine Learning'],
        'score': ['5', '5'],
        'reason': ['Good answer', 'Good answer']
    })

    pd.testing.assert_frame_equal(result, expected)

@patch('chateval.helpers.boto3.client')
def test_ask_claude(mock_boto3_client):
    mock_bedrock = MagicMock()
    mock_bedrock.invoke_model.return_value.get.return_value.read.return_value = json.dumps({
        'content': [{'text': 'response_text'}]
    })
    mock_boto3_client.return_value = mock_bedrock

    messages = "Test message"
    response = ask_claude(messages, model_version="haiku")
    assert response == ("Test message", "response_text")
