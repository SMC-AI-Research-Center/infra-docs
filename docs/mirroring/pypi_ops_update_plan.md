# PyPI 미러 운영 업데이트 기획서 (폐쇄망)

## 1. 목적

- 다운로드 서버(172.30.1.118)에서 PyPI 미러를 최신 상태로 유지한다.
- 폐쇄망 서비스 서버(119.86.100.149)에 안정적으로 배포하여 내부 사용자 pip 설치 실패를 최소화한다.
- 정기/긴급 업데이트 기준과 운영 절차(SOP)를 표준화한다.

---

## 2. 운영 구조

- 1차 미러링 서버: 172.30.1.118
  - bandersnatch 실행
  - 원본(PyPI)과 동기화
  - 배포 원본 디렉토리 보관
- 2차 서비스 서버(폐쇄망): 119.86.100.149
  - 172.30.1.118에서 동기화된 데이터 수신
  - Nginx로 내부 클라이언트 서비스
- 내부 클라이언트
  - `pip.conf`에서 `index-url = http://pypi.smc.com/simple` 사용

권장 데이터 경로:
- 172.30.1.118: `/data/pypi/web`
- 119.86.100.149: `/data/pypi/web`

---

## 3. 업데이트 정책

### 3.1 권장 주기

- 정기 미러링(172.30.1.118): 하루 2회
  - 02:30, 14:30
- 정기 배포(118 -> 149): 하루 2회
  - 03:30, 15:30 (미러링 완료 후 1시간 뒤)
- 운영 검증(149): 하루 2회
  - 04:00, 16:00
- 전체 점검(용량/성능/오류): 매주 1회 (일요일 05:00)

### 3.2 긴급 업데이트

- 보안 취약점(Critical/High) 또는 필수 패키지 배포 이슈 발생 시:
  - 요청 후 2시간 내 임시 미러링 1회
  - 즉시 149로 배포
  - 대표 서버 1대에서 pip 설치 검증 후 공지

---

## 4. 표준 운영 절차 (SOP)

### 4.1 172.30.1.118 미러링 단계

```bash
# 사전 점검
python3 --version
bandersnatch --version
df -h /data

# 미러링 실행
bandersnatch mirror

# 로그 확인(운영 환경에 맞게 로그 경로 지정 권장)
# 예: /var/log/bandersnatch/mirror.log
```

### 4.2 172.30.1.118 -> 119.86.100.149 배포 단계

배포는 분할 압축 후 SSD 오프라인 반입 방식으로 진행한다.

```bash
# 172.30.1.118에서 실행
# 1) 배포본 생성 (tar)
sudo tar -C /data/pypi -cpf /data/pypi_release/pypi_web_$(date +%F).tar web

# 2) 분할 압축 (예: 50G 단위)
sudo mkdir -p /data/pypi_release/split
sudo zstd -T0 -19 /data/pypi_release/pypi_web_$(date +%F).tar -o /data/pypi_release/pypi_web_$(date +%F).tar.zst
split -b 50G -d -a 3 /data/pypi_release/pypi_web_$(date +%F).tar.zst /data/pypi_release/split/pypi_web_$(date +%F).tar.zst.part-

# 3) 체크섬 생성
cd /data/pypi_release/split
sha256sum pypi_web_$(date +%F).tar.zst.part-* > SHA256SUMS

# 4) SSD로 복사 (SSD 마운트 경로는 환경에 맞게 변경)
sudo rsync -avh --progress /data/pypi_release/split/ /mnt/ssd/pypi_release/
```

옵션 설명:
- `split -b 50G`: 파일을 50GB 단위로 분할
- `sha256sum`: 반입 전/후 파일 무결성 검증
- `zstd -19`: 압축률 우선(속도보다 용량 절감 중점)

### 4.3 119.86.100.149 서비스 반영 단계

```bash
# 1) SSD에서 배포 파일 복사
sudo mkdir -p /data/pypi_release/incoming
sudo rsync -avh /mnt/ssd/pypi_release/ /data/pypi_release/incoming/

# 2) 체크섬 검증
cd /data/pypi_release/incoming
sha256sum -c SHA256SUMS

# 3) 분할 파일 병합 및 복원
cat pypi_web_*.tar.zst.part-* > pypi_web_restore.tar.zst
sudo zstd -d -T0 pypi_web_restore.tar.zst -o pypi_web_restore.tar

# 4) 서비스 데이터 교체
sudo mkdir -p /data/pypi/web_new
sudo tar -C /data/pypi -xpf pypi_web_restore.tar

# Nginx 설정 검증
sudo nginx -t

# Nginx reload
sudo systemctl reload nginx

# 서비스 확인
curl -I http://pypi.smc.com/simple/
```

### 4.4 클라이언트 검증 단계

대표 클라이언트 1~2대에서 검증:

```bash
pip install --index-url http://pypi.smc.com/simple --trusted-host pypi.smc.com numpy==1.26.4
pip install --index-url http://pypi.smc.com/simple --trusted-host pypi.smc.com pandas==2.2.2
```

---

## 5. 자동화 구성안

### 5.1 172.30.1.118 크론 예시

`/etc/cron.d/pypi-mirror`

```cron
# 하루 2회 미러링
30 2,14 * * * root /usr/bin/bandersnatch mirror >> /var/log/bandersnatch/mirror.log 2>&1

# 미러링 완료 후 1시간 뒤 SSD 반입용 배포본 생성
30 3,15 * * * root /bin/bash -lc 'mkdir -p /data/pypi_release /data/pypi_release/split && tar -C /data/pypi -cpf /data/pypi_release/pypi_web_$(date +\%F).tar web && zstd -T0 -19 /data/pypi_release/pypi_web_$(date +\%F).tar -o /data/pypi_release/pypi_web_$(date +\%F).tar.zst && split -b 50G -d -a 3 /data/pypi_release/pypi_web_$(date +\%F).tar.zst /data/pypi_release/split/pypi_web_$(date +\%F).tar.zst.part- && cd /data/pypi_release/split && sha256sum pypi_web_$(date +\%F).tar.zst.part-* > SHA256SUMS' >> /var/log/bandersnatch/release.log 2>&1
```

### 5.2 로그 로테이션 권장

- `/var/log/bandersnatch/mirror.log`
- `/var/log/bandersnatch/release.log`

월 1회 또는 주 1회 `logrotate` 적용 권장.

---

## 6. 모니터링 및 알림 기준

### 6.1 알림 조건

- `/data` 사용률 80% 이상: 경고
- `/data` 사용률 90% 이상: 긴급
- 미러링 실패(종료코드 != 0): 즉시 알림
- 분할 압축/체크섬 생성 실패(종료코드 != 0): 즉시 알림
- 149 Nginx `5xx` 급증: 경고

### 6.2 필수 점검 지표

- 미러링 소요 시간
- 배포본 크기(압축 전/후)
- 최근 24시간 설치 실패 건수(가능 시)

---

## 7. 장애 대응

### 7.1 미러링 실패 (172.30.1.118)

1. `bandersnatch.conf` 문법/경로 확인
2. 디스크 여유 확인
3. 네트워크 연결 확인 후 재실행
4. 반복 실패 시 직전 정상 데이터 유지 + 운영 공지

### 7.2 배포 실패 (118 -> 149)

1. SSD 파일 체크섬 검증 결과 확인
2. 손상 파일만 재복사 후 재검증
3. 실패 지속 시 149 기존 데이터로 서비스 유지
4. 원인 해소 후 수동 배포

### 7.3 서비스 오류 (149)

1. `sudo nginx -t` 점검
2. `sudo journalctl -u nginx -n 200` 확인
3. 필요 시 직전 백업으로 롤백

---

## 8. 변경 관리

- `bandersnatch.conf` 변경 시 사전 영향 검토
  - 용량 증가량
  - 제외/허용 플랫폼 변경 영향
- 변경 후 필수 검증
  - `pip index` 접근
  - 대표 패키지 설치
- 변경 이력은 월간 운영 기록으로 관리

---

## 9. 권장 운영 일정표

- 매일 02:30: 172.30.1.118 미러링
- 매일 03:30: 119.86.100.149로 배포
- 매일 04:00: 대표 클라이언트 설치 검증
- 매일 14:30/15:30/16:00: 동일 절차 1회 추가
- 매주 일요일 05:00: 용량/성능/오류 종합 점검

---

## 10. 초기 도입 체크리스트

- [ ] 172.30.1.118에서 bandersnatch 수동 동작 확인
- [ ] 118에서 분할 압축/체크섬 생성 확인
- [ ] SSD 반입 후 149에서 체크섬 검증 및 복원 확인
- [ ] 119.86.100.149 Nginx 설정/서비스 상태 정상
- [ ] 내부 클라이언트 pip.conf/hosts 반영 확인
- [ ] 대표 패키지 설치 테스트 성공
- [ ] 크론 등록 및 로그/알림 연동 완료
