import os
from lib.gnumakebase import GNUMakeTestBase
from linear.linearbase import LinearTestBase

class GNUMakeLinearTestBase(
    LinearTestBase,
    GNUMakeTestBase,
):
    def _set_up(self, temp_dir, start=1):
        super(GNUMakeLinearTestBase, self) \
            ._set_up(temp_dir)
        makefile_path = self._makefile_path(temp_dir)
        with open(makefile_path, 'w') as makefile:
            for i in xrange(self._depth - 1, 0, -1):
                makefile.write(
                   'file_{}: file_{}\n\t@cp $< $@\n'.format(
                        i + 1,
                        i,
                    ),
                )
