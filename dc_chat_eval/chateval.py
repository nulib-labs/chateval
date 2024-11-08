"""chateval

Usage: 
    chateval [options] <inputcsv> <outputcsv> 

Options:

    -c --with-context   output optional context field
    -h --help        show this screen

Description:

Takes a set of input questions with an optional "ground truth" column and outputs a csv with answers. 
"""
import pandas as pd
from docopt import docopt
from dc_chat_eval.helpers import get_answers, get_token, confirm_login

if __name__ == '__main__':
    arguments = docopt(__doc__, version='.00')
    print(arguments)

with_context = arguments['--with-context']

token = get_token()

print(confirm_login(token))
# get answers
questions = pd.read_csv(arguments['<inputcsv>'])
get_answers(questions, token, with_context)
questions.to_csv(arguments['<outputcsv>'], index=False)
