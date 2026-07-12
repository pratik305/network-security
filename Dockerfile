FROM python:3.10-slim-buster

WORKDIR /app

COPY . /app

# Update pip and install AWS CLI
RUN apt-get update -y && apt-get install -y awscli

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]