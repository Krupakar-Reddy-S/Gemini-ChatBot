import streamlit as st
import google.generativeai as genai
import random
import variables

session_state = st.session_state

if "gemini_api_key" not in session_state:
    session_state.gemini_api_key = st.secrets["gemini_api_key" + random.choice(["1", "2", "3", "4", "5"])]
    genai.configure(api_key=session_state.gemini_api_key)

if "model" not in session_state:
    session_state.model = genai.GenerativeModel("gemini-pro", safety_settings=variables.safety_settings, generation_config=variables.generation_config)


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

        if prompt:
            chat = session_state.chat

            try:
                response = chat.send_message(prompt)
                response_text = response.text
                with st.chat_message("assistant"):
                    st.markdown(to_markdown(response_text))

                print(chat.history)
                print()

                session_state.chat = chat

            except IndexError:
                st.toast("Wow your are a Hacker!", icon="🧑‍💻")
                st.error("The Response for your Prompt was empty. Please try again.")
            except Exception as e:
                st.exception(e)

    with st.sidebar:
        st.subheader("About")
        st.markdown("This is a simple chatbot powered by the Gemini API.")
        st.markdown("Find the source code on GitHub!")


def to_markdown(text):
    return text.replace("•", " *")


if __name__ == "__main__":
    main()
