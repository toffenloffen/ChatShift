"""Clickable Xbox-style controller diagram, drawn with native Tk shapes."""
import tkinter as tk


class ControllerPreview(tk.Canvas):
    def __init__(self, parent, on_pick):
        super().__init__(parent, width=700, height=310, bg='#0d1421', highlightthickness=0)
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
        self.bind('<Button-1>', self.click_picture)

    def click_picture(self, event):
        for name, (x1, y1, x2, y2, _, _) in self.buttons.items():
            if x1-3 <= event.x <= x2+3 and y1-3 <= event.y <= y2+3:
                return self.pick(name)

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

    def rounded(self, x1, y1, x2, y2, **options):
        radius = min(12, (y2-y1)/2, (x2-x1)/2)
        return self.create_polygon(x1+radius, y1, x2-radius, y1, x2, y1,
            x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2,
            x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1,
            smooth=True, splinesteps=24, **options)

    def draw(self):
        self.delete('all')
        shell = (164, 77, 201, 64, 276, 66, 309, 77, 391, 77, 424, 66,
                 499, 64, 536, 77, 560, 112, 579, 172, 590, 235,
                 581, 267, 559, 277, 540, 267, 492, 218, 454, 209,
                 413, 219, 287, 219, 246, 209, 208, 218, 160, 267,
                 141, 277, 119, 267, 110, 235, 121, 172, 140, 112)
        shadow = tuple(v + (7 if i % 2 else 0) for i, v in enumerate(shell))
        self.create_polygon(*shadow, smooth=True, splinesteps=32, fill='#090d17', outline='', width=0)
        self.create_polygon(*shell, smooth=True, splinesteps=32,
                            fill='#292e43', outline='#667191', width=2)
        # Sculpted grip panels and restrained accent lighting.
        for flip in (False, True):
            points = [(147, 169), (170, 184), (191, 210), (151, 257),
                      (137, 260), (124, 244), (130, 202)]
            coords = [v for x, y in points for v in ((700-x if flip else x), y)]
            self.create_polygon(*coords, smooth=True, fill='#1b2031', outline='#343d56')
            for offset in range(5):
                x = 139 + offset*4
                self.create_line(700-x if flip else x, 211,
                                 700-(x-5) if flip else x-5, 241,
                                 fill='#30384e', width=1)
        self.create_line(172, 81, 215, 75, 277, 77, smooth=True, fill='#77639f', width=2)
        self.create_line(423, 77, 485, 75, 528, 81, smooth=True, fill='#568b94', width=2)
        self.rounded(325, 86, 375, 112, fill='#171c2b', outline='#64758c')
        self.create_text(350, 99, text='CS', fill='#9feadd', font=('Segoe UI', 10, 'bold'))
        if self.view == 'front':
            self.create_oval(214, 146, 340, 259, fill='#202538', outline='#39435d')
            self.create_oval(165, 91, 249, 175, fill='#151a29', outline='#586482', width=2)
            self.create_oval(365, 166, 449, 250, fill='#151a29', outline='#586482', width=2)
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
            self.rounded(285, 122, 415, 207, fill='#222739', outline='#46516e', width=1)
            self.create_text(350, 157, text='REAR VIEW', fill='#a6acc6', font=('Segoe UI', 10, 'bold'))
            self.create_text(350, 180, text='via Steam Input', fill='#b69aff', font=('Segoe UI', 9))
            self.create_text(226, 101, text='RIGHT HAND', fill='#b69aff', font=('Segoe UI', 10, 'bold'))
            self.create_text(474, 101, text='LEFT HAND', fill='#b69aff', font=('Segoe UI', 10, 'bold'))
            self.buttons = {
                'Rear R4 (right hand, upper)': (186, 118, 267, 157, 'R4', False),
                'Rear R5 (right hand, lower)': (186, 176, 267, 215, 'R5', False),
                'Rear L4 (left hand, upper)': (433, 118, 514, 157, 'L4', False),
                'Rear L5 (left hand, lower)': (433, 176, 514, 215, 'L5', False)}
        face_colors = {'A': '#80dc9b', 'B': '#ff969f', 'X': '#8cc9ff', 'Y': '#ffe193'}
        for index, (name, (x1, y1, x2, y2, label, round_button)) in enumerate(self.buttons.items()):
            tag = 'button_' + str(index)
            selected = name in self.selection
            focused = self.focus_get() == self and index == self.focus_index
            color = '#c1fff1' if selected else '#40526b'
            shape = self.create_oval if round_button else self.rounded
            shape(x1-3, y1-3, x2+3, y2+3, fill='#285851' if selected else '#1b2032',
                  outline='#b69aff' if focused else color, width=2, tags=tag)
            shape(x1, y1, x2, y2, fill='#77f2db' if selected else '#202c40',
                  outline=color, width=1, tags=tag)
            if 'stick click' in name:
                self.create_oval(x1+7, y1+7, x2-7, y2-7, outline='#d6fff5' if selected else '#3a4662', width=2, tags=tag)
            self.create_text((x1+x2)/2, (y1+y2)/2, text=label,
                             fill='#10111b' if selected else face_colors.get(name, '#e2e7fa'),
                             font=('Segoe UI', 10, 'bold'), tags=tag)
        self.create_text(350, 294, text=('Rear view · Left / right refer to your hands while playing (mirrored here)'
                         if self.view == 'back' else 'LS / RS = press the stick · Click buttons to combine them'),
                         fill='#a6acc6', font=('Segoe UI', 9))
        from canvas_render import render
        self.rendered = render(self, 700, 310)
        if self.rendered is not None:
            self.create_image(0, 0, image=self.rendered, anchor='nw')
