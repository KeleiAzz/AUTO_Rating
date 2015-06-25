import re

class HitChecker:

    protected_words_mapping_list = [
        ["Inc.", "PROTECTEDINC"],
        ["Corp.",  "PROTECTEDCORP"],
        ["Dec.", "PROTECTEDDEC"],
        ["A. O. Smith", "PROTECTEDAOSMITH"],
        ["Nov.", "PROTECTEDNOV"],
        ["Oct.", "PROTECTEDOCT"],
        ["Sept.", "PROTECTEDSEPT"],
        ["Sep.", "PROTECTEDSEP"],
        ["Aug.", "PROTECTEDAUG"],
        ["Jan.", "PROTECTEDJAN"],
        ["Feb.", "PROTECTEDFEB"],
        ["Ltd.", "PROTECTEDLTD"],
        ["Co.", "PROTECTEDCO"],
        ["St. Vincent Health", "PROTECTEDSTVINCENTHEALTH"],
        ["vs.", "PROTECTEDVS"],
        ["Mr.", "PROTECTEDMR"],
        ["Ms.", "PROTECTEDMS"],
        ["U. S.", "PROTECTEDUSPACES"],
        ["U.S.", "PROTECTEDUS"],
        ["St. Simons Island", "PROTECTEDSTSIMONSISLAND"],
    ]

    def __init__(self):
        self.index = []
        self.keywords = []
        self.original_sentenses = []
        self.processed_sentense = []
        self.processed_content = ''

    # def __init__(self, ):

    def hit_check(self, content, keywords, flag, num_sentence):
        content = self.remove_short_and_long_lines(content)

        self.split_sentence_merge_split(content)
        self.get_quotted_content()
        self.remove_short_and_long_sentencs()
        self.pre_process()
        self.find_hits(flag, num_sentence)


    def remove_short_and_long_lines(self, content):
        if content is None or len(content) == 0:
            return ""

        temp_sentence = re.split('\r\n|\n|\r', content)

        merged = ''
        temp = ''

        for sentence in temp_sentence:
            temp_size = len(sentence)
            while True:
                sentence = sentence.replace('  ', ' ')
                if len(sentence) == temp_size:
                    break
                else:
                    temp_size = len(sentence)

            # size = len(temp_sentence[i])
            splited_word = sentence.split()
            if len(splited_word) <= 4:
                pass
            else:
                merged += sentence + ' '

        return merged

    def split_sentence_merge_split(self, content):
        if content is None or len(content.strip()) == 0:
            return None
        content = content.replace('\r', ' ').replace('\n', ' ')

        content = self.protect_special_words(content)

        temp_sentence = re.split('\\. |\\. |\r\n|\r|\n|! |\\? ', content)

        for i in range(len(temp_sentence)):
            temp_sentence[i] = temp_sentence[i].strip() + '.'

        for i in range(len(temp_sentence)):
            temp_sentence[i] = HitChecker.release_protection(temp_sentence[i])

        for s in temp_sentence:
            self.original_sentenses.append(s)

    def get_quotted_content(self):
        index_of_quotes = []
        for idx, s in enumerate(self.original_sentenses):
            if '\"' in s or '“' in s or '”'in s:
                for i in range(len(s)):
                    if s[i] == '\"' or s[i] == '”' or s[i] == '“':
                        index_of_quotes.append(i)
                # Remove the sentense if it contains odd number of quotes
                if len(index_of_quotes) % 2 == 1:
                    self.original_sentenses[idx] = ''
                    index_of_quotes = []
                    continue
                largest_length = 0
                recorder_of_start_quote_index = -1
                for i in range(len(index_of_quotes)-1):
                    if index_of_quotes[i+1] - index_of_quotes[i] >= largest_length:
                        largest_length = index_of_quotes[i+1] - index_of_quotes[i]
                        recorder_of_start_quote_index = i

                start = index_of_quotes[recorder_of_start_quote_index]
                end = index_of_quotes[recorder_of_start_quote_index+1]

                if start + 1 < end -1:
                    temp_string = self.original_sentenses[idx][start+1:end]
                else: temp_string = ''
                if len(temp_string) > 0 and temp_string[-1] != '.':
                    import string
                    if temp_string[-1] in string.ascii_letters:
                        temp_string += '.'
                    else:
                        temp_string = temp_string[0:-1] + '.'

                self.original_sentenses[idx] = temp_string

                index_of_quotes = []

    def remove_short_and_long_sentencs(self):
        for idx, sentence in enumerate(self.original_sentenses):
            temp_size = len(sentence)
            while '  ' in sentence:
                sentence = sentence.replace('  ', ' ')
            splited_words = sentence.split()
            if len(splited_words) <= 4 or len(splited_words) >= 43:
                self.original_sentenses[idx] = ''

    def pre_process(self):
        for sentence in self.original_sentenses:
            self.processed_sentense.append(' ' + self.flip_upper_letter_and_replace_specials(sentence))
        for i in range(len(self.keywords)):
            self.keywords[i] = self.flip_upper_letter_and_replace_specials(self.keywords[i].strip())

    def find_hits(self, flag, num_sentence):
        pass

    def flip_upper_letter_and_replace_specials(self, sentence):
        result = ''
        for c in sentence:
            pass
        return sentence

    @classmethod
    def protect_special_words(cls, content):
        """

        :rtype : str
        """
        result = content
        for word in cls.protected_words_mapping_list:
            result = result.replace(" " + word[0], " " + word[1])
            result = result.replace(word[0] + " ", word[1] + " ")
        return result

    @classmethod
    def release_protection(cls, content):
        result = content
        for word in cls.protected_words_mapping_list:
            result = result.replace(" " + word[1], " " + word[0])
            result = result.replace(word[1] + " ", word[0] + " ")
        return result



