import eel
import os
from queue import Queue

class ChatBot:

    started = False
    userinputQueue = Queue()

    @staticmethod
    def isUserInput():
        return not ChatBot.userinputQueue.empty()

    @staticmethod
    def popUserInput():
        return ChatBot.userinputQueue.get()

    @staticmethod
    def close_callback(route, websockets):
        # Called when the Chrome window is closed
        ChatBot.close()

    @staticmethod
    @eel.expose
    def getUserInput(msg):
        """Triggered from JavaScript when the user sends a message."""
        ChatBot.userinputQueue.put(msg)
        print(f"[User]: {msg}")

    @staticmethod
    def close():
        """Stop the chat UI loop cleanly."""
        ChatBot.started = False

    @staticmethod
    def addUserMsg(msg):
        """Send user message to frontend for display."""
        eel.addUserMsg(msg)

    @staticmethod
    def addAppMsg(msg):
        """Send Jerry's message to frontend for display."""
        eel.addAppMsg(msg)

    @staticmethod
    def start():
        """Start the Eel web UI."""
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

            # Keep Eel running as long as the app is active
            while ChatBot.started:
                eel.sleep(0.1)
        except Exception as e:
            print("Error launching Eel:", e)
