from CustomControls import *
from Domain import Text
import tkinter
from tkinter import filedialog


class LoadCipherTextsScreen(tkinter.Frame):
    def __init__(self, application, application_model, navigation_model):
        super(LoadCipherTextsScreen, self).__init__(application)

        self.application_model = application_model
        self.rowconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)

        title = tkinter.Label(self)
        title['text'] = "Select the file containing your ciphertexts"
        title['anchor'] = "w"
        title['font'] = ("Segoe UI",  12)
        title.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))

        self.navigation_panel = NavigationPanel(self, navigation_model)
        self.navigation_panel.add_button("Next", "Pair Selection")
        self.navigation_panel.grid(row=0, column=2)

        button = tkinter.Button(self)
        button['text'] = "Browse"
        button['command'] = self.load_file
        button['font'] = ("Segoe UI", 9)
        button.grid(row=1, column=0)

        self.label = tkinter.Label(self)
        self.label['text'] = " "
        self.label['anchor'] = "e"
        self.label['font'] = ("Segoe UI", 10, "italic")
        self.label.grid(row=1, column=1, columnspan=2, sticky='w', padx=(8, 0))

        self.cipher_text_display = CipherTextDisplay(self)
        self.cipher_text_display.list_box['selectbackground'] = "white"
        self.cipher_text_display.list_box['selectforeground'] = "black"
        self.cipher_text_display.grid(row=2, column=0, columnspan=3, sticky='nesw', pady=(8, 0))

        self.detail_bar = tkinter.Label(self)
        self.detail_bar['text'] = "No file selected"
        self.detail_bar['font'] = ("Segoe UI", 9, "italic")
        self.detail_bar['anchor'] = "w"
        self.detail_bar['foreground'] = "grey15"
        self.detail_bar.grid(row=3, column=0, columnspan=3, sticky='nesw', pady=(8, 0))

    def on_enter(self):
        if self.application_model.path != "":
            self.label['text'] = self.application_model.path
            self.cipher_text_display.update(self.application_model.cipher_texts)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        cipher_texts = [Text.from_hex_string(hex_string) for hex_string in open(path, 'r').read().splitlines()]
        self.application_model.path = path
        self.application_model.cipher_texts = cipher_texts
        self.label['text'] = self.application_model.path
        self.detail_bar['text'] = self.build_detail_bar_text()
        self.cipher_text_display.update(self.application_model.cipher_texts)
        self.navigation_panel.enable("Next")

    def build_detail_bar_text(self):
        path = str(self.application_model.path)
        lines = str(len(self.application_model.cipher_texts))
        return "File: " + path + " (" + lines + " ciphertexts)"


class PairSelectionScreen(tkinter.Frame):
    def __init__(self, application, application_model, navigation_model):
        super(PairSelectionScreen, self).__init__(application)

        self.application_model = application_model
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        title = tkinter.Label(self)
        title['text'] = "Select an XOR'd text to run crib dragging on"
        title['anchor'] = "w"
        title['font'] = ("Segoe UI",  12)
        title.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))

        self.navigation_panel = NavigationPanel(self, navigation_model)
        self.navigation_panel.add_button("Prev", "Load Cipher Texts")
        self.navigation_panel.add_button("Next", "Crib Dragging")
        self.navigation_panel.grid(row=0, column=2)

        self.cipher_text_display = CipherTextDisplay(self)
        self.cipher_text_display.grid(row=1, column=0, columnspan=3, sticky='nesw')
        self.cipher_text_display.bind_selection_changed(self.on_selection_changed)

        self.button = tkinter.Button(self)
        self.button['font'] = ("Segoe UI", 9)
        self.button['width'] = 10
        self.button.grid(row=2, column=0, pady=(8, 0))

        self.label = tkinter.Label(self)
        self.label['anchor'] = "e"
        self.label['font'] = ("Segoe UI", 10)
        self.label.grid(row=2, column=1, columnspan=2, sticky='w', padx=(8, 0), pady=(8, 0))

        self.detail_bar = tkinter.Label(self)
        self.detail_bar['text'] = "No pair selected"
        self.detail_bar['font'] = ("Segoe UI", 9, "italic")
        self.detail_bar['anchor'] = "w"
        self.detail_bar['foreground'] = "grey15"
        self.detail_bar.grid(row=3, column=0, columnspan=3, sticky='nesw', pady=(8, 0))

        self.navigation_panel.enable("Prev")

    def on_enter(self):
        self.application_model.calculate_pairs()
        self.show_promising_pairs()

    def on_selection_changed(self, value):
        self.application_model.selected_pair = value
        self.detail_bar['text'] = self.build_detail_bar_text()
        self.navigation_panel.enable("Next")

    def show_all_pairs(self):
        self.label['text'] = "Showing all possible pairs"
        self.button['text'] = "↓ Show Less"
        self.button['command'] = self.show_promising_pairs
        self.cipher_text_display.update(self.application_model.all_pairs)

    def show_promising_pairs(self):
        self.label['text'] = "Showing auto-found promising pairs"
        self.button['text'] = "↑ Show More"
        self.button['command'] = self.show_all_pairs
        self.cipher_text_display.update(self.application_model.promising_pairs)
        self.on_selection_changed(self.cipher_text_display.get_selection())

    def build_detail_bar_text(self):
        if self.application_model.selected_pair == None:
            return "No pair selected"
        index = self.application_model.all_pairs.index(self.application_model.selected_pair)
        roots = self.application_model.pair_roots[index]
        one = str(roots[0] + 1)
        two = str(roots[1] + 1)
        return "Selected xor of ciphertexts " + one + " and " + two


class CribDraggingScreen(tkinter.Frame):

    max_characters_per_row = 50
    selected_colour = "DodgerBlue2"

    def __init__(self, application, application_model, navigation_model):
        super(CribDraggingScreen, self).__init__(application)

        self.application_model = application_model
        self.crib_dragging_mode_model = None
        self.entry_boxes_list = []
        self.showing_all = False
        self.rowconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)

        title = tkinter.Label(self)
        title['text'] = "Find the original plaintext pair"
        title['anchor'] = "w"
        title['font'] = ("Segoe UI",  12)
        title.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))

        self.navigation_panel = NavigationPanel(self, navigation_model)
        self.navigation_panel.add_button("Prev", "Pair Selection")
        self.navigation_panel.grid(row=0, column=2, sticky="e")

        button = tkinter.Button(self)
        button['text'] = "Crib drag"
        button['font'] = ("Segoe UI", 9)
        button['command'] = lambda: self.set_crib_dragging_word(self.entry.get())
        button.grid(row=1, column=0, sticky="ew")

        self.entry = tkinter.Entry(self)
        self.entry['font'] = ("Segoe UI", 10)
        self.entry.grid(row=1, column=1, columnspan=2, sticky="nesw")

        self.words_box = CipherTextDisplay(self)
        self.words_box.grid(row=2, column=0, columnspan=3, sticky='nesw', pady=(8, 0))
        self.words_box.bind_selection_changed(self.on_selection_changed)

        self.toggle_button = tkinter.Button(self)
        self.toggle_button['font'] = ("Segoe UI", 9)
        self.toggle_button['state'] = "disabled"
        self.toggle_button['text'] = "↑ Show More"
        self.toggle_button['width'] = 10
        self.toggle_button['command'] = self.show_all_words
        self.toggle_button.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        self.label = tkinter.Label(self)
        self.label['anchor'] = "e"
        self.label['font'] = ("Segoe UI", 10)
        self.label.grid(row=3, column=1, sticky='w', pady=(8, 0))

        self.apply_button = tkinter.Button(self)
        self.apply_button['text'] = "Apply selection ↓"
        self.apply_button['font'] = ("Segoe UI", 9)
        self.apply_button['command'] = self.apply_selection
        self.apply_button['state'] = "disabled"
        self.apply_button.grid(row=3, column=2, sticky="e", pady=(8, 0))

        self.entry_boxes_container = tkinter.Frame(self)
        self.entry_boxes_container.grid(row=4, column=0, columnspan=3)

        self.detail_bar = tkinter.Label(self)
        self.detail_bar['text'] = "No pair selected"
        self.detail_bar['font'] = ("Segoe UI", 9, "italic")
        self.detail_bar['anchor'] = "w"
        self.detail_bar['foreground'] = "grey15"
        self.detail_bar.grid(row=5, column=0, columnspan=3, sticky='nesw', pady=(8, 0))

        self.navigation_panel.enable("Prev")

    def on_enter(self):
        self.apply_button['state'] = "disabled"
        self.toggle_button['state'] = "disabled"
        self.crib_dragging_mode_model = self.application_model.build_crib_dragging_model()
        self.words_box.update([])
        self.build_entry_boxes()
        self.detail_bar['text'] = self.build_detail_bar_text()

    def set_crib_dragging_word(self, word):
        self.on_selection_changed(None)
        self.crib_dragging_mode_model.set_crib_dragging_word(word)
        self.toggle_button['state'] = "normal"
        self.refresh_word_box()
        self.detail_bar['text'] = self.build_detail_bar_text()

    def apply_selection(self):
        self.crib_dragging_mode_model.apply_selected_result()
        self.update_all_entry_boxes()

    def refresh_word_box(self):
        if self.showing_all:
            self.show_all_words()
        else:
            self.show_promising_words()

    def show_all_words(self):
        if self.toggle_button['state'] == "normal":
            self.label['text'] = "Showing all results"
        self.toggle_button['text'] = "↓ Show Less"
        self.toggle_button['command'] = self.show_promising_words
        self.words_box.update(self.get_dictionary_values(self.crib_dragging_mode_model.lock_filtered_all_results))
        self.on_selection_changed(self.words_box.get_selection())
        self.showing_all = True

    def show_promising_words(self):
        if self.toggle_button['state'] == "normal":
            self.label['text'] = "Showing auto-found promising results"
        self.toggle_button['text'] = "↑ Show More"
        self.toggle_button['command'] = self.show_all_words
        self.words_box.update(self.get_dictionary_values(self.crib_dragging_mode_model.lock_filtered_promising_results))
        self.on_selection_changed(self.words_box.get_selection())
        self.showing_all = False

    def build_entry_boxes(self):
        if len(self.entry_boxes_list) > 0:
            for crib_dragging_pair in self.entry_boxes_list:
                crib_dragging_pair.destroy()
            self.entry_boxes_list = []

        for i in range(len(self.crib_dragging_mode_model.string1)):
            entry_box = AsciiCharacterPair(self.entry_boxes_container)
            entry_box.bind_char1_changed(lambda char, entry_box=entry_box, i=i: self.on_char1_changed(entry_box, i, char))
            entry_box.bind_char2_changed(lambda char, entry_box=entry_box, i=i: self.on_char2_changed(entry_box, i, char))
            entry_box.bind_locked_changed(lambda value, i=i: self.on_locked_changed(i, value))
            entry_box.grid(row=(i // self.max_characters_per_row), column=(i % self.max_characters_per_row), pady=(8, 0))
            self.entry_boxes_list.append(entry_box)

    def build_detail_bar_text(self):
        index = self.application_model.all_pairs.index(self.application_model.selected_pair)
        roots = self.application_model.pair_roots[index]
        one = str(roots[0] + 1)
        two = str(roots[1] + 1)
        text = "Current ciphertexts: " + one + " and " + two
        word = self.crib_dragging_mode_model.word
        if word is not None:
            text += '.   Crib dragging word: "' + word + '"'
        return text

    def set_highlight_for_selected_entry_boxes(self, highlighted):
        index = self.crib_dragging_mode_model.selected_result_index
        if index is None:
            return
        length = len(self.crib_dragging_mode_model.selected_result.ascii_string)

        for i in range(index, index + length):
            if highlighted:
                self.entry_boxes_list[i].box1.highlight()
                self.entry_boxes_list[i].box2.highlight()
            else:
                self.entry_boxes_list[i].box1.un_highlight()
                self.entry_boxes_list[i].box2.un_highlight()

    def on_locked_changed(self, i, value):
        if value:
            self.crib_dragging_mode_model.lock(i)
        else:
            self.crib_dragging_mode_model.unlock(i)
        self.refresh_word_box()

    def on_selection_changed(self, selection):
        self.set_highlight_for_selected_entry_boxes(None)
        self.crib_dragging_mode_model.set_selected_result(selection)
        if selection is None:
            self.apply_button['state'] = "disabled"
        else:
            self.apply_button['state'] = "normal"
            self.set_highlight_for_selected_entry_boxes(True)

    def on_char1_changed(self, ascii_pair, i, char):
        self.crib_dragging_mode_model.set_string1_character(i, char)
        ascii_pair.set_char2(self.crib_dragging_mode_model.get_string2_char(i))

    def on_char2_changed(self, ascii_pair, i, char):
        self.crib_dragging_mode_model.set_string2_character(i, char)
        ascii_pair.set_char1(self.crib_dragging_mode_model.get_string1_char(i))

    def update_all_entry_boxes(self):
        for i in range(len(self.entry_boxes_list)):
            char1 = self.crib_dragging_mode_model.get_string1_char(i)
            if self.entry_boxes_list[i].get_char1 != char1:
                self.entry_boxes_list[i].set_char1(char1)

            char2 = self.crib_dragging_mode_model.get_string2_char(i)
            if self.entry_boxes_list[i].get_char2 != char2:
                self.entry_boxes_list[i].set_char2(char2)

    @staticmethod
    def get_dictionary_values(dictionary):
        list = []
        if len(dictionary) < 1:
            return []
        for i in range(max(dictionary.keys()) + 1):
            if i in dictionary:
                list.append(dictionary[i])
        return list
