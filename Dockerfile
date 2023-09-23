# Create a Dockerfile for your API
FROM python:3.11.5

# Set the working directory
WORKDIR /app

# Install the required packages
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . ./app

EXPOSE 80

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
