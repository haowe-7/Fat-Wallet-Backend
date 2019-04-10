FROM python:3.7.3

COPY assets /tmp/assets
RUN env bash /tmp/assets/install.sh

CMD ["/usr/local/bin/init"]

EXPOSE 5000 22