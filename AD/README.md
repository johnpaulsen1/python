# README - AD query tool.
## What does it do?
1 of 3 things at this stage.
1. Returns set AD information for a given user / account.
2. Returns a list of groups that a given user / account has membership to.
3. Returns a list of members (users  / accounts) for a given group.

## Things to know
- The script is written in python.
- OS package dependencies
  - Debian:
    - python3
    - python-dev-is-python3
    - ldap-utils
    - libldap-common
    - libldap-dev
    - libsasl2-dev
    - gcc
  - RHEL:
    - python3
    - python-devel
    - openldap-devel
    - cyrus-sasl-devel
    - gcc
- python module dependencies:
  - python-ldap
  - termcolor

## How to use it?
Run the script like: `./ldap_tool.py`.

When running the script, you'll first be prompted to authenticate on AD.
Use an AD Account that can authenticate to the ldap server defined in the script.

Once you've successfully authenticated, you will be presented with a menu that looks similar to the below:
```
Please select an option:
1. Get AD INFO for a specific user
2. Get list of Groups that a user is in
3. Get list of members for a specific Group
4. exit
enter in the no. only of the option:
```

As the prompt suggests, you need ONLY to enter in the **NUMBER** of the option you'd like to run.

eg. `1`

The menu will continue to loop until the executing user feels that they are done querying whatever info they needed, at which point the user can then enter in option `4` to `exit` the script.
