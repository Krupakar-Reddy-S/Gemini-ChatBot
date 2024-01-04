import streamlit as st
import google.generativeai as genai
import variables

gemini_api_key = st.secrets["gemini_api_key"]
genai.configure(api_key=gemini_api_key)
session_state = st.session_state

if "model" not in session_state:
    session_state.model = genai.GenerativeModel("gemini-pro", safety_settings=variables.safety_settings, generation_config=variables.generation_config)
model = session_state.model


def main():
    st.set_page_config(page_title="Gemini powered Chatbot", page_icon=":robot_face:", layout="centered", initial_sidebar_state="auto")

    st.header("Gemini powered Chatbot :robot_face:")

    if "chat" not in session_state:
        session_state.chat = session_state.model.start_chat(history=[])

    for part in session_state.chat.history:
        role = "user" if part.role == "user" else "assistant"
        with st.chat_message(role):
            for message_part in part.parts:
                st.markdown(to_markdown(message_part.text))

    if prompt := st.chat_input("What is up?"):
        with st.chat_message("user"):
            st.markdown(to_markdown(prompt))

        messages = [{"role": "user", "parts": [prompt]}]

        if prompt:
            chat = session_state.chat
            response = chat.send_message(prompt)

            response_text = response.text
            with st.chat_message("assistant"):
                st.markdown(to_markdown(response_text))

            print(chat.history)
            print()

            session_state.chat = chat

    with st.sidebar:
        st.subheader("About")
        st.markdown("This is a simple chatbot powered by the Gemini API.")
        st.markdown("Find the source code on GitHub!")


def to_markdown(text):
    return text.replace("•", " *")


if __name__ == "__main__":
    main()
