from lib.eyeofmordorbase import EyeOfMordorTestBase
from linear.linearbase import LinearTestBase
import os
import shutil

class EyeOfMordorLinearTestBase(
    LinearTestBase,
    EyeOfMordorTestBase,
):
    def _build(self, temp_dir, start=1):
        prefix = os.path.join(temp_dir, 'file_')
        for i in xrange(start, self._depth):
            shutil.copy(
                prefix + str(i),
                prefix + str(i + 1),
            )
