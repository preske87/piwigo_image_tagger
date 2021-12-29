# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster
WORKDIR /
RUN mkdir config
COPY lib /lib
RUN mkdir log
COPY generate_tags.py /
COPY pip_requirements.txt pip_requirements.txt
RUN pip3 install requests
RUN pip3 install -r pip_requirements.txt
CMD ["python3", "generate_tags.py"]