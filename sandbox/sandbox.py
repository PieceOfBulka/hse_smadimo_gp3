import logging
import io
import sys
from fastapi import FastAPI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title='sandbox container')

restricted_functions = ['os', 'sys', 'while True:', 'subprocess', 'shutil', 'socket', 'requests']


class CodeToExecute(BaseModel):
    code: str


@app.post('/execute')
def python_code_execute(agent_code: CodeToExecute):
    output_stdout = io.StringIO()
    old_stdout = sys.stdout

    code = agent_code.code.replace('```', '').replace('python', '').strip()

    for restricted_func in restricted_functions:
        if restricted_func in code:
            logger.warning('Агент пытается сломать код')
            return {'warning': f'Использование {restricted_func} запрещено'}

    try:
        sys.stdout = output_stdout
        logger.info('Код от агента выполняется...')
        exec(code)
        return {'output': output_stdout.getvalue()}
    except Exception as e:
        logger.error(f"Ошибка при выполнении кода: {e}")
        return {'error': f'Error: {e}'}
    finally:
        sys.stdout = old_stdout


if __name__ == '__main__':
    #print(python_code_execute("print('hello, world!')"))
    pass