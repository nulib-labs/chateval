# chateval

A simple commandline tool to evaluate nuldc's chat-based search.

## Installation

```bash 
## install chat eval
pip install git+https://github.com/nulib-labs/chateval.git
```

## Usage 

```bash
chateval

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

```

## Setup AWS Credentials

You need to setup a the chat url in your environment.

Get the DC_CHAT_URL from: 
- [staging](https://github.com/nulib/miscellany/blob/main/chat-eval/.env.staging)
- [production](https://github.com/nulib/miscellany/blob/main/chat-eval/.env.production)

```bash
export DC_CHAT_URL={CHATURL}
```


