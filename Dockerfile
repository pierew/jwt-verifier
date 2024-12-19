FROM alpine
LABEL version="1.0.0"
LABEL org.opencontainers.image.authors="coding@pierewoehl.de"
LABEL description="Container to validate JWT token against JWTS or given public key"
RUN apk add python3
RUN apk add py3-cryptography py3-jwt
RUN apk cache clean
COPY app /app
CMD ["/usr/bin/python3","/app/app.py"]
EXPOSE 8080/tcp
