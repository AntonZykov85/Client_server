from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from general.constants import *
import datetime

class ClientDB:
    class KnownUser:
        def __init__(self, user):
            self.id = None
            self.username = user

    class MessagesHistory:
        def __init__(self, sender, address, message):
            self.id = None
            self.sender = sender
            self.address = address
            self.message = message
            self.date = datetime.datetime.now()

    class ContactsList:
        def __init__(self, contact):
            self.id = None
            self.name = contact

    def __init__(self, name):
        self.database_engine = create_engine(f'sqlite:///client_{name}', echo=False, pool_recycle=7200, connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        users = Table('known_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String))

        history = Table('messages_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('from_user', String),
                        Column('to_user', String),
                        Column('message', Text),
                        Column('date', DateTime))

        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True))

        self.metadata.create_all(self.database_engine)


        mapper(self.KnownUser, users)
        mapper(self.MessagesHistory, history)
        mapper(self.ContactsList, contacts)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

    def add_contact(self, contact):
        if not self.session.query(self.ContactsList).filter_by(name=contact).count():
            contact_row = self.ContactsList(contact)
            self.session.add(contact_row)
            self.session.commit()

    def delete_contact(self, contact):
        self.session.query(self.ContactsList).filter_by(name=contact).delete()


    def add_users(self, users_list):
        self.session.query(self.KnownUser).delete()
        for user in users_list:
            user_row = self.KnownUser(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, from_user, to_user, message):
        message_row = self.MessagesHistory(from_user, to_user, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        return [contact[0] for contact in self.session.query(self.ContactsList.name).all()]

    def get_users(self):
        return [user[0] for user in self.session.query(self.KnownUser.username).all()]

    def check_user(self, user):
        if self.session.query(self.KnownUser).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        if self.session.query(self.ContactsList).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, from_who=None, to_who=None):
        query = self.session.query(self.MessagesHistory)
        if from_who:
            query = query.filter_by(from_user=from_who)
        if to_who:
            query = query.filter_by(to_user=to_who)
        return [(history_row.from_user, history_row.to_user, history_row.message, history_row.date)
                for history_row in query.all()]


if __name__ == '__main__':
    test_db = ClientDB('test1')
    for i in ['test3', 'test4', 'test5']:
        test_db.add_contact(i)
    test_db.add_contact('test4')
    test_db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    test_db.save_message('test1', 'test2', f'Test message from {datetime.datetime.now()}!')
    test_db.save_message('test2', 'test1', f'Test message from {datetime.datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('test1'))
    print(test_db.check_user('test10'))
    print(test_db.get_history('test2'))
    print(test_db.get_history(to_who='test2'))
    print(test_db.get_history('test3'))
    test_db.delete_contact('test4')
    print(test_db.get_contacts())
