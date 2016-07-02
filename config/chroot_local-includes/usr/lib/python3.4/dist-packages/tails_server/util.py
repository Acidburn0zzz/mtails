import tempfile
import os
import shutil
import threading
from gi.repository import GLib


class PolicyNoAutostartOnInstallation(object):
    policy_path = "/usr/sbin/policy-rc.d"
    policy_content = """#!/bin/sh\nexit 101"""

    def __enter__(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.old_policy_path = None
        if os.path.exists(self.policy_path):
            shutil.move(self.policy_path, self.tmp_dir)
            self.old_policy_path = os.path.join(self.tmp_dir, self.policy_path)
        with open(self.policy_path, "w+") as f:
            f.write(self.policy_content)
        os.chmod(self.policy_path, 700)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.policy_path)
        if self.old_policy_path:
            shutil.move(self.old_policy_path, self.policy_path)
        os.rmdir(self.tmp_dir)


def run_threaded(service, function, *args):
    thread = threading.Thread(target=run_with_exception_handling,
                              args=(service, function) + args)
    thread.daemon = True
    thread.start()


def run_threaded_when_idle(service, function, *args):
    thread = threading.Thread(target=run_with_exception_handling,
                              args=(service, GLib.idle_add, function) + args)
    thread.daemon = True
    thread.start()


def run_with_exception_handling(service, function, *args):
    try:
        function(*args)
    except:
        service.status.emit("update", service.status.STATUS_ERROR)
        raise
