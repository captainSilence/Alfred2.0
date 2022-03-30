FROM nginxinc/nginx-unprivileged:1-alpine
# copy configuration for nginx
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
# switch tmp to root for create files
USER root
# create directory
RUN mkdir -p /vol/static
# copy all static files
COPY nginx/static /vol/static
# give permissions to directory
RUN chmod 755 /vol/static
# switch to default user
USER nginx