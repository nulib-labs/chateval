import pandas as pd
import typer
from typing import Annotated
import chateval.chateval as chat
from enum import Enum
from rich import print


class env(str, Enum):
    """This creates choices in the CLI"""

    staging = "staging"
    production = "prod"

class model(str, Enum):
    """This creates choices in the CLI for models"""

    haiku = "haiku"
    sonnet = "sonnet"
    


def cli(inputcsv: Annotated[typer.FileText, typer.Argument()],
        outputcsv: Annotated[typer.FileTextWrite, typer.Argument()],
        with_context: bool = False,
        evaluate: bool = False,
        model: model = model.haiku,
        debug: bool = False,
        env: env = env.staging
        ):

    chat_endpoints = {"staging": "https://pimtkveo5ev4ld3ihe4qytadxe0jvcuz.lambda-url.us-east-1.on.aws",
                      "production": "https://hdtl6p2qzfxszvbhdb7dyunuxe0dgexo.lambda-url.us-east-1.on.aws"}

    dc_chat_url = chat_endpoints.get(env)
    if debug:
        print(f"[bold yellow]Using {env} endpoint[/bold yellow]")
        print(f"[bold yellow]Endpoint: {dc_chat_url}[/bold yellow]")
        print(f"[bold yellow]Input CSV: {inputcsv}[/bold yellow]")
        print(f"[bold yellow]Output CSV: {outputcsv}[/bold yellow]")
        print(f"[bold yellow]With Context: {with_context}[/bold yellow]")
        print(f"[bold yellow]Evaluate: {evaluate}[/bold yellow]")
        print(f"[bold yellow]Model: {chat_endpoints}[/bold yellow]")
         
    token = chat.get_token()

    print(chat.confirm_login(token))
    # get answers
    questions = pd.read_csv(inputcsv)
    print("[bold green]Getting answers from the chatbot[/bold green]")

    chat.get_answers(dc_chat_url, questions, token, with_context)
    if evaluate:
        print(f"[bold green]Evaluating answers with {model}[/bold green]")
        questions = chat.score_answers_df(questions, model)
        
    print(f"[bold green]Writing answers to output {outputcsv.name}[/bold green]")
    questions.to_csv(outputcsv, index=False)


def main():
    typer.run(cli)


if __name__ == "__main__":
    main()
