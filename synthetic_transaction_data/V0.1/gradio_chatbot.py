import os
import pandas as pd
import gradio as gr
from utils import read_dataframe
import manager as m
from openai_textgen import TextGenerator
from datamodel import (Goal, ChartExecutorResponse, Summary)

llm_config = {"n":1, 'max_tokens':2000, "temperature": 0}
text_gen = TextGenerator()

base_path = '/Volumes/develop/LLM_Projects/synthetic_transaction_data/data/'
xlsx_files = [f for f in os.listdir(base_path) if f.endswith('.xlsx')]
eval_report = None

def hide_fn():
    return gr.Textbox(visible=False)


def show_fn():
    return gr.Textbox(visible=True)


def save_image(
        chart: ChartExecutorResponse,
        client_name:str, 
        chart_title: str
    ) -> str:

    client_name = client_name.replace(" ","_").upper()
    chart_title = chart_title.replace(" ","_")

    client_folder = os.path.join(base_path, "images/" + client_name)
    if not os.path.exists(client_folder):
        os.makedirs(client_folder)

    img_path = os.path.join(client_folder, chart_title + ".png")
    chart.savefig(img_path)

    return img_path


def datasummary(name: str):
    """ Genearte a summary of a dataset """
    # construct file path
    file_name = name.replace(" ","_").upper() + '.xlsx'
    file_path = os.path.join(base_path, file_name)

    # read data 
    df = pd.read_excel(file_path, index_col=0)

    # instantiate
    nlviz = m.Manager(text_gen=text_gen, data=df)

    # create summary 
    summary = nlviz.summarize(textgen_config=llm_config, summary_method="default")


    # 
    client_key = summary['fields'][0]['properties']['samples'][0]
    date_min = summary['fields'][2]['properties']['min']
    date_max = summary['fields'][2]['properties']['max']
    account_numbers = str(summary['fields'][3]['properties']['min']) + ', ' +  str(summary['fields'][3]['properties']['max'])
    tran_type_examples = ', '.join(summary['fields'][4]['properties']['samples'])
    tran_type_categories = summary['fields'][4]['properties']['num_unique_values']
    tran_purpose_examples = ', '.join(summary['fields'][5]['properties']['samples'])
    tran_purpose_categories = summary['fields'][5]['properties']['num_unique_values']
    min_tran_amt = summary['fields'][6]['properties']['min']
    max_tran_amt = summary['fields'][6]['properties']['max']

    if name == 'All Clients':
        account_numbers = "(e.g." + str(summary['fields'][3]['properties']['min']) + ', ' +  str(summary['fields'][3]['properties']['max']) + ")"

    summary_text = f"""
## **Dataset Description**: 

This dataset contains information about banking transactions for various clients.

### Fields:

- **Client_Key(s)**: A unique numerical identifier for each client in the dataset: {client_key}
- **Date**: The date of the transactions, ranging from {date_min} to {date_max}.
- **Account_Number**: The account number(s) associated with the transactions: {account_numbers}
- **Transaction_Type**: The type of transaction (e.g., {tran_type_examples}). There are {tran_type_categories} unique transaction types.
- **Transaction_Purpose**: The purpose of the transaction (e.g., {tran_purpose_examples}). There are {tran_purpose_categories} unique transaction purposes.
- **Transaction_Amount**: The amount of the transaction, with a range from {int(min_tran_amt):,} to {int(max_tran_amt):,}.
- **Transaction_Description**: A textual description of the transaction.
"""
    
    return summary_text

def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def user(history, user_message):
    history = history + [(user_message, None)]
    return history, gr.Textbox(value="", interactive=True)


def bot(history, name: str):

    # construct file path
    file_name = name.replace(" ","_").upper() + '.xlsx'
    file_path = os.path.join(base_path, file_name)

    # read data 
    df = pd.read_excel(file_path, index_col=0)

    # instantiate
    nlviz = m.Manager(text_gen=text_gen, data=df)
    summary = nlviz.summarize(textgen_config=llm_config, summary_method="default")

    question = history[-1][0]
    # generate plot 
    charts = nlviz.visualize(summary=summary, goal=question, textgen_config=llm_config, return_error=True)
    chart = charts[0]
    print("\n\n ******")
    print(chart.status)
    print("\n\n ******")
    if not chart.status:
        print(chart.error)
        return chart.error

    # save image
    img_path = save_image(chart=chart, client_name=name, chart_title=question)


    history[-1][1] = ""
    # img_name = "what_are_the_most_common_transaction_types_?.png"
    # file_path = "/Volumes/develop/LLM_Projects/synthetic_transaction_data/data/images/HELEN_TROY/" + img_name
    history[-1][1] = (img_path,)
    return history
    # for character in response:
    #     history[-1][1] += character
    #     time.sleep(0.05)
    #     yield history


# function 
def vizgen(name: str, question: str):
    
    # construct file path
    file_name = name.replace(" ","_").upper() + '.xlsx'
    file_path = os.path.join(base_path, file_name)

    print(file_path)

    # read data 
    df = pd.read_excel(file_path, index_col=0)

    # instantiate
    nlviz = m.Manager(text_gen=text_gen, data=df)

    # create summary 
    # TODO need to cache the summary so it'll be faster 
    # generate a summary of client after they select the client 
    # 
    summary = nlviz.summarize(textgen_config=llm_config, summary_method="default")

    # generate plot 
    charts = nlviz.visualize(summary=summary, goal=question, textgen_config=llm_config, return_error=True)
    chart = charts[0]
    print("\n\n ******")
    print(chart.status)
    print("\n\n ******")
    if not chart.status:
        print(chart.error)
        return chart.error
    

    # evaluate the code
    global eval_report 
    eval_report = nlviz.evaluate(code=chart.code, 
        goal=Goal(question=question, visualization=question ,rationale=""), 
        summary=summary,
        textgen_config=llm_config
    )

    # save image
    img_path = save_image(chart=chart, client_name=name, chart_title=question)

    return img_path, chart.code, Summary(**summary)


def create_interface():

    client_names = [file.split(".")[0].replace('_', " ").title() for file in xlsx_files]
    client_names = sorted(client_names)

    with gr.Blocks() as demo:
        gr.Markdown(
            """
        # Generate visualization from data
        """
        )
        with gr.Row():
            client_selector = gr.Dropdown(label="Client", choices=client_names, scale=6)
            show_btn = gr.Button("Show Summary", scale=1, size='small')
            hide_btn = gr.Button("Hide Summary", scale=1, size='small')
        with gr.Row():
            client_summary_text = gr.Markdown(label="Summary") #gr.Markdown(visible=False)

        chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            bubble_full_width=False,
        )

        with gr.Row():
            txt = gr.Textbox(
                scale=4,
                show_label=False,
                placeholder="Enter your question and press enter",
                container=False,
            )
            clear = gr.Button(value="Clear")

        hide_btn.click(hide_fn, outputs=[client_summary_text])
        show_btn.click(show_fn, outputs=[client_summary_text])
        client_selector.change(datasummary, inputs=[client_selector], outputs=[client_summary_text])

        txt_msg = txt.submit(user, [chatbot, txt], [chatbot, txt], queue=False).then(
            bot, [chatbot, client_selector], chatbot, api_name="bot_response"
        )
        chatbot.like(print_like_dislike, None, None)
        clear.click(lambda: None, None, chatbot, queue=False)

    return demo

# Launch the app
if __name__ == "__main__":
    demo = create_interface()
    demo.queue()
    demo.launch()
