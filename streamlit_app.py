import streamlit as st
import google.generativeai as genai
import random
import variables
import PIL.Image
import google.api_core.exceptions

session_state = st.session_state

if "gemini_api_key" not in session_state:
    session_state.gemini_api_key = st.secrets["gemini_api_key" + random.choice(["1", "2", "3", "4", "5"])]
    genai.configure(api_key=session_state.gemini_api_key)

if "model_chat" not in session_state:
    session_state.model_chat = genai.GenerativeModel("gemini-1.0-pro-latest", safety_settings=variables.safety_settings, generation_config=variables.generation_config_chat)

if "file_uploader_key" not in session_state:
    session_state.file_uploader_key = "-1"

if "vision_history" not in session_state:
    session_state.vision_history = []

if "history" not in session_state:
    session_state.history = []


def main():
    st.set_page_config(page_title="Gemini powered Chatbot", page_icon=":robot_face:", layout="centered", initial_sidebar_state="auto")
    st.header("Gemini powered Chatbot :robot_face:")
    session_state.images = []
    history = session_state.history

    with st.sidebar:
        st.subheader("About")
        st.markdown("This is a simple chatbot powered by the Gemini API.")
        files = st.file_uploader(label="Upload an Image here", type=["png", "jpg", "jpeg"], key=session_state.file_uploader_key, accept_multiple_files=True)
        if files:
            for file in files:
                st.image(file)
            session_state.images = files if isinstance(files, list) else []

    if "chat" not in session_state:
        session_state.chat = session_state.model_chat.start_chat(history=[])

    chat = session_state.chat
    session_state.chat_index = 0
    session_state.vision_index = 0

    for part in session_state.history:
        if part[0] == "model_chat":
            for i in range(session_state.chat_index, session_state.chat_index + (part[1] * 2)):
                role = "user" if chat.history[i].role == "user" else "assistant"
                with st.chat_message(role):
                    for message_part in chat.history[i].parts:
                        st.markdown(to_markdown(message_part.text))

            session_state.chat_index += (part[1] * 2)

        else:
            for prompt, images, response_text in session_state.vision_history[session_state.vision_index: session_state.vision_index + part[1]]:
                with st.chat_message("user"):
                    st.markdown(to_markdown(prompt))
                    for image in images:
                        st.image(image)
                with st.chat_message("assistant"):
                    st.markdown(to_markdown(response_text))

            session_state.vision_index += part[1]

    if prompt := st.chat_input("Enter your message here..."):
        with st.chat_message("user"):
            st.markdown(to_markdown(prompt))

        if session_state.images:
            if "model_vision" not in session_state:
                session_state.model_vision = genai.GenerativeModel("gemini-1.0-pro-vision-latest", safety_settings=variables.safety_settings, generation_config=variables.generation_config_vision)

            vision = session_state.model_vision
            images = [PIL.Image.open(image) for image in session_state.images]

            try:
                response = vision.generate_content(list(prompt) + images)
                response_text = response.text
                with st.chat_message("assistant"):
                    st.markdown(to_markdown(response_text))

                session_state.vision_history.append((prompt, session_state.images, response_text))

                print(response_text)
                if not history:
                    history.append(("model_vision", 1))
                else:
                    if history[-1][0] == "model_vision":
                        history[-1] = ("model_vision", history[-1][1] + 1)
                    else:
                        history.append(("model_vision", 1))

                session_state.history = history
                session_state.model_vision = vision
                session_state.file_uploader_key = str(random.random() * random.random())
                st.rerun()

            except google.api_core.exceptions.GoogleAPICallError:
                st.error("The Maximum sum of the image sizes is 4MB. Please try again with smaller images.")
            except Exception as e:
                st.exception(e)
                st.error("The Response for your Prompt was empty. Please try again.")

        else:
            try:
                response = chat.send_message(prompt)
                response_text = response.text
                with st.chat_message("assistant"):
                    st.markdown(to_markdown(response_text))

                print(chat.history)
                if not history:
                    history.append(("model_chat", 1))
                else:
                    if history[-1][0] == "model_chat":
                        history[-1] = ("model_chat", history[-1][1] + 1)
                    else:
                        history.append(("model_chat", 1))

                session_state.history = history
                session_state.chat = chat

            except IndexError:
                st.error("The Response for your Prompt was empty. Please try again.")
            except Exception as e:
                st.exception(e)


def to_markdown(text):
    return text.replace("•", " *")


if __name__ == "__main__":
    main()
