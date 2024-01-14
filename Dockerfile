FROM python:3.9-slim

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Declare environment variables (values will be provided at runtime)
ENV AWS_ACCESS_KEY_ID=
ENV AWS_REGION=
ENV AWS_SECRET_ACCESS_KEY=
ENV SNOW_CLIENT_ID=
ENV SNOW_CLIENT_SECRET=
ENV SNOW_USER=
ENV SNOW_PASSWORD=
ENV SNOW_INSTANCE=

CMD ["flask", "run"]
