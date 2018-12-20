import os

import gzip
import logging
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from irrd.conf import get_setting
from irrd.storage.database_handler import DatabaseHandler
from irrd.storage.queries import RPSLDatabaseQuery, DatabaseStatusQuery
from irrd.utils.text import remove_auth_hashes

logger = logging.getLogger(__name__)


class SourceExportRunner:
    """
    This SourceExportRunner is the entry point for the expect process
    for a single source.

    If an export destination is defined, a gzipped file will be created
    with the contents of the source, along with a CURRENTSERIAL file.

    The contents of the source are first written to a temporary file, and
    then moved in place.
    """
    def __init__(self, source: str) -> None:
        self.source = source

    def run(self) -> None:
        self.database_handler = DatabaseHandler()
        try:
            export_destination = get_setting(f'sources.{self.source}.export_destination')
            logger.info(f'Starting a source export for {self.source} to {export_destination}')
            self._export(export_destination)

            self.database_handler.commit()
        except Exception as exc:
            logger.critical(f'An exception occurred while attempting to run an export '
                            f'for {self.source}: {exc}', exc_info=exc)
        finally:
            self.database_handler.close()

    def _export(self, export_destination):
        filename_export = Path(export_destination) / f'{self.source.lower()}.db.gz'
        export_tmpfile = NamedTemporaryFile(delete=False)
        filename_serial = Path(export_destination) / f'{self.source.upper()}.CURRENTSERIAL'

        query = DatabaseStatusQuery().source(self.source)
        serial = next(self.database_handler.execute_query(query))['serial_newest_seen']

        with gzip.open(export_tmpfile, 'wb') as fh:
            query = RPSLDatabaseQuery().sources([self.source])
            for obj in self.database_handler.execute_query(query):
                object_bytes = remove_auth_hashes(obj['object_text']).encode('utf-8')
                fh.write(object_bytes + b'\n')

        if filename_export.exists():
            os.unlink(filename_export)
        if filename_serial.exists():
            os.unlink(filename_serial)
        shutil.move(export_tmpfile.name, filename_export)

        with open(filename_serial, 'w') as fh:
            fh.write(str(serial))

        self.database_handler.record_serial_exported(self.source, serial)

        logger.info(f'Export for {self.source} complete, stored in {filename_export} / {filename_serial}')
