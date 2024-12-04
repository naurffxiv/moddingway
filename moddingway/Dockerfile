FROM python:3.11

# install required packages
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt

COPY . /opt/app
WORKDIR /opt/app

CMD ["python", "./main.py"]