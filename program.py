
from decimal import Decimal
import time
import webbrowser
import customtkinter
import os.path
from PIL import Image, ImageTk
from tkinter import filedialog
import dictionaries
import json
from customtkinter import CTkToplevel
import subprocess
import concurrent.futures
import threading
import pygame
import sys
from CTkMessagebox import CTkMessagebox
# File path to save the output
file_path = "output.txt"
# Open the file in append mode (creates if not exists)
file = open(file_path, "w+")
# Redirect stdout to the file
sys.stdout = file
sys.stderr = file


# Declare global variables
audio_thread = None
audio_threads = []
languages = []
ffmpeg_processes = []
file_paths = []
futures = []
total_files_to_convert=0
files_finished = 0
output_folder =""
for_small_language_lower = 2
settings_window = None
speed = Decimal('1')
temp_file_play = ""



# Check if ffmpeg is in data folder
ffmpeg_path = 'Data\\ffmpeg.exe'  

# Check if the file exists
if os.path.exists(ffmpeg_path):
    print("YAY FOUND FFMPEG!")
else:
    print("Not found "+ ffmpeg_path)
# Read the configuration file
with open('DATA\\settings.json','r', encoding='UTF-8') as config_file:
    config = json.load(config_file)
    #set the output folder to be the saved output folder
    output_folder = config['output_folder']
#if this is the first time he is opening the app    
# Get the user's home directory
home_dir = os.path.expanduser("~")
if config['output_folder'] ==  "" or home_dir not in config['output_folder']:
    # Construct the path to the Music folder
    music_folder = os.path.join(home_dir, "Music")
    #set the output folder as the users music foder
    config['output_folder'] = music_folder
    #save the change
    with open('DATA\\settings.json', 'w', encoding='UTF-8') as config_file:
        json.dump(config, config_file, indent=4)
speed = Decimal(config["speed"])

# languages get the users language
selected_language = config['language'] 
# this will be the dictionerie that the user uses based on his language
dictionarie = {}
temp_dictionarie = {}
#get the boolean from dictionere whether the app should be left to right or the oppisite
#and gat the dictiopnarie based on selected language
app_direction_ltr = True
for language_dict in dictionaries.language_dicts:
    languages.append(language_dict['language'])
    if selected_language == language_dict['language']:
        dictionarie = language_dict
        app_direction_ltr = language_dict['ltr'] 
if dictionarie["size"] == "n":
    for_small_language_lower = 0
    temp_dictionarie = dictionarie.copy()
#set app apearance
customtkinter.set_appearance_mode("system")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
# create app
app = customtkinter.CTk()  # create CTk window like you do with the Tk window

#the next couple of lines are fro making that the app opens in the middle of the screen (in the x - middle but in the y a little higher then the middle)

# Get the screen width and height
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
# Calculate the window position
window_width = 800  # Specify the window width
window_height = 365  # Specify the window height
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
# Position the window in the middle of the screen
app.geometry(f"{window_width}x{window_height}+{x}+{y-50}")# the reason why there is a -50 is because a. the ribbon\title bar of the window is not included in the calculation but it is between 30 - 35 px b. i want it to be a little higher then the middle of the screen
# 

# Get the path to the icon file
icon_path = os.path.join('DATA', 'icon.ico')
# Set the window icon
app.iconbitmap(icon_path)
#app background color
app.configure(fg_color="#ADD8E6")
# Disable window resizing
app.resizable(False, False)
#app title
app.title(dictionarie['title'])
# #if we want to use a transparent color we use #aaaaaa 
# app.wm_attributes('-transparentcolor', '#aaaaaa')


def change_text(old_dictionarie,new_dictionarie):
    #if change ltr var alert that will only change on restart
    if old_dictionarie["ltr"] != new_dictionarie["ltr"]:
        CTkMessagebox(title="Info", message=new_dictionarie["changeMsg"])
    # Loop through all buttons and labels to change the text
    found_key = None
    for widget in app.winfo_children():
        if isinstance(widget, (customtkinter.CTkButton, customtkinter.CTkLabel)):
            # Iterate over the dictionary to find the key
            for key, value in old_dictionarie.items():
                if value == widget.cget("text"):
                    found_key = key
                    break  # Exit the loop once the key is found
            if found_key is not None:
                widget.configure(text=new_dictionarie[found_key])
                if old_dictionarie["size"] != new_dictionarie["size"]:
                    change = 2
                    if(found_key == "add_files" or found_key == "remove_all_files"):
                        change = change*3.5
                    if new_dictionarie["size"] == "n":
                        print("1" +"\n\n\n\n\n")
                        print(found_key)
                        print(widget.cget("font"))
                        size = int(widget.cget("font")[1])+change
                        print("2" +"\n\n\n\n\n" )
                        widget.configure(font=("Arial", size))
                    else:
                        size = int(widget.cget("font")[1])-change
                        widget.configure(font=("Arial", size))
                found_key = None
                update_files_label(len(file_paths))
    if settings_window is not None:
        for widget in settings_window.winfo_children():
            if isinstance(widget, (customtkinter.CTkButton, customtkinter.CTkLabel)):
                # Iterate over the dictionary to find the key
                for key, value in old_dictionarie.items():
                    if value == widget.cget("text"):
                        found_key = key
                        break  # Exit the loop once the key is found
                if found_key is not None:
                    widget.configure(text=new_dictionarie[found_key])
                    # if old_dictionarie["size"] != new_dictionarie["size"]:
                    #     change = 2
                    #     if(found_key == "add_files" or found_key == "remove_all_files"):
                    #         change = change*3.5
                    #     if new_dictionarie["size"] == "n":
                    #         widget.configure(font=("Arial", widget.cget("font")[1]-size))
                    found_key = None
def change_language(self):
    global dictionarie
    temp_dic = dictionarie
    for language_dict in dictionaries.language_dicts:
        if settings_languagemenu.get() == language_dict['language']:
            dictionarie = language_dict
    change_text(temp_dic,dictionarie)
#------------ OPEN SETTINGS FUNCTION -------------#
def settings_changed_format(choice):
        if (choice == "mp3"):
            settings_bitratemenu.configure(state="normal")
            settings_bitratemenu_var.set(dictionarie["auto"])
            settings_bitratemenu.configure(values=[dictionarie["auto"],"32kbps", "64kbps", "96kbps", "128kbps", "160kbps", "192kbps", "224kbps", "256kbps", "288kbps", "320kbps"])
        elif choice == dictionarie["input"]:
            settings_bitratemenu.configure(state="disabled")
            settings_bitratemenu_var.set(dictionarie["input"])
        else:
            settings_bitratemenu.configure(state="disabled")
            settings_bitratemenu_var.set(dictionarie["auto"])

def settings_open_file_manager():
    global output_folder
    temp = output_folder
    #settings_window.grab_set()
    if settings_window is not None:
        settings_window.transient(settings_window.master)
    output_folder = filedialog.askdirectory()
    if output_folder:
        settings_destination.set(output_folder)
    else:
        output_folder = temp
    if settings_window is not None:
        settings_window.transient(None)


    

#settings save
def save():
    global temp_dictionarie
    temp_dictionarie = dictionarie.copy()
    #open settings file
    with open('DATA\\settings.json','r', encoding='UTF-8') as config_file:
        config = json.load(config_file)
    config['language'] =  settings_languagemenu.get()
    config['format'] = settings_formatmenu.get()
    config['bitrate'] = settings_bitratemenu.get()
    config['output_folder'] = settings_destination.get()
    #save the change
    with open('DATA\\settings.json', 'w', encoding='UTF-8') as config_file:
        json.dump(config, config_file, indent=4)
    if settings_window is not None:
        settings_window.transient(None)
        settings_window.destroy()


#settings cancel   
def cancel():
    global dictionarie
    change_text(dictionarie,temp_dictionarie)
    dictionarie = temp_dictionarie.copy()
    if settings_window is not None:
        settings_window.transient(None)
        settings_window.destroy()
     
#oprn setings button function
def open_settings_window():
    global settings_window
    global settings_bitratemenu 
    global settings_bitratemenu_var 
    global settings_languagemenu
    global settings_formatmenu 
    global settings_formatmenu_var
    global settings_destination
    #check if settings already exsists
    if settings_window is not None and settings_window.winfo_exists():
        # Settings window is already open, focus on it
        settings_window.focus()
        return
    settings_window = CTkToplevel(app)
    #it takes it a few seconds to open so meanwhile lift app on top
    app.lift()
    app.focus()
    settings_window.iconbitmap(icon_path)
    settings_window.title(dictionarie["settings"])
    settings_window_width = 445 # Specify the window width
    settings_window_height = 260  # Specify the window height
    settingsx = (screen_width - settings_window_width) // 2
    settingsy = (screen_height - settings_window_height-100) // 2
    settings_window.geometry(f"{settings_window_width}x{settings_window_height}+{settingsx}+{settingsy}")
    settings_window.resizable(False, False)
    settings_window.configure(fg_color="#ADD8E6")
    settings_window.transient(settings_window.master)

    
    # Raise the settings window to the top of the stacking order
    # Make the settings window the active window
    # Disable the main application window
    settings_icon_path = os.path.join('DATA', 'settings.ico')
    #dont care about the errors.........
    #we need to wait because of some errors in this library
    
    settings_window.after(250, lambda: settings_window.iconbitmap(settings_icon_path) if settings_window is not None else None)
    settings_window.after(250, lambda: settings_window.lift() if settings_window is not None else None)
    settings_window.after(300, lambda: settings_window.transient(None) if settings_window is not None else None)
    settings_window.after(350, lambda: settings_window.focus() if settings_window is not None else None)

    # Set up the "on close" event handler
    settings_window.protocol("WM_DELETE_WINDOW", lambda: settings_window.destroy() if settings_window is not None else None)
    #------------ settings widgets -------------#
    with open('DATA\\settings.json','r', encoding='UTF-8') as config_file:
        config = json.load(config_file)
    settings_label = customtkinter.CTkLabel(settings_window, text=dictionarie['default'],height=20
                                            ,bg_color="#ADD8E6",fg_color="#ADD8E6",font=("Arial", 22))
    settings_label.place(relx=0.5,y=20, anchor=customtkinter.CENTER)
    # Create a frame and adjust its position
    settings_frame = customtkinter.CTkFrame(settings_window,width=405,height=200,corner_radius = 20,fg_color="#C9DADF")
    settings_frame.place(x=20,y=40)
    

    #settings_speedmenu.place(x=50,y=70)
    settings_language_label = customtkinter.CTkLabel(settings_window, text=dictionarie['lan'],corner_radius = 20,height=16,
                                            width=90,bg_color="#C9DADF",fg_color="#91C6E1",font=("Arial", 13))
    settings_language_label.place(x=50,y=47)
    settings_languagemenu_var = customtkinter.StringVar(value=config['language'])
    settings_languagemenu = customtkinter.CTkOptionMenu(settings_window,values=languages,font=("Arial", 15),command=change_language,
                                         variable=settings_languagemenu_var,text_color="black",width=110,height=30)
    settings_languagemenu.place(x=40,y=70)

    settings_bitrate_label = customtkinter.CTkLabel(settings_window, text=dictionarie['bitrate'],corner_radius = 20,height=16
                                            ,width=90,bg_color="#C9DADF",fg_color="#91C6E1",font=("Arial", 13))
    
    settings_bitrate_label.place(x=310,y=47)
    settings_bitratemenu_var =customtkinter.StringVar(value="")
    settings_bitratemenu = customtkinter.CTkOptionMenu(settings_window,dynamic_resizing=False,variable=settings_bitratemenu_var
                                                       ,text_color="black",width=110,height=30,text_color_disabled="white")
    settings_bitratemenu.place(x=300,y=70)


    settings_format_label = customtkinter.CTkLabel(settings_window, text=dictionarie['format'],corner_radius = 20,height=16,
                                            width=90,bg_color="#C9DADF",fg_color="#91C6E1",font=("Arial", 13))
   
    settings_format_label.place(x=180,y=47)
    settings_formatmenu_var = customtkinter.StringVar(value=config['format'])
    settings_formatmenu = customtkinter.CTkOptionMenu(settings_window,values=["mp3", "ogg","flac","wav",dictionarie["input"]],command=settings_changed_format,
                                 variable=settings_formatmenu_var,text_color="black",width=110,height=30,font=("Arial", 15))
    settings_formatmenu.place(x=170,y=70)

    settings_changed_format(config['format'])
    settings_bitratemenu_var.set((config['bitrate']))






    save_button = customtkinter.CTkButton(settings_window,corner_radius = 10, width = 80, height = 40,command=save,
                            bg_color="#C9DADF",text = dictionarie["save"],font=("Arial", 18), text_color="black")

    save_button.place(x=95,y=190)
    
    cancel_button = customtkinter.CTkButton(settings_window,corner_radius = 10, width = 80, height = 40,command= cancel,
                            bg_color="#C9DADF",text = dictionarie["cancel"],font=("Arial", 18), text_color="black")

    cancel_button.place(x=270,y=190)

    settings_destination = customtkinter.StringVar(value=output_folder)
    settings_folder_entry = customtkinter.CTkEntry(settings_window, textvariable=settings_destination,height = 30,width = 240)
    # Create a button to open the file manager
    settings_select_folder_button = customtkinter.CTkButton(settings_window, text=dictionarie["change_destination_folder"],height = 20,width=160
                                               ,text_color="black", command=settings_open_file_manager,font=("Arial", 13))
    settings_folder_entry.place(x=40, y=145)
    settings_select_folder_button.place(x=80, y=115)
# Global variables

def stop_audio_threads():
    global files_finished
    files_finished = 0
    for future in futures:
        future.cancel()
    for process in ffmpeg_processes:
        process.terminate()
    futures.clear()
    start_button.configure(text=dictionarie['start'])
    start_button.configure(fg_color="#3b8ed0")
    start_button.configure(command=start_convert)
    remove_selected_files()
    

# Define a function to be called when the window is closed
def on_close():
    stop_audio_threads()
    if temp_file_play != "":
        os.remove(temp_file_play)
    app.quit()
    

# Bind the function to the <Destroy> event
app.bind("<Destroy>", lambda event: on_close())



def create_demo():
    global demo_process,demo_thread,temp_file_play

    duration = 35  # Duration in seconds
    # Create a temporary file
    output_file = os.path.join(output_folder, "temp.mp3")
    temp_file_play = output_file
    print(output_file)
    # Construct the command
    command = ['DATA\\ffmpeg', '-i', file_paths[0], '-filter:a', f'atempo={speed}', '-c:a', 'libmp3lame',
               '-t', str(duration) , output_file]
    command.insert(1, '-y') 
    # Execute the command in a separate thread
    demo_thread = threading.Thread(target=execute_demo, args=(command, output_file))
    demo_thread.start()
    # Store the thread and process information
    demo_process = (demo_thread, output_file)

 
def remove_selected_files():
    global file_paths,temp_file_play
    file_paths.clear()
    update_files_label(0)
    start_button.configure(state="disabled")
    remove_files_button.configure(state="disabled")
    demo_button.configure(state="disabled",fg_color="gray")
    if temp_file_play != "":
        if os.path.exists(temp_file_play):
            try:
                os.remove(temp_file_play)
            except:
                print("ERROR while deleating temp need to delete manually")
    temp_file_play = ""

#function to change output name if overwrite is unchecked
def new_fileName(output):
    add = 0
    # Find the index of the last occurrence of ".mp3" in the filename
    extension_index = output.rfind(".")

    while os.path.exists((output[:extension_index] +" ("+str(add)+")") + output[extension_index:]): 
       add+=1
    return ((output[:extension_index] +"("+str(add)+")") + output[extension_index:])
def get_type_out(file):
    output = file[file.rfind('.')+1:]
    if output == 'flac':
        return "flac"
    elif output == 'ogg':
        return "libvorbis" 
    elif output == 'wav':
        return "pcm_s16le"
    return "libmp3lame"
def change_tempo(input_files, speed_change, output_format, bitrate):
    remove_selected_files()
    output_folder = destination.get()
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    start_button.configure(state="normal")
    start_button.configure(text=dictionarie['stop'])
    start_button.configure(fg_color="#FF7276")
    start_button.configure(command=stop_audio_threads)
    # Generate output filenames with speed change identifier in the specified output folder
    if output_format == dictionarie["input"]:
        output_files = [os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file))[0]}_{speed_change}x.{file[file.rfind('.')+1:]}") for file in input_files]
    else:
        output_files = [os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file))[0]}_{speed_change}x.{output_format}") for file in input_files]

    # Function to process a single input file
    def process_file(input_file, output_file):
        if os.path.exists(output_file):
            if checkbox.get() == "no":
                output_file = new_fileName(output_file)
        command = ""
        # Determine the output codec based on the output format
        if output_format == 'flac':
            command = ['DATA\\ffmpeg', '-i', input_file, '-filter:a', f'atempo={speed_change}', '-c:a', 'flac']
        elif output_format == 'ogg':
            command = ['DATA\\ffmpeg', '-i', input_file, '-filter:a', f'atempo={speed_change}', '-c:a', 'libvorbis']
        elif output_format == 'wav':
            command = ['DATA\\ffmpeg', '-i', input_file, '-filter:a', f'atempo={speed_change}', '-c:a', 'pcm_s16le']
        elif output_format == dictionarie["input"]:
            command = ['DATA\\ffmpeg', '-i', input_file, '-filter:a', f'atempo={speed_change}', '-c:a', get_type_out(output_file)]
        else:
            command = ['DATA\\ffmpeg', '-i', input_file, '-filter:a', f'atempo={speed_change}', '-c:a', 'libmp3lame']
            if not bitrate == dictionarie["auto"]:
                command.extend(['-b:a', bitrate])
        
        command.append(output_file)

        if os.path.exists(output_file):
            command.insert(1, '-y') 
        process = subprocess.Popen(command, shell=False,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        ffmpeg_processes.append(process)

        # Wait for the process to finish
        process.wait()

    # Count variable to track completed file processing tasks

    # Function to increment count variable when a file processing task is completed
    def update_count(future):

        global total_files_to_convert, files_finished, file_paths
        files_finished += 1
        progressbar.set(files_finished/total_files_to_convert)
        progress_label.configure(text=str(files_finished)+"/"+str(total_files_to_convert))
        # Check if all files have been processed
        if files_finished == total_files_to_convert:
            # Print the count of completed file processing tasks
            print("All files processed")
            files_finished = 0
            # Reset the UI elements
            progress_label.configure(text=dictionarie["finished"])
            start_button.configure(text=dictionarie['start'],command=start_convert,fg_color="#3b8ed0")
            file_paths.clear()
            futures.clear()
    # Function to execute the audio processing in a separate thread
    def process_audio():
        # Process input files concurrently using multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(threadsmenu_var.get())) as executor:
            # Submit each file processing task to the executor and attach the update_count function as a callback
            for input_file, output_file in zip(input_files, output_files):
                future = executor.submit(process_file, input_file, output_file)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                update_count(future)
            
    # Create a new thread for audio processing
    audio_thread = threading.Thread(target=process_audio)
    audio_threads.append(audio_thread)
    # Start the audio processing thread
    audio_thread.start()

    



def start_convert():
        global total_files_to_convert, files_finished
        files_finished = 0
        progressbar.configure(progress_color="#50C878",border_width=1.5,border_color="black")
        progressbar.set(0)
        total_files_to_convert = len(file_paths)
        progress_label.configure(text="0/"+str(total_files_to_convert),fg_color="#78B2D6")
        change_tempo(file_paths.copy(),speed,formatmenu_var.get(),bitratemenu_var.get().replace("bps",""))



#change label after he adds files
def update_files_label(count):
    if app_direction_ltr:    
        selected_files_label.configure(text=str(count)+" "+dictionarie["files_selected"])
    else:
        selected_files_label.configure(text=dictionarie["files_selected"]+": "+str(count))
# ADD FILES BUTTON
def add_files_button_clicked():
        global file_paths,temp_file_play
        get_file_paths = file_paths.copy()
        # Open the file dialog and filter media file types
        filetypes = (
            ("Media files","*.mp3;*.aac;*.flac;*.wav;*.ogg;*.opus;*.wma;*.ac3;*.dts;*.aiff;*.alac;*.mp2;*.au;*.m4a"),
            ("All files", "*.*")
        )
        selected_files = filedialog.askopenfilenames(filetypes=filetypes)
        # Add the selected file paths to the list
        get_file_paths.extend(selected_files)
        #remove the dupilcate file paths
        file_paths = list(dict.fromkeys(get_file_paths))
        update_files_label(len(file_paths))
        if len(file_paths) > 0 and start_button.cget("text") == dictionarie['start']:
            start_button.configure(state="normal")
            remove_files_button.configure(state="normal")
        if temp_file_play != "":
            if os.path.exists(temp_file_play):
                try:
                    os.remove(temp_file_play)
                except:
                    print("ERROR while deleating temp need to delete manually")
        temp_file_play =""
        create_demo()



# frame for all the buttons in the middle
frame = customtkinter.CTkFrame(app,width=575,height=225,corner_radius = 20,fg_color="#C9DADF")
if app_direction_ltr:    
    frame.place(x=200, y=25)
else:
    frame.place(x=25, y=25)   
# frame to add a circular corner in the edge of the ad files image     
corner_frame = customtkinter.CTkFrame(app,width=400,height=400,corner_radius=20,bg_color="#C9DADF",fg_color="#ADD8E6")
if app_direction_ltr:    
    corner_frame.place(x=-200, y=-220)
else:
    corner_frame.place(x=600, y=-220)





#------------ adding to the FRAME NEXT TO ADD FILES BUTTON -------------#

# a small frame under the add files button
extra_frame = customtkinter.CTkFrame(app,width=200,height=70,corner_radius = 20,fg_color="#C9DADF")
if app_direction_ltr:    
    extra_frame.place(x=25, y=180)
else:
    extra_frame.place(x=575, y=180)
# a frame to cover the backround on 2 of the corners
Extra_frame = customtkinter.CTkFrame(app,width=40,height=70,corner_radius=0,fg_color="#C9DADF")
if app_direction_ltr:    
    Extra_frame.place(x=200, y=180)
else:
    Extra_frame.place(x=570, y=180)


#------------ SELECTED FILES LABEL -------------#
selected_files_label = customtkinter.CTkLabel(app, text="",bg_color="#C9DADF",fg_color="#78B2D6",font=("Arial", 20-for_small_language_lower),width=260,height= 40,corner_radius = 20)

if app_direction_ltr:    
    selected_files_label.place(x=225, y=50)
else:
    selected_files_label.place(x=315, y=50)
update_files_label(0)

#------------ REMOVE SELECTED FILES BUTTON -------------#

remove_files_button = customtkinter.CTkButton(app,corner_radius = 20, width = 260, height = 40,bg_color="#C9DADF",command=remove_selected_files,
                            text = dictionarie['remove_all_files'],font=("Arial", 18-for_small_language_lower*3.5), text_color="black",state="disabled")
# position button based on ltr
if app_direction_ltr:    
    remove_files_button.place(x=225, y=120)
else:
    remove_files_button.place(x=315, y=120)

#------------ ADD FILES BUTTON -------------#

# Load the image for the button
            # Get the current script's directory
            # current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the image file path
image_path = os.path.join("DATA", "addFiles.png")
# Load the image using PIL
image = Image.open(image_path)
# Resize the image
image = image.resize((80, 80))
# Create an ImageTk object from the image
image_tk = ImageTk.PhotoImage(image)
#create button
add_files_button = customtkinter.CTkButton(app, image=image_tk, compound= "top",
                            command=add_files_button_clicked,corner_radius = 20, width = 160, height = 140,
                            text = dictionarie['add_files'],font=("Arial", 24-for_small_language_lower*3.5), text_color="black")
# position button based on ltr
if app_direction_ltr:    
    add_files_button.place(x=25, y=25)
else:
    add_files_button.place(x=615, y=25)

#------------ FRAME FOR SPEED CHANGE BUTTONS AND INFO -------------#

speed_frame = customtkinter.CTkFrame(app,width=190,height=40,corner_radius = 10,bg_color="#C9DADF",fg_color="#78B2D6")
if app_direction_ltr:    
    speed_frame.place(x=505, y=50)
else:
    speed_frame.place(x=105, y=50)

#------------label and + and - CHANGE BUTTONS AND INFO BUTTON -------------#

speed_label = customtkinter.CTkLabel(app, text=dictionarie['speed'],bg_color="#C9DADF",fg_color="#78B2D6",
                                     font=("Arial", 19-for_small_language_lower),width=80,height= 40,corner_radius=10)

if app_direction_ltr:    
    speed_label.place(x=505, y=50)
else:
    speed_label.place(x=215, y=50)

#------------DEMO PLAY STOP BUTTON -------------#
# Global variable to hold the subprocess
demo_process = None
pygame.mixer.init()

# def run_demo():
#     global demo_process

#     demo_button.configure(image=stop_image_tk,command=stop_demo)
#     duration_per_conversion = 5  # Duration in seconds for each conversion
#     total_conversions = 10  # Total number of conversions

#     # Create a temporary directory for the output files
#     output_directory = tempfile.mkdtemp()

#     # Start the conversion process in a separate thread
#     conversion_thread = threading.Thread(target=execute_conversions, args=(duration_per_conversion, total_conversions))
#     conversion_thread.start()

#     # Store the thread information
#     demo_process = conversion_thread

# def execute_conversions( duration_per_conversion, total_conversions):
#     global demo_process,process
#     output_dir= os.path.join(output_folder, "demotemp")
#     if not os.path.exists(output_dir):
#         os.mkdir(output_dir)
#     for i in range(total_conversions):
#         print(i)
#         # Create a temporary file for each conversion
#         with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, dir=output_dir) as temp_file:
#             output_file = temp_file.name
#             print(output_file)
#             # Calculate the start and end time for the current conversion
#             start_time = i * duration_per_conversion
#             end_time = start_time + duration_per_conversion

#             # Construct the conversion command
#             command = ['DATA\\ffmpeg', '-i', file_paths[0], '-filter:a', f'atempo={speed}', '-c:a', 'libmp3lame',
#                        '-ss', str(start_time), '-to', str(end_time), output_file]
#             command.insert(1, '-y') 

#             # Start the conversion subprocess
#             process = subprocess.Popen(command,shell=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#             process.communicate()
#             if i != 0:
#             # Wait for the audio to finish playing
#                 while pygame.mixer.music.get_busy():
#                     continue
#             print(os.path.exists(output_file))
#             output_file = os.path.join(output_dir, str(temp_file.name))

#             # Play the converted file
#             pygame.mixer.music.load(output_file)
#             pygame.mixer.music.play()



#     # Clear the demo process variable
#     demo_process = None

# def stop_demo():
#     global demo_process,process

#     if demo_process:
#         conversion_thread = demo_process

#         # Terminate the conversion process
#         conversion_thread.join()
#         process.terminate()
#         process = None
#         # Stop the music playback
#         pygame.mixer.music.stop()
#         demo_button.configure(image=play_image_tk,command=run_demo)
#         # Delete the temporary directory and files
#         # You can implement the necessary file deletion logic here

#         # Clear the demo process variable
#         demo_process = None

def run_demo():
    demo_button.configure(image=stop_image_tk,command=stop_demo)
    play_thread = threading.Thread(target=play)
    play_thread.start()


def play():   
    try:
        pygame.mixer.music.load(temp_file_play)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        demo_button.configure(image=play_image_tk,command=run_demo)
    except:
        print("ERROR WHILW TRYING TO PLAY DEMO FILE!")
def execute_demo(command,output_file):
    global demo_process, d_process
    # Start the subprocess
    d_process = subprocess.Popen(command,shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    # Play the converted file
    # Wait for the process to complete
     # Get the file size in bytes
  # Extract the conversion percentage from the progress output

    d_process.communicate()
    #demo_button.configure(image=play_image_tk,command="run_demo")
    # Clear the demo process variable
    demo_process = None
    demo_button.configure(state="normal",fg_color="#3b8ed0",corner_radius = 10, width = 0, height = 40)

def stop_demo():
    # global demo_process, d_process


    # if demo_process:
    #     demo_thread, output_file = demo_process
    #     #Terminate the subprocess

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.quit()
    pygame.mixer.init()

    demo_button.configure(image=play_image_tk,command=run_demo)

        # d_process.terminate()
        # demo_thread.join()
        # demo_button.configure(image=play_image_tk,command=run_demo)

        # # Delete the temporary file
        # # You can implement the necessary file deletion logic here
        # # Clear the demo process variable
        # demo_process = None
play_image_path = os.path.join("DATA", "play.png")
# Load the image using PIL
play_image = Image.open(play_image_path)
# Resize the image
play_image = play_image.resize((25, 25))
# Create an ImageTk object from the image
play_image_tk = ImageTk.PhotoImage(play_image)
stop_image_path = os.path.join("DATA", "stop.png")
# Load the image using PIL
stop_image = Image.open(stop_image_path)
# Resize the image
stop_image = stop_image.resize((25, 25))
# Create an ImageTk object from the image
stop_image_tk = ImageTk.PhotoImage(stop_image)
demo_button = customtkinter.CTkButton(app,corner_radius = 10, width = 0, height = 40,image = play_image_tk,text="",bg_color="#C9DADF"
                                      ,fg_color="gray", command= run_demo,text_color="black",state="disabled")
# position button based on ltr
if app_direction_ltr:    
    demo_button.place(x=710, y=50)
else:
    demo_button.place(x=50, y=50)

#------------ MENU FOR FORMAT AND BITRATE -------------#
def changed_format(choice):
    if choice == "mp3":
        bitratemenu.configure(state="normal")
        bitratemenu_var.set(dictionarie["auto"])
        bitratemenu.configure(font=("Arial", 15))
        bitratemenu.configure(values=[dictionarie["auto"],"32kbps", "64kbps", "96kbps", "128kbps", "160kbps", "192kbps", "224kbps", "256kbps", "288kbps", "320kbps"])
    elif choice == dictionarie["input"]:
        bitratemenu.configure(state="disabled")
        bitratemenu_var.set(dictionarie["input"])
    else:
        bitratemenu.configure(state="disabled")
        bitratemenu.configure(font=("Arial", 13))
        bitratemenu_var.set(dictionarie["auto"])



formatmenu_var = customtkinter.StringVar(value=config['format'])
formatmenu = customtkinter.CTkOptionMenu(app,values=["mp3", "ogg","flac","wav",dictionarie["input"]],font=("Arial", 15),command=changed_format,
                                         variable=formatmenu_var,text_color="black",width=110,height=40)
if app_direction_ltr:    
    formatmenu.place(x=505, y=120)
else:
    formatmenu.place(x=185,y=120)

format_label = customtkinter.CTkLabel(app, text=dictionarie['format'],corner_radius = 20,height=18
                               ,width=90,bg_color="#C9DADF",fg_color="#91C6E1",font=("Arial", 14))

# position button based on ltr
if app_direction_ltr:    
    format_label.place(x=515, y=96)
else:
    format_label.place(x=195, y=96)

bitratemenu_var = customtkinter.StringVar()
bitratemenu = customtkinter.CTkOptionMenu(app,text_color_disabled="white",dynamic_resizing=False
                                          ,variable=bitratemenu_var,text_color="black",width=110,height=40)

if app_direction_ltr:    
    bitratemenu.place(x=640, y=120)
else:
    bitratemenu.place(x=50,y=120)

changed_format(formatmenu_var.get())

bitrate_label = customtkinter.CTkLabel(app, text=dictionarie['bitrate'],corner_radius = 20,height=18
                               ,width=90,bg_color="#C9DADF",fg_color="#91C6E1",font=("Arial", 14))

# position button based on ltr
if app_direction_ltr:    
    bitrate_label.place(x=650, y=96)
else:
    bitrate_label.place(x=60, y=96)


#------------ THREADS DROP DOWN MENU -------------#

threadsmenu_var = customtkinter.StringVar(value="3")
threadsmenu = customtkinter.CTkOptionMenu(app,values=["1","2","3","4","5","6"],dynamic_resizing=False,font=("Arial", 18)
                                          ,variable=threadsmenu_var,text_color="black",width=80,height=40)

if app_direction_ltr:    
    threadsmenu.place(x=670, y=190)
else:
    threadsmenu.place(x=50,y=190)

threads_label = customtkinter.CTkLabel(app, text=dictionarie['threads'],corner_radius = 20,height=18,
                               width=70,bg_color="#C9DADF",fg_color="#91C6E1",font=("Arial", 14))

# position button based on ltr
if app_direction_ltr:    
    threads_label.place(x=673.75, y=166)
else:
    threads_label.place(x=55, y=166)


#------------ OVERWRITE CHECKBOX -------------#
overwrite_label = customtkinter.CTkLabel(app, text=dictionarie['overwrite'],corner_radius = 5,height=40
                               ,width=140,bg_color="#C9DADF",fg_color="#78B2D6",font=("Arial", 16),padx=(5))

# position button based on ltr
if app_direction_ltr:    
    overwrite_label.configure(anchor='w')
    overwrite_label.place(x=505, y=190)
else:
    overwrite_label.configure(anchor='e')
    #overwrite_label.configure()
    overwrite_label.place(x=155, y=190)

checkbox_frame = customtkinter.CTkFrame(app,width=40,height=40,corner_radius = 0,bg_color="#C9DADF",fg_color="#78B2D6")
if app_direction_ltr:    
    checkbox_frame.place(x=600, y=190)
else:
    checkbox_frame.place(x=160, y=190)
check_var = customtkinter.StringVar(value="no")
checkbox = customtkinter.CTkCheckBox(app,text="",width = 0,bg_color="#78B2D6",variable=check_var, onvalue="yes", offvalue="no")
if app_direction_ltr:    
    checkbox.place(x=610, y=197.5)
else:
    checkbox.place(x=165,y=197.5)

#------------ FRAME FOR COVERING FAIL IN LABEL -------------#

second_speed_frame = customtkinter.CTkFrame(app,width=95,height=40,corner_radius = 10,bg_color="#78B2D6",fg_color="#78B2D6")
if app_direction_ltr:    
    second_speed_frame.place(x=575, y=50)
else:
    second_speed_frame.place(x=130, y=50)


clicked = False
def minus():
    global clicked,continuous_click_thread,speed
    clicked = True
    if speed > 0.05:
        speed-=Decimal('.05')
        speed_label.configure(text=speed)

    continuous_click_thread = threading.Thread(target=change,args=(-1,))
    continuous_click_thread.start()
def plus():
    global clicked,continuous_click_thread,speed
    clicked = True
    speed+=Decimal('.05')
    speed_label.configure(text=speed)
    continuous_click_thread = threading.Thread(target=change,args=(1,))
    continuous_click_thread.start()
def change(plus_or_minus_control):
    global speed
    time.sleep(.7)
    while clicked:
        if speed > 0.05 or plus_or_minus_control == 1:
            speed+=Decimal('.05')*plus_or_minus_control
            speed_label.configure(text=speed)
            time.sleep(.04)
        else:
            return

def unclicked(info):
    global clicked
    clicked = False
    stop_demo()
    demo_button.configure(state="disabled",fg_color="gray")
    if len(file_paths) > 0:
        create_demo()
    


plus_button = customtkinter.CTkButton(app,corner_radius = 10, width = 33, height = 30,command= plus,
                            bg_color="#78B2D6",text = "+",font=("Arial", 18), text_color="black")
plus_button.bind("<ButtonRelease>", unclicked)
# position button based on ltr
if app_direction_ltr:    
    plus_button.place(x=658, y=55)
else:
    plus_button.place(x=110, y=55)



minus_button = customtkinter.CTkButton(app,corner_radius = 10, width = 33, height = 30,command= minus,
                            bg_color="#78B2D6",text = "-",font=("Arial", 18), text_color="black")
minus_button.bind("<ButtonRelease>", unclicked)
# position button based on ltr
if app_direction_ltr:    
    minus_button.place(x=578, y=55)
else:
    minus_button.place(x=190, y=55)




# Create a ctk.entry field

speed_label = customtkinter.CTkLabel(app,height = 30,width = 42,font=("Arial", 12)
                                     ,bg_color="#78B2D6",justify="center",text=str(speed))




# Create a function to handle the validation on key press
# def on_key_press(event):

#     char_typed = event.char
#     print(char_typed)
#     if not validate_input(speed.get()):
#         speed_entry.configure(textvariable=speed)
#         speed_entry.delete(0, customtkinter.END)
#         speed_entry.insert(0,1)
#         speed_entry.bell()  # Optionally, emit a bell sound to indicate invalid input

# # Bind the key press event to the entry field
# speed_entry.bind("<Key>", on_key_press)

if app_direction_ltr:    
    speed_label.place(x=613, y=55)
else:
    speed_label.place(x=145,y=55)
#------------ START / STOP BUTTON ------------#

start_button = customtkinter.CTkButton(app,corner_radius = 30, width = 95, height = 50,state="disabled",command= start_convert,
                            text = dictionarie['start'],font=("Arial", 18), text_color="black")
# position button based on ltr
if app_direction_ltr:    
    start_button.place(x=680, y=290)
else:
    start_button.place(x=25, y=290)

#------------ SETTINGS BUTTON ------------#

set_image_path = os.path.join("DATA", "settings.png")
# Load the image using PIL
set_image = Image.open(set_image_path)
# Resize the image
set_image = set_image.resize((40, 40))
# Create an ImageTk object from the image
set_image_tk = ImageTk.PhotoImage(set_image)
#create button
settings_button = customtkinter.CTkButton(app, image=set_image_tk,text="",corner_radius = 50
                                          , width = 95, height = 50,command=open_settings_window)
# position button based on ltr
if app_direction_ltr:    
    settings_button.place(x=25, y=290)
else:
    settings_button.place(x=680, y=290)

#------------ PROGRESS BAR ------------#
progressbar = customtkinter.CTkProgressBar(app ,orientation="horizontal",progress_color="#ADD8E6"
                                           ,fg_color="#ADD8E6", width=530,height=50,corner_radius = 25)
progressbar.place(x=135, y=290)
progressbar.set(0)
progress_label = customtkinter.CTkLabel(app , text="",fg_color="#ADD8E6",corner_radius= 25,
                        font=("Arial", 19),width=80,height= 30)

progress_label.place(x=360, y=255)

#------------ CREDITS------------#

def open_link(event):
    webbrowser.open('https://mitmachim.top/user/10110000')

created_by_label = customtkinter.CTkLabel(app , text=dictionarie["created_by"],fg_color="#ADD8E6",corner_radius= 0,
                        font=("Arial", 11),width=40,height= 10,text_color="gray")



name_label = customtkinter.CTkLabel(app , text="10110000",fg_color="#ADD8E6",corner_radius= 0,
                        font=("Arial", 10),width=40,height= 10,cursor="hand2",text_color="blue")

name_label.bind("<Button-1>", open_link)

if app_direction_ltr:    
    created_by_label.place(x=700, y=349)
    name_label.place(x=755, y=350)
else:
    created_by_label.place(x=50, y=349)
    name_label.place(x=5, y=350)




def open_file_manager():
    global output_folder
    temp = output_folder
    output_folder = filedialog.askdirectory()
    if output_folder:
        destination.set(output_folder)
    else:
        output_folder = temp

# Create a label and entry for the folder path
folder_label = customtkinter.CTkLabel(app, text=dictionarie["destination_folder"],text_color="black",font=("Arial", 18-for_small_language_lower),fg_color="#C9DADF")
destination = customtkinter.StringVar(value=output_folder)
folder_entry = customtkinter.CTkEntry(app, textvariable=destination,height = 30,width = 260)
# Create a button to open the file manager
select_folder_button = customtkinter.CTkButton(app, text=dictionarie["change_destination_folder"],height = 20,width=160
                                               ,text_color="black", command=open_file_manager,font=("Arial", 14))
if app_direction_ltr:    
    folder_label.place(x=50, y=201)
    folder_entry.place(x=225, y=200)
    select_folder_button.place(x=275, y=175)
else:
    folder_label.place(x=600, y=201)
    folder_entry.place(x=315, y=200)
    select_folder_button.place(x=365, y=175)


app.mainloop()
