# coding: utf-8

import logging

LOGGER = logging.getLogger(__name__)


def check_pg_trgm_installed(cr):
    """
    Check if the 'pg_trgm' postgres extension has been installed in this
    database.
    :returns boolean Yes or No.
    """
    cr.execute("""
        SELECT installed_version FROM pg_available_extensions
        WHERE name = 'pg_trgm';
    """)
    result = [x[0] for x in cr.fetchall()][0]
    return True if result is not None else False


def pre_init_hook(cr):
    """ Attempt to install the postgresql extension 'pg_trgm' which is
    required for this module to work correctly. """
    LOGGER.info("Checking if postgres 'pg_trgm' extension is installed.")
    installed = check_pg_trgm_installed(cr)
    if not installed:
        LOGGER.info("Installing 'pg_trgm' postgres extension.")
        cr.execute("CREATE EXTENSION btree_gist;")
        installed = check_pg_trgm_installed(cr)
        if not installed:
            raise Warning("Unable to install pg_trgm extension.")
    LOGGER.info("Postgres 'pg_trgm' extension is installed.")
