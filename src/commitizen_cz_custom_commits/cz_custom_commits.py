import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

from commitizen import defaults, git
from commitizen.config.base_config import BaseConfig
from commitizen.cz.conventional_commits.conventional_commits import ConventionalCommitsCz


class CustomCommitsCz(ConventionalCommitsCz):
    """
    カスタムコミットルール

    https://commitizen-tools.github.io/commitizen/customization/
    """

    # コマンド`bump`：コミットから情報を抽出するための正規表現
    bump_pattern = (
        r"^(((feat|fix|perf|refactor|style|build|test|docs|ci|chore)(\(.+\))?(!)?)|\w+!):"
    )
    # コマンド`bump`：抽出された情報をSemVerのインクリメントタイプ(MAJOR、MINOR、PATCH)にマッピングする辞書
    bump_map = OrderedDict(
        (
            (r"^.*!", defaults.MAJOR),
            (r"^feat", defaults.MINOR),
            (r"^fix", defaults.PATCH),
            (r"^perf", defaults.PATCH),
            (r"^refactor", defaults.PATCH),
            (r"^style", defaults.PATCH),
            (r"^build", defaults.PATCH),
            (r"^test", defaults.PATCH),
            (r"^docs", defaults.PATCH),
            (r"^ci", defaults.PATCH),
            (r"^chore", defaults.PATCH),
        )
    )
    bump_map_major_version_zero = OrderedDict(
        (
            (r"^.+!$", defaults.MINOR),
            (r"^feat", defaults.MINOR),
            (r"^fix", defaults.PATCH),
            (r"^perf", defaults.PATCH),
            (r"^refactor", defaults.PATCH),
            (r"^style", defaults.PATCH),
            (r"^build", defaults.PATCH),
            (r"^test", defaults.PATCH),
            (r"^docs", defaults.PATCH),
            (r"^ci", defaults.PATCH),
            (r"^chore", defaults.PATCH),
        )
    )
    # コマンド`changelog`：変更履歴を作成するのに使用される情報を抽出するための正規表現
    commit_parser = (
        r"^("
        + r"(?P<change_type>feat|fix|perf|refactor|style|build|test|docs|ci|chore|BREAKING CHANGE)"
        + r"(?:\((?P<scope>[^()\r\n]*)\)|\()"
        + r"?(?P<breaking>!)?"
        + r"|\w+!"
        + r")"
        + r":\s(?P<message>.*)?"
    )
    # コマンド`changelog`：どのコミットを変更履歴に含めるかを理解するための正規表現
    # NOTE `changelog_pattern = bump_pattern`に変更することで、コマンド`bump`にて検知したコミットを変更履歴にて全て表示する
    changelog_pattern = r"^(((feat|fix|perf|refactor)(\(.+\))?(!)?)|\w+!):"
    # コマンド`changelog`：変更履歴の見出しにコミットの種類をマッピングする辞書
    change_type_map = {
        "BREAKING CHANGE": "BREAKING CHANGE",
        "feat": "Feat",
        "fix": "Fix",
        "perf": "Perf",
        "refactor": "Refactor",
        "style": "Style",
        "build": "Build",
        "test": "Test",
        "docs": "Docs",
        "ci": "CI",
        "chore": "Chore",
    }
    # コマンド`changelog`：変更履歴の見出しを順序付けするのに使用される文字列のリスト
    change_type_order = [
        "BREAKING CHANGE",
        "Feat",
        "Fix",
        "Perf",
        "Refactor",
        "Style",
        "Build",
        "Test",
        "Docs",
        "CI",
        "Chore",
    ]

    def __init__(
        self,
        config: BaseConfig,
    ) -> None:
        """
        コンストラクタ
        """

        super().__init__(config)

        github_repo_owner: Any = config.settings.get("github_repo_owner")
        if github_repo_owner is None:
            raise Exception("設定ファイルに`github_repo_owner`を設定してください。")

        github_repo_name: Any = config.settings.get("github_repo_name")
        if github_repo_name is None:
            raise Exception("設定ファイルに`github_repo_name`を設定してください。")

        # GitHubリポジトリの情報
        self.github_repo: GitHubRepo = GitHubRepo(github_repo_owner, github_repo_name)
        # 破壊的変更の辞書リスト
        self.breaking_change_dicts: list[dict[str, str]] = []

        return None

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

        message: str = parsed_message["message"]

        # IssueIDへのリンクの追加
        issue_ids: list[Any] = re.compile(r"(#\d+)").findall(message)
        issue_id: str
        for issue_id in issue_ids:
            repo_issue_url: str = self.github_repo.get_issue_url(issue_id[1:])
            message = re.compile(issue_id).sub(f"[{issue_id}]({repo_issue_url})", message)

        # コミットIDへのリンクの追加
        long_commit_id: str = commit.rev
        short_commit_id: str = long_commit_id[:7]
        repo_commit_url: str = self.github_repo.get_commit_url(long_commit_id)
        message = f"{message} ([{short_commit_id}]({repo_commit_url}))"

        parsed_message["message"] = message

        # コミット情報のbodyにおける文言`BREAKING CHANGE`の検索
        # 用途：`changelog_hook()`における破壊的変更へのコミット確認用リンクの追加
        breaking_change_word: str = "BREAKING CHANGE: "
        breaking_change_messages: list[str] = re.findall(
            rf"{breaking_change_word}.*", commit.body, re.MULTILINE
        )
        for breaking_change_message in breaking_change_messages:
            breaking_change_dict: dict[str, str] = {}
            breaking_change_dict["breaking_change_message"] = breaking_change_message[
                len(breaking_change_word) :
            ]
            breaking_change_dict["commit_id"] = commit.rev
            self.breaking_change_dicts.append(breaking_change_dict)

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

        # タグへの差分確認用リンクの追加
        tag_pattern: str = r"^#{1,2} (v\d?.\d?.\d?.*) \(.*\)"  # `## v0.0.0 (yyyy-mm-dd)`
        tags: list[str] = re.findall(tag_pattern, full_changelog, re.MULTILINE)
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

        # 破壊的変更へのコミット確認用リンクの追加
        for breaking_change_dict in self.breaking_change_dicts:
            breaking_change_message: str = breaking_change_dict["breaking_change_message"]
            long_commit_id: str = breaking_change_dict["commit_id"]
            short_commit_id: str = long_commit_id[:7]
            repo_commit_url: str = self.github_repo.get_commit_url(long_commit_id)
            breaking_change_message_with_link: str = (
                f"{breaking_change_message} ([{short_commit_id}]({repo_commit_url}))"
            )
            full_changelog = re.sub(
                rf"{breaking_change_message}$",
                breaking_change_message_with_link,
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

    def get_commit_url(self, commit_id: str) -> str:
        return f"{self.url}/commit/{commit_id}"

    def get_tag_url(self, tag: str) -> str:
        return f"{self.url}/releases/tag/{tag}"

    def get_diff_url(self, tag1: str, tag2: str) -> str:
        return f"{self.url}/compare/{tag1}...{tag2}"

    def get_issue_url(self, issue_id_without_sharp: str) -> str:
        return f"{self.url}/issues/{issue_id_without_sharp}"
