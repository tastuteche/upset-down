import git


def get_git_info(path):
    info = {}

    git_repo = git.Repo(path, search_parent_directories=True)
    info["git_root"] = git_repo.git.rev_parse("--show-toplevel")

    origin = git_repo.remotes.origin
    if origin.urls:
        urls = list(origin.urls)
        if len(urls) > 0:
            info["git_url"] = urls[0]
    return info


if __name__ == "__main__":
    print(get_git_info("."))
