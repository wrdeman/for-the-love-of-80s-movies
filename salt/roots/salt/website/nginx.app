server{
  # server_name 127.0.0.1 yourhost@example.com;
  access_log /var/log/nginx/domain-access.log;

  location / {
    proxy_pass_header Server;
    proxy_set_header Host $host:$server_port;
    proxy_redirect off;
    proxy_set_header X-Forwarded-For  $remote_addr;
    proxy_set_header X-Scheme $scheme;
    proxy_connect_timeout 10;
    proxy_read_timeout 10;

    location /static/ {
      alias /home/vagrant/app/movies/static/;
      expires 1d;
    }


    # This line is important as it tells nginx to channel all requests to port 8000.
    # We will later run our wsgi application on this port using gunicorn.
    proxy_pass http://127.0.0.1:8000/;
  }

}
