# 서버 재부팅 / 강제 종료 조사

## 1. 서버 재부팅 시간 확인

### 최근 재부팅 로그 확인
```bash
journalctl --list-boots
```

이후 아래 명령으로 최근 부팅, 종료 시점을 비교합니다.

### 현재 부팅 시간 확인
```bash
who -b
```

### 마지막 로그 확인
```bash
journalctl -b -1 -e
```

맨 마지막 로그 시간이 실제 서버가 멈춘 시점에 가장 가깝습니다.

---

## 2. 재부팅 원인 분석

### `journalctl`에서 재부팅 관련 로그 확인
```bash
journalctl | grep -i reboot
journalctl -b -1 | grep -i reboot
```

### 마지막 50줄 로그 확인
```bash
journalctl --no-pager -n 50
```

### 시스템 재부팅 히스토리 확인
```bash
last -x | head -10
```

예시:

```
reboot   system boot  2026-02-22 03:14
shutdown system down  2026-02-21 18:05
```

#### 해석

- `shutdown` 기록 있음 → 정상 종료 가능성 높음
- `shutdown` 기록 없음 → 강제 종료(전원 차단) 가능성 높음

---

## 3. 재부팅 원인 후보별 확인 순서

### A. 자동 재부팅
```bash
journalctl | grep -i unattended
cat /var/log/unattended-upgrades/unattended-upgrades.log
```

자동 재부팅이면 다음과 같은 메시지가 보입니다:

```
Automatic reboot scheduled
Rebooting system
```

### B. OOM (메모리 부족)
```bash
journalctl -b -1 | grep -i oom
journalctl | grep -i "Out of memory"
```

### C. 커널 패닉
```bash
journalctl -b -1 | grep -i panic
dmesg | grep -i panic
```

### D. systemd 재부팅
```bash
journalctl -b -1 | grep -i reboot
journalctl | grep "systemd-logind"
```

---

## 4. 빠른 판별법

| 상황 | shutdown 로그 | recover 로그 | 해석 |
| --- | --- | --- | --- |
| 정상 종료 | 있음 | 없음 | 정상 종료 |
| 전원 차단 | 없음 | 있음 | 강제 종료 가능성 높음 |
| OOM | 없음 | OOM 기록 | 메모리 문제 |
| unattended | 있음 | 자동 reboot 기록 | 자동 업데이트 |

---

## 5. 가장 정확한 시간 추적 방법

```bash
who -b
last -x | head -5
journalctl -b -1 -e
```

### 분석 방식

1. `who -b` → 현재 부팅 시간
2. `last -x` → shutdown 기록 유무
3. `journalctl -b -1 -e` → 이전 부팅 마지막 로그 시간

이 세 가지를 같이 보면 재부팅 또는 강제 정지 시점을 거의 정확하게 파악할 수 있습니다.
