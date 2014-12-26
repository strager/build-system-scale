import contextlib
import logging
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import timeit

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stderr))

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

def processors_info():
    # Code borrowed from @dbw:
    # http://stackoverflow.com/a/13078519
    # Licensed under CC BY-SA 3.0:
    # http://creativecommons.org/licenses/by-sa/3.0/

    if platform.system() == 'Windows':
        return [platform.processor()]
    elif platform.system() == 'Darwin':
        return filter(None, subprocess.check_output([
            '/usr/sbin/sysctl',
            '-n',
            'machdep.cpu.brand_string',
        ]).split('\n'))
    elif platform.system() == 'Linux':
        processors = []
        with file('/proc/cpuinfo', 'r') as cpuinfo:
            model_re = re.compile(r'^.*model name.*:(.*)$')
            for line in cpuinfo:
                match = model_re.match(line)
                if match:
                    processors.append(line)
        return processors
    else:
        logger.warn(
            'Could not determine processor information; '
            'unknown platform',
        )
        return []
