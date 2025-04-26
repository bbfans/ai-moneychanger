from typing import Tuple, Dict
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import json
from openai import OpenAI

load_dotenv()
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)


def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    """Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}/{amount}"
    response = json.loads(requests.get(url).text)
    return (base, target, amount, f'{response["conversion_result"]:.2f}')


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
        print(f"Exception {e} for {text}")
    else:
        return response  #.choices[0].message.content


def run_pipeline():
    """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary"""

    response = call_llm(user_input)

    #st.write(response)

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


st.title("AI Money Changer")

user_input = st.text_input("Enter your prompt here")

if st.button("Submit"):
    # st.write(call_llm(user_input))
    run_pipeline()
