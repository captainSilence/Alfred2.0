FROM ubuntu:latest

WORKDIR /root/
# change of variable to avoid configuration questions
ENV DEBIAN_FRONTEND=noninteractive
# update to the lastest code
RUN apt update
RUN apt install python3-pip python3-dev libpq-dev gunicorn vim -y

COPY gunicorn/requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt
COPY gunicorn/entrypoint.sh /root/entrypoint.sh



ENTRYPOINT [ "./entrypoint.sh" ]
# CMD ["gunicorn","--chdir", "/root/web_project", "-b", "0.0.0.0:8000", "web_project.wsgi"]


