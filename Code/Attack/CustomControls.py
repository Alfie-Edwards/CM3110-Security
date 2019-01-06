import tkinter


class NavigationPanel(tkinter.Frame):
    def __init__(self, master, navigation_model):
        super(NavigationPanel, self).__init__(master)
        self.navigation_model = navigation_model
        self.buttons = {}

    def add_button(self, name, destination):
        name_lower = name.lower()
        if name_lower not in self.buttons:
            self.buttons[name_lower] = tkinter.Button(self)
            self.buttons[name_lower]['text'] = name
            self.buttons[name_lower]['font'] = ("Segoe UI", 9)
            self.buttons[name_lower]['state'] = "disabled"
            self.buttons[name_lower]['command'] = lambda: self.navigation_model.show_screen(destination)
            self.buttons[name_lower].pack(side=tkinter.LEFT, padx=(8, 0))

    def enable(self, name):
        name = name.lower()
        if name in self.buttons:
            self.buttons[name]['state'] = "normal"

    def disable(self, name):
        name = name.lower()
        if name in self.buttons:
            self.buttons[name]['state'] = "disabled"


class CipherTextDisplay(tkinter.Frame):
    def __init__(self, master):
        super(CipherTextDisplay, self).__init__(master)
        self.cipher_texts = []

        self.list_box = tkinter.Listbox(self)
        scrollbar = tkinter.Scrollbar(self)

        scrollbar['command'] = self.list_box.yview
        self.list_box['yscrollcommand'] = scrollbar.set
        self.list_box['font'] = ("Consolas", 10)
        self.list_box['activestyle'] = "none"

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.list_box.grid(row=0, column=0, sticky='nesw')
        scrollbar.grid(row=0, column=1, sticky='ns')

    def update(self, cipher_texts):
        self.cipher_texts = cipher_texts
        selected_index = self.list_box.curselection()
        if selected_index != ():
            selected = self.list_box.get(selected_index[0])
        else:
            selected = None

        self.list_box.delete(0, tkinter.END)
        new_selection = 0
        for i in range(len(cipher_texts)):
            self.list_box.insert(i, cipher_texts[i].ascii_string)
            if self.list_box.get(i) == selected:
                new_selection = i

        self.list_box.selection_set(new_selection)
        self.list_box.activate(new_selection)

    def set_selection(self, item):
        i = self.cipher_texts.index(item)
        if i > 0:
            self.list_box.selection_set(i)
            self.list_box.activate(i)

    def get_selection(self):
        selection = self.list_box.curselection()
        if len(selection) < 1:
            return None
        return self.cipher_texts[selection[0]]

    def bind_selection_changed(self, func):
        self.list_box.bind('<<ListboxSelect>>', lambda e: func(self.get_selection()))


class AsciiCharacterPair(tkinter.Frame):

    lock_image = None

    def __init__(self, master):
        super(AsciiCharacterPair, self).__init__(master)
        if self.lock_image is None:
            self.lock_image = tkinter.PhotoImage(file="Padlock.gif", width=4, height=4)

        self.box1 = AsciiCharacterEntry(self)
        self.box2 = AsciiCharacterEntry(self)

        self.lock = tkinter.Checkbutton(self)
        self.lock_varaible = tkinter.BooleanVar()
        self.lock['variable'] = self.lock_varaible
        self.lock['indicatoron'] = 0
        self.lock['image'] = self.lock_image
        self.lock['state'] = "normal"

        self.bind_locked_changed(self.box1.set_lock)
        self.bind_locked_changed(self.box2.set_lock)
        self.bind_locked_changed(self.update_lock_relief)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.box1.grid(row=0, column=0)
        self.box2.grid(row=1, column=0)
        self.lock.grid(row=2, column=0)

    def update_lock_relief(self, value):
        if value:
            self.lock['relief'] = "raised"
        else:
            self.lock['relief'] = "sunken"

    def bind_char1_changed(self, func):
        self.box1.bind('<<Modified>>', lambda e: self.box1.lock_modification or func(self.get_char1()))

    def bind_char2_changed(self, func):
        self.box2.bind('<<Modified>>', lambda e: self.box2.lock_modification or func(self.get_char2()))

    def bind_locked_changed(self, func):
        self.lock_varaible.trace('w', lambda *args: func(self.lock_varaible.get()))

    def get_char1(self):
        return self.box1.get_char()

    def get_char2(self):
        return self.box2.get_char()

    def set_char1(self, char):
        self.box1.set_char(char)

    def set_char2(self, char):
        self.box2.set_char(char)


class AsciiCharacterEntry(tkinter.Text):

    valid_characters = [chr(i) for i in range(256)]
    empty_colour = "light grey"
    full_colour = "white"
    highlight_colours = ["SteelBlue1", "SteelBlue2", "SteelBlue3", "SteelBlue4"]

    def __init__(self, master):
        super(AsciiCharacterEntry, self).__init__(master)
        self['width'] = 1
        self['height'] = 1
        self['background'] = self.empty_colour
        self['state'] = "disabled"
        self.bind("<FocusIn>", self.highlight)
        self.bind("<FocusOut>", self.un_highlight)
        self.bind("<Key>", self.on_key_press)
        self.bind("<BackSpace>", self.on_backspace)
        self.bind("<Delete>", self.on_backspace)
        self.lock_modification = False
        self.highlight_level = 0
        self.locked = False

    def set_lock(self, value):
        self.locked = value

    def highlight(self, e=None):
        self.highlight_level += 1
        self.evaluate_colour()

    def un_highlight(self, e=None):
        self.highlight_level -= 1
        self.evaluate_colour()

    def evaluate_colour(self):
        if self.highlight_level > 0:
            level = min(self.highlight_level, len(self.highlight_colours) - 1)
            self['background'] = self.highlight_colours[level]
        elif len(self.get(1.0, tkinter.END)) > 1:
            self['background'] = self.full_colour
        else:
            self['background'] = self.empty_colour

    def on_key_press(self, e=None):
        self.set_char(e.char)

    def on_backspace(self, e=None):
        self.set_char(None)

    def set_char(self, char):
        if self.locked or self.get_char() == char:
            return

        if char in self.valid_characters:
            original_state = self['state']
            self['state'] = "normal"

            self.lock_modification = True
            self.delete(1.0, tkinter.END)
            self.tk.call(self._w, 'edit', 'modified', 0)
            self.lock_modification = False

            self.insert(1.0, char)
            self['state'] = original_state
            if self['background'] == self.empty_colour:
                self['background'] = self.full_colour
        elif char is None:
            original_state = self['state']
            self['state'] = "normal"

            self.lock_modification = True
            self.tk.call(self._w, 'edit', 'modified', 0)
            self.lock_modification = False

            self.delete(1.0, tkinter.END)
            self['state'] = original_state
            if self['background'] == self.full_colour:
                self['background'] = self.empty_colour

    def get_char(self):
        full_content = self.get(1.0, tkinter.END)
        if (len(full_content)) < 2:
            return None
        return self.get(1.0, tkinter.END)[0]
