import re
import os
import sys
import json
import string
import warnings
import pendulum
import numpy as np

from copy import deepcopy
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from nltk.corpus import stopwords

warnings.filterwarnings(
    'ignore', category=MarkupResemblesLocatorWarning, module='bs4')

with open('../config/ignore_words.json', 'r') as ig:
    ignore_words = json.load(ig)


def convert_html_tags(cv_text):
    cv_list = cv_text.split(' ')
    goodwords = ''
    for cword in cv_list:
        tt = BeautifulSoup(cword, 'html.parser')
        BeautifulSoup()
        goodwords = goodwords + ' ' + str(tt)
    return (goodwords)


def fix_ts(dt_stamp):
    ts = pendulum.parse(str(dt_stamp)).to_rfc3339_string()
    return (str(ts))


def lcase_email(str_text):
    tmp_emails = []
    if type(str_text) == str:
        return (str_text.lower())
    else:
        for lce in str_text:
            tmp_emails.append(str(lce).lower())
        return (tmp_emails)


def find_urls(body_txt):
    urls = re.findall(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body_txt)
    return (urls)


def clean_body(body_txt, bodytype='body'):
    body_txt = convert_html_tags(body_txt)
    body_txt = remove_punct(body_txt)
    body_txt = body_txt.replace('\n', ' ')
    body_txt = body_txt.replace('\r', ' ').lower()
    body_txt = body_txt.replace(' zwnj ', ' ')
    body_txt = body_txt.replace('’', '')

    urls = find_urls(body_txt)  # remove urls, those are seperate field
    for url in urls:
        body_txt = body_txt.replace(url, ' ')

    body_list = body_txt.split()
    body_list = unique_words(body_list)
    body_copy = deepcopy(body_list)
    for each_word in body_copy:
        if each_word in body_list:
            each_word == make_ascii(each_word)
            if len(each_word) <= 2 or len(each_word) >= 20:
                body_list.remove(each_word)
                continue

            if each_word in stopwords.words('english'):
                body_list.remove(each_word)

            if each_word in ignore_words:
                body_list.remove(each_word)

    body_copy.clear()

    if len(body_list) <= 10 and bodytype == 'body':
        return None

    if len(body_list) <= 3 and bodytype == 'subject':
        return None

    body_txt = ' '.join(body_list)
    body_txt = ' '.join(body_txt.split()).lstrip()
    return (body_txt)


def unique_words(word_list):
    tmp_list = []
    for thatword in word_list:
        if thatword not in tmp_list:
            tmp_list.append(thatword)

    return (tmp_list)


def make_ascii(to_text):
    str_en = to_text.encode('ascii', 'ignore')
    return (str_en.decode())


def remove_punct(rptext):
    rptext = str(rptext).replace('.', ' ')
    rptext = rptext.translate(str.maketrans('', '', string.punctuation))
    return (rptext)

def merge_account_emails(acct_files):
    for user_id, ufiles in acct_files.items():
        msg_db = []
        clean_files = []
        for ifile in ufiles:
            print('opening file ' + ifile)
            clean_files.append(ifile)
            with open(ifile, 'r') as infile:
                msg_import = json.load(infile)
            msg_db.extend(msg_import)
            
    for rmfile in clean_files:
        print('removing ' + rmfile)
        os.remove(rmfile)
    return(msg_db)