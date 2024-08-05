## Python Flask - Pengiuns Tools  

### What is it for?
This bit of the python-scripts repo stores the code for our Python tools flask site.
Which is used for iDigi-Tech Linux tools and automation.

### How does authentication on the site work?
You need to hit URL: https://<flask server URL> and that will direct you to a login prompt.

There you will need to enter your fnum and AD password.

The site will check against our AD servers, at "ldaps://<ldap server>:636"

If your credentials are successfully authenticated, the site will then check the AD Groups that you're apart of and if the user logging in is one of the groups in our allowed list, see file: ./flasks/penguins_master/penguins/static/auth/allowed_ad_groups for list of AD groups that have been allowed to access our site.
This AD Group checking is done with the Flask AD service account `service account`.

#### Authentication errors and what they mean:
- `your account is locked`:
  You will be prompted to vists the AD AD self-service site to unlock your account.
- `username / password mismatch` / `your credentials are invalid`:
  This means that username and password entered does match what is on AD, you'll need to try again.
  If this error persists, please ask the developer to check further for you on this error.
- `can't find user`:
  The username used to try login with does not exist in AD.
  You'll need to try again.
- `AD server unavailable`:
  The AD server: **<AD server>** used to authenticate against is unavailable. Check with the AD Team regarding the status of that AD loadbalancer.
- `You've lost connectivity to the LDAP server`:
  Your connection to the AD server: **<AD server>** has been lost, and you'll be prompted to log off of the site and re-login, to establish your connection to the AD server: **f<AD server>**.
- `permission denied for user`:
  The user attempting to login to our site, is not in one of the AD Groups that we've allowed to login to our site.
  Which is kept in and referred to in file: **flasks/penguins_master/penguins/static/auth/allowed_ad_groups**.

#### Managing access to the site:
Firstly you'll need to make sure that you have pulled this repo down to your local PC / wherever you keep and manage your git repos.

Access to this site is granted to AD Groups.

And the allowed AD Groups are stored in the below file:

`flasks/penguins_master/penguins/static/auth/allowed_ad_groups`

You can either add / remove an AD group, depending on whether you're grating / revoking access.

Once that file has been updated with your new updates, you'll then need to submit an new MR, and get someone with merge access to review your MR.

The person reviewer / merging your MR, once happy and has merged MR, needs to then pull the new updates to server: **lnx-rbflask** using the user: **flask** in the location of this git repo **/opt/flask/python-scripts** and then restart (`sudo systemctl restart penguins.service`) the service running this site, in order for the updates to take effect.


### What is currently working?  
The deployment scripts. Run this on blank hosts. It will run the following roles against the host:
- ldap querying:
  - user details
  - what AD groups a user is in
  - what users reside in an AD group
  - check which users have a `unix-` group
  - check lock status of a user
- cmdb:
  - search:
    - host name
    - BU
    - cost centre
    - company code
    - server role
    - host type
    - architecture
    - OS family
    - OS version
    - IP address
  - show latest
  - download latest
- Decommission Servers:
  - Will check the server/s architecture (VM / Physical / zLinux)
    - If VM, it will:
      - look in which VC it resides.
      - create a delete folder, if it doesn't exist already.
      - move into the delete folder.
      - power it down.
      - disable it's NIC. (this functionality has temp be disabled).
    - if Physical / zLinux, it will just power down the server.
  - Will deactivate node on puppet (<puppet ca>).
  - Will revoke puppet certificate (<puppet proxy>).
  - Will delete server out of satellite
- useful links:
  a bunch of links useful to the team, all kept in one handy location.

### Future plans:
- revamp and streamline decommission automation.
- include other Infra teams functions in the decomm process.
