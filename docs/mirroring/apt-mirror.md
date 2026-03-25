# APT Mirror & Proxy 구축 가이드 (폐쇄망 실무용)

## 1. 네트워크 구성 개요

* **Origin Mirror (151 서버):** 실제 패키지 데이터 저장 및 Nginx 서빙.
* **Reverse Proxy (149 서버):** 외부망 통신이 불가능한 클라이언트(110.X 등)를 위한 중계 서버.
* **Clients (100.X / 110.X):** * **100.X 대역:** 151 서버와 직접 통신 가능 시 151로 설정.
* **110.X 대역:** 149 서버를 Proxy로 경유하여 151 데이터 접근.

---

## 2. [151 서버] APT Mirror & Nginx 설정

### 2.1 디렉토리 구조 최적화

`apt-mirror`가 내려받는 모든 데이터는 최종적으로 `mirror` 디렉토리에 위치해야 합니다.

```bash
/data/mirror
├─ mirror/archive.ubuntu.com/ubuntu  # 실제 데이터
├─ mirror/ftp.kaist.ac.kr/ubuntu     # 실제 데이터
├─ skel/                             # 인덱스 구조 (참조용)
└─ var/                              # 로그 및 상태 정보
```

### 2.2 Nginx 설정 (`/etc/nginx/sites-available/apt-mirror`)

`$host` 변수를 사용하여 여러 도메인을 하나의 블록에서 처리합니다.

```nginx
server {
    listen 80;
    server_name archive.ubuntu.com ftp.kaist.ac.kr download.docker.com ppa.launchpad.net;

    # 실제 패키지 경로 (ubuntu 폴더 바로 위까지 지정)
    root /data/mirror/mirror/$host;

    location / {
        autoindex on;
        tcp_nodelay on;
        sendfile on;
    }
}
```

**반드시 실행:**

```bash
sudo ln -s /etc/nginx/sites-available/apt-mirror /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

---

## 3. [149 서버] Reverse Proxy 설정

151 서버에 직접 접근할 수 없는 클라이언트를 위해 요청을 중계합니다.

### 3.1 Nginx 설정 (`/etc/nginx/sites-available/apt-proxy`)

```nginx
server {
    listen 80;
    server_name archive.ubuntu.com ftp.kaist.ac.kr download.docker.com ppa.launchpad.net;

    location / {
        proxy_pass http://119.86.100.151; # 151 서버로 전달
        proxy_set_header Host $host;      # 클라이언트가 요청한 도메인 그대로 전달
        proxy_set_header X-Real-IP $remote_addr;
        
        # 대용량 패키지 다운로드 타임아웃 방지
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
```

**반드시 실행:** `sudo nginx -t && sudo systemctl reload nginx`

---

## 4. [클라이언트 서버] 대역별 설정

### 4.1 `/etc/hosts` 설정 (가장 중요)

접근 가능한 경로에 따라 IP를 다르게 매핑합니다.

* **100.X 대역 (151 직접 접근):**

    ```text
    119.86.100.151 archive.ubuntu.com ftp.kaist.ac.kr
    ```

* **110.X 대역 (149 프록시 경유):**

    ```text
    119.86.100.149 archive.ubuntu.com ftp.kaist.ac.kr
    ```

### 4.2 `/etc/apt/sources.list`

모든 클라이언트는 동일하게 설정합니다.

```bash
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
```

---

## 5. 필수 트러블슈팅 및 최적화

### 5.1 CNF(Command-Not-Found) 에러 방지

폐쇄망 미러링 시 가장 많이 발생하는 404 에러 원인입니다. 클라이언트에서 실행하세요.

```bash
# cnf 조회를 비활성화하는 설정 파일 생성
echo 'Acquire::IndexTargets::deb::Contents-deb::DefaultEnabled "false";' | sudo tee /etc/apt/apt.conf.d/99disable-cnf

# 기존 에러가 있는 인덱스 초기화
sudo rm -rf /var/lib/apt/lists/*
sudo apt update
```

### 5.2 GPG 키 인증 건너뛰기 (선택사항)

폐쇄망에서 키 등록이 번거로울 경우 `sources.list`에 직접 옵션을 부여합니다.

```bash
deb [trusted=yes] http://archive.ubuntu.com/ubuntu jammy main ...
```

### 5.3 Nginx `root` 경로 검증

클라이언트에서 테스트 시 404가 뜨면 151 서버에서 실제 파일 위치를 확인하세요.

* **요청 주소:** `http://archive.ubuntu.com/ubuntu/dists/...`
* **151 설정:** `root /data/mirror/mirror/archive.ubuntu.com;`
* **실제 경로:** `/data/mirror/mirror/archive.ubuntu.com/ubuntu/dists/...` 가 맞는지 확인.
