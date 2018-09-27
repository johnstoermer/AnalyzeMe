import requests
from datetime import datetime
from datetime import timedelta
import pandas as pd
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

class AnalyzeMe:
    def __init__(self, token):
        self.token = token
        self.groups = requests.get('https://api.groupme.com/v3/groups?token={}'.format(token)).json()

    def printGroupIDs(self):
        for group in self.groups['response']:
            print(group['name'] + ': ' + group['id'])

    def printUserIDs(self):
        for user in self.users:
            print(user[1][0] + ': ' + user[0])

    def _getUsers(self):
        users = []
        group = requests.get('https://api.groupme.com/v3/groups/{}?token={}'.format(self.id, self.token)).json()
        for user in group['response']['members']:
            users.append((user['user_id'], [user['nickname']]))
        return users

    def _getMessages(self, limit=100, start=datetime.today(), end=datetime.today()-timedelta(days=7), custom_replace=False):
        messages = []
        users = {}
        done = False
        last_id = 0
        count = 0
        sia = SIA()
        messagenum = 0
        #names = ['@' + x[1] for x in self._getUsers()]
        #names = '|'.join(names)
        #pattern = re.compile(r'\b(%s)\b' % '|'.join(names), re.UNICODE)
        print(self.users)
        self.printUserIDs()
        while True:
            count += 1
            print(count)
            try:
                if last_id == 0:
                    batch = requests.get('https://api.groupme.com/v3/groups/{}/messages?token={}'.format(self.id, self.token), {'limit':limit}).json()
                else:
                    batch = requests.get('https://api.groupme.com/v3/groups/{}/messages?token={}'.format(self.id, self.token), {'before_id':last_id,'limit':limit}).json()
                while batch['response'] == None:
                    print('bad batch')
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
                    #add to users
                    if message['sender_id'] not in users:
                        users[message['sender_id']] = {}
                    if message['text'] != None:
                        text = message['text']
                        if message['attachments'] != []:
                            for i in range(len(message['attachments'])):
                                if message['attachments'][i]['type'] == u'mentions':
                                    replacements = []
                                    for j in range(len(message['attachments'][i]['loci'])):
                                        replacements.append(text[message['attachments'][i]['loci'][j][0]:(message['attachments'][i]['loci'][j][1] + message['attachments'][i]['loci'][j][0])])
                                    for j in range(len(replacements)):
                                        if custom_replace and [name[1][0] for name in self.users if name[0] == message['attachments'][i]['user_ids'][j]] != []:
                                            text = text.replace(replacements[j], [name[1][0] for name in self.users if name[0] == message['attachments'][i]['user_ids'][j]][0])
                                        else:
                                            text = text.replace(replacements[j], message['attachments'][i]['user_ids'][j])
                        polscores = sia.polarity_scores(text)
                        users[message['sender_id']][messagenum] = {}
                        users[message['sender_id']][messagenum]['text'] = text.replace('\n', ' ')
                        users[message['sender_id']][messagenum]['date'] = message['created_at']
                        users[message['sender_id']][messagenum]['likes'] = message['favorited_by']
                        mentions = []
                        for user in self.users:
                            for nick in user[1]:
                                nick = nick.lower()
                                if (nick in text.lower() or nick + 's' in text.lower() or nick + '\'s' in text.lower()) and user[0] not in mentions:
                                    mentions.append(user[0])
                        users[message['sender_id']][messagenum]['mentions'] = mentions
                        users[message['sender_id']][messagenum].update(polscores)
                        msg = {'id':messagenum, 'user':message['sender_id'], 'text':text, 'date':message['created_at'], 'likes':message['favorited_by'], 'mentions':mentions}
                        msg.update(polscores)
                        #add to messages
                        messages.append(msg)
                        messagenum += 1
            last_id = batch['response']['messages'][-1]['id']
            if done:
                break
        return messages, users

    def loadGroup(self, id, custom_nicks=[]):
        self.id = id
        self.users = self._getUsers()
        if custom_nicks != []:
            self._custom_nicknames(custom_nicks)
            self.messages, self.user_messages = self._getMessages(custom_replace=True)
        else:
            self.messages, self.user_messages = self._getMessages()

    def toCSV(self, user_id=None):
        if user_id == None:
            df = self.getDF()
            df.to_csv('group.csv', header=True, index=False, encoding='utf-8')
        else:
            for person in self.messages.keys():
                df = pd.DataFrame(self.messages[person])
                df = df.T
                df.to_csv('messages/{}'.format(person))

    def getDF(self, user_id=None):
        if user_id == None:
            df = pd.DataFrame(self.messages)
            return df
        else:
            return pd.DataFrame(self.users[user_id]).T

    def activity(self, time_range, user_id=None, likes=True, messages=True, sample_size=None):
        count = 0
        if sample_size == None:
            sample_size = self.messages[-1]['date']
        if user_id == None:
            active_users = []
            active_messagers = []
            active_likers = []
            for tuple in self.getDF().itertuples():
                if datetime.fromtimestamp(tuple.date) < time_range[0] and datetime.fromtimestamp(tuple.date) > time_range[1]:
                    count += 1
                    if tuple.user not in active_users:
                        active_users.append(tuple.user)
                    if tuple.user not in active_messagers:
                        active_messagers.append(tuple.user)
                    for liker in tuple.likes:
                        if liker not in active_users:
                            active_users.append(liker)
                        if liker not in active_likers:
                            active_likers.append(liker)
            if likes and messages:
                return len(active_users), count
            elif messages:
                return len(active_messagers), count
            elif likes:
                return len(active_likers), count

    def _custom_nicknames(self, nicknames): #nicknames is a list of (user_id, nickname) tuples
        for nickname in nicknames:
            for user in self.users:
                if nickname[0] == user[0]:
                    self.users.remove(user)
                    self.users.append(nickname)

    def friendship_bias(self):
        df = self.getDF()
        add_total = {}
        friendship_bias = {}
        for user in self.users:
            dfuser = df[(df.likes.map(set([user[0]]).issubset)) & (df.user != 'system')]
            like_bias = {}
            for liker in self.users:
                dfliker = dfuser[df.user == liker[0]]['likes']
                like_add = 0
                for like in dfliker:
                    like_add += 1 / float(len(like))
                if liker[0] not in add_total:
                    add_total[liker[0]] = like_add
                else:
                    add_total[liker[0]] += like_add
                like_bias[liker[0]] = like_add
            friendship_bias[user[0]] = like_bias
        for user in self.users:
            for liker in self.users:
                if add_total[liker[0]] == 0:
                    friendship_bias[user[0]][liker[0]] = 0
                else:
                    friendship_bias[user[0]][liker[0]] = friendship_bias[user[0]][liker[0]] / add_total[liker[0]]
        return friendship_bias

    def _friendship_bias_names(self):
        df = self.getDF()
        add_total = {}
        friendship_bias = {}
        for user in self.users:
            dfuser = df[(df.likes.map(set([user[0]]).issubset)) & (df.user != 'system')]
            like_bias = {}
            for liker in self.users:
                dfliker = dfuser[df.user == liker[0]]['likes']
                like_add = 0
                for like in dfliker:
                    like_add += 1 / float(len(like))
                if liker[1][0] not in add_total:
                    add_total[liker[1][0]] = like_add
                else:
                    add_total[liker[1][0]] += like_add
                like_bias[liker[1][0]] = like_add
            friendship_bias[user[1][0]] = like_bias
        for user in self.users:
            for liker in self.users:
                if add_total[liker[1][0]] == 0:
                    friendship_bias[user[1][0]][liker[1][0]] = 0
                else:
                    friendship_bias[user[1][0]][liker[1][0]] = friendship_bias[user[1][0]][liker[1][0]] / add_total[liker[1][0]]
        return friendship_bias
