from typing import Tuple, Dict
from dotenv import load_dotenv
import os
import streamlit as st
import requests
import json

load_dotenv()
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")


def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    """Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}/{amount}"
    response = json.loads(requests.get(url).text)
    return (base, target, amount, f'{response["conversion_result"]:.2f}')


st.title("AI Money Changer")

user_input = st.text_input("Enter your prompt here")

if st.button("Submit"):
    st.write(f"User input: {user_input}")

# def call_llm(textbox_input) -> Dict:
#     """Make a call to the LLM with the textbox_input as the prompt.
#        The output from the LLM should be a JSON (dict) with the base, amount and target"""
#     try:
#         completion = ...
#     except Exception as e:
#         print(f"Exception {e} for {text}")
#     else:
#         return completion

# def run_pipeline():
#     """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
#     Call get_exchange_rate(...) if necessary"""

#     if True:  #tool_calls
#         # Update this
#         st.write(
#             f'{base} {amount} is {target} {exchange_response["conversion_result"]:.2f}'
#         )

#     elif True:  #tools not used
#         # Update this
#         st.write(f"(Function calling not used) and response from the model")
#     else:
#         st.write("NotImplemented")

# if __name__ == "__main__":

#     # # Where USD is the base currency you want to use
#     # url1 = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD"

#     # # Making our request
#     # response1 = requests.get(url1)
#     # data1 = response1.json()

#     # # Your JSON object
#     # print(json.dumps(data1, indent=4, sort_keys=True))

#     url2 = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/USD/CAD/100.00"

#     response2 = requests.get(url2)
#     data2 = response2.json()
#     print(json.dumps(data2, indent=4, sort_keys=True))
