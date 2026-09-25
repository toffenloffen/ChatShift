"""Clickable Xbox-style controller diagram, drawn with native Tk shapes."""
import tkinter as tk


class ControllerPreview(tk.Canvas):
    def __init__(self, parent, on_pick):
        super().__init__(parent, width=700, height=325, bg='#1b1e2e', highlightthickness=0)
        self.on_pick = on_pick
        self.selection = set()
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

    def rounded(self, x1, y1, x2, y2, **options):
        radius = min(12, (y2-y1)/2, (x2-x1)/2)
        return self.create_polygon(x1+radius, y1, x2-radius, y1, x2, y1,
            x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2,
            x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1,
            smooth=True, splinesteps=24, **options)

    def draw(self):
        self.delete('all')
        # Geometry traced from the supplied reference, in its original proportions.
        def xy(points):
            return [v for x,y in points for v in ((x-58)*1.55,(y-139)*1.55)]
        reference={
          'LT':(159,144,200,158,'LT',False),'RT':(366,144,407,158,'RT',False),
          'LB':(154,161,195,175,'LB',False),'RB':(371,161,412,175,'RB',False),
          'Left stick click':(197,205,223,231,'LS',True),
          'View':(255,211,271,227,'View',True),'Menu':(295,211,311,227,'Menu',True),
          'D-pad Up':(239,242,251,257,'↑',False),'D-pad Down':(239,271,251,286,'↓',False),
          'D-pad Left':(223,258,238,270,'←',False),'D-pad Right':(252,258,267,270,'→',False),
          'Right stick click':(308,250,334,276,'RS',True),
          'Y':(348,192,367,211,'Y',True),'X':(330,211,349,230,'X',True),
          'B':(367,211,386,230,'B',True),'A':(348,230,367,249,'A',True),
          'Rear L4 (left hand, upper)':(79,211,126,234,'L4',False),
          'Rear L5 (left hand, lower)':(79,238,126,260,'L5',False),
          'Rear R4 (right hand, upper)':(439,211,486,234,'R4',False),
          'Rear R5 (right hand, lower)':(439,238,486,260,'R5',False)}
        self.buttons={n:(*xy([(v[0],v[1]),(v[2],v[3])]),v[4],v[5]) for n,v in reference.items()}
        # Button centers measured on the shared cutout, mapped to its display bounds.
        def box(x1,y1,x2,y2):
            return (136+(x1-80)*420/1475,28+(y1-12)*280/938,
                    136+(x2-80)*420/1475,28+(y2-12)*280/938)
        internal = {
            'Left stick click':(351,249,521,419),
            'Right stick click':(933,465,1103,635),
            'View':(671,297,752,379),'Menu':(877,297,958,379),
            'Y':(1157,201,1264,308),'X':(1067,297,1173,403),
            'B':(1255,297,1361,403),'A':(1157,391,1264,498),
            'D-pad Up':(577,453,655,524),'D-pad Down':(577,610,655,680),
            'D-pad Left':(497,530,572,602),'D-pad Right':(660,530,735,602)}
        for name, coords in internal.items():
            old=self.buttons[name]
            self.buttons[name]=(*box(*coords),old[4],old[5])
        for x,title in ((102,'LEFT HAND'),(463,'RIGHT HAND')):
            self.create_text(*xy([(x,201)]),text=title,fill='#a6acc6',font=('Segoe UI',8,'bold'))
            self.create_text(*xy([(x,271)]),text='Rear buttons',fill='#a6acc6',font=('Segoe UI',8))
            self.create_text(*xy([(x,281)]),text='Click to set up',fill='#a6acc6',font=('Segoe UI',8))
        face_colors = {'A': '#80dc9b', 'B': '#ff969f', 'X': '#8cc9ff', 'Y': '#ffe193'}
        for index, (name, (x1, y1, x2, y2, label, round_button)) in enumerate(self.buttons.items()):
            if name in internal:
                continue
            tag = 'button_' + str(index)
            selected = name in self.selection
            color = '#c1fff1' if selected else '#40526b'
            shape = self.create_oval if round_button else self.rounded
            if selected:
                shape(x1-3, y1-3, x2+3, y2+3, fill='#285851' if selected else '#1b2032',
                      outline=color, width=2, tags=tag)
            if not name.startswith('D-pad') or selected:
                shape(x1, y1, x2, y2, fill='#77f2db' if selected else '#202c40',
                  outline=color, width=1, tags=(tag, 'sculpted') if round_button and not selected else tag)
            if 'stick click' in name:
                self.create_oval(x1+7, y1+7, x2-7, y2-7, outline='#d6fff5' if selected else '#3a4662', width=2, tags=tag)
            self.create_text((x1+x2)/2, (y1+y2)/2, text=('▣' if name == 'View' else '≡' if name == 'Menu' else label),
                             fill='#10111b' if selected else face_colors.get(name, '#e2e7fa'),
                             font=('Segoe UI', 10, 'bold'), tags=tag)
            if name in ('View', 'Menu'):
                self.create_text((x1+x2)/2, y2+12, text=label, fill='#a6acc6', font=('Segoe UI', 8))
        from canvas_render import render
        from PIL import Image, ImageTk, ImageDraw
        from pathlib import Path
        surface = render(self, 700, 325)
        if surface is not None:
            frame = ImageTk.getimage(surface).convert('RGBA')
            if not hasattr(self, 'artwork'):
                source = Image.open(Path(__file__).with_name('assets') / 'controller-cutout.png').convert('RGBA')
                self.artwork = source.crop((80,12,1555,950)).resize((420,280),Image.Resampling.LANCZOS)
            frame.alpha_composite(self.artwork,(136,28))
            overlay=Image.new('RGBA',frame.size)
            pen=ImageDraw.Draw(overlay)
            for name in self.selection & internal.keys():
                x1,y1,x2,y2,_,round_button=self.buttons[name]
                method=pen.ellipse if round_button else pen.rounded_rectangle
                method((x1,y1,x2,y2),fill=(65,235,174,110),outline=(119,242,219,255),width=2)
            frame=Image.alpha_composite(frame,overlay)
            self.rendered=ImageTk.PhotoImage(frame,master=self)
            self.create_image(0,0,image=self.rendered,anchor='nw')
