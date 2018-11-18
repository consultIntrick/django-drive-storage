FROM python:3.5.3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD ./requirements/ /code/requirements/
RUN pip install --upgrade pip
RUN pip install -r /code/requirements/base.txt
