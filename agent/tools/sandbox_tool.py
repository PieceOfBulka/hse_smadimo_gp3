from langchain_core.tools import tool
import httpx
import logging

logger = logging.getLogger(__name__)

@tool
def sandbox_tool(code: str):
    """
    This tool is responsible for call the sandbox container to execute the code in an isolated environment

    Args:
        code(str): the code provided by the agent to be executed

    Returns:
        str: the output after code execution
    """
    logger.info('Выполнение кода от агента в песочнице')
    with httpx.Client() as client:
        sandbox_response = client.post('http://sandbox:8080/execute', json={'code': code})
        if sandbox_response.status_code == 200:
            output = sandbox_response.json()
            if 'error' in output:
                logger.error(output['error'])
                return output['error']
            elif 'warning' in output:
                logger.warning(output['warning'])
                return output['warning']

            logger.info('Код успешно выполнился')
            return output['output']