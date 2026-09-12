# Use Python 3.11 slim image
FROM python:3.11-slim

# Install holehe and Apify SDK
# Pinned: apify SDK 4.0 (released between builds 1.0.10 and 1.0.11) removed the
# positional event-name argument of push_data(); every run on the unpinned build
# failed with "push_data() takes 2 positional arguments but 3 were given".
RUN pip install --no-cache-dir "holehe==1.61" "apify>=3.4,<4"

# Copy actor files
COPY . /app
WORKDIR /app

# Run the actor
CMD ["python", "-u", "main.py"]
