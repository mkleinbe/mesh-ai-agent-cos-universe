from __future__ import annotations

import os
import pty
import select
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIGURE = ROOT / "deployment/qnap/scripts/mesh-cos-slack-hitl-configure.sh"
SCRIPTS = CONFIGURE.parent


def _path_without_stty(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    for source_dir in (Path("/usr/bin"), Path("/bin")):
        if not source_dir.is_dir(): continue
        for source in source_dir.iterdir():
            if source.name == "stty" or (bin_dir / source.name).exists(): continue
            try: (bin_dir / source.name).symlink_to(source)
            except OSError: pass
    docker = bin_dir / "docker"
    if docker.exists() or docker.is_symlink(): docker.unlink()
    docker.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8"); docker.chmod(0o755); return bin_dir


def _run_configure_in_pty(tmp_path: Path) -> tuple[int, str, Path]:
    app = tmp_path / "app"; bundle = tmp_path / "release/cos-mcp"; (app / "secrets").mkdir(parents=True); (app / "logs/deployment").mkdir(parents=True); bundle.mkdir(parents=True)
    (bundle / ".env.runtime").write_text("MESH_COS_IMAGE=image:test\nMESH_COS_DEPLOYMENT_RELEASE=4.1.17\n", encoding="utf-8")
    (app / "secrets/slack-socket-app-token").write_text("xapp-test-socket\n", encoding="utf-8"); (app / "secrets/slack-bot-token").write_text("xoxb-test-bot\n", encoding="utf-8")
    env = os.environ.copy(); env.update({"PATH": str(_path_without_stty(tmp_path)), "QNAP_SCRIPT_ROOT": str(SCRIPTS), "QNAP_BUNDLE_APP_ROOT": str(bundle), "QNAP_APP_ROOT": str(app), "QNAP_SLACK_APPROVER_USER_ID_FILE": str(app / "secrets/slack-approver-user-id"), "QNAP_SLACK_SOCKET_APP_TOKEN_FILE": str(app / "secrets/slack-socket-app-token"), "QNAP_SLACK_BOT_TOKEN_FILE": str(app / "secrets/slack-bot-token"), "MESH_COS_LOG_ROOT": str(app / "logs/deployment"), "MESH_UID": "65532", "MESH_GID": "65532"})
    pid, fd = pty.fork()
    if pid == 0: os.execve("/bin/sh", ["/bin/sh", str(CONFIGURE)], env)
    chunks: list[bytes] = []
    while True:
        ready, _, _ = select.select([fd], [], [], 0.1)
        if ready:
            try: data = os.read(fd, 65536)
            except OSError: data = b""
            if data: chunks.append(data)
        waited, status = os.waitpid(pid, os.WNOHANG)
        if waited == pid:
            while True:
                try: data = os.read(fd, 65536)
                except OSError: break
                if not data: break
                chunks.append(data)
            os.close(fd); return os.waitstatus_to_exitcode(status), b"".join(chunks).decode("utf-8", errors="replace"), app


def test_v4117_existing_slack_credentials_configure_without_stty_dependency(tmp_path: Path) -> None:
    rc, output, app = _run_configure_in_pty(tmp_path)
    assert rc == 0; assert "stty is required for hidden secret input" not in output; assert "Slack verifier token file is missing" not in output; assert "Slack HITL protected runtime configuration complete" in output; assert (app / "secrets/slack-socket-app-token").is_file(); assert (app / "secrets/slack-bot-token").is_file(); assert not (app / "secrets/slack-verifier-token").exists()
