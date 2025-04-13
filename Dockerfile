FROM python:3.10-alpine

WORKDIR /markr_app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "run", "-h", "0.0.0.0"]