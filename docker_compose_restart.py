import os
import subprocess

def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)

def ensure_docker_permissions():
    # Add current user to docker group
    user = os.getenv("USER")
    run_command(f"sudo usermod -aG docker {user}")

    # Start Docker service if not running
    run_command("sudo systemctl start docker")

    # Ensure correct permissions on Docker socket
    run_command("sudo chown root:docker /var/run/docker.sock")

def main():
    ensure_docker_permissions()

    commands = [
        "git pull",
        "docker compose down",
        "docker compose build",
        "docker compose up -d",
    ]

    results = []
    for cmd in commands:
        success, output = run_command(cmd)
        results.append({"command": cmd, "success": success, "output": output})

    all_successful = all(result["success"] for result in results)

    if all_successful:
        print("All operations completed successfully.")
    else:
        for result in results:
            if not result["success"]:
                print(f"Error running command: {result['command']}\nOutput: {result['output']}")

if __name__ == "__main__":
    main()
