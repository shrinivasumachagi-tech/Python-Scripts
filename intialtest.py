import subprocess
import pyautogui
import time

# -----------------------------
# Tera Term Path
# -----------------------------
TERA_TERM = r"C:\Program Files\teraterm5\ttermpro.exe"

# -----------------------------
# Open Tera Term
# -----------------------------
process = subprocess.Popen(
    TERA_TERM,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

# Wait for Tera Term to open
time.sleep(3)

# -----------------------------
# If the New Connection dialog appears,
# Press ENTER to accept default connection
# -----------------------------
pyautogui.press("enter")

time.sleep(2)

# -----------------------------
# Type first BHEL command
# -----------------------------
pyautogui.write("help", interval=0.05)
pyautogui.press("enter")

time.sleep(2)

# -----------------------------
# Type second command
# -----------------------------
pyautogui.write("test ibcn_production fpga_io 1", interval=0.05)
pyautogui.press("enter")

# Wait for DUT response
time.sleep(5)

# -----------------------------
# Close only Tera Term
process.terminate()
process.wait()