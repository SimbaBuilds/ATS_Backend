import openai

openai.api_key = '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'



# for gpt 4 turbo, pip install openai==0.28
def generate_new_response(message):
  response = openai.ChatCompletion.create(
    model="gpt-4-0125-preview",
    messages=[message]
  )
  return response['choices'][0]['message']['content']


