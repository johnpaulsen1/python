## What do these python Modules do?
The main functions of the python modules in this project is find all gitlab revisions, their orphans and their respective sizes, from their the user can review the results and once happy, can run a clean.

The two modules are:
- gitlab-registery-stats.py
- gitlab-registery-cleaner.py

### gitlab-registery-stats.py
This must be run on the gitlab server, i.e. `<gitlab server>`.

It will look under the base git directory: `/opt/git-registry/docker/registry/v2`.

It will go through each project, recursively, looking for all revisions and tags under each project.
Once done gathering all of the above it will detemine the sizes of each revision, as well as which ones have been orphaned (it determines orphaned revisions if it does not exist in tags).

The data gathered with be displayed back the user, this module is to be run before the 'cleaner' module.

So as to make sure what will be cleaned.

Example of running this module:
```
./gitlab-registry-stats.py
```


### gitlab-registery-cleaner.py
This module works very much like ths stats module, also must be run on the gitlab server, i.e. `<git server>`.

And will also look under the base git directory: `/opt/git-registry/docker/registry/v2`.

The only difference with this module is that it will clean up each orphaned revision and any associated tags, as well as revisions older than the `'--keep <KEEP>'` number specified by the user, see below for details on that.

See below params to be parsed when running this module:
```
-h | --help                             -> shows help message and will exit.
-d | --dry-run                          -> Only displays (prints) back to the user what will be removed. (NOTHING is actually removed).
-k <KEEP> | --keep <KEEP>               -> Number of NEWEST revisions to keep, anything older, will be cleaned out.
-b <BASE_DIR> | --base-dir <BASE_DIR>   -> Base directory of gitlab registry (ending with registry/v2).
```

Example of running this module:
```
./gitlab-registry-cleaner.py -k 5 -b '/opt/git-registry/docker/registry/v2' --dry-run
```

So running like this, will keep the `5` newest revisions of each project, looking under base_dir: `'/opt/git-registry/docker/registry/v2'`, run ONLY as a `'--dry-run'` (so nothing will actually be deleted, it'll just show you what WOULD of been deleted, should the module have been run without the '--dry-run tag').

