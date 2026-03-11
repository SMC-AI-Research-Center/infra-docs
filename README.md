# 서버 관리 저장소 (Server Management Repository)

이 저장소는 다양한 서버, Docker, 네트워크 및 백업 환경의 구축과 관리를 위한 문서 및 설정 파일을 포함하고 있습니다.

## 디렉토리 구조

- **docs/**
- **setup_server/**: Ubuntu(22.04/24.04), CUDA, DGX-V100 및 서버 클러스터 설치/설정 가이드
- **setup_docker/**: Docker, Docker Compose, Docker Swarm 환경 설정 (splash/esplash 설정 포함)
- **network/**: 터널링 및 NFS 설정 정보
- **mirroring/**: 미러링(lsyncd, pypi) 설정 및 가이드
- **miscellaneous/**: 기타 서버 관련 문서 (예: 항온항습기실/서버실 관리)

- **configs/**: Jupyter Lab 설정 및 Dockerfile과 같은 구성 스크립트

---

## 문서 인덱스

### 1. 서버 구축 (Server Setup)

- [Ubuntu 22.04 CUDA 12.8](docs/setup_server/ubuntu_22.04_cuda_12.8.md)
- [Ubuntu 24.04 CUDA 13.0](docs/setup_server/ubuntu_24.04_cuda_13.0.md)
- [DGX V100 설정](docs/setup_server/dgx_v100.md)
- [Ubuntu 22.04 병원 네트워크 설정](docs/setup_server/ubuntu_22.04_hospital_network.md)
- [서버 클러스터](docs/setup_server/server_cluster.md)

### 2. Docker 구축 (Docker Setup)

- [Docker eSplash](docs/setup_docker/docker_esplash.md)
- [Docker Splash](docs/setup_docker/docker_splash.md)
- [Docker Compose eSplash](docs/setup_docker/docker_compose_esplash.md)
- [Docker Compose Splash](docs/setup_docker/docker_compose_splash.md)
- [Docker Swarm](docs/setup_docker/docker_swarm.md)

### 3. 네트워크 (Network)

- [터널링 (Tunneling)](docs/network/tunneling.md)
- [NFS 서버](docs/network/nfs.md)

### 4. 미러링 (Mirroring)

- [lsyncd 실시간 동기화](docs/mirroring/lsyncd.md)
- [PyPI 미러 구성](docs/mirroring/pypi.md)

### 5. 기타 (ETC)

- [냉동고실](docs/ETC/refrigerator_room.md)

### 6. 설정 파일 (Configs)

- [Dockerfile](docs/setup_docker/configs/Dockerfile)
- [Jupyter Lab 설정](docs/setup_docker/configs/jupyter_lab_config.py)
