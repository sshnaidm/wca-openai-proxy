# Use an official Python runtime as a parent image
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/

EXPOSE 5000

# Run watson_openai_proxy.py when the container launches
# The IAM_APIKEY environment variable must be provided at runtime, e.g.,
# docker run -e IAM_APIKEY='your_actual_key' ... your_image_name
CMD ["python", "src/watson_openai_proxy.py"]
