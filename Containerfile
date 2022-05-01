FROM docker.io/library/python:3.9.2-alpine

ARG ZIP_NAME

USER root
RUN mkdir /usr/src/spam && mkdir /usr/src/srv
COPY $ZIP_NAME /usr/src/spam

WORKDIR /usr/src/srv

COPY server.sh log_injector.sh /usr/src/srv/
RUN chown -R 1001:1001 /usr/src/srv
USER 1001
ENTRYPOINT ["/usr/src/srv/server.sh"]
