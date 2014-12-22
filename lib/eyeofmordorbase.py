import bsstest

class EyeOfMordorTestBase(bsstest.BSSTest):
    name = 'eyeofmordor'

    def _wait_for_stamp_update(self):
        # eyeofmordor does not use time stamps.
        pass
