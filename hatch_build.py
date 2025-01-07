from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


# This hook purely exists to temp remove a symlink that triggers a bug in
# hatchling
# Bug is described in https://github.com/pypa/hatch/issues/1197


symlink = Path(__file__).parent / 'fibro/helix/contrib/themes'
target = Path('../runtime/themes')


class CustomBuildHook(BuildHookInterface):

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        if symlink.exists():
            assert symlink.is_symlink() and symlink.readlink() == target
            symlink.unlink()
