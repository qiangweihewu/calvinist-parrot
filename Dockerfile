# Builder stage
FROM python:3.11.5 AS builder

# Set the working directory
WORKDIR /app

# Install the required packages
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install dill

# Download the NLTK punkt tokenizer
RUN python -m nltk.downloader punkt

COPY ./query_engines/reformed_theology ./app/reformed_theology
COPY .env ./app/.env
COPY main.py ./app/main.py
COPY precompute_tasks.py ./app/precompute_tasks.py

# Precompute the data
RUN python ./app/precompute_tasks.py

# Runtime stage
FROM python:3.11.5

# Set the working directory
WORKDIR /app

# Copy the results of the precomputation from the builder stage
COPY --from=builder /app/precomputed_results/ /app/precomputed_results/

# Copy only the necessary components from the builder stage
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

EXPOSE 80

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
