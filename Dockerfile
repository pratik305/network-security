FROM python:3.10-slim-bullseye

WORKDIR /app

RUN apt-get update -y && apt-get install -y awscli

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
