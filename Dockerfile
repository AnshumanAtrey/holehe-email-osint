# Use Python 3.11 slim image
FROM python:3.11-slim

# Install holehe and Apify SDK
# SDK 4 (apify-client 3.x) is required: SDK 3.x crashed with exit 91 after delivering
# results on runs started by Apify's AI assistant (run origin APIFY_AI, 2026-10-27).
# SDK 4 makes push_data's charged_event_name keyword-only, which main.py passes by
# name. Capped below 5 so a rebuild cannot pull the next major.
RUN pip install --no-cache-dir "holehe==1.61" "apify>=4.1,<5"

# Copy actor files
COPY . /app
WORKDIR /app

# Run the actor
CMD ["python", "-u", "main.py"]
