import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import logging
from time import time

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from tools.sandbox_tool import python_code_execution

log_level = os.getenv('LOG_LEVEL', 'INFO')
if log_level:
    logging.basicConfig(level=log_level.upper())
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title='agent container')

model = ChatOpenAI(
    model=os.getenv('MODEL_NAME', 'minimax/minimax-m2.5:free'),
    base_url='https://openrouter.ai/api/v1',
    api_key=os.getenv('API_KEY')
)

agent = create_react_agent(
    model=model,
    tools=[python_code_execution],
    prompt='Ты умный помощник по написанию кода для ML проектов'
)


class Request(BaseModel):
    text: str


@app.post('/run')
def process_user_request(user_request: Request):
    with open('/app/logs/agent.txt', 'a', encoding='utf-8') as f:
        f.write('\n\n====Запрос от пользователя\n')
        f.write(user_request.text)
    try:
        logger.info('Начало обработки запроса агентом')
        start_time = time()
        agent_response = agent.invoke({'messages': [{'role':'user', 'content': user_request.text}]})

        if 'messages' in agent_response:
            logger.info(f'Агент отработал за {round(time()-start_time, 2)} сек.')
            result = agent_response['messages'][-1].content
            with open('/app/logs/agent.txt', 'a', encoding='utf-8') as f:
                f.write('\n====Ответ агента\n')
                f.write(result)
            return {'status': 'success', 'answer': result}
    except Exception as e:
        logger.error(f'Ошибка во время работы агента: {e}')
        return {'status': 'error', 'error': str(e)}


if __name__ == '__main__':
    while True:
        print('======')
        user_request = input('Введите свой запрос: ')
        if user_request == 'quit':
            break
        answer = agent.invoke({'messages': [{'role':'user', 'content': user_request}]})
        print('======')
        print('Ответ агента:\n')
        print(answer['messages'][-1].content)