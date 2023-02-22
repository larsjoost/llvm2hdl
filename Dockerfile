FROM ubuntu:22.10

RUN apt-get update && apt-get -y install clang

COPY cpp2hdl.sh .

