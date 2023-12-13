import os
import pandas as pd
import gradio as gr
from utils import read_dataframe
import manager as m
from openai_textgen import TextGenerator
from datamodel import (Goal, ChartExecutorResponse)

llm_config = {"n":1, 'max_tokens':2000, "temperature": 0}
text_gen = TextGenerator()

base_path = '/Volumes/develop/LLM_Projects/syntethic_transaction_data/data/'
xlsx_files = [f for f in os.listdir(base_path) if f.endswith('.xlsx')]

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



# function 
def vizgen(name: str, question: str):
    
    # construct file path
    file_name = name.replace(" ","_").upper() + '.xlsx'
    file_path = os.path.join(base_path, file_name)

    print(file_path)

    # read data 
    df = pd.read_excel(file_path, index_col=0)

    print(df.head(1))

    # instantiate
    nlviz = m.Manager(text_gen=text_gen, data=df)

    # create summary 
    # TODO need to cache the summary so it'll be faster 
    # generate a summary of client after they select the client 
    # 
    summary = nlviz.summarize(textgen_config=llm_config, summary_method="default")

    print(summary)

    # generate plot 
    charts = nlviz.visualize(summary=summary, goal=question, textgen_config=llm_config, return_error=True)
    chart = charts[0]
    if not chart.status:
        print(chart.error)
        return chart.error
    
    # save image
    img_path = save_image(chart=chart, client_name=name, chart_title=question)

    print(chart.code)
    return img_path, chart.code

def create_interface():

    client_names = [file.split(".")[0].replace('_', " ").title() for file in xlsx_files]
        
    with gr.Blocks() as demo:
        gr.Markdown(
            """
        # Generate visualization from data
        """
        )
        
        # client_selector = gr.Dropdown(choices=client_names, value='Robert King',label='Client', type='value')
        # with gr.Column(visible=False) as details_col:
        #     weight = gr.Slider(0, 20)
        #     details = gr.Textbox(label="Extra Details")
        #     generate_btn = gr.Button("Generate")
        #     output = gr.Textbox(label="Output")
        print(client_names)
        with gr.Row():
            client_selector = gr.Dropdown(label="Client", choices=client_names)
        with gr.Row():
            gr.Markdown("Visualization recommendations based on the data")
        # with gr.Row():
        #     goal1 = gr.Textbox()
        #     goal2 = gr.Textbox()
        #     goal3 = gr.Textbox()
        with gr.Row():
            gr.Markdown("Please enter your question below to generate visualization")
        with gr.Row():
            prompt_text = gr.Textbox(label="")
            btn = gr.Button("Generate", scale=0.15, size='small')
        with gr.Row():
            viz = gr.Image(type="filepath") #gr.Textbox()
            code = gr.Textbox(label="Python Code")
        btn.click(vizgen, inputs=[client_selector, prompt_text], outputs=[viz, code])
        # with gr.Row():
        #     for file_name in xlsx_files:
        #         gr.Button(file_name).click(fn=show_dataframe, inputs=["text"], outputs=[out_html])
    return demo

# Launch the app
if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
