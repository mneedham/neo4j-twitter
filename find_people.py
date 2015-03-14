import os
import tweepy
import csv
from collections import Counter, deque

consumer_key =  os.environ['CONSUMER_KEY']
consumer_secret =  os.environ['CONSUMER_SECRET']
access_token =  os.environ['ACCESS_TOKEN']
access_token_secret =  os.environ['ACCESS_TOKEN_SECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

counter = Counter()
users_to_process = deque()
USERS_TO_PROCESS = 50

def extract_tweet(tweet):
    user_mentions = ",".join([user["screen_name"].encode("utf-8")
                             for user in tweet.entities["user_mentions"]])
    urls = ",".join([url["expanded_url"]
                     for url in tweet.entities["urls"]])
    return [tweet.user.screen_name.encode("utf-8"),
            tweet.id,
            tweet.text.encode("utf-8"),
            user_mentions,
            urls]

starting_user = "chvest"
with open("tweets.csv", "a") as tweets:
    writer = csv.writer(tweets, delimiter=",", escapechar="\\", doublequote = False)
    for tweet in tweepy.Cursor(api.user_timeline, id=starting_user).items(50):
        writer.writerow(extract_tweet(tweet))
        tweets.flush()
        for user in tweet.entities["user_mentions"]:
            if not len(users_to_process) > USERS_TO_PROCESS:
                users_to_process.append(user["screen_name"])
                counter[user["screen_name"]] += 1
            else:
                break
    users_processed = set([starting_user])
    while True:
        if len(users_processed) >= USERS_TO_PROCESS:
            break
        else:
            if len(users_to_process) > 0:
                next_user = users_to_process.popleft()
                print next_user
                if next_user in users_processed:
                    "-- user already processed"
                else:
                    "-- processing user"
                    users_processed.add(next_user)
                    for tweet in tweepy.Cursor(api.user_timeline, id=next_user).items(10):
                        writer.writerow(extract_tweet(tweet))
                        tweets.flush()
                        for user_mentioned in tweet.entities["user_mentions"]:
                            if not len(users_processed) > 50:
                                users_to_process.append(user_mentioned["screen_name"])
                                counter[user_mentioned["screen_name"]] += 1
                            else:
                                break
            else:
                break

for user_name, count in counter.most_common(20):
    print user_name, count
