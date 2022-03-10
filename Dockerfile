FROM python:3.9-slim
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir /src
WORKDIR /src
COPY . /src