from groupy.session import Session
from groupy.client import Client

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'): #not my code, I just thought it looked cool (https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

class AnalyzeMe:
    dudes = {}
    
    def __init__(self, my_token, my_group_id, max_messages):
        self.group = Client.from_token(my_token).groups.get(my_group_id)
        self._generateDict(max_messages)
        
    def _generateDict(self, max_messages):
        message_count = 0
        for message in self.group.messages.list_all():
            if message.user_id not in self.dudes:
                self.dudes[message.user_id] = {}
            self.dudes[message.user_id][message.id] = {'likes':message.favorited_by,'text':message.text}
            message_count += 1
            printProgressBar(message_count, max_messages, prefix = 'Loading Messages:', length = 50)
            if message_count == max_messages:
                print('Finished Loading ' + str(max_messages) + ' messages')
                return
        print('Stopped early, there are only ' + str(message_count) + ' messages in this group chat')
            
    def getID(self, dude_name):
        for member in self.group.members:
            if member.nickname == dude_name:
                return member.user_id
        return dude_name
            
    def getName(self, dude_id):
        for member in self.group.members:
            if member.user_id == dude_id:
                return member.nickname
        return dude_id
            
    def getLikes(self, for_dude_id, from_dude_id):
        likes = 0
        for message in self.dudes[for_dude_id]:
            for like in self.dudes[for_dude_id][message]['likes']:
                if like == from_dude_id:
                    likes += 1
        return likes
    
    def getTotalLikes(self, dude_id):
        total_likes = 0
        for message in self.dudes[for_dude_id]:
            for like in self.dudes[for_dude_id][message]['likes']:
                total_likes += 1
        return total_likes
    
    def getWords(self, dude_id, word, case_sensitive = False):
        words = 0
        for message in self.dudes[dude_id]:
            if self.dudes[dude_id][message]['text'] != None:
                for text in self.dudes[dude_id][message]['text'].split():
                    if case_sensitive:
                        if text == word:
                            words += 1
                    else:
                        if text.lower() == word.lower():
                            words += 1
        return words

    def getKeywords(self, dude_id, keyword, case_sensitive = False):
        keywords = 0
        for message in self.dudes[dude_id]:
            if self.dudes[dude_id][message]['text'] != None:
                for text in self.dudes[dude_id][message]['text'].split():
                    if case_sensitive:
                        if keyword in text:
                            keywords += 1
                    else:
                        if keyword.lower() in text.lower():
                            keywords += 1
        return keywords

    def getDudeDict(self):
        return self.dudes
    
    def getDudeList(self):
        dude_list = []
        for dude in self.dudes:
            dude_list.append(dude);
        return dude_list
    
'''
sample code to make a rank list
a = AnalyzeMe(user stuff here)

rank_list = []
for dude in a.getDudeList():
    rank_list.append((dude, a.getKeywords(dude, 'the')))
print(rank_list)
rank_list.sort(key = lambda rank: rank[1], reverse = True)
print(rank_list)
rank_num = 1
for dude in rank_list:
    print(str(rank_num) + '. ' + a.getName(dude[0]) + ': ' + str(dude[1]))
    rank_num += 1
'''
