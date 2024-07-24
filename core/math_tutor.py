
from .chat_templates import *
import uuid
import logging

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from langchain_experimental.tools.python.tool import PythonAstREPLTool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver

logger = logging.getLogger(__name__)


class MathTutor():
    def __init__(self, config):
        chat_model = ChatOpenAI(model_name=config['model_name'],temperature=config['temperature'])
        checkpointer = SqliteSaver.from_conn_string(config['sqlite_connection'])
        self.agent_executor = create_react_agent(
            chat_model,
            tools=[PythonAstREPLTool()],
            checkpointer=checkpointer
        )
        self.agent_config = {"configurable": {"thread_id": config['id']}}
        self.messages = list()
        logger.info('Initialized math tutor agent with id {}'.format(config['id']))
    
    def get_question(self,):
        self.messages.append(HumanMessage(content=GET_QUESTION_TEMPLATE))
        question = self._execute_agent()
        return question


    def check_answer(self, answer):
        check_answer = PromptTemplate(
            input_variables=["answer"],
            template=CHECK_ANSWER_TEMPLATE,
        )

        self.messages.append(
            HumanMessage(content=check_answer.format(answer=answer)),
        )
        response=self._execute_agent()
        self._adjust_level()

        return response == 'Yes'


    def _adjust_level(self,):
        self.messages.append(UPDATE_ANSWER_STATUS)


    def generate_step_by_step_answer(self,):
        self.messages.append(
            HumanMessage(content=GENERATE_ANSWER_TEMPLATE),
        )
        response = self._execute_agent()
        return response

    def get_hint(self,):
        self.messages.append(HumanMessage(content=GIVE_A_HINT_TEMPLATE))
        response = self._execute_agent()
        return response
    
    def set_topic(self, topic):
        topic_template = PromptTemplate(
            input_variables=['topic'],
            template=SET_TOPIC_TEMPLATE
        )
        self.messages.append(HumanMessage(content=topic.format(topic=topic)))
    
    def check_topic(self, topic):
        check_topic_template = PromptTemplate(
            input_variables=['topic'],
            template=CHECK_TOPIC_TEMPLATE
        )

        self.messages.append(check_topic_template.format(topic=topic))
        response = self._execute_agent()

        if response == 'OK':
            return ''
        return response

    def _execute_agent(self,):
        logger.info('called the agent with the following input: {}'.format(self.messages))
        response_history = self.agent_executor.invoke({"messages": self.messages}, self.agent_config)
        logger.debug('agent output: {}'.format(response_history))
        last_message = response_history["messages"][-1].content
        self.messages = list()
        return last_message

    

        

    