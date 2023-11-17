FROM python:3.10.12
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3000
EXPOSE 5000
ENTRYPOINT ["python3", "main.py"]