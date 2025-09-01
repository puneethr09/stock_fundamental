# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port (replace 5001 with your app's port)
EXPOSE 5001

# Command to run the app (replace `app.py` with your entry point)
CMD ["python3", "app.py"]
