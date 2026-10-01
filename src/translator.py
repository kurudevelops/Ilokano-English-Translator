import nltk
from nltk import CFG, ChartParser
from nltk.tokenize import word_tokenize
import json
from pathlib import Path


class EnglishIlokanoTranslator:
    def __init__(self):
        self._load_resources()
        self._download_nltk_resources()

    def _load_resources(self):
        """Load all required resources"""
        self._load_grammars()
        self._load_dictionary()
        self._load_special_cases()

    def _load_grammars(self):
        """Load CFG from external files"""
        try:
            with open('data/english_CFG.txt', 'r') as f:
                english_cfg = CFG.fromstring(f.read())
            with open('data/ilokano_CFG.txt', 'r') as f:
                ilokano_cfg = CFG.fromstring(f.read())

            self.english_parser = ChartParser(english_cfg)
            self.ilokano_parser = ChartParser(ilokano_cfg)
        except Exception as e:
            raise Exception(f"Error loading grammars: {str(e)}")

    def _load_dictionary(self):
        """Load dictionary from JSON"""
        try:
            with open('data/dictionary.json', 'r') as f:
                self.dictionary = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading dictionary: {str(e)}")

    def _load_special_cases(self):
        """Load special case translations"""
        self.common_phrases = {
            'how are you': 'kumusta ka',
            'thank you': 'agyaman',
            'i love you': 'ay-ayaten ka',
            'good morning': 'naimbag a bigat',
            'good night': 'naimbag a rabii',
            'just a moment' :'mabiit laeng'
        }

        self.time_expressions = {
            'now': 'ita',
            'today': 'ita nga aldaw',
            'tomorrow': 'inton bigat',
            'yesterday': 'idi kalman',
            'later': 'inton agangay'
        }

        self.irregular_verbs = {
            'eat': ('mangan', 'nangan', 'mangan'),
            'go': ('pumanaw', 'pimmanaw', 'pumanaw'),
            'see': ('kita', 'nakita', 'kitaen'),
            'give': ('ited', 'inited', 'ited')
        }

    def _download_nltk_resources(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')

    # Core translation methods
    def translate(self, text):
        """Enhanced translation with multiple fallback levels"""
        try:
            text = text.strip()
            if not text:
                return "", None, None

            # Level 1: Check common phrases
            if common := self._check_common_phrases(text):
                return common, None, None

            # Level 2: Full grammar analysis
            pos_tags, parse_tree = self.analyze_sentence(text)

            # Level 3: Structure-aware translation
            if parse_tree:
                translation = self.translate_structure(pos_tags, parse_tree)
                if translation:
                    return translation, pos_tags, parse_tree

            # Level 4: POS-based fallback translation
            if pos_tags:
                translation = self._pos_based_translation(pos_tags)
                if translation:
                    return translation, pos_tags, "Fallback POS analysis"

            # Level 5: Final word-by-word fallback
            return self._fallback_translation(text), None, None

        except Exception as e:
            print(f"Translation error: {e}")
            return self._fallback_translation(text), None, None

    def _pos_based_translation(self, pos_tags):
        """Translation using POS tags without full parse"""
        translated = []
        for word, tag in pos_tags:
            if tag.startswith('VB'):  # Verb
                translated.append(self._conjugate_verb(word, tag))
            elif tag in ['PRP', 'PRP$']:  # Pronoun
                translated.append(self._translate_pronoun(word))
            elif tag.startswith('NN'):  # Noun
                translated.append('ti ' + self._translate_word(word))
            else:
                translated.append(self._translate_word(word))

        # Basic VSO reordering if we have a verb
        if any(tag.startswith('VB') for word, tag in pos_tags):
            return self._reorder_to_vso(translated, pos_tags)
        return ' '.join(translated)

    def _reorder_to_vso(self, words, pos_tags):
        """Attempt basic VSO reordering"""
        verbs = [i for i, (word, tag) in enumerate(pos_tags) if tag.startswith('VB')]
        if verbs:
            # Move first verb to front
            verb_index = verbs[0]
            verb = words.pop(verb_index)
            words.insert(0, verb)
        return ' '.join(words)

    def analyze_sentence(self, text):
        """Enhanced sentence analysis with fallback"""
        try:
            tokens = word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)

            # First try parsing with full grammar
            try:
                trees = list(self.english_parser.parse(tokens))
                parse_tree = str(trees[0]) if trees else None
                return pos_tags, parse_tree
            except ValueError as e:
                # Grammar doesn't cover all words - use fallback analysis
                print(f"Grammar warning: {str(e)}")
                return self._fallback_analysis(tokens, pos_tags)

        except Exception as e:
            print(f"Analysis error: {e}")
            return None, None

    def _fallback_analysis(self, tokens, pos_tags):
        """Fallback analysis when grammar doesn't cover all words"""
        # Create a minimal parse tree structure
        parse_tree = "(S "
        for word, tag in pos_tags:
            # Convert tags to simpler categories
            if tag.startswith('VB'):
                parse_tree += "(V " + word + ") "
            elif tag in ['PRP', 'PRP$']:
                parse_tree += "(PP " + word + ") "
            elif tag.startswith('NN'):
                parse_tree += "(N " + word + ") "
            elif tag.startswith('JJ'):
                parse_tree += "(Adj " + word + ") "
            elif tag.startswith('RB'):
                parse_tree += "(Adv " + word + ") "
            else:
                parse_tree += "(X " + word + ") "  # Unknown category

        parse_tree += ")"
        return pos_tags, parse_tree

    # Structure-based translation methods
    def translate_structure(self, pos_tags, parse_tree):
        """Route to appropriate translator based on sentence type"""
        if not pos_tags:
            return ""

        sentence_type = self._identify_sentence_type(pos_tags)

        if sentence_type == 'question':
            return self._translate_question(pos_tags)
        elif sentence_type == 'negative':
            return self._translate_negative(pos_tags)
        elif sentence_type == 'imperative':
            return self._translate_imperative(pos_tags)
        else:
            return self._translate_declarative(pos_tags)

    def _identify_sentence_type(self, pos_tags):
        """Determine sentence type from POS tags"""
        words = [word.lower() for word, tag in pos_tags]
        tags = [tag for word, tag in pos_tags]

        # Check for questions
        if any(word in ['what', 'where', 'when', 'why', 'how'] for word in words[:2]):
            return 'question'

        # Check for imperatives
        if tags[0] == 'VB' and words[0] not in ['do', 'have', 'be']:
            return 'imperative'

        # Check for negatives
        if 'not' in words or any(x in ["don't", "doesn't", "didn't"] for x in words):
            return 'negative'

        return 'declarative'

    # Specific structure translators
    def _translate_declarative(self, pos_tags):
        """Translate simple declarative sentences"""
        components = {'subject': None, 'verb': None, 'object': None}

        for word, tag in pos_tags:
            if tag in ['PRP', 'PRP$']:
                components['subject'] = self._translate_pronoun(word)
            elif tag.startswith('VB'):
                components['verb'] = self._conjugate_verb(word, tag)
            elif tag in ['NN', 'NNS']:
                components['object'] = self._translate_word(word)

        # Build Ilokano VSO structure
        translated = []
        if components['verb'] and components['subject']:
            # Combine verb with subject enclitic
            verb_root = components['verb']
            subject = components['subject']

            if subject == 'siak':  # I
                translated.append(verb_root + 'ak')
            elif subject == 'sika':  # you (singular)
                translated.append(verb_root + 'ka')
            elif subject == 'isuna':  # he/she
                translated.append(verb_root + 'na')
            elif subject == 'datayo':  # we (inclusive)
                translated.append(verb_root + 'tayo')
            elif subject == 'dakami':  # we (exclusive)
                translated.append(verb_root + 'kami')
            elif subject == 'isuda':  # they
                translated.append(verb_root + 'da')

            if components['object']:
                translated.append('ti ' + components['object'])

        return ' '.join(translated)

    def _translate_question(self, pos_tags):
        """Translate question structures"""
        wh_word = None
        verb = None
        subject = None

        for word, tag in pos_tags:
            if tag == 'WRB':
                wh_word = self._translate_question_word(word)
            elif tag.startswith('VB'):
                verb = self._conjugate_verb(word, tag, mood='question')
            elif tag in ['PRP', 'PRP$']:
                subject = self._translate_pronoun(word)

        # Build question structure
        translated = []
        if wh_word:
            translated.append(wh_word)
            if verb and subject:
                translated.append(verb + subject[-2:])  # Add pronoun suffix
        elif verb == 'is':  # Yes/no questions
            translated.append(verb)
            if subject:
                translated.append(subject)

        return ' '.join(translated)

    def _translate_negative(self, pos_tags):
        """Handle negative constructions"""
        translated = ['haan']  # Start with negation marker
        subject = None
        verb = None

        for word, tag in pos_tags:
            if word.lower() in ['not', "don't", "doesn't", "didn't"]:
                continue  # Already handled
            elif tag in ['PRP', 'PRP$']:
                subject = self._translate_pronoun(word)
            elif tag.startswith('VB'):
                verb = self._conjugate_verb(word, tag)

        if subject:
            translated.append(subject[-2:])  # Add pronoun enclitic
        if verb:
            translated.append(verb)

        return ' '.join(translated)

    def _translate_imperative(self, pos_tags):
        """Translate commands"""
        verb = None
        pronoun = None

        for word, tag in pos_tags:
            if tag.startswith('VB') and not verb:
                verb = self._conjugate_verb(word, tag, mood='imperative')
            elif tag == 'PRP':
                pronoun = self._translate_pronoun(word)

        translated = []
        if verb:
            translated.append(verb)
            if pronoun:
                # Add pronoun enclitic
                if pronoun == 'sika':  # you
                    translated.append('ka')
                elif pronoun == 'dakayo':  # you (plural)
                    translated.append('kayo')

        return ' '.join(translated)

    # Helper methods
    def _translate_word(self, word):
        """Basic word translation"""
        return self.dictionary.get('english_to_ilokano', {}).get(word.lower(), word)

    def _translate_pronoun(self, pronoun):
        """Pronoun translation with case handling"""
        pronoun = pronoun.lower()
        mapping = {
            'i': 'siak',
            'me': 'kaniak',
            'my': 'kukuak',
            'you': 'sika',  # singular
            'your': 'mo',  # singular
            'he': 'isuna',
            'him': 'kenkuana',
            'his': 'kuana',
            'she': 'isuna',
            'her': 'kenkuana',
            'we': 'datayo',  # inclusive
            'us': 'kadakuami',
            'they': 'isuda',
            'them': 'kadakuada',
            'their': 'da'
        }
        return mapping.get(pronoun, pronoun)

    def _conjugate_verb(self, verb, english_tag, mood='declarative'):
        """Conjugate English verbs to Ilokano"""
        verb = verb.lower()
        base = self._translate_word(verb)

        # Check irregular verbs first
        if verb in self.irregular_verbs:
            present, past, future = self.irregular_verbs[verb]
            if english_tag == 'VBD':  # Past tense
                return past
            return present

        # Regular verb conjugation
        if mood == 'imperative':
            return base
        elif english_tag == 'VBD':  # Past tense
            return 'nag' + base
        elif mood == 'question':
            return 'aga' + base
        else:  # Present/future
            return 'ag' + base

    def _translate_question_word(self, word):
        """Translate question words"""
        question_words = {
            'what': 'ania',
            'where': 'ayanna',
            'when': 'kaano',
            'why': 'apay',
            'how': 'kasano',
            'who': 'siasino'
        }
        return question_words.get(word.lower(), word)

    def _check_common_phrases(self, text):
        """Check for fixed expressions"""
        text_lower = text.lower()
        return self.common_phrases.get(text_lower, None)

    def _fallback_translation(self, text):
        """Word-by-word fallback"""
        tokens = word_tokenize(text.lower())
        return ' '.join([self._translate_word(word) for word in tokens])

    # Dictionary lookup for GUI
    def lookup_word(self, word):
        """Word lookup for dictionary feature"""
        word = word.lower().strip()
        if word in self.dictionary.get('english_to_ilokano', {}):
            return self.dictionary['english_to_ilokano'][word], "ENGLISH_TO_ILOKANO"
        return "Word not found", "UNKNOWN"