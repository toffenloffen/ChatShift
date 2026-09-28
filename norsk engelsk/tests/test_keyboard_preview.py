import unittest
from keyboard_preview import highlighted_keys, ShortcutDraft


class KeyboardPreviewTests(unittest.TestCase):
    def test_every_key_hits_itself_at_each_display_size(self):
        import tkinter as tk
        from types import SimpleNamespace
        from keyboard_preview import KeyboardMousePreview
        root = tk.Tk()
        picked = []
        preview = KeyboardMousePreview(root, on_pick=lambda key, combo: picked.append(key))
        preview.pack(fill='x')
        try:
            for width in (400, 600, 755, 950):
                root.geometry(f'{width}x200'); root.update(); preview.draw()
                self.assertEqual(len({b[4] for b in preview.regions}), len(preview.regions))
                for left, top, right, bottom, key in preview.regions:
                    for x,y in (((left+right)/2,(top+bottom)/2),
                                (left+1,top+1),(right-1,bottom-1)):
                        picked.clear()
                        preview.clicked(SimpleNamespace(x=x,y=y,state=0))
                        self.assertEqual(picked,[key], (width,key,x,y))
        finally:
            root.destroy()

    def test_every_controller_button_hits_itself(self):
        import tkinter as tk
        from types import SimpleNamespace
        from controller_preview import ControllerPreview
        root=tk.Tk(); picked=[]
        preview=ControllerPreview(root,picked.append)
        try:
            for name,(left,top,right,bottom,_,_) in preview.buttons.items():
                picked.clear()
                preview.click_picture(SimpleNamespace(x=(left+right)/2,y=(top+bottom)/2))
                self.assertEqual(picked,[name])
        finally:
            root.destroy()

    def test_default_marks_right_control_and_enter_only(self):
        self.assertEqual(highlighted_keys(None), {0xA3, 13})

    def test_custom_binding_preserves_side_and_letter(self):
        self.assertEqual(highlighted_keys({'modifiers': [0xA2, 0xA1], 'key': 69}),
                         {0xA2, 0xA1, 69})

    def test_altgr_does_not_highlight_synthetic_left_control(self):
        self.assertEqual(highlighted_keys({'modifiers': [0xA2, 0xA5], 'key': 13}),
                         {0xA5, 13})

    def test_f10_marks_only_f10(self):
        self.assertEqual(highlighted_keys({'modifiers': [], 'key': 121}), {121})

    def test_removing_last_key_disables_instead_of_restoring_default(self):
        draft = ShortcutDraft()
        draft.pick(269)
        draft.pick(269)
        self.assertEqual(draft.binding(), {'modifiers': [], 'key': None})
        self.assertEqual(highlighted_keys(draft.binding()), set())

    def test_click_selects_function_key_and_combo_toggles_keys(self):
        draft = ShortcutDraft()
        draft.pick(122)
        self.assertEqual(draft.binding(), {'modifiers': [], 'key': 122})
        draft.pick(0xA5)
        draft.pick(13, combine=True)
        self.assertEqual(draft.binding(), {'modifiers': [0xA5], 'key': 13})
        draft.pick(13, combine=True)
        self.assertEqual(draft.binding(), {'modifiers': [], 'key': 0xA5})

    def test_combo_requires_one_main_key_and_maximum_three_keys(self):
        draft = ShortcutDraft()
        draft.pick(0xA2)
        draft.pick(0xA0, combine=True)
        draft.pick(65, combine=True)
        with self.assertRaises(ValueError):
            draft.pick(66, combine=True)
        self.assertEqual(draft.binding()['key'], 65)
