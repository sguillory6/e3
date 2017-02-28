import os
import time
import errno


class FileLock(object):
    """
    File based resource locking
    """
    def __init__(self, lock_store, lock_name, timeout=10, delay=.05):
        self.lock_store = lock_store
        self.lock_name = lock_name
        self.timeout = timeout
        self.delay = delay
        self.locked = False
        self.lock_file_file = None

    def acquire(self):
        start_time = time.time()
        while True:
            try:
                lock_disk_file = os.path.join(self.lock_store, "%s.lck" % self.lock_name)
                self.lock_file_file = os.open(lock_disk_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if (time.time() - start_time) >= self.timeout:
                    raise RuntimeError("Timeout while locking lock with name '%s'" % self.lock_name)
                time.sleep(self.delay)

    def release(self):
        if self.lock_file_file:
            os.close(self.lock_file_file)

            lock_disk_file = os.path.join(self.lock_store, "%s.lck" % self.lock_name)
            if os.path.exists(lock_disk_file):
                os.unlink(lock_disk_file)

            self.lock_file_file = None

    def __enter__(self):
        if not self.lock_file_file:
            self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.release()

    def __del__(self):
        self.release()
