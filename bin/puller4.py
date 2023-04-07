# import re
import os
import sys
import json
import datetime as dt


from jprint import jprint
from time import sleep
from threading import Thread
from Emailcrawler import Ecrawler
from email_corrector import merge_account_emails as emerge
from BayesClassifier import bayes_training as bayes

user_db = '../config/creds.json'
trained_db = '../config/trained_db.json'

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CWD = os.getcwd()
if SCRIPT_DIR != CWD:
    os.chdir(SCRIPT_DIR)


def get_users():
    with open(user_db, 'r') as cd:
        usersinfo = json.load(cd)
    return (usersinfo)


def get_trainings():

    if os.stat(trained_db).st_size == 0:
        return ({})

    with open(trained_db, 'r') as trd:
        trained_dict = json.load(trd)
    return (trained_dict)


def update_trainings(user_id, status_bool):

    try:
        with open(trained_db, 'r') as uptr:
            update_db = json.load(uptr)
    except json.decoder.JSONDecodeError:
        update_db = {}

    update_db[user_id] = status_bool

    with open(trained_db, 'w') as newtr:
        json.dump(update_db, newtr, indent=2, sort_keys=True)


def get_training_emails(imap_obj, trained_bool):

    if trained_bool == False:
        imap_obj.get_training()
    else:
        imap_obj.monitor_mailbox()


def main():
    users = get_users()
    train_dict = get_trainings()

    ithreads = []
    for user in users:
        user_files = {user['user_id']: []}
        musubi_id = user['user_id']

        try:
            train_bool = train_dict[user['user_id']]
        except KeyError:
            train_bool = False

        for account in user['accounts']:
            account['musubi_id'] = musubi_id
            imap_client = Ecrawler(account)
            user_files[user['user_id']].append(imap_client.get_filename())
            ithreads.append(Thread(target=get_training_emails,
                            args=[imap_client, train_bool]))

        for td in ithreads:
            if not td.is_alive():
                td.start()
                #print('started thread ' + td.getName())

        if train_bool == False:
            for tk in ithreads:
                #print('waiting for join ' + tk.getName())
                tk.join()

            account_emails = emerge(user_files)

            with open(f'../data/{musubi_id}.json', 'w') as ojson:
                json.dump(account_emails, ojson, indent=2)

            bayes(account_emails)
            update_trainings(user['user_id'], True)


if __name__ == main():
    main()
