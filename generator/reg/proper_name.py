__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 02/06/2017
Description:
    Proper name generation
"""

import cPickle as p
import sys
sys.path.append('../../')
from db.model import *
import nltk
import operator

class ProperNameTraining(object):
    def __init__(self):
        self.references = Reference.objects()

    def run_lm(self):
        self.trainset = {}
        self.trainset_backoff = {}
        for reference in self.references:
            text_status = reference.text_status
            entity = reference.entity.name

            for refex in reference.refexes:
                if refex.ref_type == u'name':
                    tokens = [u'START'] + nltk.word_tokenize(refex.refex) + [u'END']

                    bigrams = nltk.bigrams(tokens)
                    for bigram in bigrams:
                        n_tm1, n_t = bigram
                        if (text_status, entity, n_tm1) not in self.trainset:
                            self.trainset[(text_status, entity, n_tm1)] = []
                        if (entity, n_tm1) not in self.trainset_backoff:
                            self.trainset_backoff[(entity, n_tm1)] = []

                        self.trainset[(text_status, entity, n_tm1)].append(n_t)
                        self.trainset_backoff[(entity, n_tm1)].append(n_t)

        for key in self.trainset:
            self.trainset[key] = nltk.FreqDist(self.trainset[key])
            self.trainset[key] = sorted(self.trainset[key].items(), key=operator.itemgetter(1), reverse=True)[:3]

        for key in self.trainset_backoff:
            entity, n_tm1 = key
            self.trainset_backoff[(entity, n_tm1)] = nltk.FreqDist(self.trainset_backoff[(entity, n_tm1)])
            self.trainset_backoff[(entity, n_tm1)] = sorted(self.trainset_backoff[(entity, n_tm1)].items(), key=operator.itemgetter(1), reverse=True)[:3]

    def write(self):
        keys = sorted(self.trainset.keys(), key=lambda x: (x[0], x[1], x[2]))
        f = open('name_data/name_distribution.txt', 'w')
        for key in keys:
            entity, text_status, n_tm1 = key
            f.write(entity.encode('utf-8'))
            f.write('\t')
            f.write(text_status.encode('utf-8'))
            f.write('\t')
            f.write(n_tm1.encode('utf-8'))
            f.write('\n')

            for word in self.trainset[key]:
                f.write(word[0].encode('utf-8'))
                f.write('\t')
                f.write(str(word[1]))
                f.write('\n')
            f.write('\n')
        f.close()

        keys = sorted(self.trainset_backoff.keys(), key=lambda x: (x[0], x[1]))
        f = open('name_data/name_backoff_distribution.txt', 'w')
        for key in keys:
            entity, n_tm1 = key
            f.write(entity.encode('utf-8'))
            f.write('\t')
            f.write(n_tm1.encode('utf-8'))
            f.write('\n')

            for word in self.trainset_backoff[key]:
                f.write(word[0].encode('utf-8'))
                f.write('\t')
                f.write(str(word[1]))
                f.write('\n')
            f.write('\n')
        f.close()

    def write_pickle(self):
        p.dump(self.trainset, open('name_data/model.cPickle', 'w'))
        p.dump(self.trainset_backoff, open('name_data/backoff_model.cPickle', 'w'))

class ProperNameGeneration(object):
    def __init__(self):
        self.load_models()

    def load_models(self):
        self.model = p.load(open('reg/name_data/model.cPickle'))
        self.backoff = p.load(open('reg/name_data/backoff_model.cPickle'))

    def generate_major(self, reference, data):
        '''
        Generate based on result of reg_train.py script
        :param reference:
        :param data:
        :return:
        '''
        syntax = reference['syntax']
        text_status = reference['text_status']
        sentence_status = reference['sentence_status']
        entity = reference['entity'].name

        names = data[(syntax, text_status, sentence_status, entity)]
        if len(names) > 0:
            name = names[0][0]
        else:
            name = ' '.join(entity.replace('\'', '').replace('\"', '').split('_'))

        return name

    def generate(self, reference):
        text_status = reference['text_status']
        entity = reference['entity'].name
        n_tm1 = u'START'

        if (text_status, entity, n_tm1) in self.model:
            name, n_t = '', u'START'
            while n_t != 'END' and len(name.split()) < 8:
                name = name + n_t + ' '
                n_t = self.model[(text_status, entity, n_t)][0][0]
        elif (entity, n_tm1) in self.backoff:
            name, n_t = '', u'START'
            while n_t != 'END'  and len(name.split()) < 8:
                name = name + n_t + ' '
                n_t = self.backoff[(entity, n_t)][0][0]
        else:
            name = entity.replace('\"', '').replace('\'', '').replace('_', ' ')

        return name.replace(u'START', u'').strip()

if __name__ == '__main__':
    train = ProperNameTraining()
    train.run_lm()
    train.write_pickle()