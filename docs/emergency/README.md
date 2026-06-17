# Emergency Response Manuals

이 폴더는 서버 장애 및 비상 상황 대응을 위한 실무 매뉴얼을 정리합니다.

## 포함된 문서

- `reboot-investigation.md` - 서버 재부팅 / 강제 종료 원인 분석
- `unattended-upgrades.md` - unattended-upgrades / 자동 업데이트 재부팅 대응
- `docker-restart.md` - Docker 컨테이너 재시작 및 종료 원인 분석
- `power-failure.md` - 전원 차단 / 강제 종료 / OOM / 커널 패닉 판단

## 사용 방법

1. 처음에는 `reboot-investigation.md`를 보고 서버가 언제 재부팅되었는지 파악합니다.
2. 자동 업데이트 가능성은 `unattended-upgrades.md`를 확인합니다.
3. Docker 관련 서버면 `docker-restart.md`를 추가로 확인합니다.
4. 강제 종료, OOM, 커널 패닉 여부는 `power-failure.md`를 참고합니다.
