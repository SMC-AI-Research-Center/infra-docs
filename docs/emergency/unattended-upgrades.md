# unattended-upgrades / 자동 업데이트 대응

## 1. unattended-upgrades 부팅 여부 확인

### ① 실제 실행 로그 확인
```bash
journalctl | grep -i unattended
```

### ② 서비스 활성화 여부 확인
```bash
systemctl status unattended-upgrades
```

`active (running)` 이면 동작 중입니다.

### ③ 자동 재부팅 설정 확인
```bash
cat /etc/apt/apt.conf.d/50unattended-upgrades | grep Automatic-Reboot
```

- `Unattended-Upgrade::Automatic-Reboot "true"` → 자동 재부팅 가능
- `Unattended-Upgrade::Automatic-Reboot "false"` → 자동 재부팅 안 함

---

## 2. 자동 업데이트 종료 / 비활성화

```bash
sudo systemctl stop unattended-upgrades
sudo systemctl disable unattended-upgrades
sudo systemctl stop apt-daily.timer
sudo systemctl stop apt-daily-upgrade.timer
sudo systemctl disable apt-daily.timer
sudo systemctl disable apt-daily-upgrade.timer
```

필요 시 더 강력하게 차단하려면:

```bash
sudo systemctl mask unattended-upgrades
```

---

## 3. 구성 확인 및 재설정

### 구성 파일 위치
- `/etc/apt/apt.conf.d/50unattended-upgrades`
- `/etc/apt/apt.conf.d/20auto-upgrades`

### 재구성 명령
```bash
dpkg-reconfigure unattended-upgrades
```

### 자동 업데이트 패턴 확인 예시
```bash
grep -E "^\s*Unattended-Upgrade::Automatic-Reboot|^\s*APT::Periodic" /etc/apt/apt.conf.d/*
```

---

## 4. 점검 포인트

- 자동 재부팅이 허용되어 있으면 재부팅 전 로그를 반드시 확인
- `apt-daily` 타이머가 남아 있으면 수동으로 멈춘 후 재부팅
- 긴급 상황에서는 `mask`로 완전히 비활성화
- 재부팅 사유가 자동 업데이트인지 확인하려면 `unattended-upgrades.log`와 `journalctl` 로그를 함께 보세요
