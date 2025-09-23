import time
import pickle
import os
from pynput import mouse, keyboard

recorded_events = []
recording = False

def on_click(x, y, button, pressed):
    if recording:
        recorded_events.append(('mouse', time.time(), x, y, button, pressed))

def on_press(key):
    if recording:
        recorded_events.append(('keyboard', time.time(), key, True))

def on_release(key):
    if recording:
        recorded_events.append(('keyboard', time.time(), key, False))
        if key == keyboard.Key.esc :  # stop recording on ESC
            return False
    if not recording :
        if key == keyboard.Key.esc :
            sys.exit()

def record_macro():
    global recording, recorded_events
    recorded_events = []
    recording = True
    start_time = time.time()

    with mouse.Listener(on_click=on_click) as m_listener, \
         keyboard.Listener(on_press=on_press, on_release=on_release) as k_listener:
        k_listener.join()

    # Normalize times
    base_time = start_time
    for i in range(len(recorded_events)):
        recorded_events[i] = (recorded_events[i][0], 
                              recorded_events[i][1] - base_time, 
                              *recorded_events[i][2:])

    with open("macro.pkl", "wb") as f:
        pickle.dump(recorded_events, f)

def play_macro():
    from pynput.mouse import Controller as MouseController, Button
    from pynput.keyboard import Controller as KeyboardController, Key
    with open("macro.pkl", "rb") as f:
        events = pickle.load(f)

    mouse_ctrl = MouseController()
    keyboard_ctrl = KeyboardController()

    start = time.time()
    for event in events:
        ev_type, ev_time, *data = event
        wait = (start + ev_time) - time.time()
        if wait > 0:
            time.sleep(wait)

        if ev_type == 'mouse':
            x, y, button, pressed = data
            mouse_ctrl.position = (x, y)
            if pressed:
                mouse_ctrl.press(button)
            else:
                mouse_ctrl.release(button)

        elif ev_type == 'keyboard':
            key, pressed = data
            try:
                if pressed:
                    keyboard_ctrl.press(key.char if hasattr(key, 'char') else key)
                else:
                    keyboard_ctrl.release(key.char if hasattr(key, 'char') else key)
            except:
                pass  # skip unknown keys

if __name__ == "__main__":
    if os.path.exists("macro.pkl") :
        temp = input("Macro exists already, play macro? (Y/N)")
        if temp.lower() == 'y':
            var = input("Repeat macro how many times?")
            print("Playing back macro...")
            time.sleep(2)
            try :
                for i in range(int(var)):
                    play_macro()
            except Exception as e :
                print("error: " + e)
        else :
            print("creating new macro")
            print("Press ESC to stop recording.")
            record_macro()     
    else :
        print("no macro exists, creating new macro...")
        print("Press ESC to stop recording.")
        record_macro()
        temp = input("Play new macro? (Y/N)")
        if temp.lower() == 'y':
            var = input("Repeat macro how many times?")
            print("Playing back macro...")
            time.sleep(2)
            try :
                for i in range(int(var)):
                    play_macro()
            except Exception as e :
                print("error: " + e)
        else : pass
        
