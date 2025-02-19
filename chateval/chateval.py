"""chateval

Usage: 
  chateval [options] <inputcsv> <outputcsv> 

Options:

  -c --with-context   output optional context field
  -e --evaluate       evaluate the answers
  -m --model <model>  model to use [default: haiku]
  -d --debug          show account and model info 
  -h --help           show this screen

Description:

Takes a set of input questions with an optional "ground truth" column and outputs a csv with answers. 
"""
import pandas as pd
from docopt import docopt
import chateval.helpers as chat

def main():
    arguments = docopt(__doc__, version='.00')
    if arguments['--debug']:
        print(arguments)
    
    with_context = arguments['--with-context']

    token = chat.get_token()

    print(chat.confirm_login(token))
    # get answers
    questions = pd.read_csv(arguments['<inputcsv>'])
    print("getting answers from the chatbot")

    chat.get_answers(questions, token, with_context)
    if arguments.get('--evaluate'):
        model = arguments['--model']
        
        print(f"evaluating answers with {model}")
        chat.score_answers_df(questions, arguments['--model']).to_csv(arguments['<outputcsv>'], index=False)
    else:
        questions.to_csv(arguments['<outputcsv>'], index=False) 

if __name__ == '__main__':
    main()

