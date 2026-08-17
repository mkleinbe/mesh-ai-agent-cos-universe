from __future__ import annotations

import os

class KillSwitch:
    @staticmethod
    def enabled() -> bool:
        return os.getenv('MESH_COS_KILL_SWITCH', 'false').lower() in {'1','true','yes','on'}

    @classmethod
    def assert_automation_allowed(cls) -> None:
        if cls.enabled():
            raise RuntimeError('Automated actions disabled by emergency kill switch')
