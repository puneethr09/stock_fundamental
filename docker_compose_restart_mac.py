import os
import subprocess


def run_command(command):
    print(f"Running command: {command}")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"Command succeeded: {command}\nOutput:\n{result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}\nError:\n{e.stderr}")
        return False, e.stderr


def check_docker_daemon():
    print("Checking if Docker daemon is running...")
    result = subprocess.run(
        "docker info", shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Docker daemon is not running. Please start Docker Desktop.")
        return False
    print("Docker daemon is running.")
    return True


def check_docker_compose():
    print("Checking Docker Compose version...")
    result = subprocess.run(
        "docker-compose --version", shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Docker Compose is not installed or not accessible.")
        print("Please ensure Docker Compose is installed and accessible.")
        return False
    print(f"Docker Compose version:\n{result.stdout}")
    return True


def main():
    # Check if Docker daemon is running
    if not check_docker_daemon():
        return

    # Check if Docker Compose is accessible
    if not check_docker_compose():
        return

    # Start SSH agent and add key
    subprocess.run("eval $(ssh-agent -s)", shell=True)
    ssh_key_path = os.path.expanduser("~/.ssh/id_rsa")
    if os.path.exists(ssh_key_path):
        subprocess.run(f"ssh-add {ssh_key_path}", shell=True)
    else:
        print(f"SSH key not found at {ssh_key_path}. Skipping SSH key addition.")

    commands = [
        "git pull",
        "docker-compose down",
        "docker-compose build",
        "docker-compose up -d",
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