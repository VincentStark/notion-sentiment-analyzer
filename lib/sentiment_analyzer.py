import json
import nltk
import hashlib
import redis
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from openai import OpenAI
import os


class SentimentAnalyzer:

    def __init__(self, analyzer_type="nltk"):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", 6379)
        redis_password = os.getenv("REDIS_PASSWORD", None)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0)

        self.analyzer_type = analyzer_type
        if self.analyzer_type == "nltk":
            self.initialize_nltk_analyzer()
        elif self.analyzer_type == "gpt4":
            self.initialize_gpt4_analyzer()

    def initialize_nltk_analyzer(self):
        nltk.download("vader_lexicon")
        self.analyzer = SentimentIntensityAnalyzer()

    def initialize_gpt4_analyzer(self):
        self.analyzer = OpenAI()

    def analyze(self, text):
        if self.analyzer_type == "nltk":
            return self.analyze_with_nltk(text)
        elif self.analyzer_type == "gpt4":
            return self.analyze_with_gpt4(text)

    def analyze_with_nltk(self, text):
        sentiment_score = self.analyzer.polarity_scores(text)
        return sentiment_score["compound"]

    def analyze_with_gpt4(self, text):
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        cached_score = self.redis_client.get(text_hash)

        if cached_score is not None:
            return json.loads(cached_score)

        response = self.analyzer.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON.",
                },
                {
                    "role": "user",
                    "content": f"What's the author's happiness score of the text? Put it to 'score' field that as a float value from -1.0 (very unhappy) to 1.0 (very happy). Text: {text}",
                },
            ],
        )
        
        score = json.loads(response.choices[0].message.content)["score"]
        self.redis_client.set(text_hash, json.dumps(score))

        return score
