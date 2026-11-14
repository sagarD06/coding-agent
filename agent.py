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

    def chat(self, messages):
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
        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print(
                f"Error: Received status code {response.status_code} from the API."
            )
            print("Response content:", response.text)  # Debugging line to print the response content

        response.raise_for_status()  # Raise an exception for HTTP errors
        print(
            "Response JSON:", response.json()
        )  # Debugging line to print the response JSON
        return response.json()["message"]


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

        messages.append({"role": "user", "content": user_input})

        for step in range(MAX_STEPS):
            reply = agent.chat(messages)
            messages.append(reply)

            if not reply.get("tool_calls"):
                print("Assistant:", reply["content"])
                break

            for tool_call in reply["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"].get("arguments", {})

                if tool_name in AVAILABLE_TOOLS:
                    tool_result = AVAILABLE_TOOLS[tool_name](**tool_args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": tool_name,
                            "content": str(tool_result),
                        }
                    )
                else:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": tool_name,
                            "content": f"Tool {tool_name} not found.",
                        }
                    )
                    print(f"Tool {tool_name} not found.")
        else:
            print("Maximum steps reached without a final answer.")
