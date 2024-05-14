FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED True

WORKDIR /app

# Copy the entire project directory into the container.
COPY . /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

CMD python app.py