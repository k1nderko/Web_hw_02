
FROM python:3.10

# Установим переменную окружения
# ENV APP_HOME /app

# Установим рабочую директорию внутри контейнера
# WORKDIR $APP_HOME
WORKDIR /app

COPY . .


RUN pip install -r requirements.txt


EXPOSE 5000


ENTRYPOINT ["python", "main.py"]
