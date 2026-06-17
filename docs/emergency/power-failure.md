# 전원 차단 / 강제 종료 / OOM / 커널 패닉 대응

## 1. 강제 종료(전원 차단) 여부 확인

### 마지막 정상 로그 시점 확인
```bash
journalctl --no-pager -n 50
```

또는 이전 부팅 직전 로그 확인:

```bash
journalctl -b -1 -e
```

맨 마지막 로그 시간은 전원 차단 시점에 가장 가까운 시간입니다.

### 재부팅 히스토리 확인
```bash
last -x | head -10
```

#### 해석

- `shutdown` 기록 있음 → 정상 종료
- `shutdown` 기록 없음 → 강제 종료 가능성 높음

---

## 2. 전원 차단 / 비정상 종료 시그널

```bash
journalctl -b -1 | grep -i "unexpected"
journalctl -b -1 | grep -i "crash"
journalctl -b | grep -i "recover"
```

다음 문구가 보이면 강제 종료 가능성 높습니다:

- `recovering journal`
- `EXT4-fs (sda1): recovery complete`
- `unclean shutdown detected`

---

## 3. 시스템이 종료한 경우 확인

### 자동 업데이트 재부팅
```bash
journalctl | grep -i unattended
cat /var/log/unattended-upgrades/unattended-upgrades.log
```

### OOM(메모리 부족)
```bash
journalctl -b -1 | grep -i oom
journalctl | grep -i "Out of memory"
```

로그 예시:

```
Out of memory: Kill process 1234 (docker)
```

### 커널 패닉
```bash
journalctl -b -1 | grep -i panic
dmesg | grep -i panic
```

### systemd 재부팅
```bash
journalctl -b -1 | grep -i reboot
journalctl | grep "systemd-logind"
```

---

## 4. 빠른 판별법 요약

| 상황 | shutdown 로그 | recover 로그 | 해석 |
| --- | --- | --- | --- |
| 정상 종료 | 있음 | 없음 | 정상 종료 |
| 전원 차단 | 없음 | 있음 | 강제 종료 |
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

이 세 가지를 함께 보면 실 서버가 멈춘 시점을 거의 100%로 추정할 수 있습니다.

---

## 6. Docker / GPU 서버 추가 점검

Docker 서버가 갑자기 꺼졌다면 추가로 확인:

```bash
journalctl -b -1 | grep -i docker
journalctl -b -1 | grep -i segfault
journalctl -b -1 | grep -i nv
```

GPU 서버(A100, 1080ti 등)라면:

```bash
journalctl -b -1 | grep -i nvidia
dmesg | grep -i nv
dmesg | grep -i xid
nvidia-smi -q -d POWER
```

### 실무 팁

- `nvidia-smi`로 GPU가 제대로 올라왔는지 확인
- `dmesg`에서 `xid` 오류가 있는지 확인
- 전원 차단/강제 종료의 경우 OS 로그가 마지막이므로 하드웨어 모니터링 로그와 함께 분석
