import gradio as gr
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.


def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def user(history, user_message):
    history = history + [(user_message, None)]
    return history, gr.Textbox(value="", interactive=True)


def bot(history):
    #response = "**That's cool!**"
    history[-1][1] = ""
    img_name = "what_are_the_most_common_transaction_types_?.png"
    file_path = "/Volumes/develop/LLM_Projects/synthetic_transaction_data/data/images/HELEN_TROY/" + img_name
    history[-1][1] = (file_path,)
    return history
    # for character in response:
    #     history[-1][1] += character
    #     time.sleep(0.05)
    #     yield history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
        )
        clear = gr.Button(value="Clear")

    txt_msg = txt.submit(user, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot, api_name="bot_response"
    )
    chatbot.like(print_like_dislike, None, None)
    clear.click(lambda: None, None, chatbot, queue=False)

demo.queue()
demo.launch()