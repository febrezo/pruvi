from pruvi.splitters.file import FileSplitter


class TextFileSplitter(FileSplitter):
    """Text File Splitter object
    """
    def split_document(self, **kwargs):
        """Split a binary file

        Kwargs:
            method (str): Splitting method. One of the following: "lines", "paragraphs",
                "words".
        """
        parts = []

        with open(self.file_path, 'r') as f:
            text = f.read()
            if kwargs.get("method") == "lines":
                parts = text.splitlines()
            elif kwargs.get("method") == "words":
                parts = text.split()
            elif kwargs.get("method") == "paragraphs":
                parts = text.split("\n\n")
            else:
                parts = [text]

        self.set_parts(parts)
