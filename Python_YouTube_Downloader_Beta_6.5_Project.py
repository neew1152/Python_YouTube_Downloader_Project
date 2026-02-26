# Required install:
# pip install customtkinter
# pip install yt-dlp
# pip install pytube
# pip install tk

# Libraries
import customtkinter
import subprocess
import tkinter
import os
from yt_dlp import YoutubeDL
from pytube import Playlist
from customtkinter import *
from pytube import YouTube
from tkinter import ttk

# Our app frame
app = customtkinter.CTk()
app.title("Python YouTube Video Downloader Beta 6.5 Project")

# Get the default font of the operating system
os_font = customtkinter.CTkFont()
os_font_size = os_font.cget("size")

# Get screen dimensions
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Set graphical user interface dimensions as a 50% of the display resolution width and height size
gui_width = int(screen_width * 0.50)
gui_height = int(screen_height * 0.50)
gui_dimensions = f"{gui_width}x{gui_height}"
app.geometry(gui_dimensions)

# System Settings
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Change Appearance Mode Switch
appearance_mode = "dark"

# Change Appearance Mode Switch Function
def change_appearance_mode_function():
    global appearance_mode
    if appearance_mode == "dark":
        customtkinter.set_appearance_mode("light")
        appearance_mode = "light"
    
    elif appearance_mode == "light":
        customtkinter.set_appearance_mode("dark")
        appearance_mode = "dark"
app.update()

# StringVar
change_appearance_mode_switch_var = customtkinter.StringVar(value="off")
app.update()

# Change appearance mode switch
change_appearance_mode_switch = customtkinter.CTkSwitch(app, text="Change Appearance Mode", font=(os_font, os_font_size), command=change_appearance_mode_function, variable=change_appearance_mode_switch_var, onvalue="on", offvalue="off")
change_appearance_mode_switch.pack(anchor="nw", padx=10, pady=0)
app.update()

# Scrollable frame
video_and_audio_scroll_frame = customtkinter.CTkScrollableFrame(app)
video_and_audio_scroll_frame.pack(fill=customtkinter.BOTH, expand=True)
app.update()

# URL input
url_input = customtkinter.CTkEntry(video_and_audio_scroll_frame, placeholder_text="Video URL...", font=(os_font, os_font_size), height=40)
url_input.pack(fill=customtkinter.BOTH, expand=True, padx=0, pady=6)
app.update()

# Search Command Button
# search Format Function
def search_format_function(url):
    command = f"yt-dlp -F {url}"
    try:
        # Clear any existing content in the frame
        monitor_command_output_frame.delete('1.0', tkinter.END)
        app.update()
        
        # Open subprocess to run the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.update()

        # Auto-scroll if enabled
        if auto_scroll_enabled.get():
            monitor_command_output_frame.see(tkinter.END)
            app.update()

        # Read output line by line and insert it into the frame
        for line in process.stdout:
            monitor_command_output_frame.insert(tkinter.END, line)
            app.update()

        # Auto-scroll if enabled
        if auto_scroll_enabled.get():
            monitor_command_output_frame.see(tkinter.END)
            app.update()

        # Search for errors in stderr
        errors_output = process.communicate()[1]
        if errors_output:
            monitor_command_output_frame.insert(tkinter.END, errors_output)
            app.update()

        # Auto-scroll if enabled
        if auto_scroll_enabled.get():
            monitor_command_output_frame.see(tkinter.END)
            app.update()

    except Exception as e:
        monitor_command_output_frame.insert(tkinter.END, f"Error: {e}")
        app.update()

        # Auto-scroll if enabled
        if auto_scroll_enabled.get():
            monitor_command_output_frame.see(tkinter.END)
            app.update()
app.update()

# Search Function
def search_function():
    url = url_input.get()
    try:
        search_format_function(url)
        yt = YouTube(url, on_progress_callback=on_progress)
        app.update()

        search_label.configure(text = f'{yt.title}', text_color="white", font=(os_font, os_font_size))
        app.update()
        
        search_label.update()
        app.update()
    except:
        search_label.configure(text="It's an error or not a YouTube video URL. If it's not error, we possibly download it.", font=(os_font, os_font_size))
        app.update()
app.update()

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completed = bytes_downloaded / total_size * 100
    progress_label.configure(text =str(int(percentage_completed)) + "%")
    progress_label.update()
    progress_bar.set(float(percentage_completed / 100))
app.update()

# Search Button
search_button = customtkinter.CTkButton(video_and_audio_scroll_frame, text="Search", font=(os_font, os_font_size), fg_color="#297CD2", hover_color="#21A366", height=20, command=search_function)
search_button.pack()
app.update()

# Search Command Button Output
search_label = customtkinter.CTkLabel(video_and_audio_scroll_frame, text="", font=(os_font, os_font_size))
search_label.pack(fill=customtkinter.BOTH, expand=True, padx=0, pady=0)
app.update()

# Variable to keep track of the auto-scroll state
auto_scroll_enabled = tkinter.BooleanVar(value="on")
app.update()

# Auto-Scroll Switch
def toggle_auto_scroll():
    auto_scroll_enabled.set(not auto_scroll_enabled.get())
    app.update()

auto_scroll_switch = customtkinter.CTkSwitch(video_and_audio_scroll_frame, text="Disable Auto-Scroll Down", font=(os_font, os_font_size), command=toggle_auto_scroll, variable=auto_scroll_enabled, onvalue="on", offvalue="off")
auto_scroll_switch.pack(anchor="ne", padx=0, pady=0)
app.update()

# Monitor Command Output Frame
monitor_command_output_frame = customtkinter.CTkTextbox(video_and_audio_scroll_frame, border_color="#11810D", border_width=2)
monitor_command_output_frame.pack(fill=customtkinter.BOTH, expand=True)
app.update()

# ID input
ID_input = customtkinter.CTkEntry(video_and_audio_scroll_frame, placeholder_text="ID...", font=(os_font, os_font_size), height=40)
ID_input.pack(fill=customtkinter.BOTH, expand=True, padx=0, pady=6)
app.update()

# Rename file input
name_file_input = customtkinter.CTkEntry(video_and_audio_scroll_frame, placeholder_text="Empty = Original Titles", font=(os_font, os_font_size), height=40)
name_file_input.pack(fill=customtkinter.BOTH, expand=True, padx=0, pady=0)
app.update()

# Download Command Button
# Download function
def download_function(url, ID, name_file):
    # Check if name_file_input is empty and include placeholders for the title and extension in the output template
    if name_file.strip() == "":
        command = f"yt-dlp -f {ID} {url} -o Downloads/%(title)s.%(ext)s"
    else:
        command = f"yt-dlp -f {ID} {url} -o Downloads/{name_file}.%(ext)s"

    try:
        # Clear any existing content in the frame
        monitor_command_output_frame.delete('1.0', tkinter.END)
        app.update()

        # Open subprocess to run the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.update()

        # Read output line by line and insert it into the frame
        for line in process.stdout:
            monitor_command_output_frame.insert(tkinter.END, line)
            app.update()
            
            download_button.configure()
            app.update()

            # Auto-scroll if enabled
            if auto_scroll_enabled.get():
                monitor_command_output_frame.see(tkinter.END)
                app.update()

        # Check for errors in stderr
        errors_output = process.communicate()[1]
        if errors_output:
            monitor_command_output_frame.insert(tkinter.END, errors_output)
            app.update()
            
            download_button.configure()
            app.update()
            
            # Auto-scroll if enabled
            if auto_scroll_enabled.get():
                monitor_command_output_frame.see(tkinter.END)
                app.update()

    except Exception as e:
        monitor_command_output_frame.insert(tkinter.END, f"Error: {e}")
        app.update()
        
        # Auto-scroll if enabled
        if auto_scroll_enabled.get():
            monitor_command_output_frame.see(tkinter.END)
            app.update()
        app.update()
app.update()

# Download Button
def download():
    url = url_input.get()
    ID = ID_input.get()
    name_file = name_file_input.get()
    download_function(url, ID, name_file)

download_button = customtkinter.CTkButton(video_and_audio_scroll_frame, text="Download", font=(os_font, os_font_size), fg_color="#297CD2", hover_color="#21A366", height=20, command=download)
download_button.pack(padx=0, pady=6)
app.update()

# Progress Bar (hide)
progress_bar = customtkinter.CTkProgressBar(app, width=400)
progress_bar.set(0)

# Progress percentage (hide)
progress_label = customtkinter.CTkLabel(app, text="0%")

# Status label (hide)
status_label = customtkinter.CTkLabel(app, text="")

# Update the graphical user interface and Run app
app.update()
app.mainloop()

# The code is written by learning from
# https://www.youtube.com/watch?v=NI9LXzo0UY0
# https://www.youtube.com/watch?v=Miydkti_QVE
# https://www.youtube.com/watch?v=Envp9yHb2Ho
# https://www.youtube.com/watch?v=EwL2BwEdduE
# https://www.youtube.com/watch?v=a0MVOloNLB4
# https://www.youtube.com/watch?v=GeflXCubyrA
# https://www.youtube.com/watch?v=QRroCuY1Bhc
# https://www.youtube.com/watch?v=df30Qro3Iu4
# Some videos have been deleted.

# ChatGPT 3.5, ChatGPT-4o, GitHub and Google.

