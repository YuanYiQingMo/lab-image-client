import tkinter as tk

class PlaceholderEntry(tk.Entry):

    def __init__(self, master=None, placeholder="", color='grey'):
        super().__init__(master)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.addPlaceholder()

    def addPlaceholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

        self.bind('<FocusIn>', self._clear_placeholder)
        self.bind('<FocusOut>', self._add_placeholder)

    def _clear_placeholder(self, e):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, e):
        if not self.get():
            self.addPlaceholder()