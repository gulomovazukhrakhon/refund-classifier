# Use a lightweight Ubuntu-based Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Ensure package lists are updated and install cron 
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y cron && \
    apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Copy the crontab file
COPY config/crontab /etc/cron.d/refund_classifier_cron

# Ensure correct permissions
RUN chmod 0644 /etc/cron.d/refund_classifier_cron

# Register the crontab file
RUN echo "" >> /etc/cron.d/refund_classifier_cron && crontab /etc/cron.d/refund_classifier_cron

# Start cron and FastAPI
CMD ["sh", "-c", "service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]