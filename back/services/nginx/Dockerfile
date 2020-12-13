FROM nginx:1.17-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
RUN mkdir -p /usr/src/app/
COPY static /usr/src/app/static
