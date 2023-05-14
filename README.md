# commitizen-cz-custom-commits <!-- omit in toc -->

- [1. 概要](#1-概要)
- [2. インストール方法](#2-インストール方法)
- [3. ツール実行方法](#3-ツール実行方法)
- [4. 参考URL](#4-参考url)

## 1. 概要

変更履歴を下記ツールで自動生成する際に使用するコミットルール。

- [commitizen-tools/commitizen - GitHub](https://github.com/commitizen-tools/commitizen)

## 2. インストール方法

まずは`poetry`(パッケージ管理ツール)をインストールする。

```bash
$ python3 --version
Python 3.10.10

$ pipx install poetry
(省略)

$ poetry --version
Poetry (version 1.4.1)

$ poetry config virtualenvs.in-project true
```

次に本リポジトリを使用して変更履歴を生成したいプロジェクトの`pyproject.toml`に設定を追加する。
また、本ツールに関係ない設定に関しては省略している。

```bash
$ cat pyproject.toml
[tool.poetry.group.dev.dependencies]
commitizen = "^3.2.1"
commitizen-cz-custom-commits = {path = "../commitizen-cz-custom-commits", develop = true}

[tool.commitizen]
name = "cz_custom_commits"
version_provider = "poetry"
tag_format = "v$version"
update_changelog_on_bump = true
bump_message = "chore: bump from $current_version to $new_version"
changelog_file = "CHANGELOG.md"
# major_version_zero = true # for initial development
version_type = "semver"
github_repo_owner = "<リポジトリ所有者>"
github_repo_name = "<リポジトリ名>"
```

## 3. ツール実行方法

次に`commitizen`を実行する。
バージョンはコミットログに基づいて自動計算される。

```bash
$ poetry run cz bump
chore: bump from 0.0.0 to 1.0.0
tag to create: v1.0.0
increment detected: MAJOR

[main 95a1fa6] chore: bump from 0.0.0 to 1.0.0
 2 files changed, 25 insertions(+), 2 deletions(-)

Done!
```

## 4. 参考URL

- [commitizen-tools/commitizen - GitHub](https://github.com/commitizen-tools/commitizen)
- [Commitizen documentation](https://commitizen-tools.github.io/commitizen/)
