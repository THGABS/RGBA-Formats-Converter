import tkinter as tk
import os
from PIL import Image, ImageTk
from math import *
from tkinter import messagebox, filedialog

# Notes:
# and here we get a callback when the user hits return.
#self.entry_source.bind('<Key-Return>',
#                      self.print_source_path)

preset_to_config = {'Bedrock MERS to labPBR 1.3':'R = round((1.0-sqrt(b/255))*255)\nG = round((r/255)*225+4)\nB = round((a/255)*190+65)\nA = min(g,254) if g!=0 else 255',
                    'Old SEUS to labPBR 1.3':'R = 255*round(sqrt(r/255)) # convert to perceptual smoothness\nG = round(g*0.8980392156862745) # 0-229 range\nB = 0\nA = 255',
                    'Old Continuum to labPBR 1.3':'R = b\nG = round(g*0.8980392156862745) # 0-229 range\nB = 0\nA = a',
                    'PBR + Emissive (old BSL) to labPBR 1.3':'R = 255*round(sqrt(r/255)) # convert to perceptual smoothness\nG = round(g*0.8980392156862745) # 0-229 range\nB = 0\nA = b-1 # 1-255 to 0-254 range and 0 become 255 with underflow',
                    "Gray to labPBR 1.3 (you probably won't get good results)":'#magic number are 1-x of the one in ITU-R 601-2 (L=R*299/1000+G*587/1000+B*114/1000)\nR = int(r*0.701)\nG = int(g*0.3708901960784314) # 0.3708901960784314 = 0.413*0.8980392156862745\nB = 0\nA = 255',
                    'Custom...':'R = r\nG = g\nB = b\nA = a'}

def try_to_open(source_path):
    '''Try to open an image using Pillow.'''
    try: return Image.open(source_path)
    except: return None

def get_subfolders(root_path:str, prefix:str|None=None):
    '''Get a list of every single subfolder with the root directory given. (DFS/Recursion)'''
    ls:list[str] = []
    for each in os.listdir(root_path):
        path = os.path.join(root_path, each)
        if os.path.isdir(path):
            # Add a prefix if manually assigned or is in a subfolder
            if prefix: each = '/'.join((prefix, each))
            ls.append(each)
            # Extend the list with subfolders of the path (if exist)
            ls.extend(get_subfolders(path, each))
    return ls

def get_imgs(source_path:str, propagate:bool=False, filter:str|None=None):
    '''Get a list of image objects to process from a given source path.'''
    ls:list[Image.Image] = []
    appendable = lambda x,y: (os.path.isfile(x) and filter in y) if filter else lambda x,y: os.path.isfile(x)
    for file_name in os.listdir(source_path):
        file_path = os.path.join(source_path, file_name)
        if appendable(file_path, file_name):
            tried = try_to_open(file_path)
            if tried is not None: ls.append((tried, file_path))
    if propagate:
        for subfolder in get_subfolders(source_path):
            ls += get_imgs(os.path.join(source_path, subfolder), False, filter)
    return ls

class Application(tk.Frame):
    # Theme Palette
    bg_color_header = '#222324'
    bg_color_body = '#313233'
    bg_color_button = '#48494a'
    text_color = '#FFFFFF'
    text_color_button = '#FFFFFF'
    text_color_entry = '#FFFFFF'
    insert_color_entry = text_color_entry
    text_color_checkbox = '#000000'
    bg_color_checkbox = '#FFFFFF'
    bg_color_button_alt = '#d0d1d4'
    bg_color_readonly = '#d0d1d4'
    text_color_button_alt = '#1e1e1f'

    def __init__(self, master=None):
        #super().__init__(master)
        tk.Frame.__init__(self, master=None,
                          bg = self.bg_color_header)
        self.master = master
        self.pack(fill = tk.BOTH,
                  expand=True)
        self.create_widgets()
 
    def create_widgets(self):
        ### Convert button:
        self.convert_button_frame = tk.Frame(bg = self.bg_color_header)
        self.convert_button_frame.pack(fill = tk.BOTH,
                                       expand=True)
        
        self.convert_button = tk.Button(self.convert_button_frame,
                                        fg = 'white',
                                        bg = 'green')
        self.convert_button["text"] = "CONVERT"
        self.convert_button["command"] = self.convert_img
        self.convert_button.pack(padx=10, pady=10)


        ### Source and target path:
        # source:
        self.source_frame = tk.Frame(bg = self.bg_color_header)
        
        self.source_frame.pack(fill = tk.BOTH, expand=True)
        self.entry_source = tk.Entry(master = self.source_frame)

        self.source_path = tk.StringVar()
        self.source_path.set("Put the source path here. It can be a folder with images inside, or simply an image file.")
        self.entry_source["textvariable"] = self.source_path
        
        self.source_button = tk.Button(self.source_frame,
                                       bg = self.bg_color_button,
                                       fg = self.text_color_button)
        self.source_button["text"] = "..."
        self.source_button["command"] = self.open_source_dir_windows

        # target/output:
        self.target_frame = tk.Frame(bg = self.bg_color_header)
        self.target_frame.pack(fill = tk.BOTH, expand=True)
        
        self.entry_output = tk.Entry(master = self.target_frame)

        self.output_path = tk.StringVar()
        self.output_path.set("Put the output path here. It will be created automatically if not existing.")
        
        self.entry_output["textvariable"] = self.output_path
        
        self.target_button = tk.Button(self.target_frame,
                                      bg = self.bg_color_button,
                                      fg = self.text_color_button)
        self.target_button["text"] = "..."
        self.target_button["command"] = self.open_target_dir_windows
        
        # Packing:
        for widget in (self.entry_source, self.entry_output):
            widget.configure(bg = self.bg_color_button,
                             fg = self.text_color_entry,
                             readonlybackground = self.bg_color_readonly,
                             insertbackground = self.insert_color_entry)
            widget.pack(padx=10, pady=10, fill = tk.X, side = "left", expand=True)

        for widget in (self.source_button, self.target_button): widget.pack(padx=5, side = "left")

        # Checkboxes:
        # Overwrite
        self.overwrite_frame = tk.Frame(bg = self.bg_color_body)
        self.overwrite_frame.pack(fill = tk.X)
        self.overwrite_on = tk.BooleanVar()
        self.overwrite_check = tk.Checkbutton(master = self.overwrite_frame,
                                              variable = self.overwrite_on,
                                              onvalue = True,
                                              offvalue = False,
                                              bg = self.bg_color_body,
                                              fg = self.text_color_checkbox,
                                              activebackground = self.bg_color_body,
                                              activeforeground = self.text_color_checkbox,
                                              selectcolor=self.bg_color_checkbox)

        self.overwrite_label = tk.Label(master = self.overwrite_frame,
                                        text = 'Directly output to the source path',
                                        bg = self.bg_color_body,
                                        fg = self.text_color)

        # Propagate
        self.propagate_frame = tk.Frame(bg = self.bg_color_body)
        self.propagate_frame.pack(fill = tk.X)
        self.propagate_on = tk.BooleanVar()
        self.propagate_check = tk.Checkbutton(master = self.propagate_frame,
                                              variable = self.propagate_on,
                                              onvalue = True,
                                              offvalue = False,
                                              bg = self.bg_color_body,
                                              fg = self.text_color_checkbox,
                                              activebackground = self.bg_color_body,
                                              activeforeground = self.text_color_checkbox,
                                              selectcolor=self.bg_color_checkbox)
        self.propagate_label = tk.Label(master = self.propagate_frame,
                                        text = 'Also convert images in subfolder(s)',
                                        bg = self.bg_color_body,
                                        fg = self.text_color)

        ## Filter
        self.filter_frame = tk.Frame(bg = self.bg_color_body)
        self.filter_frame.pack(fill = tk.X)
        self.filter_on = tk.BooleanVar()
        self.filter_check = tk.Checkbutton(master = self.filter_frame,
                                           variable = self.filter_on,
                                           onvalue = True,
                                           offvalue = False,
                                           bg = self.bg_color_body,
                                           fg = self.text_color_checkbox,
                                           activebackground = self.bg_color_body,
                                           activeforeground = self.text_color_checkbox,
                                           selectcolor=self.bg_color_checkbox)

        self.filter_start_label = tk.Label(self.filter_frame,
                                           text = 'Only convert images with keyword ',
                                           bg = self.bg_color_body,
                                           fg = self.text_color)

        self.filter_entry = tk.Entry(self.filter_frame,
                                     state = 'normal' if self.filter_on.get() else 'readonly',
                                     bg = self.bg_color_button,
                                     fg = self.text_color_entry,
                                     readonlybackground = self.bg_color_readonly,
                                     insertbackground = self.insert_color_entry)

        self.filter_end_label = tk.Label(self.filter_frame,
                                         text = ' in their original file names',
                                         bg = self.bg_color_body,
                                         fg = self.text_color)
        
        self.filter_used = tk.StringVar()
        self.filter_used.set("_mers.tga")
        self.filter_entry["textvariable"] = self.filter_used

        # Replace
        self.replace_frame = tk.Frame(bg = self.bg_color_body)
        self.replace_frame.pack(fill = tk.X)
        self.replace_on = tk.BooleanVar()
        self.replace_check = tk.Checkbutton(self.replace_frame,
                                           variable = self.replace_on,
                                           onvalue = True,
                                           offvalue = False,
                                           state = 'normal' if self.filter_on.get() else 'disabled',
                                           bg = self.bg_color_body,
                                           fg = self.text_color_checkbox,
                                           activebackground = self.bg_color_body,
                                           activeforeground = self.text_color_checkbox,
                                           selectcolor=self.bg_color_checkbox)

        self.replace_start_label = tk.Label(self.replace_frame,
                                           text = 'Replace the keyword with ',
                                           bg = self.bg_color_body,
                                           fg = self.text_color)

        self.replace_entry = tk.Entry(self.replace_frame,
                                      state = 'normal' if self.replace_on.get() else 'readonly',
                                      bg = self.bg_color_button,
                                      fg = self.text_color_entry,
                                      readonlybackground = self.bg_color_readonly,
                                      insertbackground = self.insert_color_entry)

        self.replace_end_label = tk.Label(self.replace_frame,
                                           text = ' in output files',
                                           bg = self.bg_color_body,
                                           fg = self.text_color)
        
        self.replace_used = tk.StringVar()
        self.replace_used.set("_s.png")
        self.replace_entry["textvariable"] = self.replace_used
        
        
        for frm in (self.overwrite_frame, self.propagate_frame, self.filter_frame, self.replace_frame):
            for widget in frm.winfo_children():
                widget.pack(side = "left")

        # Update control states
        self.overwrite_on.trace_add('write', self.update_control_state_reversed(self.overwrite_on, self.entry_output))
        self.overwrite_on.trace_add('write', self.update_control_state_reversed(self.overwrite_on, self.target_button))
        self.filter_on.trace_add('write', self.update_control_state(self.filter_on, self.filter_entry))
        self.filter_on.trace_add('write', self.update_control_state(self.filter_on, self.replace_check))
        self.replace_on.trace_add('write', self.update_control_state(self.replace_on, self.replace_entry))

        self.filter_check.select()
        self.propagate_check.select()
        # self.overwrite_check.select()

        ### See preview button:
        self.preview_button_frame = tk.Frame(bg = self.bg_color_body)
        self.preview_button_frame.pack(fill = tk.BOTH,
                                       expand = True)
        
        self.preview = tk.Button(self.preview_button_frame, fg = self.text_color_button_alt, bg = self.bg_color_button_alt)
        self.preview["text"] = "Preview"
        self.preview["command"] = self.display_preview
        self.preview.pack(padx=10, pady=10)


        ### preview:
        self.preview_frame_frame = tk.Frame(bg = self.bg_color_body)
        self.preview_frame_frame.pack(fill = tk.BOTH,
                                      expand = True)
        
        self.preview_frame = tk.Frame(self.preview_frame_frame,
                                      bg = self.bg_color_body)
        self.preview_frame.pack()
        
        self.old_img_canvas = tk.Canvas(self.preview_frame,
                                        height = 130,
                                        width = 130,
                                        bg = '#000000',
                                        bd = 0,
                                        highlightthickness = 0)
        self.old_img_canvas.pack(side = 'left',
                                 padx=10)
        self.new_img_canvas = tk.Canvas(self.preview_frame,
                                        height = 130,
                                        width = 130,
                                        bg = '#000000',
                                        bd = 0,
                                        highlightthickness = 0)
        self.new_img_canvas.pack(side = 'right',
                                 padx=10)
        

        ### Preset selection:
        self.preset_frame = tk.Frame(bg = self.bg_color_body)
        self.preset_frame.pack(fill = tk.X)
        
        self.preset_list = list(preset_to_config)
        self.selected_preset = tk.StringVar()
        self.selected_preset.trace_add("write", self.display_config_text)
        
        self.preset_list_menu = tk.OptionMenu(self.preset_frame,
                                              self.selected_preset,
                                              *self.preset_list)
        self.preset_list_menu.configure(bd=0, bg=self.bg_color_button_alt, fg=self.text_color_button_alt)

        self.preset_list_menu.pack(padx=10, pady=10)
        

        ### Config:        
        self.config = tk.Label(text = 'Config:',
                               bg = self.bg_color_body,
                               fg = self.text_color)
        self.config.pack(fill = tk.BOTH,
                         expand = True)

        
        self.config_box_frame = tk.Frame(bg = self.bg_color_body)
        self.config_box_frame.pack(fill = tk.BOTH,
                                   expand = True)
        self.config_box = tk.Text(self.config_box_frame,
                                  bg = self.bg_color_button,
                                  fg = self.text_color_entry,
                                  insertbackground = self.insert_color_entry)
        # to use to get the value: config_box.get("1.0", tk.END)
        self.config_box.pack(side = 'bottom')

        # It's annoying, but there's not really any choice but to put it there...
        self.selected_preset.set(self.preset_list[0])

    def update_control_state(self, variable, control, *args):
        # Somehow it must return a lambda only with no function body, or this function won't work
        return lambda *args: control.config(state='normal' if variable.get() else 'readonly' if isinstance(control, tk.Entry) else 'disabled')

    def update_control_state_reversed(self, variable, control, *args):
        # Somehow it must return a lambda only with no function body, or this function won't work
        return lambda *args: control.config(state='normal' if not variable.get() else 'readonly' if isinstance(control, tk.Entry) else 'disabled')

    def display_config_text(self, *args):
        self.config_box.delete("1.0", tk.END)
        self.config_box.insert("1.0", preset_to_config[self.selected_preset.get()])

    def open_source_dir_windows(self):
        new_path = filedialog.askdirectory()
        if new_path: self.source_path.set(new_path)
    
    def open_target_dir_windows(self):
        new_path = filedialog.askdirectory()
        if new_path: self.output_path.set(new_path)

    def get_expressions(self):
        config_text = self.config_box.get("1.0", tk.END)
        R_expression = config_text[config_text.find('R =')+4:config_text.find('G =')-1]
        G_expression = config_text[config_text.find('G =')+4:config_text.find('B =')-1]
        B_expression = config_text[config_text.find('B =')+4:config_text.find('A =')-1]
        A_expression = config_text[config_text.find('A =')+4::]
        R_expression = compile(R_expression, 'NoSource', 'eval')
        G_expression = compile(G_expression, 'NoSource', 'eval')
        B_expression = compile(B_expression, 'NoSource', 'eval')
        A_expression = compile(A_expression, 'NoSource', 'eval')
        return R_expression, G_expression, B_expression, A_expression

    def convert(self, img: Image.Image):
        """ Return the converted version of img.
        """
        if img.mode != "RGBA": img = img.convert("RGBA")
        l, h = img.size
        converted = img.copy() # Otherwise it will modify the original which breaks preview
        for x in range(l):
            for y in range(h):
                r, g, b, a = converted.getpixel((x, y))
                # I know, "eVal iS DanGErOUs", but you literally see what's gonna be inputed if you take the preset from someone
                # What *is* eval, however, is slow, but that's why compile() is used
                R = eval(self.R_expression)
                G = eval(self.G_expression)
                B = eval(self.B_expression)
                A = eval(self.A_expression)
                # just to make sure, in case it's a custom config:
                if R >= 255: R = 255
                elif R < 0: R = 255 + R
                if G >= 255: G = 255
                elif G < 0: G = 255 + G
                if B >= 255: B = 255
                elif B < 0: B = 255 + B
                if A >= 255: A = 255
                elif A < 0: A = 255 + A
                converted.putpixel((x,y), (R, G, B, A))
        return converted
    
    def convert_img(self, preview=False):
        """ Apply convert() to the images in source_path, and save them in output_path.
            Except if:
                - self.filter_on is True, it apply convert() only to the remaining image
                - self.propagate_on is True, it convert sub_floder images too (need self.overwrite_on = True)
                - self.overwrite_on is True, it save them in their original location
                - preview is True, it take the first image to convert and display it converted in preview
        """
        source_path  = self.source_path.get()
        filter_on    = self.filter_on.get()
        replace_on = self.replace_on.get()
        filter_used  = self.filter_used.get() if filter_on else ''
        replace_with  = self.replace_used.get() if replace_on else ''
        propagate_on = self.propagate_on.get()
        overwrite_on = self.overwrite_on.get()
        
        # get what we have to convert:
        if os.path.isfile(source_path):
            tried = try_to_open(source_path)
            if tried is None:
                messagebox.showwarning('Unsupported or not an image', 'This file is either in an unsupported format, or not an image.')
                return
            else:
                to_convert_list = [(tried, source_path)]
                source_path = os.path.dirname(source_path)

        elif os.path.isdir(source_path):
            to_convert_list = get_imgs(source_path, propagate_on, filter_used)
            if len(to_convert_list) == 0:
                messagebox.showwarning('No images in directory', 'There is no compatible image in the specified directory.')
                return
        else:
            messagebox.showwarning('Not a valid path', 'The current input path is not a folder of images or an image.')
            return

        # We get the expressions from config:
        try:
            expressions = self.get_expressions()
            self.R_expression, self.G_expression, self.B_expression, self.A_expression = expressions
        except:
            messagebox.showwarning('Invalid config', 'The current config seems to cause issues.')
            return

        # then we convert:
        if preview:
            old = to_convert_list[0][0]
            new = self.convert(old)
            print("Image Size:", old.size)
            if old.size != (128, 128): old = old.resize((128, 128), resample = Image.NEAREST)
            if new.size != (128, 128): new = new.resize((128, 128), resample = Image.NEAREST)
            # self.old_tkv and self.new_tkv because of a tkinter referencement bug
            self.old_tkv = ImageTk.PhotoImage(old)
            self.old_img_canvas.create_image(65, 65, image = self.old_tkv)
            self.new_tkv = ImageTk.PhotoImage(new)
            self.new_img_canvas.create_image(65, 65, image = self.new_tkv)
            print('Preview created:', to_convert_list[0][1])
        else:
            img_ls: list[Image.Image] = []
            for to_convert in to_convert_list:
                try:
                    img_ls.append(self.convert(to_convert[0]))
                except:
                    messagebox.showwarning('Config caused crash during conversion', 'The current config have a valid syntax bpput must have some problems (most likely a 0div) as it caused a crash during conversion.')
                    return
            # Save part:
            output_file_paths = [to_convert[1].replace(filter_used, replace_with) for to_convert in to_convert_list] if (filter_on and replace_on) else [to_convert[1] for to_convert in to_convert_list]
            if not overwrite_on:
                output_path = self.output_path.get()
            # Try to create output folders if not exist
                def try_to_create_folder(path):
                    if not os.path.exists(path):
                        try:
                            os.makedirs(path, exist_ok=True)
                            print('Folder created:', path)
                        except Exception as ex:
                            print('Invalid output path:', path)
                            print(ex)
                            messagebox.showerror('Invalid output path', 'The output path is invalid.\n{}'.format(ex))
                try_to_create_folder(output_path)
                if propagate_on:
                    for subfolder in get_subfolders(source_path):
                        try_to_create_folder(os.path.join(output_path, subfolder))
                output_file_paths = [output_file.replace(source_path, output_path) for output_file in output_file_paths]
            for img, output_file_path in zip(img_ls, output_file_paths):
                img.save(output_file_path)
                print("Saved:", output_file_path)
            print("Output completed.")
        messagebox.showinfo('Conversion completed', 'RGBA formats of all images are successfully converted.')

    def display_preview(self):
        """ Convert and display one image with current preset without saving it."""
        self.convert_img(preview = True)

    def print_source_path(self, event):
        print("source_path: ", self.source_path.get())

root = tk.Tk()
app = Application(master=root)

app.master.title("RGBA Formats Converter")
root.geometry("640x720+128+64")
app.mainloop()
