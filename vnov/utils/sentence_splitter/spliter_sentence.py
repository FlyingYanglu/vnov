import os
import spacy

class Spliter:
    def __init__(self, language='en', max_length=100, min_length=40, hard_max_length=150):
        # Initialize the appropriate SpaCy model
        if language == 'en':
            self.nlp = spacy.load("en_core_web_sm")
        elif language == 'zh':
            self.nlp = spacy.load("zh_core_web_sm")
        else:
            raise ValueError("Language must be either 'en' or 'zh'.")
        self.max_length = max_length
        self.min_length = min_length
        self.hard_max_length = hard_max_length

    def cut_to_sentences(self, text):
        # Use SpaCy to split sentences
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        # Refine sentences based on length constraints
        return self.refine_sentences(sentences)

    def refine_sentences(self, sentences):
        refined = []
        buffer = ""

        for sentence in sentences:
            if self.min_length <= len(sentence) <= self.max_length:
                # Sentence is within acceptable bounds
                if buffer:
                    refined.append(buffer.strip())
                    buffer = ""
                refined.append(sentence)
            elif len(sentence) > self.max_length:
                # Sentence is too long; split it
                refined.extend(self.split_long_sentence(sentence))
            else:
                # Sentence is too short; buffer it
                if buffer:
                    sentence = buffer + " " + sentence
                    buffer = ""
                if len(sentence) >= self.min_length:
                    refined.append(sentence)
                else:
                    buffer = sentence

        # Append any remaining buffered sentence
        if buffer:
            refined.append(buffer.strip())
        return refined

    def split_long_sentence(self, sentence):
        # Split a long sentence into parts respecting the hard max length
        parts = []
        while len(sentence) > self.hard_max_length:
            part = sentence[:self.hard_max_length]
            sentence = sentence[self.hard_max_length:]
            parts.append(part.strip())
        if sentence:
            parts.append(sentence.strip())
        return parts