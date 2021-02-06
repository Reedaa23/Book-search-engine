FROM python:3

ENV PYTHONUNBUFFERED 1
# copy code and install dependencies
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/

# run server
CMD python3 manage.py runserver 0.0.0.0:8000


