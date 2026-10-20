# Hmong ontology
# Original code Copyright © 2022 Nathan M. White

# Copyright notice
__copyright__ = "Copyright © 2022 Nathan M. White"

# author
__author__ = "Nathan M. White"
__author_email__ = "nathan.white1@jcu.edu.au"

import xml.etree.ElementTree as ET


class Sense:
    def __init__(self):
        self.meanings = []
        self.variants = []
        self.source = None
        self.category = None
    
    def assign_meaning(self, meaning_text):
        self.meanings.append(meaning_text)
    
    # TODO: need to protect self.category
    def assign_category(self, category_text):
        if self.category is None:
            self.category = category_text
            
    def __repr__(self):
        return "Sense('"+self.meanings[0].replace(' ', '_')+"-"+self.category+"')"
        

class Lemma:
    def __init__(self, text):
        self.text = text
        self.variants = []
        self.source = None
        self.senses = []
        
    def assign_sense(self, sense):
        self.senses.append(sense)
        
    def __repr__(self):
        return "Lemma('"+self.text.replace(' ', '_')+"')"


class Ontology:
    def __init__(self):
        self._load_ontology_data()

    def _load_ontology_data(self):
        self.tree = ET.parse('data/hmong_ontology.xml')
        word_set_idx = 3
        self.word_set = self.tree.getroot()[word_set_idx]

    def _get_lemma(self, word):
        word = word.replace(' ', '_')
        found_lemma = None
        for lemma in self.word_set.iter('lemma'):
            form = lemma[0]
            if form.text == word:
                found_lemma = lemma
        if found_lemma is None:
            return None
        
        lemma_iter = found_lemma.getiterator()
        lemma_obj = None
        lemma_sense = None
        current_sense = None
        for line in lemma_iter:
            if line.tag == 'form':
                lemma_obj = Lemma(line.text)
            # TODO: redo 'variant' and 'source' to handle 
            #     context-specific nesting
            elif line.tag == 'variant':
                lemma_obj.variants.append(line.text)
            elif line.tag == 'source':
                lemma_obj.source = line.text
            elif line.tag == 'sense':
                current_sense = Sense()
                lemma_obj.assign_sense(current_sense)
            elif line.tag == 'meaning':
                try:
                    current_sense.assign_meaning(line.text)
                except AttributeError:
                    print('Error: Meaning accessed before a sense was found.')
                    raise
            elif line.tag == 'category':
                try:
                    current_sense.assign_category(line.text)
                except AttributeError:
                    print('Error: Category accessed before a sense was found.')
                    raise
        return lemma_obj
                
    # TODO: determine whether this is viable as its own function
    #  or should be subsumed under sense_sets
    def lexname(self, word):
        lemma = self._get_lemma(word)
        if lemma == None:
            return []
        else:
            return [sense.category for sense in lemma.senses]

    def sense_sets(self, word):
        lemma = self._get_lemma(word)
        if lemma == None:
            return []
        else:
            return lemma.senses
