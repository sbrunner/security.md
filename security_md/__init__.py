"""Read the table of versions from SECURITY.md."""

import xml.etree.ElementTree as ET  # nosec
from typing import Optional

import markdown
from markdown.extensions.tables import TableExtension

HEADER_VERSION = "Version"
HEADER_ALTERNATE_TAG = "Alternate Tag"
HEADER_SUPPORTED_UNTIL = "Supported Until"
SUPPORT_TO_BE_DEFINED = "To be defined"
SUPPORT_BEST_EFFORT = "Best effort"
SUPPORT_UNSUPPORTED = "Unsupported"


class Security:
    """Read the table of versions from SECURITY.md."""

    headers: list[str]
    data: list[list[str]]
    _row: list[str] | None = None

    def __init__(self, status: str, check: bool = True) -> None:
        """
        Initialize.

        Arguments:
        ---------
            status: the content of the SECURITY.md file.
            check: Set to `False` to skip the check.

        """
        self.headers = []
        self.data = []

        markdown_instance = markdown.Markdown(extensions=[TableExtension()])

        elem = markdown_instance.parser.parseDocument(
            [s for s in status.split("\n") if s != "" and s[0] == "|"],
        )
        self._pe(elem.getroot())

        self.data = [r for r in self.data if len([c for c in r if c is not None]) > 0]

        self.version_index = self.headers.index(HEADER_VERSION) if HEADER_VERSION in self.headers else -1
        self.alternate_tag_index = (
            self.headers.index(HEADER_ALTERNATE_TAG) if HEADER_ALTERNATE_TAG in self.headers else -1
        )
        self.support_until_index = (
            self.headers.index(HEADER_SUPPORTED_UNTIL) if HEADER_SUPPORTED_UNTIL in self.headers else -1
        )

        # Check the content if the content isn't empty
        if check and status and not self.check(verbose=0):
            msg = "SECURITY.md file is not valid."
            raise ValueError(msg)

    def check(self, verbose: int = -1) -> bool:
        """
        Check the content.

        Arguments:
        ---------
            verbose: the verbosity level, `-1` for no output, `0` for errors only, `1` for all.

        Return:
        ------
            `True` if the content is valid, `False` otherwise.

        """
        success = True
        if self.version_index == -1:
            if verbose >= 0:
                print("`Version` column not found.")
            success = False
        elif verbose >= 1:
            print(f"`Version` column found at index {self.version_index}.")

        if self.alternate_tag_index == -1:
            if verbose >= 1:
                print("Optional `Alternate Tag` column not found.")
        elif verbose >= 1:
            print(f"`Alternate Tag` column found at index {self.alternate_tag_index}.")

        if self.support_until_index == -1:
            if verbose >= 0:
                print("`Supported Until` column not found.")
            success = False
        elif verbose >= 1:
            print(f"`Supported Until` column found at index {self.support_until_index}.")

        return success

    def _pe(self, elem: ET.Element | None) -> None:
        """
        Parse the HTML table.

        Arguments:
        ---------
            elem: The XML element

        """
        if elem is None:
            return
        if elem.tag == "th":
            assert elem.text is not None
            self.headers.append(elem.text)
        if elem.tag == "tr":
            self._row = []
            self.data.append(self._row)
        if elem.tag == "td":
            self._row.append(elem.text)  # type: ignore[union-attr,arg-type]
        for element in list(elem):
            self._pe(element)

    def branches(self) -> list[str]:
        """
        Get the list of supported branches.

        Return:
        ------
            The list of supported branches.

        """
        alternate_tags = set()
        if self.alternate_tag_index >= 0:
            for raw in self.data:
                alternate_tags.update(self._get_alternate_tag(raw[self.alternate_tag_index]))

        return [
            r[self.version_index]
            for r in self.data
            if r[self.support_until_index] != SUPPORT_UNSUPPORTED
            and r[self.version_index] not in alternate_tags
        ]

    def _get_alternate_tag(self, value: str) -> list[str]:
        """
        Get the clean list of alternate tags.

        Arguments:
        ---------
            value: The value of the alternate tag.

        Return:
        ------
            The list of alternate tags as clean list.

        """
        return [tag.strip() for tag in value.split(",") if tag.strip()]

    def all_tags(self, branch: str) -> set[str]:
        """
        Get the list of all tags related to a branch.

        Arguments:
        ---------
            branch: The branch name.

        Return:
        ------
            The list of tags.

        """
        has_latest = False
        used_alternate_tags = set()
        used_raw = None
        for raw in self.data:
            alternate_tags = (
                set(self._get_alternate_tag(raw[self.alternate_tag_index]))
                if self.alternate_tag_index >= 0
                else set()
            )
            if raw[self.version_index] == branch:
                used_raw = raw
                used_alternate_tags = alternate_tags
            if "latest" in alternate_tags:
                has_latest = True

        if used_raw is None:
            msg = f"Branch {branch} not found."
            raise ValueError(msg)

        if used_raw[self.support_until_index] == SUPPORT_UNSUPPORTED:
            return set()
        tags = {branch}
        if self.alternate_tag_index >= 0:
            tags.update(used_alternate_tags)
        if not has_latest and self.data[-1][self.version_index] == branch:
            tags.add("latest")
        return tags
