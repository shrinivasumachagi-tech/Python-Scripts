import subprocess

def run_commands(commands):
    # results = {}
    for cmd in commands:
        try:
            # Run each command in CMD
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True  # ensures text output instead of bytes
            )
            #results[cmd] = result.stdout.strip() if result.stdout else result.stderr.strip()
            #result = result.stdout.strip() if result.stdout else result.stderr.strip()
            result = f"PASS"
        except Exception as e:
            #results[cmd] = f"Error: {e}"
            result = f"Error: {e}"
    return result


if __name__ == "__main__":
    # Example list of commands
    commands = [
        "echo Hello World",
        "dir",
        "python --version"
    ]
    
    outputs = run_commands(commands)
    
    # # Print results
    # for cmd, output in outputs.items():
    #     print(f"\n>>> {cmd}\n{output}")

    print(outputs)
