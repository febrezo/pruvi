import json
import logging
import os
import tempfile

from pymerkle import MerkleTree
from pymerkle.proof import Proof
from pymerkle import validateProof

from pruvi.exceptions import NoPartsException
from pruvi.hashing import hash_bytes

class BaseSplitter(object):
    """Base Splitter object

    Attributes:
        _parts (list): List of elements to proof.
        hash_type (str): The hash type to be used.
        tree: The Merkle Tree created.
        proofs (list): List of proofs.
    """
    def __init__(self, parts=[], hash_type="sha3_512"):
        """Constructor

        Args:
            parts (list): List of elements to proof.
            hash_type (str): The hash type to be used.
        """
        self._parts = []
        self.set_parts(parts)
        self.hash_type = hash_type
        self.tree = None
        self.proofs = []

    def _export_proofs(self, output_file):
        """Export all proofs to a file

        Args:
            output_file (str): Output file.
        """
        info = {
            "merkle_root": self.tree.rootHash.decode(),
            "proofs": self.proofs
        }

        with open(output_file, "w") as f:
            f.write(json.dumps(info, indent=2))

    def _export_tree(self, output_file):
        """Export tree

        Args:
            output_file (str): Output file.
        """
        self.tree.export(f"{output_file}")

    def _write_parts(self, output_folder=tempfile.gettempdir()):
        """Writes a file for each part

        Args:
            output_folder (str): The folder where the parts will be written.
        """
        if not os.path.exists(output_folder):
            logging.info(f"Creating parts folder at '{output_folder}'...")
            os.makedirs(output_folder)

        ext = os.path.splitext(self.file_path)[-1]

        for i, part in enumerate(self._parts):
            output_file = os.path.join(
                output_folder,
                f"part-{i+1}{ext}"
            )

            logging.info(f"Writing part {i+1} at '{output_file}'...")
            with open(output_file, "wb") as f:
                f.write(self._parts[i])

            output_file_proof = output_file.replace(ext, "-proof.json")
            logging.info(f"Writing proof for part {i+1} at '{output_file_proof}'...")
            with open(output_file_proof, "w") as f:
                f.write(json.dumps(self.proofs[i], indent=2))

    def create_tree(self):
        """Create the tree

        Args:
            output_folder (str): The folder where the parts will be written.
        """
        self.tree = MerkleTree(hash_type=self.hash_type, security=False, raw_bytes=True)

        # Creating tree
        for i, f in enumerate(self.get_parts()):
            x = self.tree.update(f)

        # Creating proofs
        for i, f in enumerate(self._parts):
            self.proofs.append(self.tree.auditProof(i).serialize())

    def export(self, output_folder):
        """Export the splitted information

        Args:
            output_folder (str): Output folder.
        """
        if not os.path.exists(output_folder):
            logging.info(f"Creating export folder at '{output_folder}'...")
            os.makedirs(output_folder)

        tree_file = os.path.join(output_folder, "tree.json")
        logging.info(f"Creating tree file at '{tree_file}'...")
        self._export_tree(tree_file)

        proof_file = os.path.join(output_folder, "all_proofs.json")
        logging.info(f"Creating proofs file at '{proof_file}'...")
        self._export_proofs(proof_file)

        parts_folder = os.path.join(output_folder, "parts")
        logging.info(f"Creating parts at '{parts_folder}/'...")
        self._write_parts(parts_folder)

    def get_parts(self):
        """Set parts appropiately

        Args:
            parts (list): List of parts to process

        Raises:
            pruvi.exceptions.NoPartsException.
        """
        if self._parts:
            return self._parts
        else:
            raise NoPartsException

    def set_parts(self, parts, codification="utf-8"):
        """Set parts appropiately

        Args:
            parts (list): List of parts to process.
            codification (str): The codification of the charset.
        """
        for p in parts:
            if isinstance(p, str):
                self._parts.append(p.encode(codification))
            elif isinstance(p, list) or isinstance(p, dict):
                element = json.dumps(p)
                self._parts.append(element.encode(codification))
            elif isinstance(p, bytes) or isinstance(p, bytearray):
                self._parts.append(p)
            else:
                self._parts.append(str(p).encode(codification))

    def verify_file(self, data_file, proof_file, merkle_root=None):
        """Verify a file

        Args:
            data_file (str): Path to the data file to verify.
            proof_file (str): Path to the proof file.
            merkle_root (str): A merkle root to proof.

        Returns:
            bool.
        """
        logging.info(f"Step 1/3: Hashing the file: '{data_file}'")
        with open(data_file, "rb") as f:
            data = f.read()
        calculated_digest = hash_bytes(data)
        logging.info(f"\tFile hash: '{calculated_digest}'")

        logging.info(f"Step 2/3: Verifying if the hash matches with that of the proof...")
        with open(proof_file) as f:
            proof_data = json.load(f)
        proof_index = proof_data["body"]["proof_index"]
        proof_digest = proof_data["body"]["proof_path"][proof_index][1]
        if proof_digest == calculated_digest:
            logging.info("\t✔️ OK!")
        else:
            logging.error("\t✕ Verification failed!")
            return

        logging.info(f"Step 3: Verifying the Merkle Proof...")
        if self.verify_proof(proof_data, merkle_root):
            logging.info("\t✔️ Verification successful!")
            return True
        else:
            logging.error("\t✕ Verification failed!")
            return False

    def verify_proof(self, data, merkle_root=None):
        """Verify a proof

        Args:
            data (dict): A Merkle proof to verify.
            merkle_root (str): A merkle root to proof.

        Returns:
            bool.
        """
        if not merkle_root:
            merkle_root = self.tree.rootHash
        else:
            if isinstance(merkle_root, str):
                merkle_root = merkle_root.encode()

        p = Proof(from_dict=data)
        return validateProof(target=merkle_root, proof=p)
