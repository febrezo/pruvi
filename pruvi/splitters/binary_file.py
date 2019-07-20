from pruvi.splitters.file import FileSplitter


class BinaryFileSplitter(FileSplitter):
    """Binary File Splitter object
    """
    def split_document(self, **kwargs):
        """Split a binary file

        Kwargs:
            size (int): Number of bytes in which to split the contents
        """
        self._parts = []

        with open(self.file_path, 'rb') as f:
            while 1:
               content = f.read(kwargs.get("size"))
               if content:
                   self._parts.append(content)
               else:
                   break
