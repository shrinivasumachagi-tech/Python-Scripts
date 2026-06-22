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

# Change text color to Green
pyautogui.write("color a", interval=0.05)
pyautogui.press("enter")

time.sleep(1)

# Type the command
pyautogui.write("getmac", interval=0.05)
pyautogui.press("enter")

# Wait for command to execute
time.sleep(3)

# Type exit
pyautogui.write("exit", interval=0.05)
pyautogui.press("enter")