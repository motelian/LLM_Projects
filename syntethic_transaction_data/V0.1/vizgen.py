from openai_textgen import TextGenerator
from datamodel import Goal, LLMResponse


system_prompt = """
You are a helpful assistant highly skilled in writing PERFECT code for visualizations. Given some code template, you complete the template to generate a visualization given the dataset and the goal described. The code you write MUST FOLLOW VISUALIZATION BEST PRACTICES ie. meet the specified goal, apply the right transformation, use the right visualization type, use the right data encoding, and use the right aesthetics (e.g., ensure axis are legible). The transformations you apply MUST be correct and the fields you use MUST be correct. The visualization CODE MUST BE CORRECT and MUST NOT CONTAIN ANY SYNTAX OR LOGIC ERRORS (e.g., it must consider the field types and use them correctly). You MUST first generate a brief plan for how you would solve the task e.g. what transformations you would apply e.g. if you need to construct a new column, what fields you would use, what visualization type you would use, what aesthetics you would use, etc. .
"""

class VizGenerator:
    """Generate visualizations from prompt"""
    def __init__(self) -> None:
        pass

    def get_template(self, goal: str, library: str = 'matplotlib'):
        general_instructions = f"If the solution requires a single value (e.g. max, min, median, first, last etc), ALWAYS add a line (axvline or axhline) to the chart, ALWAYS with a legend containing the single value (formatted with 0.2F). If using a <field> where semantic_type=date, YOU MUST APPLY the following transform before using that column i) convert date fields to date types using data[''] = pd.to_datetime(data[<field>], errors='coerce'), ALWAYS use  errors='coerce' ii) drop the rows with NaT values data = data[pd.notna(data[<field>])] iii) convert field to right time format for plotting.  ALWAYS make sure the x-axis labels are legible (e.g., rotate when needed). Solve the task  carefully by completing ONLY the <imports> AND <stub> section. Given the dataset summary, the plot(data) method should generate a {library} chart ({goal.visualization}) that addresses this goal: {goal.question}. DO NOT WRITE ANY CODE TO LOAD THE DATA. The data is already loaded and available in the variable data."

        matplotlib_instructions = f" {general_instructions} DO NOT include plt.show(). The plot method must return a matplotlib object (plt). Think step by step. \n"

        if library == "matplotlib":
            instructions = {
                "role": "assistant",
                "content": f"  {matplotlib_instructions}. Use BaseMap for charts that require a map. "}
            template = \
                f"""
import matplotlib.pyplot as plt
import pandas as pd
<imports>
# plan -
def plot(data: pd.DataFrame):
    <stub> # only modify this section
    plt.title('{goal.question}', wrap=True)
    return plt;

chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line."""
        else:
            raise ValueError("Unsupported library. Only 'matplotlib' is supported.")
        return template, instructions
    

    def generate(self, summary: dict, goal: Goal,
                 textgen_config: dict, text_gen: TextGenerator, library='matplotlib'):
        """Generate visualization code given a summary and a goal"""

        library_template, library_instructions = self.get_template(goal, library)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"The dataset summary is : {summary} \n\n"},
            library_instructions,
            {"role": "user",
             "content":
             f"Always add a legend with various colors where appropriate. The visualization code MUST only use data fields that exist in the dataset (field_names) or fields that are transformations based on existing field_names. Only use variables that have been defined in the code or are in the dataset summary. You MUST return a FULL PYTHON PROGRAM ENCLOSED IN BACKTICKS ``` that starts with an import statement. DO NOT add any explanation. \n\n THE GENERATED CODE SOLUTION SHOULD BE CREATED BY MODIFYING THE SPECIFIED PARTS OF THE TEMPLATE BELOW \n\n {library_template} \n\n.The FINAL COMPLETED CODE BASED ON THE TEMPLATE above is ... \n\n"}]
        
        self.messages = messages

        completions: LLMResponse = text_gen.generate(
            messages=messages, config=textgen_config)
        response = [x.content for x in completions.text]

        return response

