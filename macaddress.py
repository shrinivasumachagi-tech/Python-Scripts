import subprocess
import time
import pyautogui

# Open visible Command Prompt
subprocess.Popen("cmd.exe")

# Wait for the window to appear
time.sleep(2)

# Type the command automatically
pyautogui.write("getmac", interval=0.05)

# Press Enter
pyautogui.press("enter")

# Wait so you can see the result
time.sleep(5)

# Type exit
pyautogui.write("exit", interval=0.05)

# Press Enter
pyautogui.press("enter")