from commitizen import git
from commitizen.cz.conventional_commits.conventional_commits import ConventionalCommitsCz


class CustomCommitsCz(ConventionalCommitsCz):
    def changelog_message_builder_hook(self, parsed_message: dict, commit: git.GitCommit) -> dict:
        rev = commit.rev
        short_rev = rev[:7]
        message = parsed_message["message"]
        parsed_message["message"] = f"{message} ({short_rev})"
        return parsed_message
