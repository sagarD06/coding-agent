import requests

from constants import MAX_STEPS
from tool_registry import TOOL_REGISTRY


class Agent:
    def __init__(self, base_url, model, debug=None):
        self.base_url = base_url
        self.model = model
        self.debug = debug

    def post(self, messages):
        """
        Sends a POST request to the API with the given messages and returns the response.
        """

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": [tool["schema"] for tool in TOOL_REGISTRY.values()],
            "stream": False,
            "keep_alive": "30m",
            "think": False,
            "options": {"num_ctx": 4096},
            "temperature": 0.1,
        }
        response = requests.post(url, json=payload, timeout=600)

        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from the API.")
            print(
                "Response content:", response.text
            )  # Debugging line to print the response content

        response.raise_for_status()  # Raise an exception for HTTP errors
        # hide the debug JSON print behind a flag.
        if self.debug:
            print(
                "Response JSON:", response.json()
            )  # Debugging line to print the response JSON
        return response.json()["message"]

    def tool_call(self, tool_name, tool_args):
        """
        Calls the specified tool with the given arguments and returns the result.
        """
        if tool_name in TOOL_REGISTRY:
            try:
                result = TOOL_REGISTRY[tool_name]["function"](**tool_args)
                return result
            except Exception as e:
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

if __name__ == "__main__":
    base_url = "http://localhost:11434"
    model = "qwen3:8b"
    agent = Agent(base_url, model, debug=True)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful coding assistant, answer concisely, code first, no greetings, read files from the project folder, and do not make assumptions about file contents. call tools to read files instead of guessing their contents.",
        },
    ]
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        answer = agent.run_turn(messages, user_input)
        print("Assistant:", answer)
