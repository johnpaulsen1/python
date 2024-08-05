#!/usr/bin/python3

import gitlab
import os, sys, subprocess, shlex
from os import listdir
from termcolor import cprint

os.system('clear')

# base variables

# get branch name from develop MR that was merged.
# CI_COMMIT_TITLE
gitCommitTitleList = list()
gitCommitTitleList.append(sys.argv[1])
gitCommitTitleList.append(sys.argv[2])
gitCommitTitleList.append(sys.argv[3])
gitCommitTitleList.append(sys.argv[4])
gitCommitTitleList.append(sys.argv[5])
print('gitCommitTitle: ' + str(gitCommitTitleList))

# gitCommitTitle = "Merge branch 'f3669076_testing_pipelines8' into 'develop'"
developMRBranch = gitCommitTitleList[2].strip("'")
# developMRBranch = 'f3669076_testing_MR'
print('developMRBranch: ' + developMRBranch)

# get the name of the repo where we doing the merginess...
# CI_PROJECT_NAME
gitRepo = sys.argv[6]
# gitRepo = 'test_gitlab_api'
print('gitRepo: ' + gitRepo)

# get the repo url in case we need to clone it
# CI_REPOSITORY_URL
# gitRepoUrl = sys.argv[7]
# gitRepoUrl = 'git@<git URL>:automators/test_gitlab_api.git'
# print('gitRepoUrl: ' + gitRepoUrl)

# get the git user
# GITLAB_USER_LOGIN
gitCommitAuthor = sys.argv[7]
# gitCommitAuthor = 'jpaulsen'
print('gitCommitAuthor: ' + gitCommitAuthor)

masterMRBranch = developMRBranch + '_master'
gitServer = '<git URL>'
gitUrl = 'https://'+gitServer

baseGitDir = '/opt/gitlab-runner/git_repos'

# svc for git auth
gitAuthTokenName = 'my_git_auth_token'
gitAuthToken = os.environ[gitAuthTokenName]

gitAutomatorsGroup = 'automators'

developBranch = 'develop'
masterBranch = 'master'

certFile = 'not_ever.crt'

mergeConflictString = 'Merge conflict in'
beginningOfOldCodeForMergeConflict = '<<<<<<< HEAD'
endOfOldCodeForMergeConflict = '======='
endOfNewCodeForMergeConflict = '>>>>>>>'

hashes = '#'*100
stars = '*'*100
smallStars = '*'*41
dashes = '-'*100

def establish_git_connection(gitUrl, gitAuthToken, certFile):
    cprint('establishing connection to gitlab server:', 'cyan')
    cprint(gitUrl, 'cyan')
    print()
    cprint('please wait a couple seconds while being authenticated...', 'cyan')

    try:
        gl = gitlab.Gitlab(gitUrl, private_token=gitAuthToken, ssl_verify=certFile)
    except KeyboardInterrupt as ki:
        cprint('User initiated a Keyboard Interrupt...', 'red')
        cprint('Quiting Base Tag Updater tool', 'red')
        sys.exit()
    except Exception as e:
        cprint('Error encountered...', 'red')
        cprint('Exception:', 'red')
        cprint(str(e), 'red', attrs=['bold'])

    if gl:
        cprint('successfully authenticated and connected to git url: ' + gitUrl, 'green')

    return gl


def getOScmdOutput(cmd):
	cmd_args = shlex.split(cmd)
	exec_cmd = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	raw_output = exec_cmd.communicate()[0]
	output = raw_output.decode("utf-8")
	return output.strip()


def create_master_mr(gitUrl, gitRepo, gitAuthToken, certFile, mrBranchName, targetBranch, gitCommitAuthor):
    print()
    cprint(dashes, 'cyan', attrs=['bold'])
    cprint('Method to create master MR by pulling develop branch', 'cyan', attrs=['bold'])
    cprint(dashes, 'cyan', attrs=['bold'])
    print()
    gitBranchObjects = list()
    gitBranches = list()
    gitProjectNamespace = gitAutomatorsGroup+'/'+gitRepo

    gl = establish_git_connection(gitUrl, gitAuthToken, certFile)
    print()

    try:
        gitProject = gl.projects.get(gitProjectNamespace)
    except Exception as e:
        cprint('Failed to get git project namespace object for repo: \'{}\''.format(gitRepo), 'red')
        cprint('Exception:', 'red')
        cprint(str(e), 'red', attrs=['bold'])
        gitProject = None
    

    if targetBranch == 'master':

        mrLabel = 'Release'
        activeMRFound = False
        gitRepoUrl = 'git@{}:{}/{}.git'.format(gitServer, gitAutomatorsGroup, gitRepo)

        # check if MR / branch exists on gitlab
        cprint('checking if there is an existing MR open for branch: \''+ mrBranchName +'\' on gitlab.', 'cyan')

        try:
            activeMRs = gitProject.mergerequests.list(state='opened')
        except Exception as e:
            cprint('Failed to find active MRs on git project: \'{}\''.format(gitRepo), 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])
            activeMRs = list()
        
        if len(activeMRs) > 0:
            for activeMR in activeMRs:
                if activeMR.source_branch == mrBranchName:
                    cprint('branch: \'{}\' already has an active MR on gitlab, attempting to close it, to be re-created.'.format(mrBranchName), 'yellow')
                    try:
                        activeMR.state_event = 'close'
                        activeMR.save()
                        cprint('active MR for branch: \'{}\' SUCCESSFULLY closed'.format(mrBranchName), 'green')
                        activeMRFound = True
                        break
                    except Exception as e:
                        cprint('Failed to close active MR for branch: \'{}\' on git project: \'{}\''.format(mrBranchName, gitRepo), 'red')
                        cprint('Exception:', 'red')
                        cprint(str(e), 'red', attrs=['bold'])
                        activeMR = None
                    break
                
        if activeMRFound == False:
            cprint('NO active MR found for branch: \'{}\' in project: \'{}\' on gitlab.'.format(mrBranchName, gitRepo), 'green')
                    
        print()

        cprint('checking if branch: \''+ mrBranchName +'\' exists on gitlab.', 'cyan')
        try:
            gitBranchObjects = gitProject.branches.list()
        except Exception as e:
            cprint('Failed to get branches for git project: \'{}\''.format(gitRepo), 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])
        
        if len(gitBranchObjects) > 0:
            for gitBranchObject in gitBranchObjects:
                gitBranches.append(gitBranchObject.name)
            
            if mrBranchName in gitBranches:
                cprint('branch: \'{}\' already exists on gitlab, attempting to delete it, to be re-created.'.format(mrBranchName), 'yellow')
                try:
                    gitProject.branches.delete(mrBranchName)
                    cprint('branch: \'{}\' SUCCESSFULLY removed from gitlab'.format(mrBranchName), 'green')
                except Exception as e:
                    cprint('Failed to delete branch: \'{}\''.format(gitRepo), 'red')
                    cprint('Exception:', 'red')
                    cprint(str(e), 'red', attrs=['bold'])
            else:
                cprint('branch: \'{}\' does not exist in project: \'{}\' on gitlab.'.format(mrBranchName, gitRepo), 'green')
        print()

        # git repos locally
        # check if repo exists locally
        cprint('checking if repo directory: \''+ gitRepo +'\' exists locally.', 'cyan')

        os.chdir(baseGitDir)
        if os.path.exists(gitRepo):
            cprint("repo dir: '{}' exists locally, no need to pull it down.".format(gitRepo), 'green')
        else:
            cprint("repo dir: '{}' DOES NOT exist, need to pull it down.".format(gitRepo), 'yellow')
            try:
                os.system('git clone ' + gitRepoUrl + ' --quiet')
                cprint("repo: '{}' SUCCESSFULLY cloned.".format(gitRepo), 'green')
            except Exception as e:
                cprint('FAILED to clone repo:\'\''.format(gitRepo), 'red')
                cprint('Exception:', 'red')
                cprint(str(e), 'red', attrs=['bold'])
                exitCode = 1
        
        print()
        repoDir = baseGitDir+'/'+gitRepo

        # change into git repo dir
        os.chdir(repoDir)

        # switch to target branch first...
        cprint('checking out target branch: \''+ targetBranch +'\'.', 'cyan')
        try:
            os.system('git checkout ' + targetBranch)
        except Exception as e:
            cprint('Failed to checkout target branch: \'{}\''.format(targetBranch), 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])
        print()

        # check if branch exists locally
        cprint('checking if branch: \''+ mrBranchName +'\' exists locally.', 'cyan')
        try:
            checkBranchCmd = os.system('git branch | grep ' + mrBranchName + '> /dev/null')
            exitCode = os.WEXITSTATUS(checkBranchCmd)
        except Exception as e:
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])
            exitCode = 1

        if exitCode == 0:
            # delete local branch
            try:
                os.system('git branch -D ' + mrBranchName)
            except Exception as e:
                cprint('Failed to delete local git branch: \'{}\''.format(mrBranchName), 'red')
                cprint('Exception:', 'red')
                cprint(str(e), 'red', attrs=['bold'])
        else:
            cprint('branch: \'{}\' does not exist locally.'.format(mrBranchName), 'green')

        
        print()
        cprint(stars, 'cyan')
        cprint('attempting to create MR: \''+ mrBranchName +'\' for repo: \'' + gitRepo + '\'', 'cyan')

        # checkout master, to pull latest
        os.system('git checkout ' + targetBranch)

        # set git merge conf
        os.system('git config pull.rebase false')

        # pull latest from master
        try:
            os.system('git pull origin ' + targetBranch + ' --quiet')
        except Exception as e:
            cprint('Failed to pull branch: \'{}\''.format(targetBranch), 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])

        # create new branch to be merged into master
        try:
            os.system('git checkout -b ' + mrBranchName)
        except Exception as e:
            cprint('Failed to checkout new branch: \'{}\''.format(mrBranchName), 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])
        

        # fetch develop
        cprint('fetching branch: \''+ developBranch +'\'', 'cyan')
        try:
            os.system('git fetch origin ' + developBranch)
            cprint('branch: \''+ developBranch +'\' fetch successful', 'green')
        except Exception as e:
            cprint('Failed to fetch branch: \'{}\''.format(developBranch), 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])

        # fix merge conflicts, if any.
        cprint('attempting to fix merge conflicts, if any', 'cyan')
        try:
            os.system('git merge -s recursive -X theirs origin/' + developBranch)
            cprint('merge conflicts sorted.', 'green')
        except Exception as e:
            cprint('Failed to fix merge conflicts', 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])
            
        # pullDevelopCmd = 'git pull origin ' + developBranch
        # try:
        #     pullDevelopOutput = getOScmdOutput(pullDevelopCmd)
        # except Exception as e:
        #     cprint('Failed to pull branch: \'{}\''.format(developBranch), 'red')
        #     cprint('Exception:', 'red')
        #     cprint(str(e), 'red', attrs=['bold'])
        #     pullDevelopOutput = None
        
        # if pullDevelopOutput is not None:
        #     pullDevelopOutputLines = pullDevelopOutput.split('\n')
        #     mergeConflictFiles = []
        #     mergeConflictFound = False

        #     # get files that have a merge conflict:
        #     for line in pullDevelopOutputLines:
        #         if mergeConflictString in line:
        #             splitLineToList = line.split(' ')
        #             fileWithConflict = splitLineToList[-1]
        #             mergeConflictFiles.append(fileWithConflict)
        #             mergeConflictFound = True

        #     if mergeConflictFound:
        #         cprint('files with merge conflicts:', 'yellow')

        #     for conflictFile in mergeConflictFiles:
        #         conflictFileToUpdate = repoDir + '/' + conflictFile
        #         cprint(conflictFileToUpdate, 'yellow')

        #         file = open(conflictFileToUpdate, 'r')
        #         lines = file.readlines()
        #         newLinesList = []

        #         cprint('Updating file to keep LATEST updates.', 'cyan')

        #         writeFlag = True
        #         for line in lines:
        #             if line.startswith(beginningOfOldCodeForMergeConflict):
        #                 writeFlag = False
        #             if writeFlag:
        #                 if line.startswith(endOfNewCodeForMergeConflict):
        #                     pass
        #                 else:
        #                     newLinesList.append(line)
        #             if line.startswith(endOfOldCodeForMergeConflict):
        #                 writeFlag = True

        #         file.close()

        #         if len(newLinesList) > 0:
        #             file = open(conflictFileToUpdate, 'w')
        #             file.writelines(newLinesList)
        #             cprint('file: \'' + conflictFileToUpdate + '\' SUCCESSFULLY updated.', 'green')
        #             file .close()

        print()
        # push up git changes
        try:
            os.system('git commit -am ' + mrBranchName + ' --quiet')
        except Exception as e:
            cprint('Failed to commit branch: \'{}\''.format(mrBranchName), 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])
        
        try:
            os.system('git push origin ' + mrBranchName + ' --quiet')
        except Exception as e:
            cprint('Failed to push branch: \'{}\' up to gitlab'.format(mrBranchName), 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])
        

        try:
            mr = gitProject.mergerequests.create({'source_branch': mrBranchName,
                                        'target_branch': targetBranch,
                                        'title': mrBranchName,
                                        'author[username]': gitCommitAuthor,
                                        'labels': mrLabel,
                                        'remove_source_branch': True,
                                        'squash': True
                                        })
        except Exception as e:
            cprint('Failed to create MR', 'red')
            cprint('Exception:', 'red')
            cprint(str(e), 'red', attrs=['bold'])

        if mr:
            print()
            cprint('MR SUCCESSFULLY created.', 'green', attrs=['bold'])
            cprint('MR URL: ' + mr.web_url, 'cyan', attrs=['bold'])
            print()
    print()

    # change back to safe dir:
    os.chdir(baseGitDir)


def cleanUpPostCreate(gitRepo, mrBranchName, targetBranch):
    print()
    cprint(dashes, 'cyan', attrs=['bold'])
    cprint('Method to cleanup post MR creation.', 'cyan', attrs=['bold'])
    cprint(dashes, 'cyan', attrs=['bold'])
    print()

    repoDir = baseGitDir+'/'+gitRepo

    # change into git repo dir
    os.chdir(repoDir)

    # first change to target branch
    cprint('checking out target branch: \''+ targetBranch +'\'.', 'cyan')
    try:
        os.system('git checkout ' + targetBranch)
    except Exception as e:
        cprint('Failed to checkout target branch: \'{}\''.format(targetBranch), 'red')
        cprint('Exception:', 'red')
        cprint(str(e), 'red', attrs=['bold'])
    
    # check if branch exists locally
    cprint('attempting to delete local branch: \''+ mrBranchName +'\'.', 'cyan')
    try:
        os.system('git branch -D ' + mrBranchName)
        cprint('local branch: \''+ mrBranchName +'\' SUCCESSFULLY deleted.', 'green')
    except Exception as e:
        cprint('Failed to delete local git branch: \'{}\''.format(mrBranchName), 'red')
        cprint('Exception:', 'red')
        cprint(str(e), 'red', attrs=['bold'])
    print()

    # checkout target branch locally
    cprint('checking out target branch: \''+ targetBranch +'\'.', 'cyan')
    try:
        os.system('git checkout ' + targetBranch)
        cprint('branch: \''+ targetBranch +'\' SUCCESSFULLY checked out.', 'green')
    except Exception as e:
        cprint('Failed to checkout target branch: \'{}\''.format(targetBranch), 'red')
        cprint('Exception:', 'red')
        cprint(str(e), 'red', attrs=['bold'])
    print()

    # change back to safe dir:
    os.chdir(baseGitDir)


# run the scripty...

create_master_mr(gitUrl, gitRepo, gitAuthToken, certFile, masterMRBranch, masterBranch, gitCommitAuthor)
cleanUpPostCreate(gitRepo, masterMRBranch, masterBranch)
