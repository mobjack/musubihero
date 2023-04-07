import sys
import pickle
from jprint import jprint
from collections import defaultdict
from nltk import word_tokenize, FreqDist

from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer


class junknotjunk():
    def __init__(self, musubi_id):
        fileloc = f'../data/{musubi_id}'
        self.body_clf = f'{fileloc}_body.class.pkl'
        self.body_vect = f'{fileloc}_body.vector.pkl'
        self.body_nb = pickle.load(open(self.body_clf, 'rb'))
        self.body_vc = pickle.load(open(self.body_vect, 'rb'))

        self.from_clf = f'{fileloc}_from.class.pkl'
        self.from_vect = f'{fileloc}_from.vector.pkl'
        self.from_nb = pickle.load(open(self.from_clf, 'rb'))
        self.from_vc = pickle.load(open(self.from_vect, 'rb'))

        self.sub_clf = f'{fileloc}_subject.class.pkl'
        self.sub_vect = f'{fileloc}_subject.vector.pkl'
        self.sub_nb = pickle.load(open(self.sub_clf, 'rb'))
        self.sub_vc = pickle.load(open(self.sub_vect, 'rb'))

        self.urls_clf = f'{fileloc}_urls.class.pkl'
        self.urls_vect = f'{fileloc}_urls.vector.pkl'
        self.urls_nb = pickle.load(open(self.urls_clf, 'rb'))
        self.urls_vc = pickle.load(open(self.urls_vect, 'rb'))

    def get_junk_stats(self, email_dict):
        email_stats = {'body': 0, 'from': 0, 'sub': 0,
                       'urls': 0, 'total': 0, 'is_junk': False}

        if email_dict['body']:
            bodypred = self.body_nb.predict(
                self.body_vc.transform([email_dict['body']]))
            # if bodypred[0] == 'junk':
            if bodypred[0] == True:
                email_stats['body'] = 1
                email_stats['total'] += 1

        if email_dict['from']:
            frompred = self.from_nb.predict(
                self.from_vc.transform([email_dict['from']]))
            # if frompred[0] == 'junk':
            if frompred[0] == True:
                email_stats['from'] = 1
                email_stats['total'] += 1

        if email_dict['subject']:
            subpred = self.sub_nb.predict(
                self.sub_vc.transform([email_dict['subject']]))
            # if subpred[0] == 'junk':
            if subpred[0] == True:
                email_stats['sub'] = 1
                email_stats['total'] += 1

        if email_dict['urls']:
            url_score = 0
            for url in email_dict['urls']:
                urlspred = self.urls_nb.predict(self.urls_vc.transform([url]))

                if urlspred[0] == True:
                    url_score += 1

                if url_score >= 2:
                    email_stats['urls'] = 1
                    email_stats['total'] += 1
                    break

        if email_stats['total'] >= 2:
            email_stats['is_junk'] = True

        return (email_stats)


class bayes_training():
    def __init__(self, emails_listodict):
        self.musubi_id = emails_listodict[0]['aid']
        self.email_dict = emails_listodict
        self.email_parts = ['body', 'from', 'subject', 'urls']
        self.total_emails = len(self.email_dict)

        self.from_train_label = []
        self.from_train_data = []

        self.body_train_label = []
        self.body_train_data = []

        self.sub_train_label = []
        self.sub_train_data = []

        self.url_train_label = []
        self.url_train_data = []

        email_trk = 0
        for mail_data in self.email_dict:
            if len(mail_data['from']) > 0:
                self.from_train_label.append(mail_data['junk_bool'])
                self.from_train_data.append(mail_data['from'])

            if mail_data['body']:
                self.body_train_label.append(mail_data['junk_bool'])
                self.body_train_data.append(mail_data['body'])

            if mail_data['subject']:
                self.sub_train_label.append(mail_data['junk_bool'])
                self.sub_train_data.append(mail_data['subject'])

            if len(mail_data['urls']) > 0:
                for url in mail_data['urls']:
                    self.url_train_label.append(mail_data['junk_bool'])
                    self.url_train_data.append(url)

        self.train_classifier('body')
        self.train_classifier('subject')
        self.train_classifier('from')
        self.train_classifier('urls')

    def train_classifier(self, emailfield):
        if emailfield not in self.email_parts:
            raise ValueError(f'Error: {emailfield} not valid')
        # reqired_fields = ['body', 'subject', 'from']
        # if emailfield in reqired_fields:

        if emailfield == 'body':
            y_train_label = self.body_train_label
            X_train = self.body_train_data

        if emailfield == 'subject':
            y_train_label = self.sub_train_label
            X_train = self.sub_train_data

        if emailfield == 'from':
            y_train_label = self.from_train_label
            X_train = self.from_train_data

        # y_train_label = self.all_train_label

        if emailfield == 'urls':
            X_train = self.url_train_data
            y_train_label = self.url_train_label

        vectorizer = CountVectorizer(stop_words='english',
                                     ngram_range=(1, 3),
                                     min_df=3,
                                     analyzer='word')

        dtm = vectorizer.fit_transform(X_train)
        naive_bayes_classifier = MultinomialNB().fit(dtm, y_train_label)

        # store the classifier & vectorizer
        cls_filename = f'../data/{self.musubi_id}_{emailfield}.class.pkl'
        vect_filename = f'../data/{self.musubi_id}_{emailfield}.vector.pkl'

        pickle.dump(naive_bayes_classifier, open(cls_filename, 'wb'))
        pickle.dump(vectorizer, open(vect_filename, 'wb'))
