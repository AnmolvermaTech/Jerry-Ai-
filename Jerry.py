# Jerry.py - Balanced Mode + Gesture UI Status + Chat History + Clear Chat Support

import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Controller
import sys
import os
import json
import Gesture_Controller
import app
from threading import Thread
import gemini_handler
import eel

today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init()
engine.setProperty('voice', engine.getProperty('voices')[0].id)

is_awake = True
gc_thread = None
gc_active = False

HISTORY_FILE = "chat_history.json"

apps = {
    "spotify": "spotify",
    "whatsapp": "whatsapp",
    "chrome": "chrome",
    "notepad": "notepad",
    "calculator": "calc",
    "vs code": "code"
}

gemini_handler.initialize_gemini()


def save_message(sender, message):
    try:
        data = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
        data.append({"sender": sender, "text": message})
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass


@eel.expose
def clearHistory():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


@eel.expose
def loadHistory():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def reply(audio):
    app.ChatBot.addAppMsg(audio)
    save_message("bot", audio)
    print(f"Jerry: {audio}")
    if len(audio) < 200:
        engine.say(audio)
        engine.runAndWait()


def record_audio():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=5)
        except:
            return ""
    try:
        return r.recognize_google(audio).lower()
    except:
        return ""


def start_gesture_control():
    global gc_thread, gc_active
    if gc_active:
        reply("Gesture controller is already running.")
        eel.updateGestureStatus("on")
        return
    reply("Starting Gesture Controller...")
    gc_active = True
    eel.updateGestureStatus("on")
    gc_thread = Thread(target=Gesture_Controller.GestureController().start)
    gc_thread.daemon = True
    gc_thread.start()


def stop_gesture_control():
    global gc_active
    if not gc_active:
        reply("Gesture controller is already off.")
        return
    reply("Stopping Gesture Controller...")
    Gesture_Controller.GestureController.gc_mode = 0
    gc_active = False
    eel.updateGestureStatus("off")


def respond(command):
    save_message("user", command)
    app.ChatBot.addUserMsg(command)
    command = command.lower()

    if "turn on gesture" in command:
        return start_gesture_control()
    if "turn off gesture" in command:
        return stop_gesture_control()

    if "time" in command:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])
        return

    if "date" in command:
        reply(today.strftime("%B %d, %Y"))
        return

    if "search" in command:
        term = command.replace("search", "").strip()
        reply(f"Searching {term}")
        webbrowser.open(f"https://google.com/search?q={term}")
        return

    for app_name in apps:
        if app_name in command:
            reply(f"Opening {app_name}")
            os.system(f"start {apps[app_name]}")
            return

    reply(gemini_handler.get_gemini_response(command))


@eel.expose
def voiceInput():
    return record_audio()


# Start UI
t1 = Thread(target=app.ChatBot.start)
t1.start()
while not app.ChatBot.started:
    time.sleep(0.5)

# ✅ Greet only if chat history is empty
if not os.path.exists(HISTORY_FILE):
    reply("I am Jerry. I am listening.")
else:
    print("History loaded. Skipping greeting.")

eel.updateGestureStatus("off")

while True:
    if app.ChatBot.isUserInput():
        respond(app.ChatBot.popUserInput())
        continue

    heard = record_audio()
    if "jerry" in heard:
        reply("Yes, I'm listening.")
