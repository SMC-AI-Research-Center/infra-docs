# Docker in Server

1. **Docker Image/Container**
1. *Docker Compose*
1. *Docker Swarm*

---

## 1. Docker Image/Container

### 주피터 설정 파일 생성

`vim jupyter_lab_config.py`

```python
c = get_config()
c.ServerApp.ip = "0.0.0.0"
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False

import os
from jupyter_server.auth.security import passwd

# 환경변수에서 비밀번호를 읽어서 해시. 빈 값이면 토큰 인증 유지
raw_pw = os.environ.get("JUPYTER_PASSWORD", "")
c.ServerApp.token = ""
if raw_pw:
    c.ServerApp.password = passwd(raw_pw)
else:
    c.ServerApp.password = passwd("default_123")

```

---

### Image

- Dockerfile
  - 우분투22.04 사용: [nvidia-container-runtime 가능 OS](https://nvidia.github.io/nvidia-container-runtime/) 확인
  - Cuda 12.6 사용: Torch 지원 버전 확인
  - 순서
    1. 시스템 패키지 설치
    1. 백엔드 처리 및 시간대 설정
    1. 파이썬 설치(3.11)
    1. jupyter 설치

`vim Dockerfile`

```Dockerfile
FROM nvcr.io/nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

# 1. 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    apt-utils build-essential ca-certificates curl gpg kmod file \
    libelf-dev libglvnd-dev pkg-config wget vim zlib1g-dev \
    libncurses5-dev libgdbm-dev libnss3-dev libssl-dev \
    libreadline-dev libffi-dev software-properties-common coreutils \
    && rm -rf /var/lib/apt/lists/*


ARG DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    apt-get update && \
    apt-get install -y tzdata && \
    dpkg-reconfigure -f noninteractive tzdata

ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ARG INSTALLER_URL_LINUX64=https://repo.anaconda.com/miniconda/Miniconda3-py311_26.1.1-1-Linux-x86_64.sh
ARG SHA256SUM_LINUX64=52d1f19154b0716d7dc0872f0d858702640da08a4e53fd0035ba988608203d6b

# [1단계] 다운로드 및 무결성 검사
RUN set -x && \
    wget "${INSTALLER_URL_LINUX64}" -O miniconda.sh -q && \
    echo "${SHA256SUM_LINUX64}  miniconda.sh" > shasum && \
    sha256sum --check shasum && \
    bash miniconda.sh -b -p ${CONDA_DIR} && \
    rm miniconda.sh shasum

# [2단계] 시스템 경로 및 셸 설정
# 여기서 터진다면: 심볼릭 링크 생성 실패 혹은 파일 경로 오타
RUN set -x && \
    ln -s ${CONDA_DIR}/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". ${CONDA_DIR}/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate" >> ~/.bashrc
# [3단계] 약관 동의 및 용량 최적화 (Clean up)
# 여기서 터진다면: conda 명령어 인식 불가 혹은 라이선스 동의 모듈 누락
RUN set -x && \
    ${CONDA_DIR}/bin/conda tos accept && \
    ${CONDA_DIR}/bin/conda remove --force-remove -y conda-anaconda-tos && \
    rm -rf ~/.conda/tos && \
    find ${CONDA_DIR}/ -follow -type f -name '*.a' -delete && \
    find ${CONDA_DIR}/ -follow -type f -name '*.js.map' -delete

# 최신 pip 업그레이드 후, Jupyter Lab 설치
RUN conda install -y -c conda-forge jupyterlab nb_conda_kernels && \
    conda clean -afy

# 폐쇄망에서 conda create 불가하므로 빌드 시 미리 환경 생성
# nb_conda_kernels가 자동으로 Jupyter 커널로 인식함
RUN conda create -y -n py39 python=3.9 ipykernel && \
    conda create -y -n py310 python=3.10 ipykernel && \
    conda create -y -n py312 python=3.12 ipykernel && \
    conda create -y -n py313 python=3.13 ipykernel && \
    conda clean -afy

WORKDIR /home/jupyter

RUN echo "[global]\nindex-url = http://pypi.smc.com/simple\ntrusted-host = pypi.smc.com" > /etc/pip.conf
COPY jupyter_lab_config.py /home/jupyter/jupyter_lab_config.py

# Bash를 실행하고, 환경 설정을 불러온 뒤 주피터를 실행하도록 강제함
CMD ["/opt/conda/bin/jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser", "--config=/etc/jupyter/jupyter_lab_config.py"]
```

- Docker image

`sudo docker build <옵션> <Dockerfile 경로>`

```bash
sudo docker build --tag jupyter_s:1.1 .
```

---

## 참고할 사항

### 도커 정리

```bash
docker system prune
docker system prune -a --volumes
docker container prune
docker network prune
docker volume prune
docker image prune
```
