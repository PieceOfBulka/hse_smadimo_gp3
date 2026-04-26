import logging
import io
import sys

logger = logging.getLogger(__name__)

def python_code_execute(code: str) -> str:
    output_stdout = io.StringIO()
    old_stdout = sys.stdout

    try:
        sys.stdout = output_stdout
        logger.info('Код от агента выполняется...')
        exec(code)
        return output_stdout.getvalue()
    except Exception as e:
        logger.error(f"Ошибка при выполнении кода: {e}")
        return f'Error: {e}'
    finally:
        sys.stdout = old_stdout

if __name__ == '__main__':
    print(python_code_execute("print('hello, world!')"))