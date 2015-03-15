import argparse
import sys
import os
import tweepy
import csv
import json
from collections import  deque

class Users:
    def __init__(self):
        self.users = {}
        with open("data/users.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                row[1] = None if row[1] == ""  else row[1]
                self.users[row[0]] = {"lastTweetRetrieved" : row[1]}

    def all(self):
        return self.users

    def find(self, username):
        return self.users[username]

    def save(self, username, value):
        self.users[username] = value

        with open('data/users.csv', "w") as file:
            writer = csv.writer(file, delimiter = ",")
            for key, value in self.users.iteritems():
                writer.writerow([key, value["lastTweetRetrieved"]])

def seed(api, username):
    USERS_TO_PROCESS = 50
    users_to_process = deque()
    users_processed = set([username])

    for tweet in tweepy.Cursor(api.user_timeline, id=username).items(50):
        for user in tweet.entities["user_mentions"]:
            if not len(users_to_process) > USERS_TO_PROCESS:
                users_to_process.append(user["screen_name"])
            else:
                break
    users_processed = set([username])
    while True:
        if len(users_processed) >= USERS_TO_PROCESS:
            break
        else:
            if len(users_to_process) > 0:
                next_user = users_to_process.popleft()
                print next_user
                if not next_user in users_processed:
                    users_processed.add(next_user)
                    for tweet in tweepy.Cursor(api.user_timeline, id=next_user).items(10):
                        for user_mentioned in tweet.entities["user_mentions"]:
                            if not len(users_processed) > 50:
                                users_to_process.append(user_mentioned["screen_name"])
                            else:
                                break
            else:
                break
    with open("data/users.csv", "w") as usersfile:
        writer = csv.writer(usersfile, delimiter=",")
        for user in users_processed:
            writer.writerow([user, "", ""])

def read_user(api, username):
    print username
    profile_file_path = "data/profiles/{0}.json".format(username)
    if os.path.exists(profile_file_path):
        with open(profile_file_path, "r") as file:
            profile = json.loads(file.read())
            print profile["name"]
            print profile["description"]
            print "Friends: {0}".format(len(profile["friends"]))
            print "Followers: {0}".format(len(profile["followers"]))

    file_path = "data/tweets/{0}.json".format(username)

    if not os.path.exists(file_path):
        tweets = []
    else:
        with open(file_path, "r") as file:
            tweets = json.loads(file.read())

    print "# of tweets: {0}".format(len(tweets))
    if len(tweets) > 0:
        print "latest tweets:"
        for tweet in tweets[:5]:
            print tweet["id"], tweet["text"]

def download_user_tweets(api, users, username):
    print username
    value = users.find(username)

    file_path = "data/tweets/{0}.json".format(username)
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            tweets =  json.loads(file.read())
    else:
        tweets = []

    first_tweet_done = False
    since_id = value["lastTweetRetrieved"]
    for tweet in tweepy.Cursor(api.user_timeline, id=username, since_id = since_id).items(50):
        print tweet.id
        if not first_tweet_done:
            value["lastTweetRetrieved"] = tweet.id
            first_tweet_done = True
        tweets.append(tweet._json)

    users.save(username, value)

    with open("data/tweets/{0}.json".format(username), "w") as file:
        file.write(json.dumps(tweets))

def download_profile(api, username):
    print username

    profile = api.get_user(username)._json
    followers = list(tweepy.Cursor(api.followers_ids, username).items())
    friends = list(tweepy.Cursor(api.friends_ids, username).items())

    profile["followers"] =  followers
    profile["friends"] =  friends

    with open("data/profiles/{0}.json".format(username), "w") as file:
        file.write(json.dumps(profile))

def main(argv=None):
    consumer_key =  os.environ['CONSUMER_KEY']
    consumer_secret =  os.environ['CONSUMER_SECRET']
    access_token =  os.environ['ACCESS_TOKEN']
    access_token_secret =  os.environ['ACCESS_TOKEN_SECRET']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

    parser = argparse.ArgumentParser(description='Query the Twitter API')
    parser.add_argument('--seed')
    parser.add_argument('--download-tweets')
    parser.add_argument('--download-profile')
    parser.add_argument('--read-user')

    if argv is None:
        argv = sys.argv

    args = parser.parse_args()

    if args.seed:
        seed(api, args.seed)

    if args.download_tweets:
        users = Users()
        download_user_tweets(api, users,  args.download_tweets)

    if args.download_profile:
        users = Users()
        download_profile(api, args.download_profile)

    if args.read_user:
        read_user(api, args.read_user)

if __name__ == "__main__":
    sys.exit(main())
