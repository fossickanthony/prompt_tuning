from openai import OpenAI
import streamlit as st
import time

st.title("Fossick Prompt Tester")
client = OpenAI()

with st.sidebar:
    first_pass_translation_persona_base = st.text_input("first", value="You are a {input_language} to {output_language} translator. When provided a document segment, you will translate while trying to maintain tone and accuracy.")
    second_pass_translation_persona_base = st.text_input("second", value="You are going to be presented a section of text in {input_language} and translated to {output_language}. Review the translation and try to make improvements. Output the entire {output_language} translation with improvements. Only output the complete text, do not add commentary on what changed.")
    review_persona_base = st.text_input("review", value="You are being provided with excerpts of an original text and a translated text. Rate the quality of the translation for content and tone on a scale from 1 to 10 with 1 meaning terrible and 10 meaning perfect. Offer a very brief explaination of why.")

def get_translation_from_model(text, persona):
    try:
        for response in client.chat.completions.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": text}
            ],
            temperature=0,
            stream=True,
        ):
            yield response.choices[0].delta.content or ""
    except BadRequestError as bad_request:
        pass

def run_pass(label, persona, text):
    label
    full_response = ""
    message_placeholder = st.empty()
    for response in get_translation_from_model(text, persona):
        full_response += response
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response

original_prompt = "What can Fossick translate for you today?"
input_language = "English"
# output_language = "Spanish"

message_placeholder = st.empty()
full_response = ""

original_text = st.text_area("English")
languages = ("Arabic", "Burmese", "French", "Haitian Creole", "Korean", "Mandarin", "Russian", "Spanish", "Vietnamese")
output_language = st.selectbox(
   "What language do you want to translate into?",
   languages,
   index=None,
   placeholder="Select target language...",
)

if not original_text:
    for c in original_prompt:
        full_response += c
        message_placeholder.markdown(full_response + "▌")
        time.sleep(0.03)
    message_placeholder.markdown(full_response)
elif not output_language:
    message_placeholder.markdown(original_prompt)
else:
    first_pass_translation_persona = first_pass_translation_persona_base.format(input_language=input_language, output_language=output_language)
    second_pass_translation_persona = second_pass_translation_persona_base.format(input_language=input_language, output_language=output_language)
    review_persona = review_persona_base.format(input_language=input_language, output_language=output_language)

    message_placeholder.markdown(original_prompt)

    first = run_pass("First pass:", first_pass_translation_persona, original_text)
    second = run_pass("Second pass:", second_pass_translation_persona, f'"""{original_text}""" """{first}"""')
    review = run_pass("Review:", review_persona, f'"""{original_text}""" """{second}"""')
