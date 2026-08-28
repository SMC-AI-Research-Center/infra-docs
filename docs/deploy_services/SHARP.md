# 폐쇄망 서비스 배포 절차

## 핵심 배포 순서

```text
① 인터넷 PC
   └─ Frontend + Backend 준비
        ↓
② USB
        ↓
③ 내부망 PC → 119.86.100.151
        ↓
④ Backend .env 백업
        ↓
⑤ 기존 Uvicorn 종료
        ↓
⑥ Backend 교체 + .env 복구
        ↓
⑦ Frontend → /var/www/web 교체
        ↓
⑧ Uvicorn 재실행
        ↓
⑨ 서비스 확인
```

---

## 1. 인터넷 PC에서 배포 파일 준비

### Frontend

김강현 선생님이 버전 업한 **Flutter 포팅 Frontend**를 다운로드한다.

### Backend

GitHub에서 Backend를 다운로드하고 **반드시 `master` 브랜치**로 변경한다.

```bash
git clone <BACKEND_GITHUB_REPOSITORY>
cd <BACKEND_DIRECTORY>

git checkout master
git pull origin master
```

Frontend와 Backend를 각각 압축하여 USB에 복사한다.

```text
frontend.zip
backend.zip
```

---

## 2. USB → 내부망 서버

USB를 통해 내부망 PC로 이동한 후 `119.86.100.151` 서버로 파일을 업로드한다.

```bash
scp frontend.zip <USER>@119.86.100.151:~/
scp backend.zip <USER>@119.86.100.151:~/
```

---

## 3. Backend 배포

### ① 기존 `.env` 백업

**PostgreSQL 비밀번호 등 운영 설정이 있으므로 반드시 먼저 백업한다.**

```bash
cp ~/backend/.env ~/.env.backup
```

### ② 기존 Uvicorn 종료

```bash
ps -ef | grep uvicorn
kill <PID>
```

필요하면:

```bash
kill -9 <PID>
```

### ③ 기존 Backend 교체

기존 버전을 백업한다.

```bash
mv ~/backend ~/backend_old
```

새 Backend 압축 해제:

```bash
unzip ~/backend.zip -d ~/
```

### ④ `.env` 복구

```bash
cp ~/.env.backup ~/backend/.env
```

---

## 4. Frontend 교체

기존 Frontend를 백업한다.

```bash
sudo mv /var/www/web /var/www/web_old
```

새 Frontend를 `/var/www/web`에 배치한다.

```bash
sudo unzip ~/frontend.zip -d /var/www/
```

최종 구조:

```text
/var/www/web
```

---

## 5. Backend 재실행

```bash
cd ~/backend

nohup uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

※ 기존에 사용하던 `uvicorn` 실행 옵션이 있다면 **기존 명령어를 그대로 사용한다.**

실행 확인:

```bash
ps -ef | grep uvicorn
ss -lntp | grep 8000
```

로그 확인:

```bash
tail -f ~/backend/backend.log
```

---

## 6. 최종 확인

* [ ] Frontend 접속 확인
* [ ] 로그인 확인
* [ ] Backend API 정상 동작 확인
* [ ] PostgreSQL 연결 확인
* [ ] 주요 기능 확인

문제 발생 시:

```text
/var/www/web_old  → 기존 Frontend
~/backend_old     → 기존 Backend
~/.env.backup     → 기존 환경설정
```

을 이용해 롤백한다.

---

## ⚠️ 배포 시 반드시 기억할 것

1. **Backend는 `master` 브랜치**
2. **`.env`는 배포 전에 반드시 백업**
3. **Backend 교체 전에 Uvicorn 종료**
4. **Frontend → `/var/www/web`**
5. **Backend → `~/backend`**
6. **배포 후 Uvicorn 실행 및 서비스 확인**
