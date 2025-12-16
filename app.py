import eel
import os
from queue import Queue, Empty

class ChatBot:

    started = False
    userinputQueue = Queue()

    # ✅ SAFE INPUT (NO empty())
    @staticmethod
    def getUserInputSafe(timeout=0.1):
        try:
            return ChatBot.userinputQueue.get(timeout=timeout)
        except Empty:
            return None

    @staticmethod
    def close_callback(route, websockets):
        ChatBot.close()

    @staticmethod
    @eel.expose
    def getUserInput(msg):
        ChatBot.userinputQueue.put(msg)
        print(f"[User]: {msg}")

    @staticmethod
    def close():
        ChatBot.started = False
        os._exit(0)   # 🔥 IMPORTANT for COM + pycaw + mediapipe

    @staticmethod
    def addUserMsg(msg):
        eel.addUserMsg(msg)

    @staticmethod
    def addAppMsg(msg):
        eel.addAppMsg(msg)

    @staticmethod
    def start():
        path = os.path.dirname(os.path.abspath(__file__))
        eel.init(os.path.join(path, 'web'), allowed_extensions=['.js', '.html'])

        try:
            eel.start(
                'index.html',
                mode='chrome',
                host='localhost',
                port=27005,
                block=False,
                size=(350, 480),
                position=(10, 100),
                disable_cache=True,
                close_callback=ChatBot.close_callback
            )
            ChatBot.started = True

            while ChatBot.started:
                eel.sleep(0.1)

        except Exception as e:
            print("Error launching Eel:", e)
            os._exit(0)
