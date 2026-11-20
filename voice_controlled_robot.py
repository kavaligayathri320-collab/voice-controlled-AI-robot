"""
Voice Controlled AI Robot - Python voice controller
Assumption: A computer microphone captures speech and sends commands to Arduino UNO
through USB serial. Arduino UNO controls an L298N motor driver.
"""

import time
import serial
import speech_recognition as sr

# Change this to your Arduino port:
# Windows example: "COM3" or "COM4"
# Linux example: "/dev/ttyACM0"
# macOS example: "/dev/cu.usbmodemXXXX"
SERIAL_PORT = "COM3"
BAUD_RATE = 9600

COMMANDS = {
    "forward": ("F", ["forward", "go forward", "move forward"]),
    "backward": ("B", ["backward", "go backward", "move backward", "reverse"]),
    "left": ("L", ["left", "turn left", "go left"]),
    "right": ("R", ["right", "turn right", "go right"]),
    "stop": ("S", ["stop", "halt", "stay", "freeze"]),
}

def convert_speech_to_command(text):
    text = text.lower()
    for command, (code, phrases) in COMMANDS.items():
        if any(phrase in text for phrase in phrases):
            return command, code
    return None, None

def main():
    print("Voice Controlled AI Robot")
    print("Say: forward, backward, left, right, or stop.")
    print("Press Ctrl+C to exit.")

    try:
        robot = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow Arduino to reset after serial connection
    except serial.SerialException as error:
        print(f"Could not open {SERIAL_PORT}: {error}")
        print("Check the USB cable and update SERIAL_PORT in this file.")
        return

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as microphone:
            recognizer.adjust_for_ambient_noise(microphone, duration=1)
            while True:
                try:
                    print("\nListening...")
                    audio = recognizer.listen(microphone, timeout=5, phrase_time_limit=4)
                    spoken_text = recognizer.recognize_google(audio)
                    print("Heard:", spoken_text)

                    command, code = convert_speech_to_command(spoken_text)
                    if code:
                        robot.write((code + "\n").encode("utf-8"))
                        print("Command sent:", command)
                    else:
                        robot.write(b"S\n")
                        print("Command not recognized. Robot stopped for safety.")

                except sr.WaitTimeoutError:
                    print("No speech detected.")
                except sr.UnknownValueError:
                    robot.write(b"S\n")
                    print("Sorry, I did not understand. Robot stopped.")
                except sr.RequestError as error:
                    robot.write(b"S\n")
                    print("Speech service error:", error)
                    print("Check your internet connection.")
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
    except (OSError, AttributeError) as error:
        print("Microphone problem:", error)
    finally:
        try:
            robot.write(b"S\n")
            robot.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
