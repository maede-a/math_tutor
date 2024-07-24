import streamlit as st
from dotenv import load_dotenv,find_dotenv
import uuid
import tomllib
import logging
from core.math_tutor import MathTutor

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s:%(message)s %(lineno)d', 
                    level=logging.DEBUG, datefmt='%Y/%m/%d %h:%M:%S %p')

load_dotenv(find_dotenv())

if "id" not in st.session_state:
    st.session_state["id"] = uuid.uuid4()
if "topic" not in st.session_state:
    st.session_state['topic'] = ''
if 'disabled_topic' not in st.session_state:
    st.session_state['disabled_topic'] = False
if st.session_state['topic'] != '':
    st.session_state['topic_widget'] = st.session_state['topic']



@st.experimental_fragment()
def response_box():
    answer = st.text_input('Put your answer here and hit Enter:', key='answer')
    if answer != '':
        answer_status = math_tutor.check_answer(answer)
        if answer_status:
            st.text("Great Job!")
        else:
            st.text("Your Answer is not Correct. Here is the correct answer.")
            answer = math_tutor.generate_step_by_step_answer()
            st.markdown(answer)


@st.experimental_fragment()
def hint():
    if st.button('Get a Hint'):
        hint = math_tutor.get_hint()
        st.markdown(hint)


@st.experimental_fragment()
def show_question():
    st.session_state['answer'] = ''
    question = math_tutor.get_question()

    st.markdown(question)
    hint()
    response_box()
    st.button("Next Question")


def main_page():
    st.title("Interactive Math Tutor")

    topic = st.text_input("What topic would you like to practice today?", 
                            disabled=st.session_state['disabled_topic'], 
                            key='topic_widget')
    
    if (st.session_state['topic'] == '') & (topic != ''):
        topic_check = math_tutor.check_topic(topic)
        if topic_check:
            topic_list = topic_check.split(',')
            col1, col2, col3 = st.columns([1,1,1])
            next_col = {col1: col2, col2: col3, col3: col1}
            col = col1
            for topic in topic_list:
                with col:
                    if st.button(topic):
                        st.session_state['topic'] = topic
                col = next_col[col]
        else:
            st.session_state['topic'] = topic
            st.session_state['disabled_topic'] = True

    if st.session_state['topic'] != '':
        math_tutor.set_topic(st.session_state.topic)
        show_question()


def load_config():
    with open("config.toml", "rb") as file:
        config = tomllib.load(file)
    logger.info("Read the config file from config.toml successfully.")
    return config



if __name__ == "__main__":
    config = load_config()
    math_tutor_config = config['agent']
    math_tutor_config['id'] = st.session_state.id
    math_tutor = MathTutor(math_tutor_config)
    logger.info('initialized math tutor with config: {}'.format(math_tutor_config))

    main_page()
