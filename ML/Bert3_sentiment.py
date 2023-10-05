#BERT model: finiteautomata/bertweet-base-sentiment-analysis

import os
from environs import Env
import praw
from io import BytesIO
import base64
from .models import Query_data
from transformers import pipeline
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud


# Initialize the sentiment analysis pipeline for the specific model
bert3_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

# Initialize the Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv('Marvel_Client_ID'),
    client_secret=os.getenv('Marvel_Client_Secret'),
    user_agent=os.getenv('Marvel_user_agent'),
)

def analyze_sentiment_with_bert3(comments):
    """
    Analyze sentiment for a list of comments using a specific BERT-based sentiment analysis model.

    Args:
        comments (list): List of comments.

    Returns:
        sentiments (list): List of sentiment labels for each comment.
        scores (dict): Dictionary containing sentiment scores for each sentiment label.
    """
    sentiments = []
    scores = {'POS': [], 'NEU': [], 'NEG': []}

    for comment in comments:
        # Analyze sentiment for each comment using the specific model
        max_comment_length = 128  # Adjust as needed
        if len(comment) > max_comment_length:
            # Skip this comment
            continue
        result = bert3_pipeline(comment)
        sentiment_label = result[0]['label']
        sentiments.append(sentiment_label)
        scores[sentiment_label].append(result[0]['score'])

    return sentiments, scores

def calculate_total_average(scores_bert3):
    """
    Calculate the total average sentiment score for all comments using specific model scores.

    Args:
        scores_bert3 (dict): Dictionary containing sentiment scores for each sentiment label.

    Returns:
        total_average (float): Total average sentiment score.
    """
    total_score = 0.0
    total_count = 0

    for scores in scores_bert3.values():
        total_score += sum(scores)
        total_count += len(scores)

    if total_count > 0:
        total_average = total_score / total_count
        return total_average

    return None  # Handle the case when there are no scores

def plot_sentiments(sentiments_data_bert3):
    """
    Generate a bar chart to visualize sentiment analysis results.

    Args:
        sentiments_data_bert3 (list): List of sentiment labels for each comment.

    Returns:
        img_str (str): Base64-encoded image string of the generated plot.
    """
    # Count the occurrences of each sentiment label
    sentiment_counts = Counter(sentiments_data_bert3)

    # Define color mapping for sentiment labels
    color_mapping = {
        'POS': 'green',    # Positive sentiment
        'NEG': 'red',      # Negative sentiment
        'NEU': 'yellow'    # Neutral sentiment
    }

    # Extract labels and counts
    labels = sentiment_counts.keys()
    counts = sentiment_counts.values()

    # Assign colors based on sentiment labels
    colors = [color_mapping.get(label, 'green') for label in labels]

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color=colors)
    plt.xlabel('Sentiment Labels')
    plt.ylabel('Count')
    plt.title('Sentiment Analysis of Comments')
    plt.ylim(0, max(counts) + 1)  # Set the y-axis range based on the maximum count

    # Convert the plot image to a base64-encoded string
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png")
    img_str = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

    return img_str

def generate_wordcloud(comments):
    """
    Generate a word cloud from a list of comments.

    Args:
        comments (list): List of comments.

    Returns:
        img_str (str): Base64-encoded image string of the generated word cloud.
    """
    # Combine comments into a single text string
    comments_text = ' '.join(comments)

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400).generate(comments_text)

    # Convert the word cloud image to a base64-encoded string
    img_buffer = BytesIO()
    wordcloud.to_image().save(img_buffer, format="PNG")
    img_str = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

    return img_str

def start_sentiment_analysis_BERT3(query):

    try:
        comments_max = 50
        limit = 5
        comments = []

        # Check if there are existing comments related to 'query' in the database.
        existing_query = Query_data.objects.filter(query_name=query).first()

        if existing_query and existing_query.get_comments():
            # Use existing comments from the database.
            comments = existing_query.get_comments()
            print(query + ' data fetched from the database')
        else:
            for submission in reddit.subreddit("all").search(query, limit=limit):
                submission.comments.replace_more(limit=None)
                for comment in submission.comments.list():
                    max_comment_length = 120  # Adjust as needed
                    if len(comment.body) > max_comment_length:
                        # Skip this comment
                        continue
                    comments.append(comment.body)
                    if len(comments) >= comments_max:
                        break

            # Save the newly fetched comments to the database.
            if not existing_query:
                # If the query doesn't exist in the database, create a new instance and save comments.
                query_instance = Query_data(query_name=query)
                query_instance.save_comments(comments)
                print(query + ' data saved to the database')
        
        sentiments_data_bert3, scores_bert3 = analyze_sentiment_with_bert3(comments)
        average_score_bert3 = calculate_total_average(scores_bert3)
        sentiments_bert3_plot = plot_sentiments(sentiments_data_bert3)
        comments_wordcloud = generate_wordcloud(comments)
       
    except praw.exceptions.PRAWException as reddit_exception:
        print('Reddit API error:', str(reddit_exception))
        return None, None, None

    except Exception as e:
        print('Error:', str(e))
        return None, None, None

    return average_score_bert3, sentiments_bert3_plot, comments_wordcloud

