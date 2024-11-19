from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import language_v1
from google.cloud import translate_v2 as translate  # Import translation API
import requests
import logging

# Set up logging to output error details
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/analyze-news": {"origins": "*"}})  # Enable CORS for all routes

# Set up Google Cloud Natural Language and Translation API clients
language_client = language_v1.LanguageServiceClient()
translate_client = translate.Client()

# Replace this with your News API key
NEWS_API_KEY = 'e9bb28c784e54cc28cdec90b89d39c26'

def analyze_sentiment(text):
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = language_client.analyze_sentiment(request={'document': document})
    sentiment = response.document_sentiment
    return {'score': sentiment.score, 'magnitude': sentiment.magnitude}

def translate_text(text, target_lang='en'):
    """Translate text to the target language using Google Cloud Translation API."""
    if target_lang != 'en':  # If the target language is not English
        translation = translate_client.translate(text, target_language=target_lang)  # Corrected argument name
        return translation['translatedText']
    return text  # Return text as is if the target language is English


@app.route('/analyze-news', methods=['GET'])
def analyze_news():
    query = request.args.get('query', 'cryptocurrency news')
    page = request.args.get('page', 1)
    target_lang = request.args.get('lang', 'en')  # Get target language from request (default to 'en')

    try:
        # Fetch news articles from News API
        news_url = f'https://newsapi.org/v2/everything?q={query}&pageSize=5&page={page}&apiKey={NEWS_API_KEY}'
        news_response = requests.get(news_url)
        news_data = news_response.json()

        if 'articles' not in news_data or not news_data['articles']:
            return jsonify({'message': 'No articles found'}), 404

        analyzed_articles = []
        for article in news_data['articles']:
            title = article.get('title', 'No Title')
            description = article.get('description', 'No Description')

            # Translate the title and description if needed
            try:
                title = translate_text(title, target_lang)
                description = translate_text(description, target_lang)
            except Exception as e:
                logging.error(f"Error translating text: {e}")
                title = "Translation Error"
                description = "Translation Error"

            # Perform sentiment analysis on the title or description
            try:
                sentiment_result = analyze_sentiment(title)
            except Exception as e:
                logging.error(f"Error analyzing sentiment: {e}")
                sentiment_result = {'score': 0, 'magnitude': 0}

            # Add sentiment data to each article
            analyzed_articles.append({
                'title': title,
                'description': description,
                'url': article.get('url'),
                'image_url': article.get('urlToImage', 'https://via.placeholder.com/250x150'),
                'sentiment': sentiment_result  # Include sentiment score and magnitude
            })

        return jsonify(analyzed_articles)

    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return jsonify({'message': 'Error processing request'}), 500

if __name__ == '__main__':
    app.run(debug=True)
