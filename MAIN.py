import tkinter as tk
import os
from PIL import Image, ImageTk
from math import *
from tkinter import messagebox, filedialog

# Notes :
# and here we get a callback when the user hits return.
#self.entry_source.bind('<Key-Return>',
#                      self.print_source_path)

preset_to_config = {'Bedrock MERS to labPBR 1.3':'R = round((1.0-sqrt(b/255))*255)\nG = round((r/255)*225+4)\nB = round((a/255)*190+65)\nA = min(g,254) if g!=0 else 0',
                    'Old SEUS to labPBR 1.3':'R = 255*round(sqrt(r/255)) # convert to perceptual smoothness\nG = round(g*0.8980392156862745) # 0-229 range\nB = 0\nA = 255',
                    'Old Continuum to labPBR 1.3':'R = b\nG = round(g*0.8980392156862745) # 0-229 range\nB = 0\nA = a',
                    'PBR + Emissive (old BSL) to labPBR 1.3':'R = 255*round(sqrt(r/255)) # convert to perceptual smoothness\nG = round(g*0.8980392156862745) # 0-229 range\nB = 0\nA = b-1 # 1-255 to 0-254 range and 0 become 255 with underflow',
                    "Gray to labPBR 1.3 (you probably won't get good results)":'#magic number are 1-x of the one in ITU-R 601-2 (L=R*299/1000+G*587/1000+B*114/1000)\nR = int(r*0.701)\nG = int(g*0.3708901960784314) # 0.3708901960784314 = 0.413*0.8980392156862745\nB = 0\nA = 255',
                    'Custom...':'R = r\nG = g\nB = b\nA = a'}

def try_to_open(source_path):
    try: return Image.open(source_path)
    except: return None

def add_imgs_with_propagation(source_path,to_convert_list,filter_on,filter_used):
    for file_name in os.listdir(source_path):
        file_path = os.path.join(source_path, file_name)
        if os.path.isfile(file_path):
            if filter_on:
                if filter_used in file_name:
                    tried = try_to_open(file_path)
                    if tried is not None: to_convert_list.append((tried, file_path))
            else:
                tried = try_to_open(file_path)
                if tried is not None: to_convert_list.append((tried, file_path))
        else: add_imgs_with_propagation(file_path,to_convert_list,filter_on,filter_used)

class Application(tk.Frame):
    # Color Palette
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
        ### Convert button :
        self.convert_button_frame = tk.Frame(bg = self.bg_color_header)
        self.convert_button_frame.pack(fill = tk.BOTH,
                                       expand=True)
        
        self.convert_button = tk.Button(self.convert_button_frame,
                                        fg = 'white',
                                        bg = 'green')
        self.convert_button["text"] = "CONVERT"
        self.convert_button["command"] = self.convert_img
        self.convert_button.pack(padx=10, pady=10)


        ### Source and cible path :
        # source :
        self.source_frame = tk.Frame(bg = self.bg_color_header)
        
        self.source_frame.pack(fill = tk.BOTH, expand=True)
        self.entry_source = tk.Entry(master = self.source_frame)

        self.source_path = tk.StringVar()
        self.source_path.set("put the source path here. It can be a folder with images inside, or directly the path to a image.")
        self.entry_source["textvariable"] = self.source_path
        
        self.source_button = tk.Button(self.source_frame,
                                       bg = self.bg_color_button,
                                       fg = self.text_color_button)
        self.source_button["text"] = "..."
        self.source_button["command"] = self.open_source_dir_windows

        # cible/output :
        self.cible_frame = tk.Frame(bg = self.bg_color_header)
        self.cible_frame.pack(fill = tk.BOTH, expand=True)
        
        self.entry_output = tk.Entry(master = self.cible_frame)

        self.output_path = tk.StringVar()
        self.output_path.set("put the ouput path here.")
        
        self.entry_output["textvariable"] = self.output_path
        
        self.cible_button = tk.Button(self.cible_frame,
                                      bg = self.bg_color_button,
                                      fg = self.text_color_button)
        self.cible_button["text"] = "..."
        self.cible_button["command"] = self.open_cible_dir_windows
        
        # Packing :
        for widget in (self.entry_source, self.entry_output):
            widget.configure(bg = self.bg_color_button,
                             fg = self.text_color_entry,
                             insertbackground = self.insert_color_entry)
            widget.pack(padx=10, pady=10, fill = tk.X, side = "left", expand=True)

        for widget in (self.source_button, self.cible_button):  widget.pack(padx=5, side = "left")
        

        # Checkboxes:
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

        self.filter_label = tk.Label(master = self.filter_frame,
                                           text = 'Only convert image with keyword ',
                                           bg = self.bg_color_body,
                                           fg = self.text_color)

        self.filter_entry = tk.Entry(master = self.filter_frame,
                                     bg = self.bg_color_button,
                                     fg = self.text_color_entry,
                                     insertbackground = self.insert_color_entry)
        self.filter_used = tk.StringVar()
        self.filter_used.set("_mers.tga")
        self.filter_entry["textvariable"] = self.filter_used

        self.replace_frame = tk.Frame(bg = self.bg_color_body)
        self.replace_frame.pack(fill = tk.X)

        # Replace
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
                                           text = 'Replace the key word with ',
                                           bg = self.bg_color_body,
                                           fg = self.text_color)

        self.replace_entry = tk.Entry(self.replace_frame,
                                     bg = self.bg_color_button,
                                     fg = self.text_color_entry,
                                     insertbackground = self.insert_color_entry)
        self.replace_used = tk.StringVar()
        self.replace_used.set("_s.png")
        self.replace_entry["textvariable"] = self.replace_used
        
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
                                        text = 'Overwrite original instead of outputing to output path',
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
                                              state = 'normal' if self.overwrite_on.get() else 'disabled',
                                              bg = self.bg_color_body,
                                              fg = self.text_color_checkbox,
                                              activebackground = self.bg_color_body,
                                              activeforeground = self.text_color_checkbox,
                                              selectcolor=self.bg_color_checkbox)
        self.propagate_label = tk.Label(master = self.propagate_frame,
                                        text = 'Propagate the conversion to sub-folder (work only in overwrite mode)',
                                        bg = self.bg_color_body,
                                        fg = self.text_color)

        for frm in (self.filter_frame, self.replace_frame, self.overwrite_frame, self.propagate_frame):
            for widget in frm.winfo_children():
                widget.pack(side = "left")

        # Update control states
        self.filter_on.trace_add('write', self.update_control_state(self.filter_on, self.replace_check))
        self.replace_on.trace_add('write', self.update_control_state(self.replace_on, self.replace_entry))
        self.overwrite_on.trace_add('write', self.update_control_state(self.overwrite_on, self.propagate_check))

        self.filter_check.select()
        # self.overwrite_check.select()
        # self.propagate_check.select()

        ### See preview button :
        self.preview_button_frame = tk.Frame(bg = self.bg_color_body)
        self.preview_button_frame.pack(fill = tk.BOTH,
                                       expand = True)
        
        self.preview = tk.Button(self.preview_button_frame, fg = self.text_color_button_alt, bg = self.bg_color_button_alt)
        self.preview["text"] = "See preview"
        self.preview["command"] = self.display_preview
        self.preview.pack(padx=10, pady=10)


        ### preview :
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
        

        ### Preset selection :
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
        

        ### Config :        
        self.config = tk.Label(text = 'Config :',
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
        # to use to get the value : config_box.get("1.0", tk.END)
        self.config_box.pack(side = 'bottom')

        # It's annoying, but there's not really any choice but to put it there...
        self.selected_preset.set(self.preset_list[0])

    def update_control_state(self, variable, control, *args):
        # Somehow it must return a lambda only with no function body, or this function won't work
        return lambda *args: control.config(state='normal' if variable.get() else 'readonly' if isinstance(control, tk.Entry) else 'disabled')

    def display_config_text(self, *args):
        self.config_box.delete("1.0", tk.END)
        self.config_box.insert("1.0", preset_to_config[self.selected_preset.get()])

    def open_source_dir_windows(self):
        self.source_path.set(filedialog.askdirectory())
    
    def open_cible_dir_windows(self):
        self.output_path.set(filedialog.askdirectory())

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

    def convert(self, img):
        """ Return the converted version of img.
        """
        if img.mode != "RGBA": img = img.convert("RGBA")
        l, h = img.size
        being_converted = img.copy() #otherwise it modify the original which bug preview
        for x in range(l):
            for y in range(h):
                r, g, b, a = being_converted.getpixel((x, y))
                # I know, "eVal iS DanGErOUs", but you literally see what's gonna be inputed if you take the preset from someone
                # What *is* eval, however, is slow, but that's why compile() is used
                R = eval(self.R_expression)
                G = eval(self.G_expression)
                B = eval(self.B_expression)
                A = eval(self.A_expression)
                # just to make sure, in case it's a custom config :
                if R >= 255: R = 255
                elif R < 0: R = 255 + R
                if G >= 255: G = 255
                elif G < 0: G = 255 + G
                if B >= 255: B = 255
                elif B < 0: B = 255 + B
                if A >= 255: A = 255
                elif A < 0: A = 255 + A
                being_converted.putpixel((x,y), (R, G, B, A))
        return being_converted
    
    def convert_img(self, preview=False):
        """ Apply convert() to the images in source_path, and save them in output_path.
            Except if :
                - self.filter_on is True, it apply convert() only to the remaining image
                - self.propagate_on is True, it convert sub_floder images too (need self.overwrite_on = True)
                - self.overwrite_on is True, it save them in their original location
                - preview is True, it take the first image to convert and display it converted in preview
        """
        to_convert_list = []
        source_path  = self.source_path.get()
        filter_on    = self.filter_on.get()
        replace_on = self.replace_on.get()
        filter_used  = self.filter_used.get()
        replace_with  = self.replace_used.get()
        propagate_on = self.propagate_on.get()
        overwrite_on = self.overwrite_on.get()
        
        # get what we have to convert :
        if os.path.isfile(source_path):
            tried = try_to_open(source_path)
            if tried is None:
                messagebox.showwarning('Unsuported, or not a image.', 'This file is either in a unsuported format, or not a image.')
                return None
            else: to_convert_list = [(tried, source_path)]

        elif os.path.isdir(source_path):
            if overwrite_on and propagate_on:
                add_imgs_with_propagation(source_path, to_convert_list, filter_on, filter_used)
            else:
                for file_name in os.listdir(source_path):
                    if os.path.isfile(os.path.join(source_path, file_name)):
                        if filter_on:
                            if filter_used in file_name:
                                tried = try_to_open(os.path.join(source_path, file_name))
                                if tried is not None: to_convert_list.append((tried, file_name))
                        else:
                            tried = try_to_open(os.path.join(source_path, file_name))
                            if tried is not None: to_convert_list.append((tried, file_name))

            if len(to_convert_list) == 0:
                messagebox.showwarning('No images in directory.', 'There is no compatible image in the specified directory.')
                return None
        else:
            messagebox.showwarning('Not a valid path.', 'The current input path is not a folder of images or an image.')
            return None

        # We get the expressions from config :
        try:
            expressions = self.get_expressions()
            self.R_expression, self.G_expression, self.B_expression, self.A_expression = expressions
        except:
            messagebox.showwarning('Invalid config.', 'The current config seems to cause issues.')
            return None

        # then we convert :
        if preview:
            old = to_convert_list[0][0]
            new = self.convert(old)
            print(f"size : {old.size}")
            if old.size != (128, 128): old = old.resize((128, 128), resample = Image.NEAREST)
            if new.size != (128, 128): new = new.resize((128, 128), resample = Image.NEAREST)
            # self.old_tkv and self.new_tkv because of a tkinter referencement bug
            self.old_tkv = ImageTk.PhotoImage(old)
            self.old_img_canvas.create_image(65, 65, image = self.old_tkv)
            self.new_tkv = ImageTk.PhotoImage(new)
            self.new_img_canvas.create_image(65, 65, image = self.new_tkv)
            print('Preview created.')
        else:
            output_path = self.output_path.get()
            for to_convert in to_convert_list:
                try:
                    img = self.convert(to_convert[0])
                except:
                    messagebox.showwarning('Config caused crash during conversion.', 'The current config have a valid syntax but must have some problems (most likely a 0div) as it caused a crash during conversion.')
                    return None
                #save part :
                if filter_on:
                    if replace_on: to_convert[1] = to_convert[1].replace(filter_used, replace_with)
                if overwrite_on:
                    if propagate_on: img.save(to_convert[1])
                    else: img.save(os.path.join(source_path, to_convert[1]))
                else: img.save(os.path.join(output_path, to_convert[1].replace('tga','png')))
        
        print("Done.")
        messagebox.showinfo('Conversion complete.', 'Done.\nNo errors where encoutered during the conversion.')

    def display_preview(self):
        """ convert one image with current preset, don't save it and display it """
        self.convert_img(preview = True)

    def print_source_path(self, event):
        print("source_path : ",
              self.source_path.get())

root = tk.Tk()
app = Application(master=root)

app.master.title("RGBA Formats Converter")
root.geometry("640x720+128+64")
app.mainloop()
