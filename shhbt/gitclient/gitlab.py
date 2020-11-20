import base64
import os
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool
from os.path import splitext
from typing import Any, Dict, List, Optional, Tuple

from shhbt.data import HitFind
from shhbt.gitclient import CommitStatus, GitClient, Options
from shhbt.session import Session
from shhbt.utils import extract_additions


def handle_gitlab_event(event_body: Dict[str, Any]):
    gitlab_token = os.getenv("GITLAB_TOKEN", None)
    gitlab_host = os.getenv("GITLAB_URI", None)

    _cli = _GitLab(hostname=gitlab_host, token=gitlab_token)

    exists, content = _cli.config_in_repo(proj_id=event_body.get("project", {}).get("id"))
    if exists:
        _cli.session = Session(config_content=content)

    else:
        with open(file=os.getenv("CONFIG_LOCATION", "NOT_THIS_ONE"), mode="r") as f:
            _cli.session = Session(config_content=f)

    _cli.handle_event(event_body)


class _GitLab(GitClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_session.headers.update({"PRIVATE-TOKEN": self.token})
        self.last_request_at = datetime.now() - timedelta(hours=1)
        self.session = None if kwargs.get("session") is None else kwargs.get("session")
        self.options = Options(**kwargs)

    def config_in_repo(self, proj_id: str) -> Tuple[bool, Optional[str]]:
        """ "
        repo_config reaches out to GitLab's API to look for the configuration file of shhbt.
        If the response code is not 200, the file does not exist or something with this request went wrong. For that,
        it loads the default file instead.
        Lastly, it decodes the contents from base64, which is the encoded format, according to the documentation.
        """
        req = self.http_session.request(
            method="GET",
            url=f"{self.hostname}/api/v4/projects/{proj_id}/repository/files/%2Eshhbt_config%2Eyamlref=master?ref=master",
        )

        if req.status_code != 200:
            return False, None

        res_body = req.json()
        return True, base64.decode(res_body.get("content"))

    def handle_event(self, event: Dict[str, Any]):
        """
        handle_event abstract the logic behind processing one event received. It sets base important variables, and
        also updates the commit status (which changes the MR).
        Afterwards it fetches the diff and processes it accordingly.
        """
        proj_id = event.get("project", {}).get("id")
        namespace = event.get("project", {}).get("path_with_namespace")
        commit_sha = event.get("object_attributes", {}).get("last_commit", {}).get("id")

        self._update_commit_status(proj_id, commit_sha, CommitStatus.PENDING)

        diffs = self._fetch_diff(proj_id=proj_id, commit=commit_sha)
        errors, findings = self._process_changes(namespace=namespace, diffs=diffs)
        if errors:
            self._update_commit_status(proj_id, commit_sha, CommitStatus.FAILED)

        else:
            if len(findings) > 0:
                self._update_commit_status(proj_id, commit_sha, CommitStatus.FAILED)
            else:
                self._update_commit_status(proj_id, commit_sha, CommitStatus.SUCCESS)

    def _update_commit_status(self, proj: str, commit: str, status: CommitStatus, **kwargs):
        """ "
        _update_commit_status takes all required logic to update a commit status on GitLab.
        Users can provide a findings variable that contains all the things the scans might have found and those
        will be used to add more context.
        """
        description = ""

        if status == CommitStatus.SUCCESS:
            description = "No secrets found in modified code."

        if status == CommitStatus.FAILED and kwargs.get("description") and kwargs.get("findings"):
            description = "".join([f"{issue.signature_name}" for issue in kwargs.get("findings")])

        req = self.http_session.request(
            method="POST",
            url=f"{self.hostname}/api/v4/projects/{proj}/statuses/{commit}?state={status.value}&description={description}",
        )
        req.raise_for_status()

    def _fetch_diff(self, proj_id: str, commit: str) -> List[Dict]:
        """
        _fetch_diff has the logic required to fetch a diff from GitLab so we can analyse only the differences between
        two changes.
        :returns: Python object of a given response body.
        """
        req = self.http_session.request(
            method="GET", url=f"{self.hostname}/api/v4/projects/{proj_id}/repository/commits/{commit}/diff"
        )
        req.raise_for_status()

        return req.json()

    def _process_changes(self, namespace: str, diffs: List[Dict]) -> Tuple[bool, List["HitFind"]]:
        """
        _process_changes takes all changes performed to a given file from a diff, and processes them in a multithreaded
        implementation.
        Skips deleted files
        :return: a tuple that corresponds to whether any error occurred or not and the findings.
        """
        self.logger.info("Processing diffs. Received %s diffs.", len(diffs))

        try:
            non_del_diffs = [d for d in diffs if not d.get("deleted_file")]
            with ThreadPool(processes=self.options.threads) as pool:
                findings = pool.starmap(
                    self._process_file_change,
                    [(d.get("new_path"), d.get("diff")) for d in non_del_diffs],
                )
            # removes None findings and merge all findings into single list for better processing.
            return False, [finding for sub_findings in findings for finding in sub_findings if finding]
        except Exception as e:
            self.logger.exception("Failed processing repository %s with error %s", namespace, e)
            return True, []
        finally:
            pool.close()
            pool.join()

    def _process_file_change(self, new_path, content) -> List[Optional["HitFind"]]:
        """
        _process_file_change handles processing each change separately. It uses the session that was preloaded into
        this client so it makes use of custom blacklists or signatures.
        :return: a list of findings if any.
        """
        self.logger.info("Processing change in file %s", new_path)

        name_splits = new_path.split("/")
        filename = name_splits[len(name_splits) - 1]
        # extract extension from filename. Index 1 should be the extension
        extension = splitext(filename)[1].lstrip(".")

        for item in self.session.blacklists:
            if item.match_item(file_path=new_path, extension=extension):
                return [None]

        additions = extract_additions(text=content)

        hits: List[HitFind] = []

        for signature in self.session.signatures:
            if signature.part == signature.PART_CONTENTS:
                for add in additions:
                    matches = signature.get_content_matches(content=add)
                    if matches:
                        hits.append(
                            HitFind(nr_findings=len(matches), signature_name=signature.name, file_rel_path=new_path)
                        )
            else:
                matched, part = signature.match(
                    path=new_path,
                    filename=filename,
                    extension=extension,
                    content=content,
                )
                if matched:
                    hits.append(HitFind(nr_findings=1, file_rel_path=new_path, signature_name=signature.name))

        return hits
