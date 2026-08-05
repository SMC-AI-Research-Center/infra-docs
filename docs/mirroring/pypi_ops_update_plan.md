# PyPI 미러 증분 업데이트 운영 기획서 (폐쇄망)

## 1. 목적

* 다운로드 서버 `172.30.1.118`에서 PyPI 미러를 최신 상태로 유지한다.
* 전체 PyPI 미러를 매번 복사하지 않고, Bandersnatch 동기화 과정에서 신규 생성되거나 변경된 파일만 차분 배포본으로 생성한다.
* 차분 배포본을 USB 또는 외장 SSD로 폐쇄망 서비스 서버 `119.86.100.149`에 반입한다.
* 폐쇄망 서비스 서버의 기존 미러에 차분 파일만 병합한다.

---

## 2. 운영 구조

### 2.1 1차 미러링 서버: `172.30.1.118`

* Bandersnatch로 PyPI를 동기화한다.
* 신규·변경 파일 목록을 생성한다.
* 신규·변경 파일만 압축하여 USB에 복사한다.

### 2.2 2차 서비스 서버: `119.86.100.149`

* USB로 차분 배포본을 반입한다.
* 기존 PyPI 미러에 신규·변경 파일만 병합한다.
* Nginx를 통해 내부 클라이언트에 PyPI 서비스를 제공한다.

### 2.3 내부 클라이언트 설정

`pip.conf`:

```ini
[global]
index-url = http://pypi.smc.com/simple
trusted-host = pypi.smc.com
```

### 2.4 사용 경로

#### 172.30.1.118

```text
/data/pypi/          전체 PyPI 미러
/data/pypi/web/      실제 서비스 데이터
/data/pypi_diff/     Bandersnatch 변경 파일 목록
/data/pypi_delta/    차분 압축본 생성 경로
```

#### 119.86.100.149

```text
/data/pypi/web/      현재 서비스 중인 PyPI 미러
/data/pypi_delta/    USB 반입 및 압축 해제 경로
```

---

## 3. 증분 배포 방식

전체 `/data/pypi/web` 디렉터리를 매번 복사하지 않는다.

Bandersnatch의 `diff-file` 기능을 사용하여 각 동기화에서 신규 생성되거나 변경된 파일의 경로를 기록한다.

주요 변경 대상은 다음과 같다.

* 새로 다운로드된 wheel 및 sdist 파일
* 변경된 프로젝트별 Simple Index
* 변경된 루트 Simple Index
* 새로 생성되거나 변경된 JSON·HTML 메타데이터

`diff-append-epoch = true`를 사용하면 Bandersnatch 실행마다 별도의 변경 파일 목록이 생성된다.

### 배포 흐름

```text
PyPI 동기화
  ↓
신규·변경 파일 목록 생성
  ↓
오늘 생성된 변경 목록 병합
  ↓
변경 파일만 별도 디렉터리에 복사
  ↓
tar.zst 압축 및 SHA-256 생성
  ↓
USB 또는 외장 SSD 반입
  ↓
폐쇄망 기존 미러에 병합
```

### 삭제 파일 처리

`diff-file`은 신규·변경 파일을 기록하며 삭제 파일을 별도로 전달하지 않는다.

따라서 일상적인 증분 업데이트에서는 신규·변경 파일만 반영하고, 오래되어 사용되지 않는 파일은 분기 또는 반기 점검 시 별도로 정리한다.

---

## 4. 초기 설정

### 4.1 Bandersnatch 설정

`/etc/bandersnatch.conf`:

```ini
[mirror]
directory = /data/pypi
json = false
release-files = true
cleanup = false
master = https://pypi.org
timeout = 200
global-timeout = 3600
workers = 10
hash-index = false
simple-format = ALL
stop-on-error = false
storage-backend = filesystem
verifiers = 3
compare-method = hash

# 신규·변경 파일 목록 저장
diff-file = /data/pypi_diff/mirrored-files

# 실행마다 별도의 목록 파일 생성
diff-append-epoch = true

[plugins]
enabled =
    exclude_platform
    latest_release
    blacklist_project

[blocklist]
platforms =
    etc
    py2
    py3.1
    py3.2
    py3.3
    py3.4
    py3.5
    py3.6
    py3.7
    py3.8

[latest_release]
keep = 20
```

변경 파일 목록은 다음과 같이 생성된다.

```text
/data/pypi_diff/mirrored-files-1785461400
/data/pypi_diff/mirrored-files-1785504600
```

각 파일에는 다음과 같은 절대경로가 기록된다.

```text
/data/pypi/web/packages/ab/cd/example.whl
/data/pypi/web/simple/setuptools/index.html
/data/pypi/web/simple/setuptools/index.v1_json
```

### 4.2 디렉터리 생성

Bandersnatch를 `super` 계정으로 실행하는 경우:

```bash
sudo mkdir -p \
  /data/pypi_diff \
  /data/pypi_delta

sudo chown -R super:super \
  /data/pypi_diff \
  /data/pypi_delta

sudo chmod 755 \
  /data/pypi_diff \
  /data/pypi_delta
```

실제 Bandersnatch 실행 계정이 다르면 `super:super`를 해당 계정과 그룹으로 변경한다.

---

## 5. 업데이트 정책

### 5.1 정기 업데이트

* 분기 1회 정기 미러링 및 폐쇄망 반입
* 필요하면 운영 일정에 따라 추가 수행

### 5.2 긴급 업데이트

다음 상황에서는 정기 일정과 관계없이 즉시 증분 업데이트한다.

* 보안 취약점이 발견된 경우
* 필수 패키지의 신규 버전이 필요한 경우
* 내부 클라이언트에서 패키지 설치 오류가 발생한 경우

---

## 6. 172.30.1.118 작업

### 6.1 PyPI 미러링

```bash
sudo bandersnatch mirror
```

미러링이 완료되면 `/data/pypi_diff/`에 `mirrored-files-<epoch>` 형식의 변경 목록이 생성된다.

생성 여부를 확인한다.

```bash
ls -lh /data/pypi_diff/mirrored-files-*
```

---

### 6.2 오늘 변경된 파일 압축

아래 명령 전체를 한 번에 실행한다.

```bash
set -e

TODAY=$(date +%F)
TOMORROW=$(date -d "$TODAY +1 day" +%F)

DELTA_DIR="/data/pypi_delta"
UPDATE_DIR="${DELTA_DIR}/update"
LIST_FILE="${DELTA_DIR}/changed_files.txt"
ARCHIVE="${DELTA_DIR}/pypi_delta_${TODAY}.tar.zst"
CHECKSUM="${DELTA_DIR}/pypi_delta_${TODAY}.sha256"

# 이전 작업 파일 삭제
sudo rm -rf "$UPDATE_DIR"
sudo rm -f "$LIST_FILE" "$ARCHIVE" "$CHECKSUM"
sudo mkdir -p "$UPDATE_DIR"

# 오늘 생성된 모든 변경 목록을 합치고 중복 제거
sudo find /data/pypi_diff \
  -maxdepth 1 \
  -type f \
  -name 'mirrored-files-*' \
  -newermt "${TODAY} 00:00:00" \
  ! -newermt "${TOMORROW} 00:00:00" \
  -exec cat {} + \
  | grep '^/data/pypi/web/' \
  | sort -u \
  | sed 's#^/data/pypi/web/##' \
  | sudo tee "$LIST_FILE" > /dev/null

# 변경 파일이 없는 경우 중단
if [ ! -s "$LIST_FILE" ]; then
    echo "오늘 변경된 파일이 없습니다."
    exit 1
fi

# 변경된 파일만 원래 디렉터리 구조를 유지하여 복사
sudo rsync -a \
  --files-from="$LIST_FILE" \
  /data/pypi/web/ \
  "$UPDATE_DIR/"

# 변경 파일 목록도 압축본에 포함
sudo cp "$LIST_FILE" "$UPDATE_DIR/CHANGED_FILES.txt"

# 차분 파일 압축
sudo tar -C "$DELTA_DIR" \
  -I 'zstd -6 -T0' \
  -cf "$ARCHIVE" \
  update

# 체크섬 생성
cd "$DELTA_DIR"
sudo sha256sum "$(basename "$ARCHIVE")" \
  | sudo tee "$(basename "$CHECKSUM")" > /dev/null

# 결과 확인
sudo zstd -t "$ARCHIVE"
sudo sha256sum -c "$CHECKSUM"

echo
echo "변경 파일 수: $(wc -l < "$LIST_FILE")"
sudo du -sh "$UPDATE_DIR" "$ARCHIVE"
ls -lh "$ARCHIVE" "$CHECKSUM"
```

생성되는 파일은 다음 두 개이다.

```text
/data/pypi_delta/pypi_delta_YYYY-MM-DD.tar.zst
/data/pypi_delta/pypi_delta_YYYY-MM-DD.sha256
```

---

### 6.3 USB 또는 외장 SSD에 복사

USB 마운트 경로를 `/mnt/usb`로 가정한다.

```bash
TODAY=$(date +%F)

sudo mkdir -p "/mnt/usb/pypi_delta_${TODAY}"

sudo rsync -avh --progress \
  "/data/pypi_delta/pypi_delta_${TODAY}.tar.zst" \
  "/data/pypi_delta/pypi_delta_${TODAY}.sha256" \
  "/mnt/usb/pypi_delta_${TODAY}/"
```

USB에 복사된 파일의 체크섬을 확인한다.

```bash
TODAY=$(date +%F)

cd "/mnt/usb/pypi_delta_${TODAY}"
sha256sum -c "pypi_delta_${TODAY}.sha256"
```

복사가 완료되면 디스크 쓰기를 완료하고 마운트를 해제한다.

```bash
sync
sudo umount /mnt/usb
```

---

## 7. 119.86.100.149 서비스 반영

USB를 `/mnt/usb`에 마운트했다고 가정한다.

반입한 배포 날짜를 지정한다.

```bash
RELEASE_DATE=YYYY-MM-DD
```

예:

```bash
RELEASE_DATE=2026-07-31
```

### 7.1 차분 파일 복사 및 검증

```bash
set -e

RELEASE_DATE=YYYY-MM-DD
DELTA_DIR="/data/pypi_delta"

sudo rm -rf "$DELTA_DIR"
sudo mkdir -p "$DELTA_DIR"

sudo rsync -avh --progress \
  "/mnt/usb/pypi_delta_${RELEASE_DATE}/" \
  "$DELTA_DIR/"

cd "$DELTA_DIR"
sudo sha256sum -c "pypi_delta_${RELEASE_DATE}.sha256"
```

체크섬 검증에 실패하면 서비스에 반영하지 않는다.

---

### 7.2 압축 해제 및 기존 미러에 병합

```bash
set -e

RELEASE_DATE=YYYY-MM-DD
DELTA_DIR="/data/pypi_delta"

cd "$DELTA_DIR"

sudo tar \
  -I zstd \
  -xf "pypi_delta_${RELEASE_DATE}.tar.zst"

sudo rsync -av \
  --delay-updates \
  "${DELTA_DIR}/update/" \
  /data/pypi/web/
```

Nginx 설정 변경은 없으므로 일반적으로 reload할 필요는 없다.

서비스 접근 여부를 확인한다.

```bash
curl -fsSI http://pypi.smc.com/simple/
```

정상이라면 `HTTP/1.1 200 OK` 또는 `HTTP/2 200` 응답이 표시된다.

---

## 8. 클라이언트 검증

대표 클라이언트에서 추가된 패키지가 조회되고 다운로드되는지 확인한다.

### 8.1 setuptools 버전 조회

```bash
python3 -m pip index versions setuptools \
  --index-url http://pypi.smc.com/simple \
  --trusted-host pypi.smc.com
```

### 8.2 setuptools 다운로드 확인

```bash
rm -rf /tmp/pypi-test
mkdir -p /tmp/pypi-test

python3 -m pip download \
  --no-deps \
  --index-url http://pypi.smc.com/simple \
  --trusted-host pypi.smc.com \
  --dest /tmp/pypi-test \
  setuptools

ls -lh /tmp/pypi-test
```

추가된 최신 setuptools 파일이 정상적으로 다운로드되면 증분 업데이트가 완료된 것이다.

다른 패키지를 검증할 때는 명령의 `setuptools`를 해당 패키지명으로 변경한다.

검증 후 임시 파일을 삭제한다.

```bash
rm -rf /tmp/pypi-test
```
