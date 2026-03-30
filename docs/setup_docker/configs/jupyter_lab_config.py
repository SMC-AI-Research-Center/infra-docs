# Configuration file for lab.

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
