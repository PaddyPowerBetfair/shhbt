from dataclasses import dataclass


@dataclass
class Issue:
    """
    Class to keep track of the elements found when a signature captures some insecure content in a repository scan.
    """

    nr_findings: int
    signature_name: str
    file_rel_path: str
