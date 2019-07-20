import argparse
import json
import logging
import os
import sys

import pruvi
from pruvi.splitters.base import BaseSplitter
from pruvi.splitters.audio_file import AudioFileSplitter
from pruvi.splitters.binary_file import BinaryFileSplitter
from pruvi.splitters.pdf_file import PDFFileSplitter
from pruvi.splitters.text_file import TextFileSplitter

def main():
    """Main parser"""
    def get_parser():
        """Method that gets a valid parser

        Returns:
            argparse.ArgumentParser.
        """
        with open(
            os.path.join(
                os.path.dirname(pruvi.__file__),
                ".banner.txt"
            )
        ) as iF:
            banner = iF.read()

        print(banner)
        print("""
                            Coded with ♥ by @febrezo

        """)

        parser = argparse.ArgumentParser(
            description="Pruvi | A tool for generating partial proofs of big documents",
            epilog="For each subcommand, add '--help' for additional parameters.",
            add_help=False
        )

        about_parser = parser.add_argument_group(
            'Other commands',
            'Get additional information about this program.'
        )
        about_parser.add_argument(
            '-h', '--help',
            action='help',
            help='shows this help and exits.'
        )
        about_parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s ' + pruvi.__version__,
            help='shows the version of this package and exits.'
        )
        about_parser.add_argument(
            '-L', '--log-level',
            metavar='<LOG_LEVEL>',
            action='store',
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="The log level to be set."
        )

        # Add subparsers
        # --------------
        subparsers = parser.add_subparsers(
            description='Available commands.',
            dest='subcommand',
            metavar="<SUBCOMMAND>"
        )

        # Generate parser
        # --------------
        generate_subparser = subparsers.add_parser(
            'split',
            help='Split different files and obtain proofs.',
            conflict_handler='resolve'
        )

        generate_subparser.add_argument(
            '-o', '--output-folder',
            metavar='<OUTPUT_FOLDER>',
            action='store',
            default="./",
            help="The default output folder."
        )

        # Add parsers for from files
        # --------------------------
        from_subparsers = generate_subparser.add_subparsers(
            description='Available input files: json, csv.',
            dest='from_file',
            metavar="<FROM_FILE>"
        )

        # Audio subparser
        audio_subparser = from_subparsers.add_parser(
            'audio',
            help='get proofs from an audio file',
            conflict_handler='resolve'
        )
        audio_subparser.add_argument(
            '-f', '--file',
            metavar='<SOURCE_FILE>',
            required=True,
            help="the path to the given file to split."
        )
        audio_subparser.add_argument(
            '-s', '--seconds',
            metavar='<SECONDS>',
            action='store',
            type=int,
            required=True,
            help="The seconds in which the audio will be splitted."
        )

        # Binary subparser
        binary_subparser = from_subparsers.add_parser(
            'binary',
            help='get proofs from a binary file',
            conflict_handler='resolve'
        )
        binary_subparser.add_argument(
            '-f', '--file',
            metavar='<SOURCE_FILE>',
            required=True,
            help="the path to the given file to split."
        )
        binary_subparser.add_argument(
            '-b', '--bytes',
            metavar='<BYTE_NUMBER>',
            action='store',
            type=int,
            required=True,
            help="Number of bytes to use to split."
        )

        # PDF subparser
        pdf_subparser = from_subparsers.add_parser(
            'pdf',
            help='get proofs from the pages in a PDF file',
            conflict_handler='resolve'
        )
        pdf_subparser.add_argument(
            '-f', '--file',
            metavar='<SOURCE_FILE>',
            required=True,
            help="the path to the given file to split."
        )

        # Text file subparser
        text_file_subparser = from_subparsers.add_parser(
            'text',
            help='get proofs from a text file',
            conflict_handler='resolve'
        )
        text_file_subparser.add_argument(
            '-f', '--file',
            metavar='<SOURCE_FILE>',
            required=True,
            help="the path to the given file to split."
        )
        text_file_subparser.add_argument(
            '-m', '--method',
            metavar='<METHOD>',
            action='store',
            choices=["lines", "paragraphs", "words"],
            default="lines",
            help="Method to split the file."
        )

        # Subparser for validating proofs
        # -------------------------------
        validate_subparser = subparsers.add_parser(
            'validate',
            help='Validate a proof.',
        )

        template_main_subparser = validate_subparser.add_argument_group(
            'Validate a provided proof',
            'Verify if a given file and its proof are linked to a given Merkle root hash.'
        )
        template_main_subparser.add_argument(
            '-p', '--proof-file',
            metavar='<PROOF_FILE>',
            required=True,
            help="the path to a Merkle proof."
        )
        template_main_subparser.add_argument(
            '-d', '--data-file',
            metavar='<DATA_FILE>',
            required=True,
            help="the path to a data file."
        )
        template_main_subparser.add_argument(
            '-m', '--merkle-root',
            metavar='<MERKLE_ROOT>',
            required=True,
            help="the Merkle root that allegedly contains that file."
        )

        return parser

    parser = get_parser()

    args = parser.parse_args()

    logging.basicConfig(
        format='Pruvi [%(levelname)s] > %(message)s',
        level=logging.getLevelName(args.log_level)
    )

    if args.subcommand == "split":
        logging.info(f"Launch splitter process for '{args.from_file}' files...")

        if args.from_file == "audio":
            splitter = AudioFileSplitter(file_path=args.file)
            splitter.split_document(seconds=args.seconds)
        elif args.from_file == "binary":
            splitter = BinaryFileSplitter(file_path=args.file)
            splitter.split_document(size=args.bytes)
        elif args.from_file == "pdf":
            splitter = PDFFileSplitter(file_path=args.file)
            splitter.split_document()
        elif args.from_file == "text":
            splitter = TextFileSplitter(file_path=args.file)
            splitter.split_document(method=args.method)
        else:
            logging.error("No valid file type provided.")
            parser.print_help()
            sys.exit(1)

        logging.info("Creating tree...")
        splitter.create_tree()

        logging.info(f"Tree created. Merkle root hash: '{splitter.tree.rootHash.decode()}'")

        logging.info("Exporting proofs...")
        splitter.export(args.output_folder)
    elif args.subcommand == "validate":
        logging.info(f"Launch verification process for '{args.data_file}'...")
        splitter = BaseSplitter()
        splitter.verify_file(args.data_file, args.proof_file, args.merkle_root)
    else:
        logging.error(f"'{args.subcommand}' is not a valid subcommand.")
        parser.print_help()


if __name__ == "__main__":
    main()
