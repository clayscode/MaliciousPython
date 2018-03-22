FROM ubuntu:xenial
ADD ./server /server

WORKDIR /server
RUN apt-get update && apt-get install python python-pip python-dev screen netcat-traditional -y 
RUN pip install flask uwsgi
CMD ["uwsgi", "--ini", "config.ini"]
