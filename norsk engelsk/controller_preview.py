"""Clickable Xbox-style controller diagram, drawn with native Tk shapes."""
import tkinter as tk


class ControllerPreview(tk.Canvas):
    def __init__(self, parent, on_pick):
        super().__init__(parent, width=700, height=310, bg='#121625', highlightthickness=0)
        self.on_pick = on_pick
        self.selection = set()
        self.view = 'front'
        self.buttons = {}
        self.focus_index = 0
        self.configure(takefocus=True)
        self.draw()
        self.bind('<Left>', lambda e: self.move_focus(-1))
        self.bind('<Right>', lambda e: self.move_focus(1))
        self.bind('<space>', lambda e: self.pick(list(self.buttons)[self.focus_index]))
        self.bind('<Return>', lambda e: self.pick(list(self.buttons)[self.focus_index]))
        self.bind('<FocusIn>', lambda e: self.draw())
        self.bind('<FocusOut>', lambda e: self.draw())

    def move_focus(self, step):
        self.focus_index = (self.focus_index + step) % len(self.buttons)
        self.draw()
        return 'break'

    def pick(self, name):
        self.focus_index = list(self.buttons).index(name)
        self.focus_set()
        self.on_pick(name)
        return 'break'

    def set_selection(self, names):
        self.selection = set(names)
        self.draw()

    def set_view(self, view):
        self.view = view
        self.focus_index = 0
        self.draw()

    def draw(self):
        self.delete('all')
        self.create_polygon(175, 68, 240, 58, 460, 58, 525, 68, 566, 121,
            595, 248, 566, 286, 530, 278, 473, 219, 227, 219, 170, 278,
            134, 286, 105, 248, 134, 121, smooth=True,
            fill='#242a40', outline='#526084', width=2)
        self.create_line(235, 81, 465, 81, fill='#51416e', width=3)
        self.create_text(350, 101, text='CHATSHIFT', fill='#b69aff', font=('Segoe UI', 10, 'bold'))
        self.buttons = {
            'LT': (185, 20, 275, 46, 'LT', False), 'RT': (425, 20, 515, 46, 'RT', False),
            'LB': (175, 51, 280, 78, 'LB', False), 'RB': (420, 51, 525, 78, 'RB', False),
            'Left stick click': (172, 98, 242, 168, 'LS', True),
            'View': (285, 118, 331, 147, 'View', False),
            'Menu': (369, 118, 415, 147, 'Menu', False),
            'D-pad Up': (260, 157, 294, 187, '↑', False),
            'D-pad Left': (225, 188, 259, 218, '←', False),
            'D-pad Right': (295, 188, 329, 218, '→', False),
            'D-pad Down': (260, 219, 294, 249, '↓', False),
            'Right stick click': (372, 173, 442, 243, 'RS', True),
            'Y': (494, 89, 530, 125, 'Y', True),
            'X': (455, 128, 491, 164, 'X', True),
            'B': (533, 128, 569, 164, 'B', True),
            'A': (494, 167, 530, 203, 'A', True)}
        if self.view == 'back':
            self.create_rectangle(285, 113, 415, 215, fill='#1b2032', outline='#46516e', width=2)
            self.create_text(350, 157, text='REAR VIEW', fill='#a6acc6', font=('Segoe UI', 10, 'bold'))
            self.create_text(350, 180, text='via Steam Input', fill='#b69aff', font=('Segoe UI', 9))
            self.buttons = {
                'Rear upper left': (186, 118, 267, 157, 'Upper', False),
                'Rear lower left': (186, 176, 267, 215, 'Lower', False),
                'Rear upper right': (433, 118, 514, 157, 'Upper', False),
                'Rear lower right': (433, 176, 514, 215, 'Lower', False)}
        face_colors = {'A': '#80dc9b', 'B': '#ff969f', 'X': '#8cc9ff', 'Y': '#ffe193'}
        for index, (name, (x1, y1, x2, y2, label, round_button)) in enumerate(self.buttons.items()):
            tag = 'button_' + str(index)
            selected = name in self.selection
            focused = self.focus_get() == self and index == self.focus_index
            color = '#78f5b0' if selected else '#46516e'
            shape = self.create_oval if round_button else self.create_rectangle
            shape(x1-3, y1-3, x2+3, y2+3, fill='#163d32' if selected else '#1b2032',
                  outline='#b69aff' if focused else color, width=2, tags=tag)
            shape(x1, y1, x2, y2, fill='#245743' if selected else '#161b2c',
                  outline=color, width=1, tags=tag)
            self.create_text((x1+x2)/2, (y1+y2)/2, text=label,
                             fill='#b8ffce' if selected else face_colors.get(name, '#e2e7fa'),
                             font=('Segoe UI', 10, 'bold'), tags=tag)
            self.tag_bind(tag, '<Button-1>', lambda e, n=name: self.pick(n))
        self.create_text(350, 294, text=('Illustrative paddle positions · Click for keyboard mapping setup'
                         if self.view == 'back' else 'LS / RS = press the stick · Click buttons to combine them'),
                         fill='#a6acc6', font=('Segoe UI', 9))
