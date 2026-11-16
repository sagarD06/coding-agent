import requests

from schema import get_current_date_schema
from tools import get_current_date

AVAILABLE_TOOLS = {
    "get_current_date": get_current_date,
}

MAX_STEPS = 5  # Maximum number of steps to prevent infinite loops


class Agent:
    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model

    def post(self, messages):
        """
        Sends a POST request to the API with the given messages and returns the response.
        """

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": [get_current_date_schema],
            "stream": False,
            "keep_alive": "30m",
            "think": False,
            "options": {"num_ctx": 4096},
        }
        response = requests.post(url, json=payload, timeout=600)

        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from the API.")
            print(
                "Response content:", response.text
            )  # Debugging line to print the response content

        response.raise_for_status()  # Raise an exception for HTTP errors
        # hide the debug JSON print behind a flag.
        if hasattr(self, 'debug') and self.debug:
            print(
                "Response JSON:", response.json()
            )  # Debugging line to print the response JSON
        return response.json()["message"]

    def tool_call(self, tool_name, tool_args):
        """
        Calls the specified tool with the given arguments and returns the result.
        """
        if tool_name in AVAILABLE_TOOLS:
            #wrap with try catch
            try:
                result = AVAILABLE_TOOLS[tool_name](**tool_args)
                return result
            except (TypeError, ValueError) as e:
                return f"Error calling tool {tool_name}: {e!s}"
        else:
            return f"Tool {tool_name} not found."

    def run_turn(self, messages, user_input):
        """
        Handles one user turn and returns the assistant's final reply.
        """
        messages.append({"role": "user", "content": user_input})

        for _ in range(MAX_STEPS):
            reply = self.post(messages)
            messages.append(reply)

            if not reply.get("tool_calls"):
                return reply["content"]

            for tool in reply["tool_calls"]:
                tool_name = tool["function"]["name"]
                tool_args = tool["function"].get("arguments", {})

                tool_result = self.tool_call(tool_name, tool_args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": str(tool_result),
                    }
                )

        return "Maximum steps reached without a final answer."

    debug = None


if __name__ == "__main__":
    base_url = "http://localhost:11434"
    model = "qwen3:8b"
    agent = Agent(base_url, model)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful coding assistant, answer concisely, code first, no greetings.",
        },
    ]
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        answer = agent.run_turn(messages, user_input)
        print("Assistant:", answer)
