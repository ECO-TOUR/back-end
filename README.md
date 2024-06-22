# back-end

## 🔍 백엔드 초기 환경세팅

### • 라이브러리 설치

### 1. 가상환경 생성

```
python3.9 -m venv venv
```

### 2. 가상환경 이동

BaseDir= {BACK-END}

```
source ./venv/bin/activate
```

### 3. pip install upgrade

```
pip install --upgrade pip
```

### 4. requirements.txt 설치

```
pip install -r requirements.txt
```

<br>

---

### 🖍️ nginx 설정: os에 따라 명령어는 상이하므로 확인 필요

### 5. nginx 설치

```
brew install nginx
```

### 6. nginx.conf 서버설정 추가

- ecotour pjt 소유자 user 확인 {username}

```
ls -l | grep ecotour

>> drwxr-xr-x  4 {username}  staff   128  6 13 20:21 ecotour
```

- nginx.conf 위치 확인

```
sudo nginx -t

>>  /opt/homebrew/etc/nginx/nginx.conf
```

- nginx.conf 수정

### | (로컬 설정)

1. user (ecotour 소유자) 설정과<br>
   다른 user 주석처리
2. 서버 설정 추가(80: proxy port / 8000: WAS port)<br>
   베이스 경로 설정 (자신 환경의 디렉토리 경로로 변경)<br>
   set $base_path /Users/{username}/Dev/aivlekakao/back-end/ecotour;
   - 주의<br>
     #error_log는 $base_path가 적용되지 않게 내부 설정되어 있어서 주석처리

<br>
- nginx.conf 에 구성 설정

```
vi /opt/homebrew/etc/nginx/nginx.conf
```

아래 내용 추가

```
user {username} staff;
#user nobody;
#user root;
.
.
.

# Server block for uwsgi application and static/media files
server {
    listen 8000;
    server_name localhost;

    set $base_path /Users/{username}/Dev/aivlekakao/back-end/ecotour;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:$base_path/uwsgi.sock;
    }

    location /static/ {
        alias $base_path/staticfiles/;
    }

    location /media/ {
        alias $base_path/media/;
    }

    #error_log $base_path/logs/nginx_error.log;
    access_log $base_path/logs/nginx_access.log;
}

# Proxy server block
server {
    listen 80;
    server_name localhost;

    set $base_path /Users/{username}/Dev/aivlekakao/back-end/ecotour;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:8000/staticfiles/;
    }

    location /media/ {
        proxy_pass http://127.0.0.1:8000/media/;
    }

    #error_log $base_path/logs/nginx_proxy_error.log;
    access_log $base_path/logs/nginx_proxy_access.log;

}
```

### | (배포 설정: HTTPS - SSL인증서 발급)

- openssl 설치

```
sudo apt update
sudo apt install openssl
openssl version
```

- SSL인증서 발급

```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
-keyout /etc/ssl/private/localhost-selfsigned.key \
-out /etc/ssl/certs/localhost-selfsigned.crt
```

- nginx.conf user 설정 변경

```
sudo vi /etc/nginx/nginx.conf

>>
user ubuntu;
#user nobody;
#user root;
```

- sites-available/ecotour 에 server 구성 설정

```
sudo vi /etc/nginx/sites-available/ecotour
```

아래 내용 작성

```

# Server block for uwsgi application and static/media files
server {
    listen 8000;
    server_name localhost;

    set $base_path /home/ubuntu/back-end/ecotour;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:$base_path/uwsgi.sock;
    }

    location /static/ {
        alias $base_path/staticfiles/;
    }

    location /media/ {
        alias $base_path/media/;
    }

    #error_log $base_path/logs/nginx_error.log;
    access_log $base_path/logs/nginx_access.log;
}


# HTTPS server block for uwsgi application and static/media files
server {
    listen 443 ssl;
    server_name localhost;  # or your_domain_or_ip for production

    ssl_certificate /etc/ssl/certs/localhost-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/localhost-selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    set $base_path /home/ubuntu/back-end/ecotour;

    location / {
        proxy_pass http://127.0.0.1:8000;  # Internal communication
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias $base_path/staticfiles/;
    }

    location /media/ {
        alias $base_path/media/;
    }

    # error_log $base_path/logs/nginx_error.log;
    access_log $base_path/logs/nginx_access.log;
}

# HTTP server block to redirect all traffic to HTTPS
server {
    listen 80;
    server_name localhost;  # or your_domain_or_ip for production

    location / {
        return 301 https://$host$request_uri;
    }

    # error_log $base_path/logs/nginx_http_error.log;
    access_log $base_path/logs/nginx_http_access.log;
}
```

- 심볼릭 링크 연결

```
sudo ln -s /etc/nginx/sites-available/ecotour /etc/nginx/sites-enabled/
```

- default 구성 포트 변경(80 -> 8080)

```
sudo vi /etc/nginx/sites-available/default
>>
listen 8080 default_server;
listen [::]:8080 default_server;
```

<br>

---

<br>

## 🔍 서버 실행 방법

### 0. /BACK-END/ecotour 하위에 디렉토리 생성 (존재하지 않을 경우)

```
/ecotour/logs
/ecotour/media
```

### 1. app static 모아 정적파일 생성

- app에 새로운 static 추가가 있었을 경우 필요

```
python manage.py collectstatic
```

### 2. nginx 실행

- 개발 서버

```
>>> 개발 서버
sudo brew services start nginx
>>> 배포 서버
sudo nginx
```

### 3. uwsgi 실행

```
uwsgi --ini uwsgi.ini
```

### 4. 사이트 접속

- 개발 서버 http://localhost <br>
- 배포 서버 https://{domain_ip | domain_url}

---
