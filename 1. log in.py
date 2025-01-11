import tkinter as tk
from tkinter import messagebox, Toplevel
import sqlite3
from PIL import Image, ImageTk, ImageSequence
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webbrowser
import pygame
import random



# Connect to SQLite
conn = sqlite3.connect("zen_zone.db")

# cursor to execute SQL commands
cursor = conn.cursor()

# Users Table
cursor.execute(''' CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL, password TEXT NOT NULL )''')

# Database Initialization
cursor.execute("""CREATE TABLE IF NOT EXISTS achievement_rates (  username TEXT, date TEXT,achievement_rate INTEGER)""")
conn.commit()

# Mental Health Responses Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mental_health_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        question TEXT NOT NULL,
        response TEXT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# mood_checkins table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mood_checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        mood INTEGER NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()


# USER REGISTRATION
def register():
    username = username_entry.get()
    password = password_entry.get()

    if username and password:
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
    else:
        messagebox.showerror("Error", "Please enter both username and password")

# LOGIN FUNCTION
def login():
    global logged_in_user
    username = username_entry.get()
    password = password_entry.get()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        logged_in_user = username
        open_main_page()
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password")


# MAIN PAGE
def open_main_page():
    login_window.destroy()
    global main_window
    main_window = tk.Tk()
    main_window.title("ZenZone UMPSA")
    main_window.geometry("1400x1400")

    try:
        bg_img = Image.open("background_main.png")
        bg_img = ImageTk.PhotoImage(bg_img)
        bg_label = tk.Label(main_window, image=bg_img)
        bg_label.place(relwidth=1, relheight=1)
        bg_label.image = bg_img
    except:
        main_window.configure(bg="#f0f1f0")

    tk.Label(main_window, text=f"Welcome, {logged_in_user}!", font=("Comic Sans MS", 30, "bold"), bg="#f0f1f0").pack(pady=15)

    # Buttons for features
    tk.Button(main_window, text="Daily Habit Test", width=30, font=("Comic Sans MS", 20), bg="#ffc6ff", #pink
              command=habit_tracker).pack(pady=10)
    tk.Button(main_window, text="Mood Tracker", width=30, font=("Comic Sans MS", 20), bg="#b1f0f7", #blue
              command=mood_check_in).pack(pady=10)
    tk.Button(main_window, text="Community & Connections", width=30, font=("Comic Sans MS", 20), bg="#ffe893", #yellow
              command=open_community_connections).pack(pady=10)
    tk.Button(main_window, text="ZenZone Tips", width=30, font=("Comic Sans MS", 20), bg="#b6ffa1", #green
              command=zenzone_tips).pack(pady=10)

# DAILY HABIT TEST
def habit_tracker():
    habit_window = tk.Toplevel(main_window)
    habit_window.title("Habit Test")
    habit_window.geometry("600x900")
    habit_window.configure(bg="#ffc6ff")
    try:
        bg_img = Image.open("habit track.png")
        bg_img = ImageTk.PhotoImage(bg_img)
        bg_label = tk.Label(habit_window, image=bg_img)
        bg_label.place(relwidth=1, relheight=1)
        bg_label.image = bg_img
    except:
        habit_window.configure(bg="#f0f1f0")
    tk.Label(
        habit_window,
        text="Answer a few questions to reflect on your mental health:", font=("Comic Sans MS", 15, "bold"),
        bg="#ffc6ff", fg="#000000").pack(pady=20)

    questions = [
        "How well did you sleep last night?",
        "How stressed are you feeling today?",
        "How much energy do you have?",
        "How connected do you feel to others?",
        "How motivated do you feel to complete tasks?"
    ]

    dropdown_values = ["Very Good", "Good", "Neutral", "Poor", "Very Poor"]
    responses = {}

    for question in questions:
        frame = tk.Frame(habit_window, bg="#fb9ec6")
        frame.pack(pady=10, anchor="w", padx=20)

        tk.Label(
            frame,
            text=question,font=("Arial", 15),bg="#fb9ec6",fg="#000000").pack(side=tk.LEFT, padx=10)

        response_var = tk.StringVar(value="Select an option")
        responses[question] = response_var

        tk.OptionMenu( frame, response_var,*dropdown_values).pack(side=tk.LEFT)

    def calculate_achievement_rate():
        scores = {
            "Very Poor": 1,
            "Poor": 2,
            "Neutral": 3,
            "Good": 4,
            "Very Good": 5
        }
        total_score = sum(scores[response_var.get()] for response_var in responses.values())
        max_score = len(questions) * 5
        return int((total_score / max_score) * 100)

    def get_supportive_quote(achievement_rate):
        if achievement_rate >= 80:
            return "Great job! You're doing really well. Keep up the good work!"
        elif achievement_rate >= 50:
            return "You're doing okay, but there's room for improvement. Remember to take time for self-care!"
        else:
            return "It seems like you're having a tough time. It's okay to seek support and be kind to yourself."

    def submit_all():
        if any(response_var.get() == "Select an option" for response_var in responses.values()):
            messagebox.showwarning("Incomplete", "Please answer all questions.")
        else:
            try:
                # question-answer responses
                for question, response_var in responses.items():
                    cursor.execute(
                        "INSERT INTO mental_health_responses (username, question, response) VALUES (?, ?, ?)",
                        (logged_in_user, question, response_var.get())
                    )
                conn.commit()

                # Calculate achievement rate and save to database
                achievement_rate = calculate_achievement_rate()
                cursor.execute(
                    "INSERT INTO achievement_rates (username, date, achievement_rate) VALUES (?, DATE('now'), ?)",
                    (logged_in_user, achievement_rate)
                )
                conn.commit()

                # Display supportive message
                quote = get_supportive_quote(achievement_rate)
                messagebox.showinfo(
                    "Success",
                    f"Your responses have been recorded!\n\n"
                    f"Achievement Rate: {achievement_rate}%\n\n"
                    f"{quote}"
                )
                habit_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    # Submit Button
    tk.Button(
        habit_window,text="Submit",font=("Arial", 16, "bold"), bg="#e195ab", fg="#000000", command=submit_all).pack(pady=20)


# MOOD CHECK-IN
def mood_check_in():
    mood_window = tk.Toplevel(main_window)
    mood_window.title("Mood Tracker")
    mood_window.geometry("800x900")
    mood_window.configure(bg="white")

    tk.Label(
        mood_window,
        text="How are you feeling today?",
        font=("Comic Sans MS", 25, "bold"),
        bg="#b1f0f7",
        fg="#000000"
    ).pack(pady=15)

    moods = {
        "😔": {"rating": 1, "color": "#caffbf", "name": "Sad"},
        "🙁": {"rating": 2, "color": "#9bf6ff", "name": "Disappointed"},
        "😐": {"rating": 3, "color": "#a0c4ff", "name": "Neutral"},
        "🙂": {"rating": 4, "color": "#bdb2ff", "name": "Happy"},
        "😄": {"rating": 5, "color": "#ffc6ff", "name": "Excited"}
    }

    # Create a frame for emoji notes on the left (smaller width)
    notes_frame = tk.Frame(mood_window, bg="#FFFFFF", width=150)
    notes_frame.pack(side=tk.LEFT, padx=10, pady=15, fill=tk.Y)

    # Add labels with emoji names and their descriptions
    for emoji, details in moods.items():
        tk.Label(
            notes_frame,
            text=f"{emoji} - {details['name']}",
            font=("Arial", 12),
            bg="#FFFFFF",
            fg="black"
        ).pack(pady=5)

    # Label to show the success message after selecting mood
    result_label = tk.Label(mood_window, text="", font=("Arial", 12), bg="#FFFFFF", fg="green")
    result_label.pack(pady=10)

    def submit_mood(mood):
        cursor.execute("INSERT INTO mood_checkins (username, mood) VALUES (?, ?)", (logged_in_user, mood))
        conn.commit()

        # Update the result label with a success message
        result_label.config(text=f"Your mood ({mood}) has been saved!")

        # Immediately refresh the pie chart to reflect updated data
        display_mood_stats()

    # Create the mood buttons for the user to choose, arranged horizontally
    button_frame = tk.Frame(mood_window, bg="#FFFFFF")
    button_frame.pack(pady=15)

    for emoji, details in moods.items():
        tk.Button(
            button_frame,
            text=f"{emoji} {details['rating']}",
            font=("Arial", 14),  # Smaller font size for better fit
            bg=details["color"],
            fg="black",
            activebackground="#FFFFFF",
            activeforeground=details["color"],
            command=lambda r=details['rating']: submit_mood(r),
            relief="groove",
            width=8,  # Smaller width for better horizontal fit
            height=2
        ).pack(side=tk.LEFT, padx=5)

    # Add the pie chart to display mood check-in statistics
    def display_mood_stats():
        cursor.execute("SELECT mood, COUNT(*) FROM mood_checkins WHERE username = ? GROUP BY mood", (logged_in_user,))
        mood_counts = cursor.fetchall()

        # Ensure that all 5 moods are represented, even if some have zero counts
        all_mood_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  # Initial count for each mood

        for mood, count in mood_counts:
            all_mood_counts[mood] = count

        # Prepare the data for the pie chart
        mood_labels = [details['name'] for emoji, details in moods.items()]  # Use mood names for pie chart labels
        mood_sizes = [all_mood_counts[details['rating']] for emoji, details in moods.items()]

        # Create the pie chart
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(mood_sizes, labels=mood_labels, autopct='%1.1f%%', startangle=90,
               colors=[details["color"] for emoji, details in moods.items()])
        ax.axis('equal')


        for widget in mood_window.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=mood_window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)


    display_mood_stats()


# COMMUNITY & CONNECTIONS
def open_community_connections():
    community_window = Toplevel(main_window)
    community_window.title("Community & Connections")
    community_window.geometry("600x900")
    community_window.configure(bg="#fff8b0")

    try:
        logo_image = Image.open("umpsalogo.png")
        logo_image = logo_image.resize((200, 200), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(community_window, image=logo, bg="#fff8b0")
        logo_label.image = logo
        logo_label.pack(pady=10)
    except:
        tk.Label(community_window, text="[Logo Not Found]", bg="#fff8b0").pack()

    tk.Label(community_window, text="UMPSA Counselors", font=("Helvetica", 15), bg="#fff8b0").pack(pady=10)

    contacts = [
        "Pn. Hajah Paridah: 0199153440",
        "Pn. Fara Hazlini: 0199819094",
        "Pn. Azila: 0134689721",
        "Pn. Siti Norni: 0139621886"
    ]

    for contact in contacts:
        tk.Label(community_window, text=contact, font=("Helvetica", 15), bg="#fff8b0").pack(pady=5)

    def join_group():
        #  WhatsApp link in a web browser
        webbrowser.open("https://chat.whatsapp.com/LukYFzypZ1Y4UZ8GjvyxZV")

    tk.Button(community_window, text="Join Support Group", command=join_group, bg="#f6fb7a").pack(pady=10)
    tk.Button(community_window, text="Contact Emergency Counselor", command=lambda: messagebox.showinfo("Contact Counselors", "Please call one of the above counselors."), bg="#f6fb7a").pack(pady=5)

#ZENZONE TIPS
def zenzone_tips():
    def display_meditation():
        meditations = [
            {"gif": "breathing.gif"},
            {"gif": "beach.gif"},
            {"gif": "deep breath.gif"}
        ]

        tip = random.choice(meditations)
        meditation_window = tk.Toplevel()
        meditation_window.title("Meditation Tip")
        meditation_window.geometry("600x500")
        meditation_window.config(bg="#c1ff72")

        try:
            gif_image = Image.open(tip["gif"])
            gif_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif_image)]

            label = tk.Label(meditation_window, bg="#caf2c2")
            label.pack(pady=20)

            def update_gif(index=0):
                frame = gif_frames[index]
                label.config(image=frame)
                meditation_window.image = frame  # Keep reference to prevent garbage collection
                meditation_window.after(100, update_gif, (index + 1) % len(gif_frames))

            update_gif()

        except Exception as e:
            tk.Label(meditation_window, text=f"GIF could not be loaded: {e}", font=("Comic Sans MS", 12), fg="black",
                     bg="#caf2c2").pack()

        tk.Button(meditation_window, text="Close", command=meditation_window.destroy, bg="#006400", fg="black",
                  font=("Comic Sans MS", 12)).pack(pady=10)


    def display_tip():
        tips = [
            {"gif": "meditation.gif"},
            {"gif": "journal.gif"},
            {"gif": "smile.gif"},
            {"gif": "eating.gif"},
            {"gif": "exercise.gif"}
        ]

        tip = random.choice(tips)
        tip_window = tk.Toplevel()
        tip_window.title("Stress Management Tip")
        tip_window.geometry("600x500")
        tip_window.config(bg="#c1ff72")

        try:
            gif_image = Image.open(tip["gif"])
            gif_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif_image)]

            label = tk.Label(tip_window, bg="#caf2c2")
            label.pack(pady=20)

            def update_gif(index=0):
                frame = gif_frames[index]
                label.config(image=frame)
                tip_window.image = frame  # Keep reference to prevent garbage collection
                tip_window.after(100, update_gif, (index + 1) % len(gif_frames))

            update_gif()

        except Exception as e:
            tk.Label(tip_window, text=f"GIF could not be loaded: {e}", font=("Comic Sans MS", 12), fg="black",
                     bg="#caf2c2").pack()

        tk.Button(tip_window, text="Close", command=tip_window.destroy, bg="#006400", fg="black",
                  font=("Comic Sans MS", 12)).pack(pady=10)

    def play_affirmation_quiz():
        affirmations = [
            "I am capable of overcoming challenges.",
            "I deserve happiness and success.",
            "I am grateful for the good things in my life.",
            "I believe in my ability to achieve my goals.",
            "I am strong, resilient, and confident."
        ]
        quiz_window = tk.Toplevel(combined_window)
        quiz_window.title("Positive Affirmations Quiz")
        quiz_window.geometry("600x400")
        quiz_window.config(bg="#caf2c2")

        question = random.choice(affirmations)
        tk.Label(quiz_window, text=question, font=("Comic Sans MS", 16), wraplength=350, pady=20, fg="black", bg="#caf2c2").pack()

        def respond(agree):
            if agree:
                messagebox.showinfo("Great!", "Keep up the positive mindset!")
            else:
                messagebox.showinfo("Reminder", "It's okay to not feel positive all the time. Take it one step at a time!")
            quiz_window.destroy()

        tk.Button(quiz_window, text="Agree", command=lambda: respond(True), bg="#538c50", fg="black", font=("Comic Sans MS", 12)).pack(pady=10)
        tk.Button(quiz_window, text="Disagree", command=lambda: respond(False), bg="#88b984", fg="black", font=("Comic Sans MS", 12)).pack(pady=10)

    # Initialize pygame mixer for sound playback
    pygame.mixer.init()

    def play_sound():
        # Path to the sound file
        sound_path = r"C:\Users\User\Desktop\music\comfort_music.mp3"
        try:
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play(-1)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to play sound: {e}")

    def stop_sound():
        pygame.mixer.music.stop()

    combined_window = tk.Toplevel(main_window)
    combined_window.title("Meditation, Tips, and Game")
    combined_window.geometry("600x900")
    combined_window.config(bg="#caf2c2")

    # Add Play and Stop buttons at the top
    play_button = tk.Button(combined_window, text="Play Sound", command=play_sound, bg="#88b984", fg="black", font=("Comic Sans MS", 12))
    play_button.pack(pady=10, anchor="w", padx=20)

    stop_button = tk.Button(combined_window, text="Stop Sound", command=stop_sound, bg="#538c50", fg="black", font=("Comic Sans MS", 12))
    stop_button.pack(pady=10, anchor="w", padx=20)

    # ZenZone Tips header
    tk.Label(combined_window, text="Reset Your Mind", font=("Comic Sans MS", 25, "bold"), fg="black", bg="#caf2c2").pack(pady=40)

    tk.Label(combined_window, text="Guided Meditation", font=("Comic Sans MS", 20, "bold"), fg="black", bg="#caf2c2").pack(pady=10)
    tk.Button(combined_window, text="Get Meditation Tip", command=display_meditation, bg="#f0f1f0", fg="black", font=("Comic Sans MS", 15)).pack(pady=10)

    tk.Label(combined_window, text="Stress Management Tips", font=("Comic Sans MS", 20, "bold"), fg="black", bg="#caf2c2").pack(pady=10)
    tk.Button(combined_window, text="Get Stress Tip", command=display_tip, bg="#f0f1f0", fg="black", font=("Comic Sans MS", 15)).pack(pady=10)

    tk.Label(combined_window, text="Positive Affirmations Quiz", font=("Comic Sans MS", 20, "bold"), fg="black", bg="#caf2c2").pack(pady=10)
    tk.Button(combined_window, text="Play Quiz", command=play_affirmation_quiz, bg="#f0f1f0", fg="black", font=("Comic Sans MS", 15)).pack(pady=10)

# --- LOGIN WINDOW ---
login_window = tk.Tk()
login_window.title("ZenZone UMPSA")
login_window.geometry("1400x1400")

# Background
try:
    bg_img = Image.open("background 4.png")
    bg_img = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(login_window, image=bg_img)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_img
except:
    login_window.configure(bg="#f0f1f0")

# Center frame
center_frame = tk.Frame(login_window, bg="#f0f1f0")
center_frame.place(relx=0.5, rely=0.4, anchor="center")

# Username field
tk.Label(center_frame, text="Username:", font=("Sans Sarif", 15), bg="#f0f1f0").pack(pady=10)
username_entry = tk.Entry(center_frame, font=("Arial", 15))
username_entry.pack(pady=10)

# Password field
tk.Label(center_frame, text="Password:", font=("Sans Sarif", 15), bg="#f0f1f0").pack(pady=10)
password_entry = tk.Entry(center_frame, show="*", font=("Arial", 15))
password_entry.pack(pady=10)

# Buttons
tk.Button(center_frame, text="Login", font=("Sans Sarif", 15), bg="#ffadad", command=login).pack(pady=10)
tk.Button(center_frame, text="Register", font=("Sans Sarif", 15), bg="#ffd6a5", command=register).pack(pady=10)

def login():
    print("Login button pressed")

def register():
    print("Register button pressed")

login_window.mainloop()
