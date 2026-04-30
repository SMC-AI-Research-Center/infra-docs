# NFS 서버 연결 설정 가이드

서버: `172.30.1.118`  
클라이언트: `172.30.1.112`

---

# 1. 서버 설정 (118)

## 1.1 NFS 서버 설치

```bash
sudo apt update
sudo apt install -y nfs-kernel-server
```

---

## 1.2 공유할 디렉토리 생성

```bash
sudo mkdir -p /data/mimic3
```

---

## 1.3 exports 설정

NFS로 공유할 디렉토리를 `/etc/exports`에 등록합니다.

```bash
sudo vim /etc/exports
```

아래 내용을 추가합니다.

```bash
# /data/mimic3 172.30.1.0/24(sync,wdelay,hide,no_subtree_check,sec=sys,rw,secure,no_root_squash,no_all_squash)
/data/mimic3 172.30.1.0/24(rw, sync, no_root_squash)
```

설정 적용

```bash
sudo exportfs -ra
```

설정 확인

```bash
sudo exportfs -v
```

---

## 1.4 UFW 설정

NFS와 RPC 관련 포트를 허용합니다.

```bash
sudo ufw allow from 172.30.1.0/24 to any port 111
sudo ufw allow from 172.30.1.0/24 to any port 2049
sudo ufw allow from 172.30.1.0/24 to any port 20048
```

확인

```bash
sudo ufw status
```

---

## 1.5 `/etc/nfs.conf` mountd 포트 고정

mountd 포트를 고정하면 방화벽 관리가 쉬워집니다.

```bash
sudo vim /etc/nfs.conf
```

아래 내용을 추가하거나 수정합니다.

```bash
[mountd]
port=20048
```

설정 적용

```bash
sudo systemctl restart nfs-kernel-server
```

---

# 2. 클라이언트 설정 (112)

## 2.1 NFS 클라이언트 설치

```bash
sudo apt update
sudo apt install -y nfs-common
```

---

## 2.2 서버 공유 확인

```bash
showmount -e 172.30.1.118
```

정상 출력 예

```bash
Export list for 172.30.1.118:
/data/mimic3 172.30.1.0/24
```

---

## 2.3 마운트 디렉토리 생성

```bash
sudo mkdir -p /data/mimic_nfs
```

---

## 2.4 NFS 연결 (마운트)

```bash
sudo mount -t nfs 172.30.1.118:/data/mimic3 /data/mimic_nfs
```

---

## 2.5 자동 마운트 설정

재부팅 시 자동으로 마운트되도록 `/etc/fstab`에 추가합니다.

```bash
sudo vim /etc/fstab
```

아래 내용을 추가합니다.

```bash
172.30.1.118:/data/mimic3 /data/mimic_nfs nfs defaults 0 0
```

설정 테스트

```bash
sudo mount -a
```

---

# 3. 연결 확인

마운트 확인

```bash
df -h
```

또는

```bash
mount | grep nfs
```

예시

```bash
172.30.1.118:/data/mimic3 on /data/mimic_nfs type nfs4
```

파일 생성 테스트

```bash
touch /data/mimic_nfs/test.txt
```

서버에서 `/data/mimic3/test.txt` 파일이 생성되면 정상적으로 연결된 것입니다.

---
