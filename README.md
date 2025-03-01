# chateval

A simple commandline tool to evaluate nuldc's chat-based search.

## Installation

```bash 
## install chat eval
pip install git+https://github.com/nulib-labs/chateval.git
```
## Pre-requisites 

You need to setup a the chat url in your environment.

Get the DC_CHAT_URL from: 
- [staging](https://github.com/nulib/miscellany/blob/main/chat-eval/.env.staging)
- [production](https://github.com/nulib/miscellany/blob/main/chat-eval/.env.production)

```bash
export DC_CHAT_URL={CHATURL}
```

Set your aws profile and login: 

```bash
export AWS_PROFILE=your-sso-profile
aws sso login
```

## Usage 

```bash
chateval --help

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

