# F1 : 86.6%
# model : https://github.com/undertheseanlp/ner
from underthesea import ner
from itertools import tee, islice, chain
import io

def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

# return sentence with NER
def ner_sentence(text):
    entity_key_B = ['B-LOC', 'B-PER', 'B-ORG']
    entity_key_I = ['I-LOC', 'I-PER', 'I-ORG']
    entity_key = ['LOC', 'PER', 'ORG']

    new_text = ''
    entity_merge = ['', -1] # word_to_merge, position in enity_key

    for pre_word, word, nxt_word in previous_and_next(ner(text)):
        if word[-1] != 'O':
            if (word[-1] in entity_key_I) and (entity_key_I.index(word[-1]) == entity_merge[1]): # check if entity if I-entity and the same entity type            
                entity_merge[0] += word[0] + ' '
            elif word[-1] in entity_key_B:
                entity_merge = [word[0] + ' ', entity_key_B.index(word[-1])]
            
            if(nxt_word != None):
                # check if next word is I, if true continue
                if (nxt_word[-1] in entity_key_I) and (entity_key_I.index(nxt_word[-1]) == entity_merge[1]):
                    continue
                else: 
                    # rstrip to remove space at the end of str
                    new_text += '<' + entity_key[entity_merge[1]] + '>' + entity_merge[0].rstrip() + '</' + entity_key[entity_merge[1]] + '> ' 
                    entity_merge = ['', -1]
                    continue
            else:
                # if next word is None which means there're no word left, concatenate text
                new_text += '<' + entity_key[entity_merge[1]] + '>' + entity_merge[0].rstrip() + '</' + entity_key[entity_merge[1]] + '> '
                entity_merge = ['', -1]

        if word[-1] == 'O':
            # check if there're B-entity
            if(entity_merge[0] != ''):
                new_text += '<' + entity_key[entity_merge[1]] + '>' + entity_merge[0].rstrip() + '</' + entity_key[entity_merge[1]] + '> '
                entity_merge = ['', -1]
            new_text += word[0] + ' '
    return new_text


# write ner result to file
ner_sentence_lst = []
with io.open("corpus-full.txt", "r", encoding="utf-8") as data_file:
    ner_sentence_lst = map(ner_sentence, data_file.readlines())
    data_file.close()

with io.open("NER_corpus.txt", "w", encoding="utf-8") as ner_file:
    for sentence in ner_sentence_lst:
        ner_file.write(sentence + "\n")
    ner_file.close()

