import os

# Function to run shell commands
def run_shell_command(command):
    print(f"Running command: {command}")
    os.system(command)

# Main function to execute all steps
def main():
    # git cheeck for update and do it
    run_shell_command('git pull')

    # Stop any running containers
    run_shell_command('docker compose down')
    
    # Build the Docker images
    run_shell_command('docker compose build')
    
    # Start the containers in detached mode
    run_shell_command('docker compose up -d')

    print("All operations completed successfully.")

if __name__ == "__main__":
    main()
