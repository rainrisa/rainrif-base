FROM python:3.8-slim-buster

WORKDIR /rainrif

RUN apt update

# node is needed by py-tgcalls
RUN apt install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash
RUN apt install -y nodejs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]