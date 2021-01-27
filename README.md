# monco
  running under existing website subfolder (virtual host), settings for gunicorn and nginx
  make sure you read about SCRIPT_NAME environment settings of gunicorn

## systemd gunicorn service:
* /etc/systemd/system/monco.service
```
[Unit]
Description=Gunicorn instance to serve monco
After=network.target

[Service]
User=xxxx
Group=www-data
WorkingDirectory=/home/xxxxx/xxxx/monco
Environment="PATH=/home/xxxxx/xxxx/monco/env/bin"
#ExecStart=/home/xxxxx/xxxx/monco/env/bin/gunicorn --workers 2 --bind unix:monco.sock -m 007 wsgi:application
ExecStart=/home/xxxxx/xxxx/monco/env/bin/gunicorn --workers 2 --env SCRIPT_NAME=/monco --bind unix:monco.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

## nginx settings:
* /etc/nginx/sites-available/xxx.com
```
upstream monco_server {
 server unix:/home/xxxxx/xxxx/monco/monco.sock fail_timeout=0;
}

......

server {
    listen 443 ssl http2;
    server_name abcd.com;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    # Proxy headers
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # SSL parameters
    ........

    # log files
    ........

    # Handle longpoll requests
    .......

    # Handle / requests
    location / {
       proxy_redirect off;
       proxy_pass http://xxxxxx;
    }

    # Handle /monco requests
    location /monco {
       proxy_set_header Host $http_host;
       proxy_redirect off;
       #include proxy_params;
       proxy_pass http://monco_server;
    }
    .......

```


