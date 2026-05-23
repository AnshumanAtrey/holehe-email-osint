# Use Python 3.11 slim image
FROM python:3.11-slim

# Install holehe and Apify SDK
RUN pip install --no-cache-dir holehe apify-client apify

# Copy actor files
COPY . /app
WORKDIR /app

# Run the actor
CMD ["python", "-u", "main.py"]
