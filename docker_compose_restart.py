import os
import subprocess
import sys


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


def ensure_docker_permissions():
    user = os.getenv("USER")
    if user:
        print(f"Adding {user} to docker group...")
        run_command(f"sudo usermod -aG docker {user}")

    print("Starting Docker service...")
    run_command("sudo systemctl start docker")

    print("Setting Docker socket permissions...")
    run_command("sudo chown root:docker /var/run/docker.sock")

    print(
        "If you were added to the docker group, please log out and back in for changes to take effect."
    )


def fix_docker_dns():
    """Configure Docker to use Google DNS to avoid Tailscale MagicDNS issues during build"""
    print("Checking Docker DNS configuration...")
    daemon_path = "/etc/docker/daemon.json"
    dns_config = '{\n  "dns": ["8.8.8.8", "8.8.4.4"]\n}'
    
    # Check if needs update (simple check)
    needs_update = True
    if os.path.exists(daemon_path):
        try:
             # Need sudo to read? logical check first.
             # We will just overwrite if it doesn't look right or force it.
             # But let's verify if we can read it.
             result = subprocess.run(f"sudo cat {daemon_path}", shell=True, capture_output=True, text=True)
             if result.returncode == 0:
                 content = result.stdout
                 if '"dns":' in content and '8.8.8.8' in content:
                     print("Docker DNS already configured.")
                     needs_update = False
        except Exception as e:
             print(f"Error checking daemon.json: {e}")
             
    if needs_update:
        print("Configuring Docker to use Google DNS (fixing Tailscale conflict)...")
        # Ensure directory exists
        run_command("sudo mkdir -p /etc/docker")
        
        # Write config using tee (sudo)
        # Use simple echo to avoid string escape hell
        cmd = f"echo '{dns_config}' | sudo tee {daemon_path}"
        run_command(cmd)
        
        # Restart docker
        print("Restarting Docker to apply DNS changes...")
        run_command("sudo systemctl restart docker")
        import time
        time.sleep(5) # Wait for Docker to restart


def main():
    fix_docker_dns()
    ensure_docker_permissions()

    # Start SSH agent and add key
    subprocess.run("eval $(ssh-agent -s)", shell=True)
    subprocess.run("ssh-add ~/.ssh/id_rsa", shell=True)

    # Debug: Check if DNS applied
    print("Verifying Docker DNS setup...")
    run_command("sudo docker info | grep -i dns")

    commands = [
        "git pull",
        "sudo docker-compose down",
        "sudo DOCKER_BUILDKIT=0 docker-compose build", # Disable BuildKit to force legacy builder which might respect DNS better
        "sudo docker-compose up -d",
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
