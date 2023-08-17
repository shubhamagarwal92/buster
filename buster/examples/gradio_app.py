import cfg
import gradio as gr
import pandas as pd
from cfg import setup_buster
import pathlib
import json
import argparse
from typing import Any

buster = setup_buster(cfg.buster_cfg)


def load_json(path: str) -> Any:
    """
    This function opens and JSON file path
    and loads in the JSON file.

    :param path: Path to JSON file
    :type path: str
    :return: the loaded JSON file
    :rtype: dict
    """
    with open(path, "r",  encoding="utf-8") as file:
        json_object = json.load(file)
    return json_object


def format_sources(matched_documents: pd.DataFrame) -> str:
    if len(matched_documents) == 0:
        return ""

    matched_documents.similarity_to_answer = matched_documents.similarity_to_answer * 100

    documents_answer_template: str = (
        "📝 Here are the sources I used to answer your question:\n\n{documents}\n\n{footnote}"
    )
    document_template: str = "[🔗 {document.title}]({document.url}), relevance: {document.similarity_to_answer:2.1f} %"

    documents = "\n".join([document_template.format(document=document) for _, document in matched_documents.iterrows()])
    footnote: str = "I'm a bot 🤖 and not always perfect."

    return documents_answer_template.format(documents=documents, footnote=footnote)


def add_sources(history, completion):
    if completion.answer_relevant:
        formatted_sources = format_sources(completion.matched_documents)
        history.append([None, formatted_sources])

    return history


def user(user_input, history):
    """Adds user's question immediately to the chat."""
    return "", history + [[user_input, None]]


def chat(history):
    user_input = history[-1][0]

    completion = buster.process_input(user_input)

    history[-1][1] = ""

    for token in completion.answer_generator:
        history[-1][1] += token

        yield history, completion


class GradioChatApp:
    """
    Class to define Gradio based chat app
    """

    def __init__(self, config):
        self.name = "GradioChatApp"
        self.config = config        

    def launch_app(self):
        """
        Gradio app defined here
        """
        # Close all apps running on servers
        gr.close_all()

        examples = load_json(self.config.examples_json)["examples"]

        block = gr.Blocks(css="#chatbot .overflow-y-auto{height:500px}")

        with block:
            with gr.Row():
                gr.Markdown(f"<h3><center>{self.config.title}</center></h3>")

            chatbot = gr.Chatbot()

            with gr.Row():
                question = gr.Textbox(
                    label="What's your question?",
                    placeholder="Ask a question to AI here...",
                    lines=1,
                )
                submit = gr.Button(value="Send", variant="secondary").style(full_width=False)

            examples = gr.Examples(
                examples=examples,
                inputs=question,
            ) 

            gr.Markdown("This application uses GPT to search the docs for relevant info and answer questions.")

            gr.HTML(f"️<center> Created with ❤️ by {self.config.app_by}")

            response = gr.State()

            submit.click(user, [question, chatbot], [question, chatbot], queue=False).then(
                chat, inputs=[chatbot], outputs=[chatbot, response]
            ).then(add_sources, inputs=[chatbot, response], outputs=[chatbot])
            question.submit(user, [question, chatbot], [question, chatbot], queue=False).then(
                chat, inputs=[chatbot], outputs=[chatbot, response]
            ).then(add_sources, inputs=[chatbot, response], outputs=[chatbot])

        kwargs = {}
        if self.config.use_auth:
            creds = load_json(self.config.auth_json)
            kwargs = {"auth": (creds["username"], creds["pwd"])}
        if self.config.share:
            kwargs["share"] = True
        if self.config.use_diff_server:
            kwargs["server_name"] = self.config.server_name
            kwargs["server_port"] = self.config.server_port
            print(f"Hosting on {self.config.server_name}:{self.config.server_port}")

        block.queue(concurrency_count=16)
        block.launch(**kwargs)


def parse_args() -> argparse.Namespace:
    """
    Argument parser function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--examples_json",
        default="resources/examples.json",
        help="Examples to show on gradio app",
    )
    parser.add_argument(
        "-ua",
        "--use_auth",
        action='store_false',
        help="Use the auth credentials",
    ) # Default true
    parser.add_argument(
        "-a",
        "--auth_json",
        default="resources/auth.json",
        help="Credentials used",
    )
    parser.add_argument(
        "-us",
        "--use_diff_server",
        action='store_true',
        help="Host on different server name. Provide server name and port as the args",
    ) # Default false
    parser.add_argument(
        "-s",
        "--server_name",
        default="0.0.0.0",
        help="Server name to host on",
    )
    parser.add_argument(
        "-p",
        "--server_port",
        default=8800,
        help="Port to host gradio app on",
    ) 
    parser.add_argument(
        "-sh",
        "--share",
        action='store_true',
        help="Share using gradio link",
    ) # Default false
    parser.add_argument(
        "-t",
        "--title",
        default='Buster 🤖: A Question-Answering Bot for your documentation',
        help="Title shown",
    )
    parser.add_argument(
        "-b",
        "--app_by",
        default='@jerpint and @hadrienbertrand',
        help="Created with love by",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    parsed_args = parse_args()
    test_app = GradioChatApp(parsed_args)
    test_app.launch_app()