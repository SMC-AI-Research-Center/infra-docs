# lsyncd 기반 서버 간 자동 동기화 구축 가이드

## 목적

소스 서버의 특정 디렉토리를
목적 서버 `super@172.30.1.118:/data/server_XXX/{dir_name}` 로
자동 동기화한다.

* 동기화 방식: `lsyncd + rsync + ssh`
* 동기화 형태: 단방향 (Source → Target)
* 삭제 반영: O (`--delete`)
* [링크](https://lsyncd.github.io/lsyncd/manual/config/file/)

---

## 구성 구조

```bash
[Source Server]
    /data/{dir_name}
           │
           │  lsyncd
           ▼
    rsync + ssh
           ▼
[Target Server]
    /data/server_XXX/{dir_name}
```

예시:

```bash
소스(62 서버):   /home/ubuntu/Downloads/doctor-dairy-COPD-API/data
목적(118서버):   super@172.30.1.118:/data/server_62/doctor-dairy-COPD-API/data
```

---

## 1️⃣ 소스 서버 설정

### 1. 패키지 설치

```bash
sudo apt update
sudo apt install -y lsyncd rsync
sudo mkdir -p /var/log/lsyncd
```

---

### 2. SSH 무비밀번호 접속 설정

#### ① 키 생성

```bash
sudo ssh-keygen -t ed25519
```

#### ② 목적 서버로 키 복사

```bash
sudo ssh-copy-id super@172.30.1.118
```

#### ③ 접속 확인

```bash
sudo ssh super@172.30.1.118
```

비밀번호 없이 접속되면 정상

---

## 2️⃣ 목적 서버 설정 (172.30.1.118)

### 1. 대상 디렉토리 생성

예: server_62, dir_name=model

```bash
sudo mkdir -p /data/server_62/doctor-dairy-COPD-API/data
sudo chown -R super:super /data/server_62
```

---

## 3️⃣ lsyncd 설정 파일 작성 (소스 서버)

```bash
sudo vim /etc/lsyncd/lsyncd.conf.lua
```

---

### ✅ 설정 예시 (server_62 / model)

```lua
settings {
    logfile        = "/var/log/lsyncd/lsyncd.log",
    pidfile        = "/var/run/lsyncd.pid",
    nodaemon       = false,

    statusFile     = "/var/log/lsyncd/lsyncd.status",
    statusInterval = 30,

    logfacility    = "user",
    logident       = "lsyncd",

    insist         = true,

    inotifyMode    = "CloseWrite or Modify",

    maxProcesses   = 1,
}

sync {
    default.rsyncssh,
    source = "/home/ubuntu/Downloads/doctor-dairy-COPD-API/data",
    host   = "super@172.30.1.118",
    targetdir = "/data/server_62/doctor-dairy-COPD-API/data",

    delay = 3600,   -- 변경 후 1시간 뒤 동기화

    rsync = {
        archive  = true,
        compress = true,
        verbose  = true,
        _extra   = {"--delete"}
    }
}
```

---

## 🔎 변수 설명

| 항목           | 설명                 |
| ------------ | ------------------ |
| source       | 소스 서버 디렉토리         |
| target       | 목적 서버 디렉토리         |
| delay        | 변경 감지 후 실행 대기 시간   |
| maxProcesses | 동시 실행 rsync 수      |
| --delete     | 소스에서 삭제 시 목적에서도 삭제 |
| exclude      | 제외 파일/디렉토리         |

---

## 4️⃣ 서비스 실행

```bash
sudo systemctl enable lsyncd
sudo systemctl restart lsyncd
```

---

## 5️⃣ 서비스 상태 확인(필수)

```bash
sudo systemctl status lsyncd
sudo tail -f /var/log/lsyncd/lsyncd.log
```

```bash
# 파일 생성 해보기
touch /home/ubuntu/Downloads/doctor-dairy-COPD-API/data/test_test_test_test_test
```

---

## 여러 서버 / 여러 dir_name 설정 방법

각각 별도 sync 블록 추가 가능:

```lua
sync {
    default.rsyncssh,
    source = "/home/ubuntu/Downloads/doctor-dairy-COPD-API/data",
    host   = "super@172.30.1.118",
    target = "/data/server_62/doctor-dairy-COPD-API/data",
}
```

---

## ⚠ 운영 시 주의사항

1. lsyncd는 단방향
2. DB 파일 실시간 복제 용도로는 부적합
3. 초기 동기화 시 시간 오래 걸림
4. 대용량은 `delay` 값 조절 필요

---

## 📂 예시 최종 구조

소스 서버(예 172.30.1.62):

```bash
/home
 └── ubuntu
   └── Downloads
      └── doctor-dairy-COPD-API
          └── data
            ├── model
            ├── dataset
            └── logs
```

목적 백업 서버(172.30.1.118):

```bash
/data
 └── server_62
   └── doctor-dairy-COPD-API
      └── data
        ├── model
        ├── dataset
        └── logs
```

---

## 미래 권장 운영 구조 (GPU/AI 서버 환경)

* 모델 파일 → lsyncd
* 로그 → lsyncd
* DB → 별도 replication
* 장기 확장 → Ceph 고려
