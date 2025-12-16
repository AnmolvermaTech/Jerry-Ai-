import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Controller
import requests
import json
import psutil
import os
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

# -------------------- CHAT HISTORY --------------------
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

# -------------------- SPEAK --------------------
def reply(text):
    app.ChatBot.addAppMsg(text)
    save_message("bot", text)
    print("Jerry:", text)
    if len(text) < 200:
        engine.say(text)
        engine.runAndWait()

# -------------------- STREAMING SAFE --------------------
def reply_stream(query):
    full_reply = ""
    for chunk in gemini_handler.get_gemini_response_stream(query):
        full_reply += chunk
        eel.addAppMsgStream(chunk)
        time.sleep(0.04)

    save_message("bot", full_reply)
    print("Jerry:", full_reply)


# -------------------- VOICE --------------------
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

# -------------------- FEATURES --------------------
def weather(city):
    try:
        res = requests.get(f"https://wttr.in/{city}?format=3").text
        reply(res)
    except:
        reply("Unable to fetch weather.")

def news():
    try:
        xml = requests.get("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en").text
        titles = [line.split("</title>")[0] for line in xml.split("<title>")[3:8]]
        reply("\n".join([f"{i+1}) {t}" for i, t in enumerate(titles)]))
    except:
        reply("Unable to fetch news.")

def system_info():
    try:
        battery = psutil.sensors_battery()
        reply(f"Battery {battery.percent}%")
    except:
        reply("System info unavailable.")

# -------------------- GESTURE --------------------
def start_gesture_control():
    global gc_thread, gc_active
    if gc_active:
        reply("Gesture already running.")
        return
    gc_active = True
    eel.updateGestureStatus("on")
    gc_thread = Thread(target=Gesture_Controller.GestureController().start, daemon=True)
    gc_thread.start()

def stop_gesture_control():
    global gc_active
    Gesture_Controller.GestureController.gc_mode = 0
    gc_active = False
    eel.updateGestureStatus("off")

# -------------------- COMMAND HANDLER --------------------
def respond(command):
    save_message("user", command)
    app.ChatBot.addUserMsg(command)
    command = command.lower()

    if "weather" in command:
        return weather(command.replace("weather", ""))

    if "news" in command:
        return news()

    if "battery" in command:
        return system_info()

    if "turn on gesture" in command:
        return start_gesture_control()

    if "turn off gesture" in command:
        return stop_gesture_control()

    if "time" in command:
        return reply(datetime.datetime.now().strftime("%H:%M:%S"))

    if "date" in command:
        return reply(today.strftime("%B %d, %Y"))

    if "search" in command:
        q = command.replace("search", "")
        reply(f"Searching {q}")
        return webbrowser.open(f"https://google.com/search?q={q}")

    for app_name in apps:
        if app_name in command:
            reply(f"Opening {app_name}")
            return os.system(f"start {apps[app_name]}")

    reply_stream(command)

@eel.expose
def voiceInput():
    return record_audio()

# -------------------- START UI --------------------
Thread(target=app.ChatBot.start, daemon=True).start()

while not app.ChatBot.started:
    time.sleep(0.3)

eel.updateGestureStatus("off")
reply("I am Jerry. I am listening.")

# ✅ SAFE MAIN LOOP
while app.ChatBot.started:
    msg = app.ChatBot.getUserInputSafe()
    if msg:
        respond(msg)
    time.sleep(0.05)
