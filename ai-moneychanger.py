from typing import Tuple, Dict
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import json
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable
import streamlit.components.v1 as components

js_code = """
<script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "radjt668l0");
</script>
"""

components.html(js_code, height=0)

load_dotenv()
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = "ai-money-changer"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

##client = wrap_openai(openai.Client())


@traceable
def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    """Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}/{amount}"
    response = json.loads(requests.get(url).text)
    return (base, target, amount, f'{response["conversion_result"]:.2f}')


@traceable
def call_llm(textbox_input) -> Dict:
    """Make a call to the LLM with the textbox_input as the prompt.
       The output from the LLM should be a JSON (dict) with the base, amount and target"""
    tools = [{
        "type": "function",
        "function": {
            "name": "exchange_rate_function",
            "description":
            "Convert a given amount of money from one currency to another. Each currency will be represented as a 3-letter code",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {
                        "type": "string",
                        "description": "The base or original currency.",
                    },
                    "target": {
                        "type": "string",
                        "description": "The target or converted currency",
                    },
                    "amount": {
                        "type":
                        "string",
                        "description":
                        "The amount of money to convert from the base currency.",
                    },
                },
                "required": ["base", "target", "amount"],
                "additionalProperties": False,
            },
        },
    }]

    try:
        response = client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant.",
            }, {
                "role": "user",
                "content": textbox_input,
            }],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name,
            tools=tools,
        )

    except Exception as e:
        print(f"Exception {e}")
    else:
        return response  #.choices[0].message.content


@traceable
def run_pipeline(user_input):
    """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary"""

    response = call_llm(user_input)

    #st.write(response)
    if response == None:
        st.write("Error in calling LLM")
        exit(1)

    if response.choices[0].finish_reason == "tool_calls":  #tool_calls
        # Update this
        response_arguments = json.loads(
            response.choices[0].message.tool_calls[0].function.arguments)
        ## {"amount":"100","base":"USD","target":"CAD"}
        base = response_arguments["base"]
        target = response_arguments["target"]
        amount = response_arguments["amount"]
        _, _, _, conversion_result = get_exchange_rate(base, target, amount)
        st.write(f'{base} {amount} is {target} {conversion_result}')

    elif True:  #tools not used
        # Update this
        st.write(
            f"(Function calling not used) and {response.choices[0].message.content}"
        )
    else:
        st.write("NotImplemented")


st.title("AI Money Changer 1.0")

# Text box for user input
user_input = st.text_input(
    "Enter the amount and the currency, or a sentence describing how do you want to exchange the money:"
)

if st.button("Submit"):
    # st.write(call_llm(user_input))
    run_pipeline(user_input)

## Add Extra Info
st.markdown("""---""")

st.markdown('''# :red[ai-moneychanger 1.0]
A project using LLM and API to convert the native language money change request  

# Project Pushlished URL 
# https://ai-moneychanger.streamlit.app/


## Tech Stack 


1.  Streamlit  
2.  Exchangerate-api  
3.  Replit IDE 
4.  Github OpenAI GPT-4o mini   
5.  Langchain Smith  
6.  Microsoft clarity 
7.  Streamlit App Cloud 
8.  Python  


# Author
:balloon: Jie Chen @ 2025 :balloon:

''')
