
import json

from jprint import jprint
from BayesClassifier import bayes_training

#training_json = '../data/m23462113.json'
training_json = '../data/parkertest.json'


def main():
    with open(training_json, 'r') as jt:
        training_emails = json.load(jt)

    # print_freqency_dist(training_emails, train_type='body')
    bae_train = bayes_training(training_emails)

if __name__ == main():
    main()
