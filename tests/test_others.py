from unittest import TestCase
from test.support import EnvironmentVarGuard

from shhbt.utils import extract_additions


class TestUtilsSignatures(TestCase):
    def test_extracts_additions_only(self):
        # GIVEN an input with a online change
        diff_input = '@@ -157,7 +157,7 @@ class Command(SurfaceCommand):\n             - signature name\n         If this file has anything corresponding to a blacklist, then it returns None.\n         """\n-        self.log("Processing change %s", new_path)\n+        self.log("Processing \\n thy \\n change %s", new_path)\n \n         name_splits = new_path.split("/")\n         filename = name_splits[len(name_splits) - 1]\n'

        # WHEN the function extract_additions is called
        additions = extract_additions(text=diff_input)

        # THEN additions is not None and contains 1 entry
        assert additions is not None
        assert len(additions) == 1
        assert additions[0] == '+        self.log("Processing \\n thy \\n change %s", new_path)'

    def test_extract_additions_multiline(self):
        # GIVEN an input with a multiline change
        diff_input = (
            '@@ -0,0 +1,68 @@list_display = [\n+"vm_name",\n+"sourceid",\n+"description",\n+"virtualization",\n+\n'
        )

        # WHEN the function extract_additions is called
        additions = extract_additions(text=diff_input)

        # THEN the list of additions is not None and contains 4 strings and they all match correctly.
        assert additions is not None
        assert len(additions) == 4
        assert additions[0] == '+"vm_name",'
        assert additions[1] == '+"sourceid",'
        assert additions[2] == '+"description",'
        assert additions[3] == '+"virtualization",'

    def test_extract_removals_only(self):
        # NOTE: THIS WOULD NEVER OCCUR, BUT FOR TESTING PURPOSES
        # GIVEN an input with only removals
        diff_input = "@@ -1,161 +0,0 @@\n-import re\n-from datetime import datetime\n-\n-import hvac\n-import pytz\n-from django.conf import settings\n-\n-from inventory import models\n-from inventory.utils import xen\n-from surface.management.commands import SurfaceCommand\n-\n-\n-class Command(SurfaceCommand):\n-    "

        # WHEN the function extract_additions is called
        additions = extract_additions(text=diff_input)

        # THEN dditions is not None but is an empty list
        assert additions is not None
        assert len(additions) == 0
