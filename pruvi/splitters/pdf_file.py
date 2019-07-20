from PyPDF2 import PdfFileWriter, PdfFileReader

from pruvi.splitters.file import FileSplitter


class PDFFileSplitter(FileSplitter):
    """PDF File Splitter object
    """
    def split_document(self, **kwargs):
        """Split a PDF file

        Kwargs:
            method (str): Splitting method. One of the following: "pages".
        """
        parts = []

        if kwargs.get("method", "pages") == "pages":
            inputpdf = PdfFileReader(open(self.file_path, "rb"))

            for i in range(inputpdf.numPages):
                output = PdfFileWriter()
                output.addPage(inputpdf.getPage(i))

                part_file = self._get_file_path(i)

                with open(part_file, "wb") as outputStream:
                    output.write(outputStream)

                with open(part_file, "rb") as f:
                    pdf_data = bytearray(f.read())
                parts.append(pdf_data)
        else:
            with open(self.file_path, 'rb') as f:
                parts = [f.read()]

        self.set_parts(parts)
