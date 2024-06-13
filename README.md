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

- ecotour pjt 소유자 user 확인 (jinho)

```
ls -l | grep ecotour

>> drwxr-xr-x  4 jinho  staff   128  6 13 20:21 ecotour
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
   set $base_path /Users/jinho/Dev/aivlekakao/back-end/ecotour;
   - 주의<br>
     #error_log는 $base_path가 적용되지 않게 내부 설정되어 있어서 주석처리

<br>
- nginx.conf 에 구성 설정

```
vi /opt/homebrew/etc/nginx/nginx.conf
```

아래 내용 추가

```
user jinho staff;
#user nobody;
#user root;
.
.
.

# Server block for uwsgi application and static/media files
server {
    listen 8000;
    server_name localhost;

    set $base_path /Users/jinho/Dev/aivlekakao/back-end/ecotour;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:$base_path/uwsgi.sock;
    }

    location /static/ {
        alias $base_path/static/;
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

    set $base_path /Users/jinho/Dev/aivlekakao/back-end/ecotour;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:8000/static/;
    }

    location /media/ {
        proxy_pass http://127.0.0.1:8000/media/;
    }

    #error_log $base_path/logs/nginx_proxy_error.log;
    access_log $base_path/logs/nginx_proxy_access.log;

}
```

### | (배포 설정)

- nginx.conf user 설정 변경

```
vi /etc/nginx/nginx.conf

>>
user ubuntu;
#user nobody;
#user root;
```

- sites-available/ecotour 에 server 구성 설정

```
vi /etc/nginx/sites-available/ecotour
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
        alias $base_path/static/;
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

    set $base_path /home/ubuntu/back-end/ecotour;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:8000/static/;
    }

    location /media/ {
        proxy_pass http://127.0.0.1:8000/media/;
    }

    #error_log $base_path/logs/nginx_proxy_error.log;
    access_log $base_path/logs/nginx_proxy_access.log;

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
/ecotour/logs<br>
/ecotour/media
```

### 1. app static 모아 정적파일 생성

- app에 새로운 static 추가가 있었을 경우 필요

```
python manage.py collectstatic
```

### 2. nginx 실행

```
sudo brew services start nginx
```

### 3. uwsgi 실행

```
uwsgi --ini uwsgi.ini
```

### 4. 사이트 접속

http://localhost

---
