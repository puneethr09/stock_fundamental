import os
import subprocess
import sys

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
    if user:
        print(f"Adding {user} to docker group...")
        run_command(f"sudo usermod -aG docker {user}")

    # Start Docker service if not running
    print("Starting Docker service...")
    run_command("sudo systemctl start docker")

    # Ensure correct permissions on Docker socket
    print("Setting Docker socket permissions...")
    run_command("sudo chown root:docker /var/run/docker.sock")

    # Inform the user to log out and back in if they were added to the docker group
    print("If you were added to the docker group, please log out and back in for changes to take effect.")

def main():
    # Check if script is run with sudo
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
        print(f"Running command: {cmd}")
        success, output = run_command(cmd)
        results.append({"command": cmd, "success": success, "output": output})
        if not success:
            print(f"Error running command: {cmd}\nOutput: {output}")

    all_successful = all(result["success"] for result in results)

    if all_successful:
        print("All operations completed successfully.")
    else:
        print("Some operations failed. Please check the output above for details.")

if __name__ == "__main__":
    main()
