# README - AD query tool.
## What does it do?
1 of 4 things at this stage.
1. Returns set AD information for a given user / account.
2. Returns a list of groups that a given user / account has membership to.
3. Returns a list of members (users  / accounts) for a given group.
4. Checks if a given user / account is locked out or not.

## Things to know
- The script is written in python.
- OS package dependencies:
  - python3
  - openldap-devel
- python module dependencies:
  - python-ldap
  - termcolor

## How to?
The script resides on server: `<jump server>`.

Location: `/root/ldap_tool.py`.


When running the script, you'll first be prompted to authenticate on AD.

Once you've successfully authenticated, you will be presented with a menu that looks similar to the below:
```
Please select an option:
1. Get AD INFO for a specific user
2. Get list of Groups that a user is in
3. Get list of members for a specific Group
4. Check if a user is locked out
5. exit
enter in the no. only of the option:
```

As the prompt suggests, you need ONLY to enter in the **NUMBER** of the option you'd like to run.

eg. `1`

The menu will continue to loop until the executing user feels that they are done querying whatever info they needed, at which point the user can then enter in option `5` to `exit` the script.

