# APT Mirror 다운로드

## 1. 준비 단계: 저장소 확보 및 도구 설치

### SSD 연결

* **도구 설치:**

  ```bash
  sudo apt update
  sudo apt install apt-mirror -y
  ```

---

## 2. 핵심 설정: `/etc/apt/mirror.list` 작성

```bash
############# 설정 섹션 #############
set base_path    /data/mirror
set mirror_path  $base_path/mirror
set skel_path    $base_path/skel
set var_path     $base_path/var
set postmirror_script $var_path/postmirror.sh
set nthreads     20
set _tilde 0
set defaultarch  amd64

############# 미러링 대상 저장소 #############

# 1. Ubuntu 공식 (Main, Updates, Security)
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-security main restricted universe multiverse

# 2. KAIST 미러 (선택 사항 - 위와 데이터가 겹치면 하나만 유지해도 됨)
deb http://ftp.kaist.ac.kr/ubuntu jammy main restricted universe multiverse
deb http://ftp.kaist.ac.kr/ubuntu jammy-updates main restricted universe multiverse

# 3. Docker 공식
deb [arch=amd64] https://download.docker.com/linux/ubuntu jammy stable

# 4. PPA (예: Graphics Drivers)
deb http://ppa.launchpad.net/graphics-drivers/ppa/ubuntu jammy main

############# 청소 설정 (불필요한 구버전 삭제) #############
clean http://archive.ubuntu.com/ubuntu
clean http://ftp.kaist.ac.kr/ubuntu
clean https://download.docker.com/linux/ubuntu
```

---

## 3. 디렉토리 생성 및 권한 부여

`apt-mirror`가 파일을 쓸 수 있도록 구조를 만들고 권한을 넘겨줍니다.

```bash
# 디렉토리 생성
sudo mkdir -p /data/mirror/{mirror,skel,var}

# 권한 설정 (Nginx와 apt-mirror가 접근 가능하도록)
sudo chown -R www-data:www-data /data/mirror
sudo chmod -R 755 /data/mirror
```

---

## 4. 다운로드 실행 (최초 동기화)

최초 실행 시에는 용량이 매우 크기 때문에(Ubuntu Jammy 기준 약 2TB) 백그라운드에서 실행하는 것을 권장합니다.

```bash
# 백그라운드 실행 (로그 확인 가능)
sudo nohup apt-mirror > /data/mirror/var/mirror.log 2>&1 &

# 진행 상황 모니터링
tail -f /data/mirror/var/mirror.log
```

---

## 5. 사후 관리 (Maintenance)

### 5.1 불필요한 파일 삭제 (Clean)

동기화가 끝나면 `/data/mirror/var/clean.sh`라는 스크립트가 자동 생성됩니다. 이를 실행해야 구버전 패키지가 삭제되어 디스크 용량을 아낄 수 있습니다.

```bash
sudo sh /data/mirror/var/clean.sh
```

### 5.2 자동 업데이트 설정 (Cron)

매일 새벽 3시에 새로운 보안 패치를 받아오도록 설정합니다.

```bash
# /etc/cron.d/apt-mirror 파일 수정
sudo nano /etc/cron.d/apt-mirror

# 아래 줄의 주석(#)을 제거
0 3 * * * apt-mirror /usr/bin/apt-mirror > /data/mirror/var/cron.log
```

---

## ⚠️ 다운로드 가이드 핵심 팁

1. **용량 부족 주의:** `/data` 마운트 지점의 남은 용량을 수시로 확인하세요. (`df -h`)
2. **CNF 파일 수동 생성:** `apt-mirror`는 `cnf` 관련 메타데이터를 안 가져오는 경우가 많습니다. 클라이언트에서 `99disable-cnf` 설정을 하는 것이 정신 건강에 이롭습니다.
3. **InRelease 에러:** 동기화 도중 중단되면 `InRelease` 파일이 깨질 수 있습니다. 이럴 땐 해당 폴더의 파일만 지우고 다시 돌리세요.

**이제 151번 서버에서 `apt-mirror`를 돌려볼까요?** 혹시 특정 패키지가 계속 안 받아진다면 `mirror.list`에 적힌 아키텍처(`amd64`)나 배포판 이름(`jammy`)을 다시 한번 확인해 드릴 수 있습니다.