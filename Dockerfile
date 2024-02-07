# Use a specific Python base image
FROM python:3.10

# Set the working directory
WORKDIR /usr/src/app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Run the application
CMD ["python", "./main.py"]
