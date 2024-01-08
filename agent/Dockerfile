FROM ericjuice/bcc-env-ubuntu20:1.0

COPY ./build/agent.o /app
COPY ./src/ /app/src

WORKDIR /app

EXPOSE 30002

CMD ["./agent.o"]