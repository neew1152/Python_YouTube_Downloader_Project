# Required install: pip install customtkinter tk yt-dlp

# --- 1. Import necessary libraries ---
# We need these libraries to build the app, run commands, and work with files.
import customtkinter
import os
import subprocess
import tkinter

# --- 2. Create the main application window ---
app = customtkinter.CTk()
app.title("Python YouTube Downloader Beta 8.0 Project")

# --- 3. Set the window size ---
# Get the user's screen dimensions.
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Set the window size to be 50% of the screen's width and height.
gui_width = int(screen_width * 0.50)
gui_height = int(screen_height * 0.50)
app.geometry(f"{gui_width}x{gui_height}")


# --- 4. Define the functions that the buttons will use ---
# We define these functions before we create the buttons themselves.

def run_search():
    """Gets the URL from the input box and searches for video formats."""
    url = url_input.get().strip() # .strip() removes any accidental spaces

    if not url:
        # If the URL is empty, show a message and stop.
        monitor_frame.delete("1.0", tkinter.END)
        monitor_frame.insert("1.0", "Please enter a video URL first.\n")
        return

    # This is the command that will be run in the terminal.
    command = f"yt-dlp -F {url}"

    # Clear the output monitor before running the command.
    monitor_frame.delete("1.0", tkinter.END)
    app.update() # Update the screen to show the message

    # Run the command and show its output in real-time.
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        # Read the output line by line as it comes in.
        for line in process.stdout:
            monitor_frame.insert(tkinter.END, line)
            app.update() # Update the GUI with the new line
        
        # Check if there were any errors.
        errors = process.communicate()[1]
        if errors:
            monitor_frame.insert(tkinter.END, errors)

    except Exception as e:
        monitor_frame.insert(tkinter.END, f"An error occurred: {e}\n")

def download():
    """Gets the URL, ID, and filename, then downloads the video."""
    url = url_input.get().strip()
    video_id = id_input.get().strip()
    filename = filename_input.get().strip()

    if not url or not video_id:
        # Check if both URL and ID have been entered.
        monitor_frame.delete("1.0", tkinter.END)
        monitor_frame.insert("1.0", "Please enter a URL and a video ID to download.\n")
        return

    # Create a folder named "Downloads" if it doesn't already exist.
    os.makedirs("Downloads", exist_ok=True)

    # Build the final command. The output path changes based on whether
    # a custom filename was provided.
    if not filename:
        # If no filename is given, use the video's original title.
        command = f'yt-dlp -f "{video_id}" "{url}" -o "Downloads/%(title)s.%(ext)s"'
    else:
        # If a filename is given, use it.
        command = f'yt-dlp -f "{video_id}" "{url}" -o "Downloads/{filename}.%(ext)s"'

    # Clear the output monitor and run the download command.
    monitor_frame.delete("1.0", tkinter.END)
    app.update()

    # The logic to run the command is the same as in run_search().
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        for line in process.stdout:
            monitor_frame.insert(tkinter.END, line)
            app.update()
        
        errors = process.communicate()[1]
        if errors:
            monitor_frame.insert(tkinter.END, errors)

    except Exception as e:
        monitor_frame.insert(tkinter.END, f"An error occurred: {e}\n")


# --- 5. Create and arrange the UI widgets ---
# These are the input boxes, buttons, and text areas the user sees.

# URL Input Box
url_input = customtkinter.CTkEntry(app, placeholder_text="Step 1: Paste Video URL here...")
url_input.pack(fill="x", padx=5, pady=5) # fill='x' makes it fill horizontally

# Search Button
search_button = customtkinter.CTkButton(
    app,
    text="Search for Video Formats",
    fg_color="#297CD2",
    hover_color="#21A366",
    command=run_search  # This button calls the run_search function
)
search_button.pack(padx=5, pady=5)

# Output Monitor (Text Box)
monitor_frame = customtkinter.CTkTextbox(app, border_color="#11810D", border_width=2)
monitor_frame.pack(fill="both", expand=True, padx=5, pady=5) # expand=True makes it fill the remaining space

# ID Input Box
id_input = customtkinter.CTkEntry(app, placeholder_text="Step 2: Enter the 'ID' of the format you want...")
id_input.pack(fill="x", padx=5, pady=5)

# Filename Input Box
filename_input = customtkinter.CTkEntry(app, placeholder_text="Step 3 (Optional): Enter a new filename...")
filename_input.pack(fill="x", padx=5, pady=5)

# Download Button
download_button = customtkinter.CTkButton(
    app,
    text="Download Video",
    fg_color="#297CD2",
    hover_color="#21A366",
    command=download # This button calls the download function
)
download_button.pack(padx=5, pady=5)


# --- 6. Start the application ---
# This line tells the program to display the window and wait for user actions.
# It must always be the last line.
app.mainloop()

# The code is rewritten by Gemini 2.5 Pro

