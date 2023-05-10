import re
from dataclasses import dataclass
from typing import Any, Optional

from commitizen import git, out
from commitizen.config.base_config import BaseConfig
from commitizen.cz.conventional_commits.conventional_commits import ConventionalCommitsCz


class CustomCommitsCz(ConventionalCommitsCz):
    """カスタムコミットルール"""

    def __init__(
        self,
        config: BaseConfig,
    ) -> None:
        """
        コンストラクタ
        """

        super().__init__(config)
        github_repo_owner: Any = config.settings.get("github_repo_owner")
        github_repo_name: Any = config.settings.get("github_repo_name")
        self.github_repo = GitHubRepo(github_repo_owner, github_repo_name)

    def changelog_message_builder_hook(
        self,
        parsed_message: dict[Any, Any],
        commit: git.GitCommit,
    ) -> dict:
        """
        この関数は解析されたコミットごとに実行される。

        メッセージの出力に必要な情報(リンクなど)を追加してカスタマイズすることができる。

        Args:
            parsed_message (dict[Any, Any]): 解析コミット
            commit (git.GitCommit): コミット情報 (rev, title, body, author, author_email)

        Returns:
            dict: 解析コミット(カスタマイズ済み)
        """

        long_revision: str = commit.rev
        short_revision: str = long_revision[:7]
        message: str = parsed_message["message"]
        repo_commit_url: str = self.github_repo.get_commit_url(long_revision)
        parsed_message["message"] = f"{message} ([{short_revision}]({repo_commit_url}))"

        return parsed_message

    def changelog_hook(
        self,
        full_changelog: str,
        partial_changelog: Optional[str],
    ) -> str:
        """
        この関数は変更履歴生成の最後に実行される。

        Slackメッセージを送信したり、コンプライアンス部門に通知したりするのに利用できる。

        Args:
            full_changelog (str): 全ての変更履歴 ※ファイルに書き込まれようとしているデータ
            partial_changelog (Optional[str]): 部分的な変更履歴

        Returns:
            str: 全ての変更履歴(更新済み)

        Note:
            - `cz bump --dry-run`を実行する前に下記処理を差分のように変更する
            - commitizen.commands.changelog#write_changelog

            ```diff
            - changelog_file.write(changelog_out)
            + if self.dry_run:
            +     out.write(changelog_out)
            +     raise DryRunExit()
            + else:
            +     changelog_file.write(changelog_out)
            ```

            - commitizen.commands.changelog#__call__

            ```diff
            - if self.dry_run:
            -     out.write(changelog_out)
            -     raise DryRunExit()
            ```
        """

        tag_pattern: str = r"^#{1,2} (v\d?.\d?.\d?.*) \(.*\)"  # `## v0.0.0 (yyyy-mm-dd)`
        tags: list[str] = re.findall(tag_pattern, full_changelog, re.MULTILINE)
        out.write(f"tags in full_changelog: {tags}\n")
        for tag_index, tag in enumerate(tags):
            search_pattern_of_newer_tag: str = rf"(^#{{1,2}}) ({tag})"
            replacement_str_of_newer_tag: str
            try:
                older_tag: str = tags[tag_index + 1]
                newer_tag: str = tags[tag_index]
                repo_diff_url: str = self.github_repo.get_diff_url(older_tag, newer_tag)
                replacement_str_of_newer_tag = rf"\1 [\2]({repo_diff_url})"
            except IndexError:  # if newer_tag is the oldest tag
                replacement_str_of_newer_tag = rf"\1 \2"
            full_changelog = re.sub(
                search_pattern_of_newer_tag,
                replacement_str_of_newer_tag,
                full_changelog,
                flags=re.MULTILINE,
            )

        return full_changelog


@dataclass
class GitHubRepo:
    """GitHubリポジトリの情報を保持するクラス"""

    owner: str
    name: str

    @property
    def url(self) -> str:
        return f"https://github.com/{self.owner}/{self.name}"

    def get_commit_url(self, revision: str) -> str:
        return f"{self.url}/commit/{revision}"

    def get_tag_url(self, tag: str) -> str:
        return f"{self.url}/releases/tag/{tag}"

    def get_diff_url(self, tag1: str, tag2: str) -> str:
        return f"{self.url}/compare/{tag1}...{tag2}"
