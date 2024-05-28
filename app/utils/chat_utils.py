import openai

openai.api_key = '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'



# gpt4o,  pip install openai==0.28
def generate_new_response(messages):
  response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=messages
  )
  return response['choices'][0]['message']['content']


