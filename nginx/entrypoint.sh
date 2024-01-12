#!/bin/sh

# Odnawianie certyfikatów i uruchomienie NGINX

certbot renew --quiet && nginx -g 'daemon off;'
