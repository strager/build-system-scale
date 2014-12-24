import contextlib
import shutil
import sys
import tempfile
import time
import timeit

get_time = timeit.default_timer

def temp_file_system_stamp_resolution():
    resolutions = []
    if sys.platform == 'darwin':
        # HGFS+ mtime resolution.
        resolutions.append(1)
    if sys.platform not in ('cygwin', 'darwin', 'win32'):
        # ext3 mtime resolution.
        resolutions.append(1)
        # ext4 mtime resolution.
        resolutions.append(10 ** -9)
    if sys.platform in ('cygwin', 'win32'):
        # FAT32 mtime resolution.
        resolutions.append(2)
        # NTFS mtime resolution.
        resolutions.append(100 * (10 ** -9))
    # System clock resolution.
    resolutions.append(0.02)
    return max(resolutions)

def wait_for_temp_file_system_stamp_update():
    time.sleep(temp_file_system_stamp_resolution())

@contextlib.contextmanager
def temporary_directory():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)
