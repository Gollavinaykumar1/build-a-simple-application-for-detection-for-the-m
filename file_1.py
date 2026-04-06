import aiohttp
import asyncio
from typing import Dict
import json
from embeddings import Embeddings
from ai_config import AIConfig
from prompt_templates import PROMPT_TEMPLATES

class AIEngine:
    def __init__(self, config: AIConfig):
        self.config = config
        self.embeddings = Embeddings()

    async def detect_malware(self, file_contents: str) -> Dict:
        prompt = PROMPT_TEMPLATES["malware_detection"].format(file_contents)
        response = await self.query_ai(prompt)
        return response

    async def query_ai(self, prompt: str) -> Dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config.api_url,
                json={"prompt": prompt, "max_tokens": self.config.max_tokens, "temperature": self.config.temperature},
                headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    await self.retry_query_ai(session, prompt)

    async def retry_query_ai(self, session: aiohttp.ClientSession, prompt: str) -> Dict:
        retry_count = 0
        while retry_count < self.config.max_retries:
            try:
                async with session.post(
                    self.config.api_url,
                    json={"prompt": prompt, "max_tokens": self.config.max_tokens, "temperature": self.config.temperature},
                    headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"},
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        retry_count += 1
                        await asyncio.sleep(2 ** retry_count)
            except Exception as e:
                print(f"Error: {e}")
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)
        raise Exception("Max retries exceeded")

    def estimate_cost(self, prompt: str) -> float:
        tokens = len(prompt.split())
        return self.config.cost_per_token * tokens

async def main():
    config = AIConfig()
    engine = AIEngine(config)
    file_contents = "example file contents"
    response = await engine.detect_malware(file_contents)
    print(response)

asyncio.run(main())