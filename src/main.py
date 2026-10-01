from translator import EnglishIlokanoTranslator
import nltk
from tkinter import messagebox

class TranslationApp:
    def __init__(self):
        self.translator = EnglishIlokanoTranslator()
        self.word_translator = self  # Alias for GUI compatibility
        self._download_nltk_resources()

    def _download_nltk_resources(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')

    def translate(self, text):
        """Handle English to Ilokano translation"""
        return self.translator.translate(text)

    def lookup_word(self, word):
        """Dictionary lookup for English words"""
        return self.translator.lookup_word(word)

    # GUI-compatible methods
    def translate_words(self, words):
        text = ' '.join(words)
        translation, _, _ = self.translate(text)
        return translation.split()

    def lookup(self, word):
        return self.lookup_word(word)