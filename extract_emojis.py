import sys
import random
import json
import csv
import argparse
from typing import Dict, Sequence, IO
from collections import Counter

import emoji


def read_tweets(
    source: IO, languages: Sequence[str], language_id="lang", tweet_id="text"
) -> Dict[str, Sequence[str]]:
    """
    Read tweets from an IO stream. The stream is required to contain a single JSON-serialized object per line.
    :param source: The IO stream.
    :param languages: The languages of interest used to filter all the tweets.
    :param language_id: The JSON object key for getting the language of a tweet.
    :param tweet_id: The JSON object key for getting the content of a tweet.
    :return: A dictionary mapping languages to all the available text contents of tweets.
    """

    tweets = {language: [] for language in languages}

    # For each line ...
    for line in source:
        # ... load the corresponding JSON object ...
        data = json.loads(line)

        # ... and add it to its language, if it is not filtered.
        if data[language_id] in tweets:
            tweets[data[language_id]].append(data[tweet_id])

    return tweets


def extract_emojis(tweets_by_language: Dict[str, Sequence[str]]) -> Dict[str, Counter]:
    """
    Extract all the emoji from a dict of languages and their related tweets.
    :param tweets_by_language: A dictionary mapping languages to all the available text content of tweets.
    :return: A dictionary mapping languages to the used emojis.
    """

    emojis = {language: Counter() for language in tweets_by_language.keys()}

    # Find the minimal available amount of tweets
    num_tweets = min((len(tweets) for tweets in tweets_by_language.values()))

    for language, tweets in tweets_by_language.items():
        # If a language contains more tweets than another subsample its tweets.
        if len(tweets) > num_tweets:
            tweets = random.sample(tweets, num_tweets)

        # Extract all the emoji and convert their unicode representation to ASCII text.
        for tweet in tweets:
            emojis[language].update(
                emoji.demojize(c).strip(":") for c in tweet if c in emoji.UNICODE_EMOJI
            )

    return emojis


def export_tweets(output: IO, emojis: Dict[str, Counter]) -> None:
    """
    Write the results of the extraction process as CSV into an IO stream.
    :param output: The output IO stream.
    :param emojis: A dictionary mapping languages to the used emojis.
    """

    EMOJI_COLUMN = "EMOJI"

    # Get a collection of all existing emoji
    emoji_names = frozenset(
        emoji_name
        for emoji_collection in emojis.values()
        for emoji_name in emoji_collection.keys()
    )

    languages = list(emojis.keys())

    # Create the columns all uppercase as proposed by Gries.
    columns = [EMOJI_COLUMN] + [language.upper() for language in languages]

    # Create a CSV writer and write the column row
    writer = csv.DictWriter(output, fieldnames=columns, delimiter="\t")
    writer.writeheader()

    # For all existing emojis in all available languages ...
    for emoji_name in emoji_names:
        # ... create a CSV row ...
        counts = {EMOJI_COLUMN: emoji_name}
        counts.update(
            {
                language.upper(): emojis[language].get(emoji_name, 0)
                for language in languages
            }
        )

        # ... and write it.
        writer.writerow(counts)


class FileType:
    """ A type for argparse. Unlike argparse.FileType, it does support arbitrary open arguments. """

    def __init__(self, mode: str, **kwargs):
        self.mode = mode
        self.arguments = kwargs

    def __call__(self, argument):
        if self.mode == "r" and argument == "-":
            return sys.stdin
        elif self.mode == "w" and argument == "-":
            return sys.stdout
        else:
            return open(argument, self.mode, **self.arguments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-input",
        type=FileType("r", encoding="utf-8"),
        default=sys.stdin,
        help="The input with the tweets. By default read from STDIN.",
    )
    parser.add_argument(
        "-output",
        type=FileType("w", encoding="utf-8", newline=""),
        default=sys.stdout,
        help="The target for the CSV output. By default write to STDOUT.",
    )
    parser.add_argument(
        "languages", type=str, nargs="+", help="Languages to be extracted."
    )
    parser.add_argument(
        "-language_key",
        type=str,
        default="lang",
        help="The language attribute of JSON tweet object",
    )
    parser.add_argument(
        "-tweet_key",
        type=str,
        default="text",
        help="The text attribute of JSON tweet object",
    )
    parser.add_argument(
        "-seed",
        type=int,
        default=42,
        help="The random seed for extracting emojis reproducable.",
    )

    arguments = parser.parse_args()

    # Set the random seed to make the process reproducable
    random.seed(arguments.seed)

    # Extract all tweet contents by language
    tweets_by_language = read_tweets(arguments.input, arguments.languages)

    # Extract the emojis
    emojis = extract_emojis(tweets_by_language)

    # Write the results
    export_tweets(arguments.output, emojis)
