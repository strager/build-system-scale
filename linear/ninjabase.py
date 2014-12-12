import os
from lib.ninjabase import NinjaTestBase
from linear.linearbase import LinearTestBase

class NinjaLinearTestBase(LinearTestBase, NinjaTestBase):
    def _set_up(self, temp_dir):
        super(NinjaLinearTestBase, self)._set_up(temp_dir)
        build_ninja_path = self._build_ninja_path(temp_dir)
        with open(build_ninja_path, 'w') as ninja:
            ninja.write('ninja_required_version = 1.0\n')
            ninja.write('rule cp\n command = cp $in $out\n')
            for i in xrange(self._depth - 1, 0, -1):
                ninja.write(
                   'build file_{}: cp file_{}\n'.format(
                        i + 1,
                        i,
                    ),
                )
            ninja.write('default file_{}\n'.format(
                self._depth,
            ))
