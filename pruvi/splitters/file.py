import os
import tempfile

from pruvi.splitters.base import BaseSplitter


class FileSplitter(BaseSplitter):
    """File Splitter object

    Attributes:
        file_path (str): The file to split.
    """
    def __init__(self, file_path, parts=[], hash_type="sha3_512"):
        """Constructor

        Args:
            file_path (str): The file to split.
            parts (list): List of elements to proof.
            hash_type (str): The hash type to be used.
        """
        BaseSplitter.__init__(self, parts=parts, hash_type=hash_type)
        self.file_path = file_path

    def _get_file_path(self, part):
        return os.path.join(
            tempfile.gettempdir(),
            f"document-part{part}"
        )

    def split_document(self, text, method="lines"):
        """Split a text

        Args:
            text (str): Any kind of object to proof.
            method (str): The splitting method.

        Returns:
            bytes.
        """
        self._parts = []

        if method == "lines":
            self._parts = text.splitlines()
        elif method == "sentences":
            self._parts = text.split(".")
        else:
            self._parts = [text]
