import os
import subprocess
import sys

def run_command(command):
    print(f"Running command: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Command succeeded: {command}\nOutput:\n{result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}\nError:\n{e.stderr}")
        return False, e.stderr

def ensure_docker_permissions():
    user = os.getenv("USER")
    if user:
        print(f"Adding {user} to docker group...")
        run_command(f"sudo usermod -aG docker {user}")

    print("Starting Docker service...")
    run_command("sudo systemctl start docker")

    print("Setting Docker socket permissions...")
    run_command("sudo chown root:docker /var/run/docker.sock")

    print("If you were added to the docker group, please log out and back in for changes to take effect.")

def main():
    if os.geteuid() != 0:
        print("This script requires administrative privileges. Please run with sudo.")
        sys.exit(1)

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
        print("Some operations failed. Please check the output above for details.")

if __name__ == "__main__":
    main()
