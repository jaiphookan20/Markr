FROM python:3.10-alpine

WORKDIR /markr_app

# Add PostgreSQL client for both runtime and testing
RUN apk add --no-cache postgresql-libs postgresql-client && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

# Copy application code and setup scripts
COPY . .
COPY setup-test.sh /markr_app/setup-test.sh
RUN chmod +x /markr_app/setup-test.sh

CMD ["flask", "run", "-h", "0.0.0.0"]