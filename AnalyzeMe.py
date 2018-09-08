import requests
from datetime import datetime
from datetime import timedelta
import pandas as pd

class AnalyzeMe:
    def __init__(self, token):
        self.token = token
        self.groups = requests.get('https://api.groupme.com/v3/groups?token={}'.format(token)).json()

    def printGroupIDs(self):
        for group in self.groups['response']:
            print(group['name'] + ': ' + group['id'])

    def printUserIDs(self):
        for user in self.users:
            print(user[1] + ': ' + user[0])

    def _getUsers(self):
        users = []
        group = requests.get('https://api.groupme.com/v3/groups/{}?token={}'.format(self.id, self.token)).json()
        for user in group['response']['members']:
            users.append((user['user_id'], user['nickname']))
        return users

    def _getMessages(self, limit=100, start=datetime.today(), end=datetime.today()-timedelta(days=1)):
        messages = {}
        done = False
        last_id = 0
        count = 0
        while True:
            count += 1
            print(count)
            try:
                if last_id == 0:
                    batch = requests.get('https://api.groupme.com/v3/groups/{}/messages?token={}'.format(self.id, self.token), {'limit':limit}).json()
                else:
                    batch = requests.get('https://api.groupme.com/v3/groups/{}/messages?token={}'.format(self.id, self.token), {'before_id':last_id,'limit':limit}).json()
            except:
                print('Finished Messages')
                break
            for message in batch['response']['messages']:
                if datetime.fromtimestamp(message['created_at']) < end:
                    done = True
                    break
                else:
                    if message['sender_id'] not in messages:
                        messages[message['sender_id']] = {}
                    messages[message['sender_id']][message['id']] = {}
                    if message['text'] != None:
                        messages[message['sender_id']][message['id']]['text'] = message['text'].replace('\n', ' ')
                    else:
                        messages[message['sender_id']][message['id']]['text'] = ''
                    messages[message['sender_id']][message['id']]['date'] = datetime.fromtimestamp(message['created_at']).strftime('%y%m%d')
                    messages[message['sender_id']][message['id']]['likes'] = message['favorited_by']
            last_id = batch['response']['messages'][-1]['id']
            if done:
                break
        return messages

    def loadGroup(self, id):
        self.id = id
        self.users = self._getUsers()
        self.messages = self._getMessages()

    def toCSV(self):
        for person in self.messages.keys():
            df = pd.DataFrame(self.messages[person])
            df = df.T
            df.to_csv('messages\\{}'.format(person))

    def getDF(self, user_id):
        return pd.DataFrame(self.messages[user_id]).T
