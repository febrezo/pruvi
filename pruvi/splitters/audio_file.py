from pruvi.splitters.file import FileSplitter


class AudioFileSplitter(FileSplitter):
    """Audio File Splitter object
    """
    def split_document(self, **kwargs):
        """Split an audio file

        Kwargs:
            seconds (int): Number of seconds in which to split the contents. Default: 1.
            format (str): Format of the output file. Default: "wav".
        """
        # Dirty hotfix to prevent pydub from printing information at the startup
        # This information will only be printed when the split_document is provided
        from pydub import AudioSegment
        self._parts = []
        audio = AudioSegment.from_wav(self.file_path)

        current_second = 0
        i = 0
        last_part = False

        while 1:
            end_second = current_second + kwargs.get("seconds", 1) * 1000
            if end_second > len(audio):
                end_second = len(audio)
                last_part = True

            new_part = audio[current_second:end_second]

            part_file = self._get_file_path(i)
            new_part.export(part_file, format=kwargs.get("format", "wav"))

            with open(part_file, "rb") as f:
                self._parts.append(f.read())

            if last_part:
                break
            else:
                current_second = end_second
                i += 1
