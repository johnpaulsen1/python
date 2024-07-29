#!/usr/bin/python3

import os
from . import os_commands

standard_dir = "/opt/flask/python-scripts/flasks/penguins_master"

def initialize(branch,gitdir):
    print(f"{os.getcwd()}")
    os.chdir(gitdir)
    print(f"{os.getcwd()}")
    print("Creating new branch...")
    try:
        checkout_master_cmd = "/bin/git checkout master"
        os_commands.getOScmdOutput(checkout_master_cmd)
    except Exception:
        print("checkout error")
        raise
    try:
        pull_latest = "/bin/git pull origin master"
        os_commands.getOScmdOutput(pull_latest)
    except Exception:
        print("unable to pull latest branch")
        raise

    try:
        create_new_branch = "/bin/git checkout -b {}".format(branch)
        os_commands.getOScmdOutput(create_new_branch)
        print("{} has been created...".format(branch))
    except Exception:
        print("unable to create new branch: {}".format(branch))
        raise

def pushup(branch,gitdir):
    os.chdir(gitdir)
    addfiles = "/bin/git add ."
    commit_file = "/bin/git commit -am \"{}\"".format(branch)
    push_MR = "/bin/git push origin {}".format(branch)
    print("Adding files to git")
    try:
        print(os_commands.getOScmdOutput(addfiles))
    except Exception:
        print("unable to add files to git.")
    print("Committing files")
    try:
        print(os_commands.getOScmdOutput(commit_file))
    except Exception:
        print("unable to commit. (not a new problem...)")
    print("Pushing changes...")
    try:
        os_commands.getOScmdOutput(push_MR)
    except Exception:
        print("unable to push up to git.")

    os.chdir(standard_dir)
