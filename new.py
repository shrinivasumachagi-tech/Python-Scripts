import subprocess
import time
import pyautogui

# Open a NEW visible Command Prompt
process = subprocess.Popen(
    "cmd.exe",
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

# Wait until CMD is ready
time.sleep(2)

# Change text color
pyautogui.write("color a", interval=0.05)
pyautogui.press("enter")

time.sleep(1)

# Get MAC Address
pyautogui.write("getmac", interval=0.05)
pyautogui.press("enter")

time.sleep(2)

# Run ASCII Earth
pyautogui.write("curl ascii.live/earth", interval=0.05)
pyautogui.press("enter")

# Let it run for 5 seconds
time.sleep(5)

# Force close the Command Prompt
process.terminate()