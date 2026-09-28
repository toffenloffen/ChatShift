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



def keyboard_mouse_regions():
    """Keycap bounds traced on the 2048-wide reference, then mapped with the artwork."""
    boxes = []
    ratio = 2172 / 2048
    def key(vk, left, top, right, bottom, mouse=False):
        crop_x, crop_y, sx, sy, dx, dy = ((1886,135,87/246,137/413,656,12)
            if mouse else (38,103,624/1796,164/479,9,2))
        boxes.append(((left*ratio-crop_x)*sx+dx, (top*ratio-crop_y)*sy+dy,
                      (right*ratio-crop_x)*sx+dx, (bottom*ratio-crop_y)*sy+dy, vk))
    key(27,68,134,146,187)
    for i,x in enumerate((188,262,336,408,516,589,663,736,843,918,995,1075)):
        key(112+i,x,134,x+63,187)
    for i,x in enumerate((143,217,291,365,439,512,586,660,734,808)):
        key(ord(str((i+1)%10)),x,202,x+65,255)
    key(8,1031,202,1144,255)
    key(9,68,266,166,319)
    for c,x in zip('QWERTYUIOP',(178,252,326,400,474,548,622,696,770,844)):
        key(ord(c),x,266,x+64,319)
    key(13,1010,330,1144,383)
    for c,x in zip('ASDFGHJKL',(198,272,346,420,494,568,642,716,790)):
        key(ord(c),x,330,x+64,383)
    key(0xA0,68,394,227,447); key(0xA1,972,394,1144,447)
    for c,x in zip('ZXCVBNM',(238,311,385,459,533,607,681)):
        key(ord(c),x,394,x+64,447)
    for vk,l,r in ((0xA2,68,158),(0xA4,262,349),(32,359,819),
                   (0xA5,831,920),(0xA3,1032,1144)):
        key(vk,l,458,r,514)
    for top,keys in ((202,(45,36,33)),(266,(46,35,34)),(458,(37,40,39))):
        for vk,x in zip(keys,(1175,1248,1323)): key(vk,x,top,x+63,top+53)
    key(38,1248,394,1313,447)
    for top,keys in ((266,(103,104,105)),(330,(100,101,102)),(394,(97,98,99))):
        for vk,x in zip(keys,(1420,1493,1566)): key(vk,x,top,x+63,top+53)
    for vk,l,t,r,b in ((111,1493,202,1554,255),(106,1566,202,1627,255),
                        (109,1635,202,1695,255),(107,1635,266,1695,383),
                        (NUMPAD_ENTER,1635,394,1695,514),(96,1420,458,1553,514),
                        (110,1566,458,1627,514)):
        key(vk,l,t,r,b)
    key(4,1883,169,1905,232,True)
    key(6,1785,271,1803,324,True)
    key(5,1785,334,1803,386,True)
    return boxes

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
        boxes = keyboard_mouse_regions()
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
        sx, sy = size[0]/self.artwork.width, size[1]/self.artwork.height
        self.regions=[(a*sx,b*sy,c*sx,d*sy,k) for a,b,c,d,k in boxes]
        if int(self.cget('height'))!=size[1]: self.configure(height=size[1])
