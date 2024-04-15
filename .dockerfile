FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /mydjangoapp

COPY requirements.txt /mydjangoapp/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /mydjangoapp/

COPY .env .

WORKDIR /mydjangoapp/ecom

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


