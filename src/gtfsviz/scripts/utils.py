# -*- coding: utf-8 -*-

import tempfile
import os

from zipfile import ZipFile, ZIP_DEFLATED

def create_temporary_zipfile(dirname):
    """Create a temporary zip file.

    All files with the extension '.txt' in the given dirname
    will be zipped.
    The temporary zip file must be deleted by the user.
    """

    file_handle, file_name = tempfile.mkstemp(suffix='.zip')
    os.close(file_handle)

    with ZipFile(file_name, 'w', ZIP_DEFLATED) as tmpzip:
        for path in dirname.glob('*.txt'):
            abspath = path.resolve()
            tmpzip.write(str(abspath), abspath.name)

    return (file_handle, file_name)
