class AIConfig:
    def __init__(self):
        self.api_url = "https://api.openai.com/v1/completions"
        self.api_key = "YOUR_API_KEY"
        self.max_tokens = 2048
        self.temperature = 0.7
        self.max_retries = 5
        self.cost_per_token = 0.0004