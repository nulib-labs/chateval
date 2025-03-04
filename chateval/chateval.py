import pandas as pd
import typer
import chateval.helpers as chat

def main(inputcsv: str,
         outputcsv: str, 
         with_context: bool = False, 
         evaluate: bool = False, 
         model: str = 'haiku', 
         debug: bool = False):
    

    if debug:
        print(arguments)
    
    token = chat.get_token()

    print(chat.confirm_login(token))
    # get answers
    questions = pd.read_csv(inputcsv)
    print("getting answers from the chatbot")

    chat.get_answers(questions, token, with_context)
    if evaluate:
        print(f"evaluating answers with {model}")
        chat.score_answers_df(questions, model).to_csv(outputcsv, index=False)
    else:
        questions.to_csv(outputcsv, index=False) 

def cli():
    typer.run(main)

