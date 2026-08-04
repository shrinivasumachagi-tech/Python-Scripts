import subprocess

try:
    # Execute getmac command
    result = subprocess.run(
        "getmac",
        shell=True,
        capture_output=True,
        text=True
    )

    # Return output to LabVIEW
    print(result.stdout)

except Exception as e:
    print(f"ERROR: {e}")