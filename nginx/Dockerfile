FROM nginx

# Zainstaluj potrzebne pakiety
RUN apt-get update && \
    apt-get install -y certbot 

# Skopiuj konfigurację NGINX
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-selfsigned.crt /etc/nginx/nginx-selfsigned.crt
COPY ./nginx-selfsigned.key /etc/nginx/nginx-selfsigned.key

# Skrypt uruchamiający NGINx
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["./entrypoint.sh"]
