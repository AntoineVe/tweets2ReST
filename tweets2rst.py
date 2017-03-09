#!/bin/env python3
# -*- coding: UTF-8 -*-
"""
Retrieves tweets and injects them in the pelican blog.

Code licence : WTFPL
"""

import twitter
from datetime import datetime
from tzlocal import get_localzone
import locale
from urlextract import URLExtract
import urllib.request
from io import BytesIO
import imghdr
from os import stat, mkdir, listdir
import argparse
import logging


def get_tweets(token, token_key, con_secret, con_secret_key, twitter_name):
    """
    Retrieve last tweets : do not retrieve already retrieved tweets by using
    `since_id` Twitter API feature.
    """
    try:
        articles = listdir('./content/SocialNetworks')
        articles = [article for article in articles if 'tweet' in article]
        articles.sort()
        last_recorded_tweet_id = int(articles[-1][6:-4])
        logging.debug("last recoreded tweet : " + str(last_recorded_tweet_id))
    except:
        last_recorded_tweet_id = None
        logging.debug("No recorded tweets founded")
    twitter_api = twitter.Twitter(
            auth=twitter.OAuth(
                token,
                token_key,
                con_secret,
                con_secret_key))
    if last_recorded_tweet_id:
        my_tweets = twitter_api.statuses.user_timeline(
                screen_name=twitter_name,
                count=600,
                since_id=last_recorded_tweet_id)
    else:
        my_tweets = twitter_api.statuses.user_timeline(
                screen_name=twitter_name,
                count=600)
    logging.debug(str(len(my_tweets)) + " tweets retrieved")
    return(my_tweets)


def tweet2rest(tweets_json):
    """
    Use the JSON from twitter API to make one ReST article by tweet.
    Save image if needed.
    Add some metadatas if relevant:
     - :location: show place and GPS coordinates
     - :tags: repeat twitter hashtags
     - :image: and :og_image: to display a picture and use it as OpenGraph pic
    """
    for tweet in tweets_json:
        if (
                not tweet['retweeted']
                and tweet['in_reply_to_status_id_str'] is None
                and tweet['text'][0] != '@'
                and 'Instagram' not in tweet['source']):
            text = tweet['text']
            summary = text.split("\n")[0]
            data = "####################\n"
            data += tweet['id_str'] + "\n"
            data += "####################\n"
            data += "\n"
            locale.setlocale(locale.LC_ALL, 'C')
            # Because twitter json use C
            date = datetime.strptime(
                    tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")
            locale.setlocale(locale.LC_ALL, '')
            date = date.astimezone(get_localzone())
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            data += ":date: "
            data += date + "\n"
            try:
                location = str(tweet['place']['full_name'])
                try:
                    location += "|" + str(
                            tweet['coordinates']['coordinates'][1])
                    location += "|" + str(
                            tweet['coordinates']['coordinates'][0])
                except:
                    location += "||"
                data += "location: " + location + "\n"
            except:
                pass
            if "entities" in tweet.keys():
                if "hashtags" in tweet['entities'].keys():
                    if len(tweet['entities']['hashtags']) > 0:
                        data += ":tags: "
                        for tag in tweet['entities']['hashtags']:
                            data += tag['text'] + ", "
                        data = data[:-2]  # Remove last comma-space
                        data += "\n"
                if (
                        "media" in tweet['entities'].keys()
                        and tweet['entities']['media'][0]['type'] == "photo"):
                    img = urllib.request.urlopen(
                            tweet['entities']['media'][0]['media_url']).read()
                    img_IO = BytesIO(img)
                    img_ext = '.' + imghdr.what(img_IO)
                    data += ":image: {photo}../images/tweets/"
                    data += tweet['entities']['media'][0]['id_str']
                    data += img_ext + "\n"
                    data += ":og_image: /images/tweets/"
                    data += tweet['entities']['media'][0]['id_str']
                    data += img_ext + "\n"
                    try:
                        stat("./content/images")
                    except:
                        mkdir("./content/images")
                    try:
                        stat("./content/images/tweets")
                    except:
                        mkdir("./content/images/tweets")
                    img_file = open(
                            "./content/images/tweets/"
                            + tweet['entities']['media'][0]['id_str']
                            + img_ext, "wb")
                    img_file.write(img)
                    img_file.close()
                    logging.debug(
                            "Image "
                            + tweet['entities']['media'][0]['id_str']
                            + img_ext + " saved")
                    for img in tweet['entities']['media']:
                        summary = summary.replace(img['url'], '')
                        text = text.replace(img['url'], '')
                # TODO : Add gallery support for multiple photos in a tweet.
            for url in URLExtract().find_urls(text):
                text = text.replace(url, "`"+url+" <"+url+">`_")
            text_2 = list()
            for word in text.split():
                if word[0] == "@" or word[0:2] == ".@":
                    # Take care of non alphanum at the end, like comma or point
                    if word[-1].isalnum():
                        word = word.replace(
                                word, '`'
                                + word
                                + ' <https://twitter.com/'
                                + word[1:]
                                + '>`_')
                    else:
                        word = word.replace(
                                word, '`'
                                + word[:-1]
                                + ' <https://twitter.com/'
                                + word[1:-1]
                                + '>`_'
                                + word[-1])
                if word[0] == "#":
                    if word[-1].isalnum():
                        word = word.replace(
                                word, '`'
                                + word
                                + ' <https://twitter.com/hashtag/'
                                + word[1:]
                                + '>`_')
                    else:
                        word = word.replace(
                                word, '`'
                                + word[:-1]
                                + ' <https://twitter.com/hashtag/'
                                + word[1:-1]
                                + '>`_' + word[-1])
                text_2.append(word)
            text = ' '.join(text_2)
            data += ":summary: " + summary + "\n"
            data += "\n"
            data += text
            try:
                stat("./content/SocialNetworks")
            except:
                mkdir("./content/SocialNetworks")
            f = open(
                    "./content/SocialNetworks/tweet_"
                    + tweet['id_str']
                    + ".rst", "w", encoding="UTF-8")
            f.write(data)
            logging.info("Tweet number " + tweet['id_str'] + " saved !")
            f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tweets -> ReST')
    parser.add_argument(
            '-D',
            '--debug',
            action="store_true")
    parser.add_argument(
            'token',
            help="""Please provide a Token
            (See https://apps.twitter.com/)""")
    parser.add_argument(
            'token_key',
            help="""Please provide a Token Secret
            (See https://apps.twitter.com/)""")
    parser.add_argument(
            'con_secret',
            help="""Please provide a Consumer Key
            (See https://apps.twitter.com/)""")
    parser.add_argument(
            'con_secret_key',
            help="""Please provide a Consumer Secret
            (See https://apps.twitter.com/)""")
    parser.add_argument(
            'twitter_name',
            help="""Please provide your Twitter screen name""")
    args = parser.parse_args()
    settings = vars(args)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    tweet2rest(
            get_tweets(
                settings['token'],
                settings['token_key'],
                settings['con_secret'],
                settings['con_secret_key'],
                settings['twitter_name']
                )
            )
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
