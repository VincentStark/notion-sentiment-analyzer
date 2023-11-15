import argparse
from lib.notion_connector import NotionConnector
from lib.sentiment_analyzer import SentimentAnalyzer
from lib.diagram_creator import DiagramCreator

from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Analyze sentiment from Notion entries")
    parser.add_argument("-m", "--model", default="nltk", help="Specify the analyzer type (default: nltk)")
    args = parser.parse_args()

    # Create an instance of NotionConnector
    notion_connector = NotionConnector()

    # Get entries from the Notion Database
    entries = notion_connector.get_entries()

    # Create an instance of SentimentAnalyzer with the specified model
    sentiment_analyzer = SentimentAnalyzer(analyzer_type=args.model)

    # Analyze sentiment for each entry
    sentiment_scores = []
    dates = []
    for entry in tqdm(entries, desc="Analyzing sentiment"):
        sentiment_score = {
            "date": entry["date"],
            "score": sentiment_analyzer.analyze(entry["text"]),
        }
        sentiment_scores.append(sentiment_score)
        dates.append(entry["date"])

    # Create an instance of DiagramCreator
    diagram_creator = DiagramCreator()

    # Create a diagram of sentiment over time
    diagram_creator.create_diagram(sentiment_scores)


if __name__ == "__main__":
    main()
