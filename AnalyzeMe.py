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

    def _getUsers(self):
        users = requests.get('https://api.groupme.com/v3/groups/{}?token={}'.format(self.id, self.token)).json()
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

    def getGroup(self, id):
        self.id = id
        self.messages = self._getMessages()

    def toCSV(self):
        for person in self.messages.keys():
            df = pd.DataFrame(self.messages[person])
            df = df.T
            df.to_csv('messages\\{}'.format(person))

am = AnalyzeMe('57c859b00d2c01366e14698edaba82b3')
am.printGroupIDs()
am.getGroup('24252629')
am.toCSV()
