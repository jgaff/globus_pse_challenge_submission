# -*- coding: utf-8 -*-
"""
    Globus PSE Coding Challenge Back End
    Author:Jonathon Gaff

"""

import json
import urllib
import time
import calendar
import base64

import requests
from flask import Flask, g
from flask_cors import cross_origin

app = Flask(__name__)
app.config.from_object('resources.settings')

TWITTER_OATH2_URL = "https://api.twitter.com/oauth2/token"
TWITTER_USER_BASE = ("https://api.twitter.com/1.1/statuses/"
                     "user_timeline.json?user_id=")


@app.route('/')
def challenge():
    return 'Globus Challenge'


@app.route('/tweets/<twitter_account_id>', methods=["GET"])
@cross_origin(methods=["GET"])
def get_user_tweets(twitter_account_id):
    """Fetch tweets from the public timeline of a given Twitter user.

    Arguments:
    twitter_account_id: A Twitter user's ID as an int or str.

    Returns:
    JSON array of objects representing tweets, each with the following fields:
    user_id: The provided Twitter user's ID.
    user_screen_name: The screen name associated with the given Twitter user.
    user_profile_image: A URL pointing at the Twitter user's profile image.
    tweet_text: The text of the tweet.
    tweet_id: The ID of the tweet.
    tweet_unix_timestamp: The time of the tweet, expressed as a UNIX timestamp.
    """
    try:
        try:
            user_id = int(twitter_account_id)
        except ValueError:
            return json.dumps({
                "success": False,
                "error_code": 400,
                "error_message": "Invalid Twitter account ID.",
                "error_values": {
                    "twitter_account_id": twitter_account_id
                    }
                })

        # Authenticate to Twitter's API.
        consumer_key = urllib.parse.quote(app.config["TWITTER_API_KEY"])
        consumer_secret = urllib.parse.quote(app.config["TWITTER_API_SECRET"])
        bearer_token_cred = base64.b64encode(bytes(consumer_key
                                                   + ":"
                                                   + consumer_secret,
                                                   "utf-8"))
        auth_headers = {
            "Authorization": b"Basic " + bearer_token_cred,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
            }
        auth_body = "grant_type=client_credentials"
        auth_res = requests.post(TWITTER_OATH2_URL,
                                 headers=auth_headers,
                                 data=auth_body)

        # Check if the authentication yielded a bearer token.
        if auth_res.json().get("token_type", None) != "bearer":
            return json.dumps({
                "success": False,
                "error_code": 403,
                "error_message": "Authentication with Twitter failed.",
                "error_values": {
                    "twitter_response": auth_res.json()
                    }
                })
        bearer_token = auth_res.json().get("access_token")

        # Request the user's public timeline.
        headers = {
            "Authorization": "Bearer " + bearer_token
            }
        tweet_res = requests.get(TWITTER_USER_BASE + str(user_id),
                                 headers=headers)
        if tweet_res.status_code == 404:
            return json.dumps({
                "success": False,
                "error_code": 404,
                "error_message": "Unable to find user ID.",
                "error_values": {
                    "twitter_response": tweet_res.text
                    }
                })
        elif tweet_res.status_code >= 500:
            return json.dumps({
                "success": False,
                "error_code": tweet_res.status_code,
                "error_message": "Twitter unable to return tweets.",
                "error_values": {
                    "twitter_response": tweet_res.text
                    }
                })
        elif tweet_res.status_code >= 400:
            return json.dumps({
                "success": False,
                "error_code": tweet_res.status_code,
                "error_message": "Unable to process that user ID.",
                "error_values": {
                    "twitter_response": tweet_res.text
                    }
                })
        elif tweet_res.status_code != 200:
            return json.dumps({
                "success": False,
                "error_code": tweet_res.status_code,
                "error_message": "Unable to retrieve tweets.",
                "error_values": {
                    "twitter_response": tweet_res.text
                    }
                })

        # Extract the important information out of the response.
        try:
            tweets_raw = tweet_res.json()
            tweets_list = []
            for tweet in tweets_raw:
                try:
                    tweet_data = {
                        "user_id": str(user_id),
                        "user_screen_name": tweet["user"]["screen_name"],
                        "user_profile_image": tweet["user"]
                                                   ["profile_image_url"],
                        "tweet_text": tweet["text"],
                        "tweet_id": tweet["id_str"],
                        "tweet_unix_timestamp":
                            calendar.timegm(
                                time.strptime(
                                    tweet["created_at"],
                                    '%a %b %d %H:%M:%S +0000 %Y'))
                        }

                    tweets_list.append(tweet_data)
                except (KeyError, OverflowError, ValueError):
                    pass  # Hide malformed tweets.

        except Exception as e:
            return json.dumps({
                "success": False,
                "error_code": 500,
                "error_message": "Unable to process tweets.",
                "error_values": {
                    "raw_error": repr(e),
                    "raw_tweets": tweets_raw
                    }
                })

        return json.dumps({
            "success": True,
            "tweet_list": tweets_list
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error_code": 500,
            "error_message": ("An unknown error occurred."
                              " Please try again later."),
            "error_values": {
                "raw_error": repr(e)
                }
            })

if __name__ == "__main__":
    app.run()
