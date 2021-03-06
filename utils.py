import copy
import sys
sys.path.append('/home/tcastrof/workspace/stanford_corenlp_pywrapper')
from stanford_corenlp_pywrapper import CoreNLP

def get_topic(triples, entity_map):
    entity_map = entity2tag(entity_map)

    freq = dict(map(lambda x: (x, 0), entity_map.values()))
    for triple in triples:
        tag = entity_map[triple.agent.name]
        freq[tag] += 1

        tag = entity_map[triple.patient.name]
        freq[tag] += 1

    max_freq = max(freq.values())
    f = []
    for tag in freq:
        if freq[tag] == max_freq:
            f.append(tag)

    return sorted(f)[0]

# TO DO: bring entities with references
def map_entities(triples):
    entity_map, nagents, npatients, nbridges = {}, 1, 1, 1
    predicates = []
    for triple in triples:
        agent = triple.agent
        predicate = triple.predicate
        patient = triple.patient

        predicates.append(predicate)

        f = filter(lambda tag: entity_map[tag].name == agent.name and 'PATIENT' in tag, entity_map)
        if len(f) > 0:
            original_tag = f[0]
            original_id = int(original_tag.split('-')[1])
            new_tag = 'BRIDGE-' + str(nbridges)

            entity_map[str(new_tag)] = entity_map[str(original_tag)]
            del entity_map[str(original_tag)]

            nbridges += 1
            new_entity_map = {}
            for tag in entity_map.keys():
                role, id = tag.split('-')
                id = int(id)
                if role == 'PATIENT' and id > original_id:
                    new_entity_map[role+'-'+str(id-1)] = entity_map[str(tag)]
                else:
                    new_entity_map[str(tag)] = entity_map[str(tag)]
            entity_map = copy.deepcopy(new_entity_map)
            npatients -= 1
        elif agent.name not in map(lambda entity: entity.name, entity_map.values()):
            tag = 'AGENT-' + str(nagents)
            entity_map[str(tag)] = agent
            nagents += 1

        f = filter(lambda tag: entity_map[tag].name == patient.name and 'AGENT' in tag, entity_map)
        if len(f) > 0:
            original_tag = f[0]
            original_id = int(original_tag.split('-')[1])
            new_tag = 'BRIDGE-' + str(nbridges)

            entity_map[str(new_tag)] = entity_map[str(original_tag)]
            del entity_map[str(original_tag)]

            nbridges += 1
            new_entity_map = {}
            for tag in entity_map.keys():
                role, id = tag.split('-')
                id = int(id)
                if role == 'AGENT' and id > original_id:
                    new_entity_map[role+'-'+str(id-1)] = entity_map[str(tag)]
                else:
                    new_entity_map[str(tag)] = entity_map[str(tag)]
            entity_map = copy.deepcopy(new_entity_map)
            nagents -= 1
        elif patient.name not in map(lambda entity: entity.name, entity_map.values()):
            tag = 'PATIENT-' + str(npatients)
            entity_map[str(tag)] = patient
            npatients += 1
    return entity_map, predicates

def entity2tag(entity_map):
    return dict(map(lambda x: (x[1].name, x[0]), entity_map.items()))

def get_e2f(fname):
    f = open(fname)
    doc = f.read().split('\n')
    f.close()

    e2f = {}
    for row in doc:
        aux = row.split()
        if len(aux) == 3:
            wiki, word, prob = aux

            if wiki not in e2f:
                e2f[wiki] = {}

            e2f[wiki][word] = float(prob)
    return e2f

def write_references(fname, refs):
    proc = CoreNLP('ssplit')

    f1 = open(fname+'1', 'w')
    f2 = open(fname+'2', 'w')
    f3 = open(fname+'3', 'w')
    f4 = open(fname+'4', 'w')
    f5 = open(fname+'5', 'w')
    f6 = open(fname+'6', 'w')
    f7 = open(fname+'7', 'w')

    for references in refs:
        out = proc.parse_doc(references[0].lower())
        text = ''
        for snt in out['sentences']:
            text += ' '.join(snt['tokens']).replace('-LRB-', '(').replace('-RRB-', ')')
            text += ' '

        f1.write(text.encode('utf-8'))
        f1.write('\n')

        if len(references) >= 2:
            out = proc.parse_doc(references[1].lower())
            text = ''
            for snt in out['sentences']:
                text += ' '.join(snt['tokens']).replace('-LRB-', '(').replace('-RRB-', ')')
                text += ' '

            f2.write(text.encode('utf-8'))
        f2.write('\n')

        if len(references) >= 3:
            out = proc.parse_doc(references[2].lower())
            text = ''
            for snt in out['sentences']:
                text += ' '.join(snt['tokens']).replace('-LRB-', '(').replace('-RRB-', ')')
                text += ' '
            f3.write(text.encode('utf-8'))
        f3.write('\n')

        if len(references) >= 4:
            out = proc.parse_doc(references[3].lower())
            text = ''
            for snt in out['sentences']:
                text += ' '.join(snt['tokens']).replace('-LRB-', '(').replace('-RRB-', ')')
                text += ' '
            f4.write(text.encode('utf-8'))
        f4.write('\n')

        if len(references) >= 5:
            out = proc.parse_doc(references[4].lower())
            text = ''
            for snt in out['sentences']:
                text += ' '.join(snt['tokens']).replace('-LRB-', '(').replace('-RRB-', ')')
                text += ' '
            f5.write(text.encode('utf-8'))
        f5.write('\n')

        if len(references) >= 6:
            out = proc.parse_doc(references[5].lower())
            text = ''
            for snt in out['sentences']:
                text += ' '.join(snt['tokens']).replace('-LRB-', '(').replace('-RRB-', ')')
                text += ' '
            f6.write(text.encode('utf-8'))
        f6.write('\n')

        if len(references) >= 7:
            out = proc.parse_doc(references[6].lower())
            text = ''
            for snt in out['sentences']:
                text += ' '.join(snt['tokens']).replace('-LRB-', '(').replace('-RRB-', ')')
                text += ' '
            f7.write(text.encode('utf-8'))
        f7.write('\n')

    f1.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()
    f6.close()
    f7.close()

def write_hyps(fname, hyps):
    f = open(fname, 'w')
    for hyp in hyps:
        f.write(hyp.lower().encode('utf-8'))
        f.write('\n')
    f.close()