# Docker 컨테이너 재시작 / 종료 원인 분석

## 1. 컨테이너 재시작 시간 확인

```bash
docker inspect --format '{{.State.FinishedAt}}' 컨테이너명
```

또는 컨테이너 상태 전체 확인:

```bash
docker inspect 컨테이너명 | grep FinishedAt
```

## 2. 종료 원인 추적 로그

### 컨테이너 로그 확인
```bash
docker logs --since "2026-01-01T00:00:00" 컨테이너명
```

### Docker 데몬 로그 확인
```bash
journalctl -u docker.service --since "1 hour ago"
journalctl -b -1 | grep -i docker
```

### Docker 이벤트 확인
```bash
docker events --since "1h" --filter container=컨테이너명
```

---

## 3. 재시작 정책 및 이유 확인

### 자동 재시작 정책 확인
```bash
docker inspect --format '{{.HostConfig.RestartPolicy.Name}}' 컨테이너명
```

- `always` / `unless-stopped` → 컨테이너가 죽으면 자동 재시작
- `on-failure` → 실패 시 재시작
- `no` → 자동 재시작 안 함

### 종료 코드 확인
```bash
docker inspect --format '{{.State.ExitCode}}' 컨테이너명
```

- `0` → 정상 종료
- `1`, `137`, `143` 등 → 프로세스 종료/시그널에 의한 비정상 종료

---

## 4. 추가 점검 항목

- 컨테이너 내부 OOM(메모리 부족)인지 `docker logs`에서 확인
- 호스트 시스템 OOM인지 `journalctl | grep -i oom`으로 확인
- GPU 서버면 `journalctl -b -1 | grep -i nvidia` 또는 `dmesg | grep -i xid`
- `docker ps -a`로 상태, 재시작 횟수, 종료 시각 파악

## 5. 추천 조사 순서

1. `docker inspect`로 종료 시간과 정책 파악
2. `docker logs`로 컨테이너 내부 에러 확인
3. `journalctl`에서 Docker/호스트 재부팅 로그 확인
4. `docker events`로 실제 재시작 이벤트 확인
