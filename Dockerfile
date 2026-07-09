FROM python:3.10.14-bullseye
WORKDIR /app
COPY MicroNAS-1.0.0-py3-none-any.whl MicroNAS-1.0.0-py3-none-any.whl
RUN pip3 install MicroNAS-1.0.0-py3-none-any.whl
# Install the CPU build of torch first so the CUDA build (several GB) is never pulled in.
RUN pip3 install torch==2.9.0 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
# lttbc's isolated build compiles against numpy 1.x and then fails to import
# under the numpy 2 pin — rebuild it against the installed numpy.
RUN pip3 install --force-reinstall --no-deps --no-build-isolation --no-cache-dir lttbc==0.2.4
# The executorch .pte serializer shells out to the flatbuffers compiler (flatc),
# which is not bundled in the executorch wheel.
RUN curl -fsSL "https://github.com/google/flatbuffers/releases/download/v25.2.10/Linux.flatc.binary.g%2B%2B-13.zip" -o /tmp/flatc.zip \
    && python3 -c "import zipfile; zipfile.ZipFile('/tmp/flatc.zip').extractall('/usr/local/bin')" \
    && chmod +x /usr/local/bin/flatc \
    && rm /tmp/flatc.zip \
    && flatc --version
COPY . .
CMD ["python", "main.py", "--env", "docker", "--workers", "2"]
