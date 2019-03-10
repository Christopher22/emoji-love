import sys
import json
import csv
import argparse
from typing import Dict, Sequence, IO

import emoji


def read_tweets(
    source: IO, languages: Sequence[str], language_id: str, tweet_id: str
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


def extract_emojis(
    tweets_by_language: Dict[str, Sequence[str]]
) -> Dict[str, Sequence[Sequence[str]]]:
    """
    Extract all the emoji from a dict of languages and their related tweets.
    :param tweets_by_language: A dictionary mapping languages to all the available text content of tweets.
    :return: A dictionary mapping languages to the used emojis.
    """

    emojis = {language: None for language in tweets_by_language.keys()}
    for language, tweets in tweets_by_language.items():
        # Extract all the emoji and convert their unicode representation to ASCII text.
        emojis[language] = [
            [emoji.demojize(c).strip(":") for c in tweet if c in emoji.UNICODE_EMOJI]
            for tweet in tweets
        ]

    return emojis


def export_tweets(output: IO, emojis: Dict[str, Sequence[Sequence[str]]]) -> None:
    """
    Write the results of the extraction process as CSV into an IO stream.
    :param output: The output IO stream.
    :param emojis: A dictionary mapping languages to the used emojis.
    """

    # Create the columns all uppercase as proposed by Gries.
    COLUMNS = ["TWEET", "EMOJI", "LANGUAGE"]

    # Create a CSV writer and write the column row
    writer = csv.DictWriter(output, fieldnames=COLUMNS, delimiter="\t")
    writer.writeheader()

    # Iterate trough all the languages and their tweets
    tweet_id = -1
    for language, parsed_tweets in emojis.items():
        for tweet_id, parsed_tweet in enumerate(parsed_tweets, start=tweet_id + 1):
            # Write each emoji to the output and count them
            if len(parsed_tweet) == 0:
                writer.writerow(
                    {"TWEET": tweet_id, "EMOJI": None, "LANGUAGE": language}
                )
            else:
                for emoji_id, parsed_emoji in enumerate(parsed_tweet):
                    writer.writerow(
                        {"TWEET": tweet_id, "EMOJI": parsed_emoji, "LANGUAGE": language}
                    )


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

    arguments = parser.parse_args()

    # Extract all tweet contents by language
    tweets_by_language = read_tweets(
        arguments.input,
        languages=arguments.languages,
        tweet_id=arguments.tweet_key,
        language_id=arguments.language_key,
    )

    # Extract the emojis
    emojis = extract_emojis(tweets_by_language)

    # Write the results
    export_tweets(arguments.output, emojis)
