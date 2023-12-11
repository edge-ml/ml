FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN pip3 install MicroNAS-1.0.0-py3-none-any.whl
CMD ["python", "main.py", "--env", "docker"]
