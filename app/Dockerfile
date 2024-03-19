FROM python:3.11.5

# Set the working directory
WORKDIR /app


# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the required packages
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install "cloud-sql-python-connector[pg8000]"

# Download the NLTK punkt tokenizer
RUN python -m nltk.downloader punkt

COPY . ./app

EXPOSE 8080

# Run the app
ENTRYPOINT ["streamlit", "run", "app/Home.py", "--server.address=0.0.0.0", "--server.port=8080", "--browser.gatherUsageStats=False"]
