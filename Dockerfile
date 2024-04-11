FROM python:3.10.14-bullseye
WORKDIR /app
COPY MicroNAS-1.0.0-py3-none-any.whl MicroNAS-1.0.0-py3-none-any.whl
RUN pip3 install MicroNAS-1.0.0-py3-none-any.whl
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python", "main.py", "--env", "docker", "--workers", "2"]
