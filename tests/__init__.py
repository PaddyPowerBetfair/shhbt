
import shutil


class SecretTestMixin:
    def _clean(self, tempdir):
        try:
            shutil.rmtree(tempdir)
        except FileNotFoundError:
            pass