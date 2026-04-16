# Docker in Server

1. *Docker Image/Container*
1. *Docker Compose*
1. **Docker Compose Systemd Service**

---

## 3. Docker Compose Systemd Service

Docker Compose를 서버 부팅 시 자동으로 실행되도록 systemd 서비스로 등록한다.

---

### 서비스 파일 생성

`sudo vim /etc/systemd/system/docker-compose-app.service`

```ini
[Unit]
Description=Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/home/ubuntu
ExecStart=/usr/bin/docker compose restart
ExecStop=/usr/bin/docker compose stop
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
```

> `WorkingDirectory`는 `docker-compose.yml`이 위치한 디렉토리로 변경한다.

---

### 서비스 등록 및 활성화

```bash
# systemd 재초기화 (바이너리 교체 등 이후 필요)
sudo systemctl daemon-reexec

# 서비스 파일 변경 후 반드시 실행
sudo systemctl daemon-reload

# 부팅 시 자동 시작 등록
sudo systemctl enable docker-compose-app
```

---

### 서비스 시작

```bash
sudo systemctl start docker-compose-app
```

---

### 상태 확인 및 관리

```bash
# 서비스 상태 확인
sudo systemctl status docker-compose-app

# 서비스 중지
sudo systemctl stop docker-compose-app

# 서비스 비활성화 (자동 시작 해제)
sudo systemctl disable docker-compose-app

# 로그 확인
sudo journalctl -u docker-compose-app -f
```
