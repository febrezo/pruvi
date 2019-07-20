from pruvi.splitters.base import BaseSplitter


class TextSplitter(BaseSplitter):
    """Base Splitter object
    """
    def split_document(self, text, method="lines"):
        """Split a text

        Args:
            text (str): Any kind of object to proof.
            method (str): The splitting method. One of the following: "lines", "paragraphs",
                "words".
        """
        parts = []

        if method == "lines":
            parts = text.splitlines()
        elif method == "words":
            parts = text.split()
        elif method == "paragraphs":
            parts = text.split("\n\n")
        else:
            parts = [text]

        self.set_parts(parts)
