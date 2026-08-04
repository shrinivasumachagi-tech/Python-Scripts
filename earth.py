import subprocess
import time
import pyautogui

# Open a new visible Command Prompt
process = subprocess.Popen(
    "cmd.exe",
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

# Wait for CMD to open
time.sleep(2)

# Change text color to Green
pyautogui.write("color a", interval=0.05)
pyautogui.press("enter")

time.sleep(1)

# Display ASCII Earth
pyautogui.write("curl ascii.live/earth", interval=0.05)
pyautogui.press("enter")

# Let the animation run for 5 seconds
time.sleep(5)

# Force close CMD
process.terminate()