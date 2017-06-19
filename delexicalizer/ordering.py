__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 15/06/2017
Description:
    Sentence segmentation and discourse ordering
"""

import copy
import json
import re
import sys
sys.path.append('../')
from db.model import *
sys.path.append('/home/tcastrof/workspace/stanford_corenlp_pywrapper')
from stanford_corenlp_pywrapper import CoreNLP
import utils

class Ordering(object):
    def __init__(self):
        self.proc = CoreNLP('ssplit')

    def check_tagfrequency(self, entitymap, template):
        tag_freq = {}
        for tag, entity in entitymap.items():
            tag_freq[tag] = re.findall(tag, template)

        if 0 not in tag_freq.values():
            return True
        return False

    # Fixing the tags for the correct order
    def generate_template(self, triples, template, entitymap):
        new_entitymap, predicates = utils.map_entities(triples)
        new_entitymap = dict(map(lambda x: (x[1], x[0]), new_entitymap.items()))
        new_template = []
        for token in template:
            if token in entitymap:
                new_template.append(new_entitymap[entitymap[token]])
            else:
                new_template.append(token)
        return ' '.join(new_template).replace('-LRB-', '(').replace('-RRB-', ')').strip()

    def process(self, entry):
        self.entry = entry
        entitymap, predicates = utils.map_entities(self.entry.triples)

        training_set = []
        for lex in self.entry.texts:
            template = lex.template

            if self.check_tagfrequency(entitymap, template):
                sort_triples, triples = [], copy.deepcopy(entry.triples)
                out = self.proc.parse_doc(template)

                prev_tags = []
                for i, snt in enumerate(out['sentences']):
                    tags = []

                    # get tags in order
                    for token in snt['tokens']:
                        if token in entitymap:
                            tags.append(token)

                    # Ordering the triples in the sentence i
                    sort_snt_triples, triples = self.order(triples, entitymap, prev_tags, tags)
                    sort_triples.extend(sort_snt_triples)

                # Extract template for the sentence
                if len(triples) == 0:
                    template = []
                    for snt in out['sentences']:
                        template.extend(snt['tokens'])
                    template = self.generate_template(sort_triples, template, entitymap)
                    training_set.append({'sorted_triples':sort_triples, 'triples':entry.triples, 'template':template})
        return training_set

    def order(self, triples, entitymap, prev_tags, tags):
        triples_sorted = []
        for i in range(1, len(tags)):
            tag = tags[i]
            prev_tags.insert(0, tags[i-1])

            for prev_tag in prev_tags:
                if 'AGENT' in tag and 'PATIENT' in prev_tag:
                    f = filter(lambda triple: triple.agent.name == entitymap[tag] and triple.patient.name == entitymap[prev_tag], triples)
                elif 'PATIENT' in tag and 'AGENT' in prev_tag:
                    f = filter(lambda triple: triple.patient.name == entitymap[tag] and triple.agent.name == entitymap[prev_tag], triples)
                else:
                    f = filter(lambda triple: (triple.agent.name == entitymap[tag] and triple.patient.name == entitymap[prev_tag]) or
                                              (triple.patient.name == entitymap[tag] and triple.agent.name == entitymap[prev_tag]), triples)

                if len(f) > 0:
                    triples_sorted.append(f[0])
                    triples = filter(lambda triple: triple != f[0], triples)
                    break
        return triples_sorted, triples

    def write(self, trainingset):
        result = []

        for row in trainingset:
            triples, sorted_triples, template = row['triples'], row['sorted_triples'], row['template']

            row['triples'] = map(lambda triple: triple.agent.name + ' | ' + triple.predicate.name + ' | ' + triple.patient.name, row['triples'])

            row['sorted_triples'] = map(lambda triple: triple.agent.name + ' | ' + triple.predicate.name + ' | ' + triple.patient.name, row['sorted_triples'])

            result.append({'triples':row['triples'], 'sorted':row['sorted_triples']})

            print triples
            print sorted_triples
            print template
            print 10 * '-'

        json.dump(result, open('train_order.json', 'w'), indent=4, separators=(',', ': '))

if __name__ == '__main__':
    ordering = Ordering()

    training = []
    entries = Entry.objects(set='train')
    # entries = Entry.objects(set='train', size=4, category='Building')

    for entry in entries:
        result = ordering.process(entry)
        training.extend(result)

    ordering.write(training)