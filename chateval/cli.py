import pandas as pd
import typer
import chateval.chateval as chat
from enum import Enum
from rich import print


class environment(str, Enum):
    """This creates choices in the CLI"""

    staging = "staging"
    production = "prod"


def cli(inputcsv: str,
        outputcsv: str,
        with_context: bool = False,
        evaluate: bool = False,
        model: str = 'haiku',
        debug: bool = False,
        env: environment = environment.staging
        ):

    chat_endpoints = {"staging": "https://pimtkveo5ev4ld3ihe4qytadxe0jvcuz.lambda-url.us-east-1.on.aws",
                      "production": "https://hdtl6p2qzfxszvbhdb7dyunuxe0dgexo.lambda-url.us-east-1.on.aws"}

    dc_chat_url = chat_endpoints.get(env)
    if debug:
        print(arguments)

    token = chat.get_token()

    print(chat.confirm_login(token))
    # get answers
    questions = pd.read_csv(inputcsv)
    print("[bold green]Getting answers from the chatbot[/bold green]")

    chat.get_answers(dc_chat_url, questions, token, with_context)
    if evaluate:
        print(f"[bold green]Evaluating answers with {model}[/bold green]")
        chat.score_answers_df(questions, model).to_csv(outputcsv, index=False)
    else:
        questions.to_csv(outputcsv, index=False)


def main():
    typer.run(cli)


if __name__ == "__main__":
    main()
