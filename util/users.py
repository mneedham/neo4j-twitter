import csv

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

    def add(self, user):
        value = {"lastTweetRetrieved": ""}
        self.save(user, value)

    def save(self, username, value):
        self.users[username] = value

        with open('data/users.csv', "w") as file:
            writer = csv.writer(file, delimiter = ",")
            for key, value in self.users.iteritems():
                writer.writerow([key, value["lastTweetRetrieved"]])
