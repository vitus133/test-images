FROM python:3.9-alpine

ARG ZIP_NAME
# Add application sources
USER root
RUN mkdir /usr/src/spam
WORKDIR /usr/src/spam
COPY $ZIP_NAME /usr/src/spam

RUN mkdir /usr/src/srv
WORKDIR /usr/src/srv

COPY server.sh /usr/src/srv/
RUN chown -R 1001:1001 /usr/src/srv
USER 1001
ENTRYPOINT ["/usr/src/srv/server.sh"]
