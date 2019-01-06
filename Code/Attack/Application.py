from Domain import *


class CribDraggingModeModel:
    def __init__(self, xor_text):
        self.xor_text = xor_text
        self.string1 = [None for _ in range(len(xor_text.byte_array))]
        self.string2 = [None for _ in range(len(xor_text.byte_array))]
        self.locked = []
        self.word = None
        self.lock_filtered_all_results = {}
        self.lock_filtered_promising_results = {}
        self.all_results = {}
        self.promising_results = {}
        self.selected_result = None
        self.selected_result_index = None

    def lock(self, i):
        if i not in self.locked:
            self.locked.append(i)
            self.calculate_lock_filtered_results()

    def unlock(self, i):
        self.locked.remove(i)
        self.calculate_lock_filtered_results()

    def get_string1_char(self, i):
        return self.string1[i]

    def get_string2_char(self, i):
        return self.string2[i]

    def set_string1_substring(self, i, substring):
        if i + len(substring) > len(self.string1):
            return
        for j in range(i, len(substring) + i):
            if j in self.locked:
                return
        for j in range(len(substring)):
            self.set_string1_character(i + j, substring[j])

    def set_string2_substring(self, i, substring):
        if i + len(substring) > len(self.string2):
            return
        for j in range(i, len(substring) + i):
            if j in self.locked:
                return
        for j in range(len(substring)):
            self.set_string2_character(i + j, substring[j])

    def set_string1_character(self, i, char):
        if i in self.locked or i >= len(self.string1) or self.string1[i] == char:
            return
        self.string1[i] = char
        self.string2[i] = None if char is None else chr(ord(char) ^ self.xor_text.byte_array[i])

    def set_string2_character(self, i, char):
        if i in self.locked or i >= len(self.string2) or self.string2[i] == char:
            return
        self.string2[i] = char
        self.string1[i] = None if char is None else chr(ord(char) ^ self.xor_text.byte_array[i])

    def set_crib_dragging_word(self, word):
        self.word = word
        self.lock_filtered_all_results = {}
        self.lock_filtered_promising_results = {}
        self.all_results = {}
        self.promising_results = {}

        if word is not None:
            results = CribDraggingService.crib_drag(self.xor_text, word)
            self.all_results = results[0]
            self.promising_results = results[1]
            self.calculate_lock_filtered_results()

    def calculate_lock_filtered_results(self):
        self.lock_filtered_all_results = {}
        self.lock_filtered_promising_results = {}
        for k, v in self.all_results.items():
            any_locked = False
            for i in range(k, k + len(v.ascii_string)):
                if i in self.locked:
                    any_locked = True
                    break
            if not any_locked:
                self.lock_filtered_all_results[k] = v
                if k in self.promising_results:
                    self.lock_filtered_promising_results[k] = v

    def clear_crib_dragging_word(self):
        self.set_crib_dragging_word(None)

    def set_selected_result(self, result):
        if result is None:
            self.selected_result = None
            self.selected_result_index = None
            return
        for k, v in self.all_results.items():
            if v == result:
                self.selected_result_index = k
                self.selected_result = result
                return

    def apply_selected_result(self):
        string1 = self.word
        string2 = self.selected_result.ascii_string
        self.set_string1_substring(self.selected_result_index, string1)
        self.set_string2_substring(self.selected_result_index, string2)


class ApplicationModel:
    def __init__(self):
        self.path = ""
        self.cipher_texts = []
        self.promising_pairs = []
        self.all_pairs = []
        self.pair_roots = []
        self.selected_pair = None

    def calculate_pairs(self):
        self.promising_pairs = []
        self.all_pairs = []
        self.pair_roots = []
        if len(self.cipher_texts) == 0:
            return

        number_of_texts = len(self.cipher_texts)
        for i in range(number_of_texts):
            for j in range(i + 1, number_of_texts):
                xor = self.cipher_texts[i].xor(self.cipher_texts[j])
                self.pair_roots.append((i, j))
                self.all_pairs.append(xor)
                if CribDraggingService.is_likely_plaintext_xor(xor):
                    self.promising_pairs.append(xor)

    def build_crib_dragging_model(self):
        return CribDraggingModeModel(self.selected_pair)


class NavigationModel:
    def __init__(self):
        self.screen_dictionary = {}
        self.current_screen = None

    def add_screen(self, screen, name):
        if name not in self.screen_dictionary:
            self.screen_dictionary[name] = screen

    def show_screen(self, name):
        if self.current_screen is not None:
            self.screen_dictionary[self.current_screen].pack_forget()
        self.current_screen = name
        self.screen_dictionary[self.current_screen].on_enter()
        self.screen_dictionary[self.current_screen].pack(padx=8, pady=(8, 0), fill="both", expand="yes")
