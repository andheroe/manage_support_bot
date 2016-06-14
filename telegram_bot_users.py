__author__ = 'andheroe'

import simplejson

class User(object):

    chat_id = None

    def __init__(self, chat_id):
        self.chat_id = chat_id

class TeamUser(User):

    def __init__(self, chat_id):
        super(TeamUser, self).__init__(chat_id)

class UserList(object):

    def __init__(self):
        try:
            self.load_from_file()
        except:
            self.lst = []

    def __contains__(self, key):
        return key in [user.chat_id for user in self.lst]

    def __iter__(self):
        return iter(self.lst)

    def check_type(self, obj):
        pass

    def save_to_file(self):
        pass

    def load_from_file(self):
        pass

    def add(self, user):
        self.check_type(user)
        self.lst.append(user)
        self.save_to_file()

    def remove_by_chat_id(self, chat_id):
        self.lst = [user for user in self.lst if user.chat_id != chat_id]
        self.save_to_file()

    def get_by_chat_id(self, chat_id):
        filtered_list = [user for user in self.lst if user.chat_id == chat_id]
        return filtered_list[0] if 0 < len(filtered_list) else None

class TeamUserList(UserList):

    lst = []
    filename = 'telebot_users.json'

    def __init__(self):
        super(TeamUserList, self).__init__()

    def check_type(self, obj):
        if obj.__class__.__name__ != 'TeamUser':
            raise Exception('TeamUsersList can save only TeamUser type objects')

    def save_to_file(self):
        simplejson.dump([user.chat_id for user in self.lst], open(self.filename, 'w'))

    def load_from_file(self):
        lst = simplejson.load(open(self.filename, 'r'))
        for chat_id in lst:
            self.lst.append(TeamUser(chat_id))