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

    def rounded(self, x1, y1, x2, y2, radius=4, **options):
        r = min(radius, (x2-x1)/2, (y2-y1)/2)
        return self.create_polygon(x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,
            x2,y2-r,x2,y2,x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,
            x1,y1+r,x1,y1, smooth=True, splinesteps=24, **options)

    def render_picture(self, width, height):
        from canvas_render import render
        self.rendered = render(self, width, height)
        if self.rendered is not None:
            self.create_image(0, 0, image=self.rendered, anchor='nw')

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
        unit = (max(self.winfo_width(), 400)-10) / 23.4
        self.rounded(1, 1, max(self.winfo_width(),400)-1, 174, radius=13,
                     fill='#202b3f', outline='#415478', width=3, tags='shell')
        def keycap(label, key, x, row, width=1, height=1):
            left, top = 7+x*unit, 10+row*26
            right, bottom = left+width*unit-3, top+height*26-3
            selected = key in active if key is not None else False
            if key in KEY_NAMES or key in MODIFIER_NAMES:
                self.regions.append((left, top, right, bottom, key))
            if selected:
                self.rounded(left-2, top-2, right+2, bottom+3, fill='#285851', outline='#77f2db')
            self.rounded(left, top+2, right, bottom+2, fill='#090c16', outline='')
            self.rounded(left, top, right, bottom,
                fill='#77f2db' if selected else '#202c40', outline='#c1fff1' if selected else '#0a1423')
            self.create_line(left+2, top+2, right-2, top+2,
                fill='#d6fff5' if selected else '#34465e')
            self.create_text((left+right)/2, (top+bottom)/2, text=label,
                fill='#10111b' if selected else ('#bdc5e1' if key is not None else '#8994ac'),
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
        for col,label in enumerate(('PrtSc','ScrLk','Pause')):
            keycap(label,None,15.4+col,0)
        self.render_picture(max(self.winfo_width(),400),176)


class MousePreview(KeyboardPreview):
    def __init__(self, parent, binding=None, on_pick=None, on_finish=None):
        super().__init__(parent, binding, on_pick, on_finish)
        self.configure(width=120, height=176)

    def draw(self):
        self.delete('all')
        active = highlighted_keys(self.binding) if self.selection is None else self.selection
        self.regions = []
        self.create_polygon(37,32,43,16,62,7,86,7,107,17,114,34,
                            119,89,118,120,107,140,87,148,64,147,44,137,35,118,34,85,
                            smooth=True, fill='#263348', outline='#526079', width=1, tags='shell')
        self.create_polygon(40,78,66,89,100,77,113,63,118,100,114,128,
                            99,142,76,148,55,142,41,127,36,107,
                            smooth=True,fill='#1c273a',outline='')
        self.create_line(44,132,55,143,76,148,96,141,109,129,
                         smooth=True, fill='#45d9e9', width=2)
        self.create_line(76,9,76,78,fill='#101927',width=1)
        for key, coords in [(4,(70,21,81,47)), (6,(31,65,37,86)), (5,(31,90,37,112))]:
            self.regions.append((*coords,key))
            if key in active:
                x1,y1,x2,y2 = coords
                self.rounded(x1-3,y1-3,x2+3,y2+3,fill='#285851',outline='#3f8c80')
            self.rounded(*coords,fill='#6ce5ce' if key in active else ('#6851a0' if key == 4 else '#36445c'),
                                  outline='#bcfff1' if key in active else '#6c7f9f',width=2)
        self.create_text(76,120,text='CS',fill='#b69aff',font=('Segoe UI',14,'bold'))
        self.create_text(62,167,text='Wheel + side buttons',fill='#a6acc6',font=('Segoe UI',7))
        self.render_picture(120,176)


class KeyboardMousePreview(KeyboardPreview):
    """One shared reference image and matching hit areas for both chat modes."""
    def __init__(self, parent, binding=None, on_pick=None, on_finish=None):
        from PIL import Image
        from pathlib import Path
        cutout = Image.open(Path(__file__).with_name('assets') / 'keyboard-mouse-cutout.png').convert('RGBA')
        # Place the cutout components on the established interaction coordinate grid.
        self.artwork = Image.new('RGBA', (755, 180))
        keyboard = cutout.crop((38, 103, 1834, 582)).resize((624, 164), Image.Resampling.LANCZOS)
        mouse = cutout.crop((1886, 135, 2132, 548)).resize((87, 137), Image.Resampling.LANCZOS)
        self.artwork.alpha_composite(keyboard, (9, 2))
        self.artwork.alpha_composite(mouse, (656, 12))
        super().__init__(parent, binding, on_pick, on_finish)
        self.configure(width=self.artwork.width, height=self.artwork.height)

    def draw(self):
        from PIL import Image, ImageDraw, ImageTk
        self.delete('all')
        active = highlighted_keys(self.binding) if self.selection is None else self.selection
        boxes = []
        def key(vk, x, y, w=25, h=22):
            boxes.append((x, y, x+w, y+h, vk))
        key(27,18,12,29)
        for i,x in enumerate((62,90,118,146,184,212,240,268,305,333,361,389)):
            key(112+i,x,12)
        for i in range(10): key(ord(str((i+1)%10)),45+i*27.7,37)
        key(8,374,37,45)
        key(9,18,61,39)
        for i,c in enumerate('QWERTYUIOP'): key(ord(c),59+i*27.7,61)
        key(13,369,85,50)
        for i,c in enumerate('ASDFGHJKL'): key(ord(c),66+i*27.7,85)
        key(0xA0,18,109,59); key(0xA1,353,109,66)
        for i,c in enumerate('ZXCVBNM'): key(ord(c),79+i*27.7,109)
        for vk,x,w in ((0xA2,18,34),(0xA4,90,33),(32,125,174),(0xA5,302,34),(0xA3,379,40)):
            key(vk,x,133,w)
        for y,keys in ((37,(45,36,33)),(61,(46,35,34)),(133,(37,40,39))):
            for i,vk in enumerate(keys): key(vk,429+27.5*i,y)
        key(38,457,109)
        for y,keys in ((61,(103,104,105)),(85,(100,101,102)),(109,(97,98,99))):
            for i,vk in enumerate(keys): key(vk,520+27.7*i,y)
        for vk,x,y,w,h in ((111,548,37,25,22),(106,576,37,25,22),(109,604,37,22,22),
                             (107,604,61,22,46),(NUMPAD_ENTER,604,109,22,46),
                             (96,520,133,53,22),(110,576,133,25,22),
                             (4,692,25,12,26),(6,657,61,9,24),(5,657,86,9,25)):
            key(vk,x,y,w,h)
        width=max(1,self.winfo_width())
        scale=min(1.0,width/self.artwork.width) if width>1 else 1.0
        frame=self.artwork.copy()
        # A translucent green overlay keeps the original lettering and artwork.
        tint=Image.new('RGBA',frame.size)
        pen=ImageDraw.Draw(tint)
        for x1,y1,x2,y2,vk in boxes:
            if vk in active:
                pen.rounded_rectangle((x1,y1,x2,y2),radius=3,fill=(65,235,174,115),outline=(119,242,219,255),width=2)
        frame=Image.alpha_composite(frame.convert('RGBA'),tint)
        size=(round(self.artwork.width*scale),round(self.artwork.height*scale))
        if size!=frame.size: frame=frame.resize(size,Image.Resampling.LANCZOS)
        self.rendered=ImageTk.PhotoImage(frame,master=self)
        self.create_image(0,0,image=self.rendered,anchor='nw')
        self.regions=[(a*scale,b*scale,c*scale,d*scale,k) for a,b,c,d,k in boxes]
        if int(self.cget('height'))!=size[1]: self.configure(height=size[1])
