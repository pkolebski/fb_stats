from collections import Counter, defaultdict
from utils import decode
import datetime
import os
from tqdm import tqdm
import json


class Message:
    def __init__(self):
        self.content = None
        self.author = None
        self.date = None
        self.type = None
        self.photos = None
        self.reactions = defaultdict(list)

    def __str__(self):
        return f'({self.timestamp}) {self.author}: {self.content}'


class Conversation:
    def __init__(self, data):
        self.participants = self.load_participants(data)
        self.messages = self.load_messages(data)
        self.title = decode(data['title'])
        self.thread_type = 'Group' if data['thread_type'] == 'RegularGroup' else data['thread_type']
        self.is_still_participant = data['is_still_participant']

    def __str__(self):
        return f'title: {self.title}; messages: {len(self)}'

    def __len__(self):
        return len(self.messages)

    def get_messages_number_by_name(self, name):
        return len([m for m in self.messages if m.author == name])

    def get_spammers_ranking(self, top=3):
        ret = {}
        count = Counter([msg.author for msg in self.messages]).most_common()
        i = 0
        last = 1e1000
        for k, v in count:
            if i >= top: break
            if i > 0:
                if v != last:
                    i += 1
            else:
                i += 1
            last = v
            ret[k] = [i, v]
        return ret

    def get_hours(self, since=datetime.datetime(2005, 1, 1), to=datetime.datetime.now()):
        assert type(since) in [datetime.datetime, list] and type(to) in [datetime.datetime, list], "'since' and 'to' should be list or datetime"
        if type(since) is list:
            since = datetime.datetime(*since)
        if type(to) is list:
            to = datetime.datetime(*to)
        period = since - to
        hours = []
        days = []
        months = []
        years = []
        for msg in self.messages:
            if since > msg.date > to:
                days.append(msg.date.weekday())
                hours.append(int(msg.date.strftime('%H')) + int(msg.date.strftime('%m')) / 60.)
        return hours, days

    @staticmethod
    def load_participants(conv):
        parts = []
        for i in conv['participants']:
            parts.append(decode(i['name']))
        return parts

    @staticmethod
    def load_messages(conv):
        messages = []
        for message in conv['messages']:
            msg = Message()
            if 'content' in message.keys():
                msg.content = decode(message['content'])
            if 'sender_name' in message.keys():
                msg.author = decode(message['sender_name'])
            if 'timestamp_ms' in message.keys():
                msg.date = datetime.datetime.fromtimestamp(message['timestamp_ms'] / 1000.0)
            if 'type' in message.keys():
                msg.type = decode(message['type'])
            if 'photos' in message.keys():
                msg.photos = [photo['uri'] for photo in message['photos']]
            if 'reactions' in message.keys():
                for reaction in message['reactions']:
                    msg.reactions[decode(reaction['reaction'])].append(reaction['actor'])
            messages.append(msg)
        return messages


def load_coversations(path):
    conversations = []
    for f in tqdm(os.listdir(path)):
        with open(f'{path}/{f}/message_1.json') as file:
            conv = Conversation(json.loads(file.read()))
            conversations.append(conv)
    return conversations