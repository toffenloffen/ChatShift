"""A visual shortcut guide. Never listens to or records keyboard input."""
import tkinter as tk
from shortcuts import validate_binding, MODIFIER_NAMES, KEY_NAMES, NUMPAD_ENTER


class ShortcutDraft:
    def __init__(self):
        self.keys = set()

    def pick(self, key, combine=False):
        if key in self.keys:
            self.keys.remove(key)
        elif combine:
            if len(self.keys) >= 3:
                raise ValueError('Choose up to three keys for one shortcut.')
            self.keys.add(key)
        else:
            self.keys = {key}

    def binding(self):
        if not self.keys:
            return {'modifiers': [], 'key': None}
        keys = self.keys - MODIFIER_NAMES.keys()
        if not keys:
            key = max(self.keys)
            return validate_binding({'modifiers': sorted(self.keys - {key}), 'key': key})
        if len(keys) != 1:
            raise ValueError('Choose one main key, with optional Ctrl, Alt or Shift keys.')
        return validate_binding({'modifiers': sorted(self.keys & MODIFIER_NAMES.keys()),
                                 'key': next(iter(keys))})


def highlighted_keys(binding):
    binding = validate_binding(binding)
    if binding is not None and binding['key'] is None:
        return set()
    return {0xA3, 13} if binding is None else set(binding['modifiers']) | {binding['key']}


class KeyboardPreview(tk.Canvas):
    def __init__(self, parent, binding=None, on_pick=None, on_finish=None):
        super().__init__(parent, height=176, bg='#1b1e2e', highlightthickness=0)
        self.binding = binding
        self.selection = None
        self.on_pick = on_pick
        self.on_finish = on_finish
        self.regions = []
        self.bind('<Configure>', lambda event: self.draw())
        self.bind('<Button-1>', self.clicked)
        self.bind('<Button-3>', lambda event: 'break')
        self.bind('<ButtonRelease-3>', self.finish)

    def finish(self, event):
        if self.on_finish:
            self.on_finish()
        return 'break'

    def clicked(self, event):
        if self.on_pick:
            for left, top, right, bottom, key in self.regions:
                if left <= event.x <= right and top <= event.y <= bottom:
                    self.on_pick(key, bool(event.state & 0x0400))
                    return 'break'

    def set_binding(self, binding):
        self.binding = validate_binding(binding)
        self.selection = None
        self.draw()

    def draw(self):
        self.delete('all')
        active = highlighted_keys(self.binding) if self.selection is None else self.selection
        self.regions = []
        rows = [
            [('Esc', 27, 1.5)] + [(f'F{i}', 111+i, 1.125) for i in range(1, 13)],
            [('`', None, 1)] + [(str(i), ord(str(i)), 1) for i in range(1, 10)] + [('0', 48, 1), ('-', None, 1), ('=', None, 1), ('Back', 8, 2)],
            [('Tab', 9, 1.5)] + [(k, ord(k), 1) for k in 'QWERTYUIOP'] + [('[', None, 1), (']', None, 1), ('\\', None, 1.5)],
            [('Caps', None, 1.75)] + [(k, ord(k), 1) for k in 'ASDFGHJKL'] + [(';', None, 1), ("'", None, 1), ('Enter', 13, 2.25)],
            [('L Shift', 0xA0, 2.25)] + [(k, ord(k), 1) for k in 'ZXCVBNM'] + [(',', None, 1), ('.', None, 1), ('/', None, 1), ('R Shift', 0xA1, 2.75)],
            [('L Ctrl', 0xA2, 1.5), ('Win', None, 1.25), ('L Alt', 0xA4, 1.5), ('Space', 32, 6), ('R Alt', 0xA5, 1.5), ('Menu', None, 1.25), ('R Ctrl', 0xA3, 2)]
        ]
        unit = max(self.winfo_width(), 400) / 23.4
        self.create_rectangle(0, 0, self.winfo_width(), 175, fill='#0d1421', outline='#3b4164', width=2)
        self.create_line(8, 173, self.winfo_width()-8, 173, fill='#7758ad', width=2)
        def keycap(label, key, x, row, width=1, height=1):
            left, top = 4+x*unit, 7+row*27
            right, bottom = left+width*unit-3, top+height*27-4
            selected = key in active if key is not None else False
            if key in KEY_NAMES or key in MODIFIER_NAMES:
                self.regions.append((left, top, right, bottom, key))
            if selected:
                self.create_rectangle(left-2, top-2, right+2, bottom+3, fill='#394367', outline='#6976a6')
            self.create_rectangle(left, top+2, right, bottom+2, fill='#090c16', outline='')
            self.create_rectangle(left, top, right, bottom,
                fill='#77f2db' if selected else '#202c40', outline='#c1fff1' if selected else '#40526b')
            self.create_line(left+2, top+2, right-2, top+2,
                fill='#d6fff5' if selected else '#52617a')
            self.create_text((left+right)/2, (top+bottom)/2, text=label,
                fill='#10111b' if selected else ('#bdc5e1' if key is not None else '#68718a'),
                font=('Segoe UI', 7, 'bold' if selected else 'normal'))
        for row, keys in enumerate(rows):
            x = 0
            for label, key, width in keys:
                keycap(label, key, x, row, width)
                x += width
        for row, keys in [(1, [('Ins',45),('Home',36),('PgUp',33)]), (2,[('Del',46),('End',35),('PgDn',34)]), (5,[('←',37),('↓',40),('→',39)])]:
            for column, (label, key) in enumerate(keys):
                keycap(label, key, 15.4+column, row)
        keycap('↑',38,16.4,4)
        for row, keys in [(1,[('Num',None),('/',111),('*',106),('-',109)]),
                          (2,[('7',103),('8',104),('9',105)]),
                          (3,[('4',100),('5',101),('6',102)]),
                          (4,[('1',97),('2',98),('3',99)])]:
            for column,(label,key) in enumerate(keys):
                keycap(label,key,18.8+column,row)
        keycap('+',107,21.8,2,height=2)
        keycap('Enter',NUMPAD_ENTER,21.8,4,height=2)
        keycap('0',96,18.8,5,width=2)
        keycap('.',110,20.8,5)


class MousePreview(KeyboardPreview):
    def __init__(self, parent, binding=None, on_pick=None, on_finish=None):
        super().__init__(parent, binding, on_pick, on_finish)
        self.configure(width=145, height=158)

    def draw(self):
        self.delete('all')
        active = highlighted_keys(self.binding) if self.selection is None else self.selection
        self.regions = []
        self.create_polygon(35,25,42,7,73,2,104,7,113,25,118,92,108,132,73,143,39,132,29,92,
                            smooth=True, fill='#131e30', outline='#8b70c5', width=2)
        self.create_line(42,116,52,130,73,136,95,130,104,116,
                         smooth=True, fill='#63dcca', width=2)
        self.create_line(73,10,73,59,fill='#10111b',width=2)
        self.create_line(34,61,111,61,fill='#10111b',width=2)
        for key, coords in [(4,(65,21,81,53)), (6,(25,66,36,88)), (5,(25,94,36,116))]:
            self.regions.append((*coords,key))
            if key in active:
                x1,y1,x2,y2 = coords
                self.create_rectangle(x1-3,y1-3,x2+3,y2+3,fill='#285851',outline='#3f8c80')
            self.create_rectangle(*coords,fill='#6ce5ce' if key in active else '#495674',
                                  outline='#bcfff1' if key in active else '#6c7f9f',width=2)
        for y in (28,34,40,46):
            self.create_line(68,y,78,y,fill='#10111b',width=1)
        self.create_text(76,103,text='CS',fill='#b69aff',font=('Segoe UI',14,'bold'))
        self.create_text(73,153,text='Wheel + side buttons',fill='#a6acc6',font=('Segoe UI',8))
