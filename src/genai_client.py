import json
from openai import OpenAI
import anthropic

class GenAIClient:
    def __init__(self):
        # OpenAI.api_key = "sk-dnboyxi0tL0gGP7v0cD8rw"
        self.PROXY_ENDPOINT = "https://nova-litellm-proxy.onrender.com/"

    # prompt for email - "You are a venture capitalist who gives advice to startups regarding market research, and cold emailing for support"
    # prompt for market research - "You are a market researcher that looks for companies that startups can reach out to and sell their product to."

    def get_completions_openai(self, prompt, description):
        with open("key.txt") as f:
            api_key = f.read()
        client = OpenAI(api_key=api_key, base_url=self.PROXY_ENDPOINT)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": description},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content
    
    def get_completion_anthropic(self, prompt):
        client = anthropic.Client()
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0,
            system="You are a venture capitalist who gives advice to startups regarding market research, and cold emailing for support",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
