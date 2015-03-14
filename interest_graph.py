import requests
import csv
import time
import json
import os

def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate

@RateLimited(0.3)
def topics(url):
    print url
    payload = { 'url': url,
                'api-token': os.environ["PRISMATIC_API_TOKEN"]}
    r = requests.post("http://interest-graph.getprismatic.com/url", data=payload)
    return r

urls = set()
with open("tweets.csv", "r") as file:
    reader = csv.reader(file, delimiter=",", escapechar="\\", doublequote = False)
    reader.next()
    for row in reader:
        if row[4]:
            for url in row[4].split(","):
                urls.add(url)

with open("topics.csv", "w") as topicsfile:
    topics_writer = csv.writer(topicsfile, delimiter=",")
    topics_writer.writerow(["Url", "TopicId", "Topic", "Score"])

    for url in urls:
        response = topics(url)
        if response.status_code == 200:
            tmp = response.json()
            print tmp
            for topic in tmp['topics']:
                topics_writer.writerow([url, topic["id"], topic["topic"], topic["score"]])
