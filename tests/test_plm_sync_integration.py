"""Optional check against a real Odoo 19 database with OdooPLM installed.

Skipped unless ODOO_PLM_INTEGRATION=1 and the ODOO_* variables point at that
database. CI does not start a container for this. A manual run is:

    ODOO_PLM_INTEGRATION=1 ODOO_URL=http://localhost:8069 ODOO_DB=odooplm \\
    ODOO_USER=admin ODOO_PASSWORD=admin \\
    python -m pytest tests/test_plm_sync_integration.py -q
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("ODOO_PLM_INTEGRATION") != "1",
    reason="Set ODOO_PLM_INTEGRATION=1 to sync one draft part against a live OdooPLM.",
)


def test_live_database_accepts_one_draft_part():
    from cad.tools.cli import main

    assert main(["plm-sync", "--part", "VC-SH-1301", "--apply"]) == 0
    assert main(["plm-sync", "--part", "VC-SH-1301", "--apply"]) == 0
