FROM ubuntu:latest
RUN apt-get update && \
    apt-get install -y python3 python3-flask  
COPY . .
RUN echo "net.ipv4.tcp_syncookies = 0" >> /etc/sysctl.conf
EXPOSE 5000
CMD ["python3", "webApp.py", "--debug=false", "--host=0.0.0.0"]
