"""On-demand English setup and help. No account data or messages are collected."""
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

SETUP_URL = 'https://learn.chatgpt.com/docs/windows/windows-app'
SECTIONS = {'Get started': ('Start here',
                 'If you have not finished installation, run Install ChatShift.cmd from the '
                 'extracted download and wait for Setup complete. It installs the voice components '
                 'and downloads Whisper. Keep that folder; the desktop shortcut uses it.\n\n'
                 '1. Install Codex using the link below.\n'
                 'Open the official Codex setup page ↗\n'
                 '\n'
                 '2. Open Codex and choose to sign in with ChatGPT. Follow the sign-in steps '
                 'using the same account you use for ChatGPT. If you are already signed in, '
                 'you can skip this step.\n'
                 'You do not need to start a chat or type a prompt. ChatShift sets up '
                 'the translator automatically.\n'
                 '\n'
                 '3. Open ChatShift. It connects to your translator. Wait until the status '
                 'at the top right lights up green and says READY. Green means it is ready '
                 'to use; grey means it is not ready. This usually takes a few seconds.\n'
                 '\n'
                 '4. Choose From and To. These languages apply to both text and voice.\n'
                 '\n'
                 '5. Open Text and turn on Enable text translation, or open Voice and turn on '
                 'Enable voice input. You can use both. Choose your shortcut in the matching tab. '
                 'Changes save automatically.\n'
                 '\n'
                 '6. Leave automatic sending off for your first try. Each tab has its own sending option. '
                 'For a microphone check without a game, open Voice → Microphone test → Open test.\n'
                 '\n'
                 'You need Windows, internet and an account with Codex access. ChatShift connects '
                 'automatically. No API key is needed. This installer is for Windows. '
                 'Check the GitHub platform guide for SteamOS / Linux availability.'),
 'How to use': ('Text or voice. Your choice.',
                'TEXT\n'
                'Open your chat, write a message, then press your text shortcut once.\n'
                '\n'
                'VOICE\n'
                'In Voice, select your microphone and wait for Voice ready. Open your chat first. '
                'Hold your voice shortcut, speak, then release.\n'
                'With Press to start selected, press once to record and again to finish.\n'
                '\n'
                'WAIT FOR THE RESULT\n'
                'Stay in the same field. Do not type or press Enter while waiting.\n'
                '\n'
                'It usually took about 1–3 seconds in our short-message tests. It can take '
                'longer.\n'
                '\n'
                'Voice can take longer. In Text, use Send automatically after translating. '
                'In Voice, use Send voice messages automatically. These options are independent. '
                'Leave them off to read, edit and send the result yourself.\n'
                '\n'
                'ChatShift translates what you send, not other players\' messages. Always open '
                'the chat field first; ChatShift cannot reliably tell whether game chat is open.\n'
                '\n'
                'Run in background hides ChatShift. Pause stops shortcuts. Closing the window '
                'exits it.'),
 'Shortcuts': ('Choose your buttons',
               'A shortcut is the key or mouse button you press to translate.\n'
               '\n'
               'ONE BUTTON\n'
               'Click a key in the keyboard picture, or a button in the mouse picture. It saves '
               'automatically.\n'
               'If the other tab uses that shortcut, it moves to the tab you are editing.\n'
               '\n'
               'A COMBINATION\n'
               '1. Keep the right mouse button held down.\n'
               '2. Click up to 3 buttons in the picture with the left mouse button, one at a time.\n'
               '3. Release the right mouse button to save.\n'
               '\n'
               'REMOVE A BUTTON\n'
               'Click a selected button again. Removing the last one turns the shortcut off.\n'
               '\n'
               'The highlighted buttons show your choice. Right and left keys are separate. Num '
               'Enter is separate from Enter. Dimmed keys cannot be chosen.\n'
               '\n'
               'Right mouse is only for selecting the combination. You do not need it when '
               'translating.\n'
               '\n'
               'CONTROLLER\n'
               'Open Controller and turn on Enable controller. Select Text or Voice, then click '
               'up to 3 buttons in the controller picture. Click again to remove. Changes save '
               'automatically. Text or Voice must also be enabled in its own tab.\n'
               'FRONT shows the normal buttons. BACK shows R4, R5, L4 and L5, labelled by the '
               'hand you use while holding the controller.\n'
               'Rear buttons need mapping to a keyboard shortcut in Steam Input or compatible '
               'controller software. Clicking a rear button explains the setup; it does not map '
               'the button for you. Controller buttons also reach the game, so choose an unused combination.'),
 'Troubleshooting': ('Need a hand?',
                     'NOT READY\n'
                     'Check your internet. Open Codex and sign in. Restart ChatShift.\n'
                     '\n'
                     'SHORTCUT DOES NOTHING\n'
                     'Turn on Text translation or Voice input. Check that ChatShift is not paused and a shortcut '
                     'is selected. Open your chat field and use the highlighted buttons.\n'
                     '\n'
                     'WRONG WORDS\n'
                     'Check From and To. Turn off automatic sending so you can correct the '
                     'result. For voice, open Voice → Microphone test → Open test and compare '
                     'the recognized text with the translation. Names and dialect words can be '
                     'misheard even when the correct language is selected.\n'
                     '\n'
                     'TRANSLATION STOPPED\n'
                     'Check the message before trying again. Stay in the same field while '
                     'waiting.\n'
                     '\n'
                     'WORKS IN ONE APP, BUT NOT ANOTHER\n'
                     'Some games handle chat differently. Try another shortcut. Not every game is '
                     'supported. For keypad numbers, turn Num Lock on.\n'
                     'If Alt + Enter changes fullscreen mode, the game received that shortcut. '
                     'Check that ChatShift is active or choose another combination.\n'
                     '\n'
                     'VOICE DOES NOT START\n'
                     'Enable Voice input, choose a voice shortcut and wait for Voice ready. '
                     'Open your game chat before speaking. Under Microphone test, click Open test '
                     'to check what the microphone hears. The test never types into your game.\n'
                     '\n'
                     'WRONG MICROPHONE\n'
                     'Choose your headset or microphone in Voice. This choice resets to the '
                     'system default when you restart ChatShift.\n'
                     '\n'
                     'CONTROLLER DOES NOTHING\n'
                     'Turn on the controller and check its connection status in Controller. '
                     'If needed, try another controller number. Enable the matching Text or Voice '
                     'mode and choose its controller buttons. Rear buttons need the mapping described in Shortcuts.'),
 'Privacy & usage': ('Good to know',
                     'Your messages go to OpenAI for translation and use your Codex allowance. '
                     'Usage limits depend on your account.\n'
                     '\n'
                     'Your language and shortcut choices are saved on your PC. ChatShift does not '
                     'save messages in its settings or status files. Recent translations are kept '
                     'briefly in memory.\n'
                     '\n'
                     'The optional Among Us feature reads the chat field from an image on your PC. '
                     'Only the recognized text is sent for translation.\n'
                     '\n'
                     'Voice records only when you start it. Whisper is AI that runs on your PC; '
                     'it is installed by ChatShift setup, not included with Windows. Audio stays in memory on your PC. '
                     'Recognized text goes to Luna when translation is needed.\n'
                     '\n'
                     'ChatShift uses the clipboard when reading and inserting text. Its contents '
                     'may be replaced.\n'
                     '\n'
                     'ChatShift is an independent project still in development. AI can make '
                     'mistakes.')}


def show_help(root, section=None):
    existing = getattr(root, '_chatshift_help', None)
    if existing is not None and existing.winfo_exists():
        if section in SECTIONS:
            existing.notebook.select(list(SECTIONS).index(section))
        existing.lift()
        return
    dialog = tk.Toplevel(root)
    root._chatshift_help = dialog
    dialog.title('ChatShift · Help & setup')
    dialog.geometry('820x680')
    dialog.minsize(760, 430)
    dialog.configure(bg='#10111b')
    # Reserve this row before packing the expanding text; keep buttons visible at minimum size.
    actions = tk.Frame(dialog, bg='#10111b')
    actions.pack(side='top', fill='x', padx=18, pady=(16, 0))
    def open_setup():
        try:
            if not webbrowser.open(SETUP_URL):
                raise OSError()
        except OSError:
            messagebox.showinfo('Official setup page', 'Open this address in your browser:\n'+SETUP_URL, parent=dialog)
    ttk.Button(actions, text='Close', command=dialog.destroy).pack(side='right')
    notebook = ttk.Notebook(dialog)
    dialog.notebook = notebook
    notebook.pack(fill='both', expand=True, padx=18, pady=(18, 10))
    for title, (heading, body) in SECTIONS.items():
        page = tk.Frame(notebook, bg='#1b1e2e')
        notebook.add(page, text=title)
        scrollbar = ttk.Scrollbar(page)
        scrollbar.pack(side='right', fill='y')
        text = tk.Text(page, wrap='word', bg='#1b1e2e', fg='#f2f3ff', relief='flat',
                       padx=20, pady=18, font=('Segoe UI', 11), spacing3=7,
                       yscrollcommand=scrollbar.set)
        scrollbar.configure(command=text.yview)
        text.pack(fill='both', expand=True)
        text.tag_configure('heading', font=('Segoe UI', 18, 'bold'), foreground='#a8a0ff')
        text.insert('end', heading+'\n\n', 'heading')
        text.insert('end', body)
        if title == 'Get started':
            link_label = 'Open the official Codex setup page ↗'
            start = text.search(link_label, '1.0', stopindex='end')
            text.tag_add('setup_link', start, f'{start}+{len(link_label)}c')
            text.tag_configure('setup_link', foreground='#78f5dd', underline=True)
            text.tag_bind('setup_link', '<Button-1>', lambda event: open_setup())
            text.tag_bind('setup_link', '<Enter>', lambda event, widget=text: widget.configure(cursor='hand2'))
            text.tag_bind('setup_link', '<Leave>', lambda event, widget=text: widget.configure(cursor='arrow'))
        if title == 'Shortcuts':
            text.insert('end', '\n\nAny selectable key can be used alone. While ChatShift is active, '
                        'that key triggers translation instead of its normal action. '
                        'A letter shortcut also prevents typing that letter normally. '
                        'Pause ChatShift to use it normally again.')
        text.configure(state='disabled')
    if section in SECTIONS:
        notebook.select(list(SECTIONS).index(section))
