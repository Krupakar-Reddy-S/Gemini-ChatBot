import streamlit as st
from bardapi import Bard
import requests

session_state = st.session_state
session_state.starter_prompt_sent = False


def extract_bard_cookie(cookies: bool = False) -> dict:
    import browser_cookie3

    supported_browsers = [
        browser_cookie3.chrome,
        browser_cookie3.chromium,
        browser_cookie3.opera,
        browser_cookie3.opera_gx,
        browser_cookie3.brave,
        browser_cookie3.edge,
        browser_cookie3.vivaldi,
        browser_cookie3.firefox,
        browser_cookie3.librewolf,
        browser_cookie3.safari,
    ]

    cookie_dict = {}

    for browser_fn in supported_browsers:
        try:
            cj = browser_fn(domain_name=".google.com")

            for cookie in cj:
                print(cookie.name)
                if cookie.name == "__Secure-1PSID" and cookie.value.endswith("."):
                    cookie_dict["__Secure-1PSID"] = cookie.value
                if cookies:
                    if cookie.name == "__Secure-1PSIDTS":
                        print(cookie.value)
                        cookie_dict["__Secure-1PSIDTS"] = cookie.value
                    elif cookie.name == "__Secure-1PSIDCC":
                        print(cookie.value)
                        cookie_dict["__Secure-1PSIDCC"] = cookie.value
                if len(cookie_dict) == 3:
                    return cookie_dict
        except Exception as e:
            continue

    if not cookie_dict:
        raise Exception("No supported browser found or issue with cookie extraction")

    print(cookie_dict)
    return cookie_dict


def get_bard_instance():
    if "bard" not in session_state:
        extracted_cookie_dict = extract_bard_cookie(cookies=False)
        token = extracted_cookie_dict["__Secure-1PSID"]

        session = requests.Session()
        session.headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
        session.cookies.set("__Secure-1PSID", token)
        bard = Bard(token=token, session=session, timeout=30)
        session_state.bard = bard

    return session_state.bard


def get_answer(prompt, bard):
    answer = bard.get_answer(prompt)
    return answer


def main():
    st.set_page_config(page_title="Gemini powered Chatbot", page_icon=":robot_face:")

    st.header("Gemini powered Chatbot :robot_face:")

    if "messages" not in session_state:
        session_state.messages = []

    for message in session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        session_state.messages.append({"role": "user", "content": prompt})

        bard = get_bard_instance()
        if not session_state.starter_prompt_sent:
            session_starter = get_answer(
                "Give answer to the prompts to follow after careful scrutiny and thinking about the context and always give reply to be formatted in markdown with links and images and other details wherever necessary", bard)
            print(session_starter['content'])
            session_state.starter_prompt_sent = True

        answer = get_answer(prompt, bard)

        response = f"Bard: {answer['content']}"
        with st.chat_message("assistant"):
            st.markdown(response)
        session_state.messages.append({"role": "assistant", "content": response})

    with st.sidebar:
        st.subheader("About")
        st.markdown("This is a simple chatbot powered by BARD API.")
        st.markdown("You can find the source code on github")


if __name__ == "__main__":
    main()