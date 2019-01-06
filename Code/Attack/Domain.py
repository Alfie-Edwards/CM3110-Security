import math
import re

# Represents a string, and allows conversion between ascii, hex, and bytes
class Text:
    def __init__(self, ascii_string, byte_array, hex_string):
        self.ascii_string = ascii_string
        self.byte_array = byte_array
        self.hex_string = hex_string

    @staticmethod
    def from_hex_string(hex_string):
        byte_array = bytearray.fromhex(hex_string)
        ascii_string = ''.join([chr(byte) if chr(byte).isprintable() else '·' for byte in byte_array])
        return Text(ascii_string, byte_array, hex_string)

    @staticmethod
    def from_ascii_string(ascii_string):
        byte_array = [ord(char) for char in ascii_string]
        hex_string = ''.join([format(byte, "02x") for byte in byte_array])
        return Text(ascii_string, byte_array, hex_string)

    @staticmethod
    def from_byte_array(byte_array):
        ascii_string = ''.join([chr(byte) if chr(byte).isprintable() else '·' for byte in byte_array])
        hex_string = ''.join([format(byte, "02x") for byte in byte_array])
        return Text(ascii_string, byte_array, hex_string)

    # Implementation of bitwise xoring of 2 texts using their numeric representation
    def xor(self, chyper_text):
        return Text.from_byte_array(
            [self.byte_array[i] ^ chyper_text.byte_array[i] for i in range(len(self.byte_array))])


class Dictionary:
    # new-line delimited list of lower-case english words in alphabetical order
    path = "dictionary.txt"
    # . is legal in-case of numbers
    legal_characters_regex = '[A-z0-9.]*'
    word_boundary_characters = '[\n\s/-]+'
    punctuation_with_trailing_spaces = ['\.+', ',', '\?', '!', '\)"', '"\)', '\)\'', '\'\)', '\)', '"', '\'', ':', ';']
    punctuation_with_leading_spaces = ['"\(', '\("', '\'\(', '\(\'', '\(', '"', '\'']
    inter_word_punctuation_regex =\
        '(' +\
        '|'.join(
            [x + '\s+' for x in punctuation_with_trailing_spaces] +
            ['\s+' + x for x in punctuation_with_leading_spaces]) +\
        ')'
    outer_punctuation_regex =\
        '(^(' +\
        '|'.join(['\s*' + x for x in punctuation_with_leading_spaces]) +\
        ')|(' +\
        '|'.join([x + '\s*' for x in punctuation_with_trailing_spaces]) +\
        ')$)'

    def __init__(self):
        self.english_words = open(self.path, 'r').read().splitlines()
        self.word_count = len(self.english_words)

        # Index the ranges for each start character in the alphabetical list to speed up searches
        self.alphabetical_ranges = {}
        current_start_character = self.english_words[0][0]
        current_start_index = 0
        for i in range(self.word_count):
            word = self.english_words[i]
            start_character = word[0].lower()
            if start_character != current_start_character:
                self.alphabetical_ranges[current_start_character] = (current_start_index, i)
                current_start_index = i
                current_start_character = start_character
        self.alphabetical_ranges[current_start_character] = (current_start_index, self.word_count)

    def is_english_subsring(self, string):
        # Make string lowercase to match dictionary
        string = string.lower()
        # Replace outer punctuation with spaces (separate because it may not have the usual leading/trailing spaces)
        # Leaving a space allows differentiating whole words vs parts of words at the start and end of the string
        string = re.sub(self.outer_punctuation_regex, ' ', string)
        # Replace inter-word punctuation with spaces (should always have the usual leading/trailing spaces)
        string = re.sub(self.inter_word_punctuation_regex, ' ', string)
        # Split at spaces (and other word boundaries)
        words = re.split(self.word_boundary_characters, string)

        # If words still contains non alpha-numeric characters they will fail the dictionary match
        for word in words:
            if not re.fullmatch(self.legal_characters_regex, word):
                return False

        word_count = len(words)
        if word_count == 1:
            return self.is_middle_of_word(words[0])
        else:
            first_word = words[0]
            middle_words = []
            last_word = words[-1]
            for i in range(1, word_count - 1):
                middle_words.append(words[i])

            if last_word != "" and not self.is_number(last_word) and not self.is_start_of_word(last_word):
                return False

            for word in middle_words:
                if word != "" and not self.is_number(word) and not self.is_word(word):
                    return False

            # end of word is slowest to search so do it last
            if first_word != "" and not self.is_number(first_word) and not self.is_end_of_word(first_word):
                return False
        return True

    # Used to match words in the middle of a string
    def is_word(self, string):
        start_char = string[0]
        if start_char not in self.alphabetical_ranges:
            return False
        search_range = self.alphabetical_ranges[start_char]
        for i in range(search_range[0], search_range[1]):
            if string == self.english_words[i]:
                return True
        return False

    # Used to match the last word in a string (end of word could be cut off)
    def is_start_of_word(self, string):
        length = len(string)
        start_char = string[0]
        if start_char not in self.alphabetical_ranges:
            return False
        search_range = self.alphabetical_ranges[start_char]
        for i in range(search_range[0], search_range[1]):
            word = self.english_words[i]
            if len(word) >= length and word[0:length] == string:
                return True
        return False

    # Used to match the first word in a string (start of word could be cut off)
    def is_end_of_word(self, string):
        length = len(string)
        for word in self.english_words:
            word_length = len(word)
            if word_length >= length and word[word_length - length:word_length] == string:
                return True
        return False

    # Used to string that have only 1 word (start and/or end of word could be cut off)
    def is_middle_of_word(self, string):
        for word in self.english_words:
            if string in word:
                return True
        return False

    # All words are checked against this separately as the dictionary only contains alphabetical words
    def is_number(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False


class CribDraggingService:
    # Allowable proportion of good characters vs bad in the evaluation methods below
    auto_detection_ratio = 0.1

    # Used to judge good crib dragging results
    dictionary = Dictionary()

    # Takes in the xor of 2 ciphertexts and detects if it is likely they were generated by the same key
    @staticmethod
    def is_likely_plaintext_xor(xor_text):
        bad_bytes = 0
        max_bad_bytes = math.ceil(CribDraggingService.auto_detection_ratio * len(xor_text.byte_array))

        for byte in xor_text.byte_array:
            if byte > 127:
                bad_bytes += 1
                if bad_bytes >= max_bad_bytes:
                    break
        if bad_bytes < max_bad_bytes:
            return True
        return False

    # Get all possible corresponding strings for a given word, based on an xor text
    @staticmethod
    def crib_drag(xor_text, word):
        all_results = {}
        promising_results = {}
        length = len(word)
        word = Text.from_ascii_string(word)
        for i in range(len(xor_text.ascii_string) - length + 1):
            sub_string = Text.from_byte_array(xor_text.byte_array[i:i + length])
            result = word.xor(sub_string)
            all_results[i] = result
            if CribDraggingService.dictionary.is_english_subsring(result.ascii_string):
                promising_results[i] = result
        return all_results, promising_results
