#!/usr/bin/python
import json
from typing import Optional
import argparse
import objectrest

from git import Repo
import tempfile
from pydantic import BaseModel


class AppDetailsFile(BaseModel):
    file_path: str
    commit_hash: str
    commit_message: Optional[str] = None

    @classmethod
    def from_commit(cls, commit):
        return cls(
            file_path=commit.a_path,
            commit_hash=commit.hexsha,
            commit_message=commit.message
        )

    def check_for_changes(self, repo: Repo) -> tuple[bool, dict]:
        """
        Check if the file has changed since the last stored commit hash.
        Store the new commit hash and message if it has changed.
        Returns True if the file has changed, False otherwise.

        :param repo: The git repository to check against.
        :return: True if the file has changed, False otherwise.
        """
        change_detected = False

        latest_relevant_commit = get_most_recent_file_commit(file_path=self.file_path, repo=repo)
        if latest_relevant_commit is not None and latest_relevant_commit.hexsha != self.commit_hash:
            self.commit_hash = latest_relevant_commit.hexsha
            self.commit_message = latest_relevant_commit.message
            change_detected = True

        data = {
            "file_path": self.file_path,
            "commit_hash": self.commit_hash,
            "commit_message": self.commit_message
        }

        return change_detected, data


class AppDetails(BaseModel):
    app_name: str
    git_url: str
    branch_override: Optional[str] = None
    files_to_check: Optional[list[AppDetailsFile]] = None

    def has_changed(self, repo: Repo) -> tuple[bool, list[dict], dict]:
        """
        Check if any of the files in the list have changed since the last stored commit hash.
        :param repo: The git repository to check against.
        :return: True if any file has changed, False otherwise.
        """
        changes_detected = False
        changed_files = []
        updated_file_details: list[dict] = []
        for file in self.files_to_check:
            file_changed, file_details = file.check_for_changes(repo=repo)
            if file_changed:
                changes_detected = True
                changed_files.append(file_details)
            updated_file_details.append(file_details)

        data = {
            "app_name": self.app_name,
            "git_url": self.git_url,
            "branch_override": self.branch_override,
            "files_to_check": updated_file_details
        }

        return changes_detected, changed_files, data


def get_branch(repo: Repo, branch_name: str):
    """
    Get the branch object for the given branch name.
    :param repo: The git repository to check against.
    :param branch_name: The name of the branch to get.
    :return: The branch object if it exists, None otherwise.
    """
    heads = repo.heads
    for head in heads:
        if head.name == branch_name:
            return head
    return None


def get_main_branch(repo: Repo):
    """
    Get the main branch of the repository.
    """
    branch = get_branch(repo=repo, branch_name="main")
    if branch is not None:
        return branch

    branch = get_branch(repo=repo, branch_name="master")
    if branch is not None:
        return branch

    return None


def get_most_recent_file_commit(file_path: str, repo: Repo):
    # Get the most recent commit that modified the specified file on the active branch
    commits = repo.iter_commits(max_count=1, paths=[file_path])
    return next(commits, None)


def check_app(app_details: AppDetails) -> tuple[bool, list[dict], dict]:
    """
    Check if the app has changed in the repository.
    :param app_details: The app details to check.
    :return: True if the app has changed, False otherwise.
    """
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        # Clone the repository
        repo = Repo.clone_from(url=app_details.git_url, to_path=tmpdir)

        # Fetch the latest changes
        repo.remotes.origin.fetch()

        # Check for changes in the main branch
        branch = get_branch(repo=repo, branch_name=app_details.branch_override) if app_details.branch_override else get_main_branch(repo=repo)
        if not branch:
            raise ValueError(f"Could not find applicable branch for {app_details.app_name} ({app_details.git_url})")

        branch.checkout()
        repo.git.pull()

        # Determine if the repository has any changes
        has_changed, changed_files, new_app_data = app_details.has_changed(repo=repo)

        # Delete the repository
        repo.__del__()

        # Temporary directory will be deleted automatically

    return has_changed, changed_files, new_app_data


def read_data_file(file_path: str) -> list[dict]:
    """
    Read the data file containing app details.
    :param file_path: Path to the data file.
    :return: List of dictionaries containing app details.
    """
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def write_data_file(file_path: str, data: list[dict]):
    """
    Write the app details to the data file.
    :param file_path: Path to the data file.
    :param data: List of dictionaries containing app details.
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def load_app_details(file_path: str) -> list[AppDetails]:
    """
    Load the data file containing app details.
    :param file_path: Path to the data file.
    :return: List of AppDetails objects.
    """
    data = read_data_file(file_path=file_path)

    app_details_list = []
    for app_data in data:
        app_data: dict = app_data
        app_details = AppDetails(**app_data)
        app_details_list.append(app_details)

    return app_details_list


def build_app_change_message(
        app_name: str,
        git_url: str,
        file_details: list[dict],
) -> str:
    """
    Build a summary message for the app changes.
    :param app_name: The name of the app.
    :param git_url: The git URL of the app.
    :param file_details: List of file details that changed.
    :return: Formatted message string.
    """
    message = ""
    for file_details_item in file_details:
        message += f"- {file_details_item['file_path']} (commit: {file_details_item['commit_hash']}, message: {file_details_item['commit_message']})\n"
    return message


def send_ntfy_notification(
        app_name: str,
        git_url: str,
        file_details: list[dict],
        ntfy_url: str,
        ntfy_topic: str,
        ntfy_token: str,
        repo_url: str,
):
    """
    Send a notification using ntfy.
    :param app_name: The name of the app.
    :param git_url: The git URL of the app.
    :param file_details: List of file details that changed.
    :param ntfy_url: The URL of the ntfy server.
    :param ntfy_topic: The topic to send the notification to.
    :param ntfy_token: The token for authentication.
    :param repo_url: The URL of the repository.
    """
    message = build_app_change_message(
        app_name=app_name,
        git_url=git_url,
        file_details=file_details
    )

    objectrest.post(url=f"{ntfy_url}",
                    data=json.dumps({
                        "topic": ntfy_topic,
                        "title": f"Upstream changes detected in {app_name}",
                        "message": message,
                        "actions": [
                            {
                                "action": "view",
                                "label": "Repo",
                                "url": git_url
                            },
                            {
                                "action": "view",
                                "label": "Templates",
                                "url": repo_url
                            }
                        ]
                    }),
                    headers={
                        "Authorization": f"Bearer {ntfy_token}",
                    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for changes in a git repository.")
    parser.add_argument(
        "--data_file",
        type=str,
        help="Path to the data file to use for checks.",
        required=True
    )
    parser.add_argument(
        "--ntfy-url",
        type=str,
        help="URL to send notifications to.",
        required=True
    )
    parser.add_argument(
        "--ntfy-topic",
        type=str,
        help="Topic to send notifications to.",
        required=True
    )
    parser.add_argument(
        "--ntfy-token",
        type=str,
        help="Token to use for notifications.",
        required=True
    )
    parser.add_argument(
        "--repo-url",
        type=str,
        help="URL of this repository.",
        required=True
    )
    args = parser.parse_args()

    data_file_path = args.data_file
    ntfy_url = args.ntfy_url
    ntfy_topic = args.ntfy_topic
    ntfy_token = args.ntfy_token
    repo_url = args.repo_url

    apps = load_app_details(file_path=data_file_path)
    new_data: list[dict] = []

    changes_detected = False
    changed_apps = []

    for app in apps:
        print(f"Checking {app.app_name} ({app.git_url}) for changes...")
        has_changed, changed_files, new_app_data = check_app(app_details=app)

        new_data.append(new_app_data)

        if has_changed:
            changes_detected = True
            send_ntfy_notification(
                app_name=app.app_name,
                git_url=app.git_url,
                file_details=changed_files,
                ntfy_url=ntfy_url,
                ntfy_topic=ntfy_topic,
                ntfy_token=ntfy_token,
                repo_url=repo_url
            )
            changed_apps.append({
                "app_name": app.app_name,
                "git_url": app.git_url,
                "changed_files": changed_files
            })

    if changes_detected:
        print(f"Changes detected in {len(changed_apps)} apps:")
        for app in changed_apps:
            details = build_app_change_message(
                app_name=app["app_name"],
                git_url=app["git_url"],
                file_details=app["changed_files"]
            )
            print(f"Changes in {app['app_name']}:\n{details}")
    else:
        print("No changes detected in any apps.")

    # Write the updated data back to the file
    write_data_file(file_path=data_file_path, data=new_data)
    print(f"Updated data file: {data_file_path}")
