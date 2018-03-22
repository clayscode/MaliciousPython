FROM ubuntu:xenial
ADD ./client /client

WORKDIR /client
RUN apt-get update && apt-get install python python-pip python-dev -y 
RUN pip install netifaces nmap wget requests

CMD ["python", "bot_client.py"]
