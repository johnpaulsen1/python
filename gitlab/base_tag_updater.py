#!/usr/bin/python3

import gitlab
import os, sys, subprocess, shlex
from os import listdir
from termcolor import cprint

os.system('clear')

# base variables
gitUrl = 'https://<git URL>'
gitAuthTokenName = 'my_git_auth_token'
yourFnum = os.environ['my_fnum']
myAuthToken = os.environ[gitAuthTokenName]
ourGroup = 'automators'
fnbBaseWrapperProject = 'fnb_base_wrapper'
fnbBaseWrapperProjectNamespace = ourGroup+'/'+fnbBaseWrapperProject
mrTitleFilter = 'update_base_tag'
developBranch = 'develop'
certFile = os.environ['fnb_ca_cert_file']
developPolicyfilesBaseLocation = os.environ['dev_chef_policy_files_location']
masterPolicyfilesBaseLocation = os.environ['prod_chef_policy_files_location']
mergeConflictString = 'Merge conflict in'
beginningOfOldCodeForMergeConflict = '<<<<<<< HEAD'
endOfOldCodeForMergeConflict = '======='
endOfNewCodeForMergeConflict = '>>>>>>>'
policyFileName = 'Policyfile.rb'
baseWrapperCookbookCodeSnippet = "cookbook 'fnb_base_wrapper', git: 'git@<git URL>:automators/fnb_base_wrapper.git', tag:"
hashes = '#'*100
stars = '*'*100
smallStars = '*'*41
dashes = '-'*100
menuOptions = {
    1: "DEVELOP - Deploy new base tag to ALL BU Policyfiles.",
    2: "DEVELOP - Deploy new base tag to SPECIFIC BU Policyfiles.",
    3: "MASTER - Deploy new base tag to ALL BU Policyfiles.",
    4: "MASTER - Deploy new base tag to SPECIFIC BU Policyfiles.",
    5: "View ALL OPEN 'update base tag' MR's.",
    6: "View DEVELOP OPEN 'update base tag' MR's.",
    7: "View MASTER OPEN 'update base tag' MR's.",
    8: "Merge ALL open 'update base tag' MR's.",
    9: "Merge DEVELOP open 'update base tag' MR's.",
    10: "Merge MASTER open 'update base tag' MR's."
}

cprint(smallStars + ' Base Tag Updater ' + smallStars, 'blue', attrs=['bold'])


def establish_git_connection(gitUrl, myAuthToken, certFile):
    cprint('establishing connection to gitlab server:', 'cyan')
    cprint(gitUrl, 'cyan')
    print()
    cprint('please wait a couple seconds while it auths you...', 'cyan')

    try:
        gl = gitlab.Gitlab(gitUrl, private_token=myAuthToken, ssl_verify=certFile)
    except KeyboardInterrupt as ki:
        cprint('User initiated a Keyboard Interrupt...', 'red')
        cprint('Quiting Base Tag Updater tool', 'red')
        sys.exit()
    except Exception as e:
        cprint('Error encountered...', 'red')
        cprint(str(e), 'red', attrs=['bold'])

    if gl:
        cprint('successfully authenticated and connected to git url: ' + gitUrl, 'green')

    return gl


def get_gl_objects(gitUrl, myAuthToken, certFile):

    glObjectsList = []

    gl = establish_git_connection(gitUrl, myAuthToken, certFile)
    glObjectsList.append(gl)

    print()
    cprint('Getting MR\'s, Please wait a couple seconds...', 'cyan')
    group = gl.groups.get(ourGroup)
    groupMrs = group.mergerequests.list(all=True, state='opened', order_by='updated_at')
    glObjectsList.append(groupMrs)

    return glObjectsList


def display_menu(menuOptions):
    try:
        while True:
            cprint(dashes, 'blue')
            cprint('Please select what you would like to do.', 'blue')
            for key, value in menuOptions.items():
                cprint(str(key) + ': '+ value, 'blue')
            cprint(dashes, 'blue')
            print()
            cprint('type in just the number of the option you want.', 'magenta')
            cprint('i.e.', 'magenta')
            cprint('1', 'magenta')
            cprint(dashes, 'blue')
            print()
            userOption = input()
            if int(userOption) in menuOptions.keys():
                print()
                cprint('you opted for:', 'blue')
                cprint(dashes, 'blue')
                cprint(menuOptions[int(userOption)], 'blue')
                cprint(dashes, 'blue')
                print()
                cprint('are you sure?', 'magenta')
                cprint('y | n:', 'magenta')
                cprint(dashes, 'blue')
                print()
                userSure = input()

                if userSure == 'y' or userSure == 'Y':
                    return int(userOption)
                    break;
            else:
                os.system('clear')
                cprint('invalid option selected, please try again...', 'yellow')
                print()
    except KeyboardInterrupt as ki:
        cprint('User initiated a Keyboard Interrupt...', 'red')
        cprint('Quiting Base Tag Updater tool', 'red')
        sys.exit()
    except Exception as e:
        cprint('Error encountered...', 'red')
        cprint(str(e), 'red', attrs=['bold'])


def getOScmdOutput(cmd):
	cmd_args = shlex.split(cmd)
	exec_cmd = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	raw_output = exec_cmd.communicate()[0]
	output = raw_output.decode("utf-8")
	return output.strip()


def view_update_base_tag_mrs(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, viewWhat):
    print()
    cprint(dashes, 'cyan', attrs=['bold'])
    cprint(menuOptions[userOption], 'cyan', attrs=['bold'])
    cprint(dashes, 'cyan', attrs=['bold'])
    print()

    glObjectsList = get_gl_objects(gitUrl, myAuthToken, certFile)

    gl = glObjectsList[0]
    groupMrs = glObjectsList[1]
    mrFound = False
    numMRs = len(groupMrs)

    if numMRs == 0:
        cprint('No MR\'s in group: ' + ourGroup, 'yellow')

    numMRsMatchFilter = 0
    for groupMr in groupMrs:
        if groupMr.state == 'opened' and mrTitleFilter in groupMr.title:
            numMRsMatchFilter += 1

    cprint('\'' + str(numMRsMatchFilter) + '\' MR\'s found that match filter:', 'magenta', attrs=['bold'])
    cprint('MR state = \'opened\' && \''+ mrTitleFilter +'\' in MR title.', 'magenta')

    if viewWhat == 'all':
        pass
    elif viewWhat == 'develop':
        targetBranch = viewWhat
    elif viewWhat == 'master':
        targetBranch = viewWhat
    else:
        pass

    for groupMr in groupMrs:
        if viewWhat != 'all':
            if groupMr.state == 'opened' and mrTitleFilter in groupMr.title and groupMr.target_branch == targetBranch:
                mrFound = True
                project = gl.projects.get(groupMr.project_id, lazy=True)
                thisMR = project.mergerequests.get(groupMr.iid)
                mrObjectWithChanges = thisMR.changes()
                mrChanges = mrObjectWithChanges['changes']

                cprint(stars, 'blue', attrs=['bold'])
                cprint('MR repo: ' + str(mrObjectWithChanges['references']['full'].split('!')[0]), 'cyan')
                cprint('MR URL: ' + str(mrObjectWithChanges['web_url']), 'cyan')
                cprint('MR WIP: ' + str(mrObjectWithChanges['work_in_progress']), 'cyan')
                cprint('MR title: ' + str(mrObjectWithChanges['title']), 'cyan')
                cprint('MR state: ' + str(mrObjectWithChanges['state']), 'cyan')
                cprint('MR created by: ' + str(mrObjectWithChanges['author']['name']), 'cyan')
                cprint('MR source branch: ' + str(mrObjectWithChanges['source_branch']), 'cyan')
                cprint('MR target branch: ' + str(mrObjectWithChanges['target_branch']), 'cyan')
                cprint('MR labels: ' + str(mrObjectWithChanges['labels']), 'cyan')
                cprint('MR squash commits: ' + str(mrObjectWithChanges['squash']), 'cyan')
                cprint('MR force delete source branch: ' + str(mrObjectWithChanges['force_remove_source_branch']), 'cyan')

                try:
                    if str(mrObjectWithChanges['pipeline']['status']) == 'success':
                        cprint('MR pipeline status: ' + str(mrObjectWithChanges['pipeline']['status']), 'green')
                    elif str(mrObjectWithChanges['pipeline']['status']) == 'running':
                        cprint('MR pipeline status: ' + str(mrObjectWithChanges['pipeline']['status']), 'yellow')
                    else:
                        cprint('MR pipeline status: ' + str(mrObjectWithChanges['pipeline']['status']), 'red')
                except Exception as e:
                    cprint('MR pipeline status: ' + 'unable to determine', 'red')

                try:
                    if str(mrObjectWithChanges['merge_status']) == 'can_be_merged':
                        cprint('MR merge status: ' + str(mrObjectWithChanges['merge_status']), 'green')
                    elif str(mrObjectWithChanges['merge_status']) == 'checking':
                        cprint('MR merge status: ' + str(mrObjectWithChanges['merge_status']), 'yellow')
                    else:
                        cprint('MR merge status: ' + str(mrObjectWithChanges['merge_status']), 'red')
                except Exception as e:
                    cprint('MR merge status: ' + 'unable to determine', 'red')

                cprint('MR has conflicts?: ' + str(mrObjectWithChanges['has_conflicts']), 'cyan')
                cprint('MR changes count: ' + str(mrObjectWithChanges['changes_count']), 'cyan')
                cprint('MR changes: ', 'cyan', attrs=['bold'])
                for mrChange in mrChanges:
                    cprint(hashes, 'cyan', attrs=['bold'])
                    if mrChange['renamed_file'] == True:
                        cprint('\t file RENAME detected...', 'cyan')
                        cprint('\t old file name: ' + str(mrChange['old_path']), 'cyan')
                        cprint('\t new file name: ' + str(mrChange['new_path']), 'cyan')
                        cprint(dashes, 'cyan')
                        cprint('\t' + str(mrChange['diff'].replace('\n','\n\t')), 'cyan')
                        cprint(hashes, 'cyan', attrs=['bold'])
                        print()
                    elif mrChange['new_file'] == True:
                        cprint('\t new file being CREATED detected...', 'cyan')
                        cprint('\t new file name:' + str(mrChange['new_path']), 'cyan')
                        cprint(dashes, 'cyan')
                        cprint('\t' + str(mrChange['diff'].replace('\n','\n\t')), 'cyan')
                        cprint(hashes, 'cyan', attrs=['bold'])
                        print()
                    elif mrChange['deleted_file'] == True:
                        cprint('\t file being DELETED detected...', 'cyan')
                        cprint('\t file name:' + str(mrChange['old_path']), 'cyan')
                        cprint(dashes, 'cyan')
                        cprint('\t' + str(mrChange['diff'].replace('\n','\n\t')), 'cyan')
                        cprint(hashes, 'cyan', attrs=['bold'])
                        print()
                    else:
                        cprint('\t file being updated:' + str(mrChange['new_path']), 'cyan')
                        cprint(dashes, 'cyan')
                        cprint('\t' + str(mrChange['diff'].replace('\n','\n\t')), 'cyan')
                        cprint(hashes, 'cyan', attrs=['bold'])
                        print()
        else:
            if groupMr.state == 'opened' and mrTitleFilter in groupMr.title:
                mrFound = True
                project = gl.projects.get(groupMr.project_id, lazy=True)
                thisMR = project.mergerequests.get(groupMr.iid)
                mrObjectWithChanges = thisMR.changes()
                mrChanges = mrObjectWithChanges['changes']

                cprint(stars, 'blue', attrs=['bold'])
                cprint('MR repo: ' + str(mrObjectWithChanges['references']['full'].split('!')[0]), 'cyan')
                cprint('MR URL: ' + str(mrObjectWithChanges['web_url']), 'cyan')
                cprint('MR WIP: ' + str(mrObjectWithChanges['work_in_progress']), 'cyan')
                cprint('MR title: ' + str(mrObjectWithChanges['title']), 'cyan')
                cprint('MR state: ' + str(mrObjectWithChanges['state']), 'cyan')
                cprint('MR created by: ' + str(mrObjectWithChanges['author']['name']), 'cyan')
                cprint('MR source branch: ' + str(mrObjectWithChanges['source_branch']), 'cyan')
                cprint('MR target branch: ' + str(mrObjectWithChanges['target_branch']), 'cyan')
                cprint('MR labels: ' + str(mrObjectWithChanges['labels']), 'cyan')
                cprint('MR squash commits: ' + str(mrObjectWithChanges['squash']), 'cyan')
                cprint('MR force delete source branch: ' + str(mrObjectWithChanges['force_remove_source_branch']), 'cyan')

                try:
                    if str(mrObjectWithChanges['pipeline']['status']) == 'success':
                        cprint('MR pipeline status: ' + str(mrObjectWithChanges['pipeline']['status']), 'green')
                    elif str(mrObjectWithChanges['pipeline']['status']) == 'running':
                        cprint('MR pipeline status: ' + str(mrObjectWithChanges['pipeline']['status']), 'yellow')
                    else:
                        cprint('MR pipeline status: ' + str(mrObjectWithChanges['pipeline']['status']), 'red')
                except Exception as e:
                    cprint('MR pipeline status: ' + 'unable to determine', 'red')

                try:
                    if str(mrObjectWithChanges['merge_status']) == 'can_be_merged':
                        cprint('MR merge status: ' + str(mrObjectWithChanges['merge_status']), 'green')
                    elif str(mrObjectWithChanges['merge_status']) == 'checking':
                        cprint('MR merge status: ' + str(mrObjectWithChanges['merge_status']), 'yellow')
                    else:
                        cprint('MR merge status: ' + str(mrObjectWithChanges['merge_status']), 'red')
                except Exception as e:
                    cprint('MR merge status: ' + 'unable to determine', 'red')

                cprint('MR has conflicts?: ' + str(mrObjectWithChanges['has_conflicts']), 'cyan')
                cprint('MR changes count: ' + str(mrObjectWithChanges['changes_count']), 'cyan')
                cprint('MR changes: ', 'cyan', attrs=['bold'])
                for mrChange in mrChanges:
                    cprint(hashes, 'cyan', attrs=['bold'])
                    if mrChange['renamed_file'] == True:
                        cprint('\t file RENAME detected...', 'cyan')
                        cprint('\t old file name: ' + str(mrChange['old_path']), 'cyan')
                        cprint('\t new file name: ' + str(mrChange['new_path']), 'cyan')
                        cprint(dashes, 'cyan')
                        cprint('\t' + str(mrChange['diff'].replace('\n','\n\t')), 'cyan')
                        cprint(hashes, 'cyan', attrs=['bold'])
                        print()
                    elif mrChange['new_file'] == True:
                        cprint('\t new file being CREATED detected...', 'cyan')
                        cprint('\t new file name:' + str(mrChange['new_path']), 'cyan')
                        cprint(dashes, 'cyan')
                        cprint('\t' + str(mrChange['diff'].replace('\n','\n\t')), 'cyan')
                        cprint(hashes, 'cyan', attrs=['bold'])
                        print()
                    elif mrChange['deleted_file'] == True:
                        cprint('\t file being DELETED detected...', 'cyan')
                        cprint('\t file name:' + str(mrChange['old_path']), 'cyan')
                        cprint(dashes, 'cyan')
                        cprint('\t' + str(mrChange['diff'].replace('\n','\n\t')), 'cyan')
                        cprint(hashes, 'cyan', attrs=['bold'])
                        print()
                    else:
                        cprint('\t file being updated:' + str(mrChange['new_path']), 'cyan')
                        cprint(dashes, 'cyan')
                        cprint('\t' + str(mrChange['diff'].replace('\n','\n\t')), 'cyan')
                        cprint(hashes, 'cyan', attrs=['bold'])
                        print()
    if viewWhat != 'all':
        if mrFound == False:
            cprint('No \'open\' MR\'s that match our title filter: \'' + mrTitleFilter + '\' and taget branch: \''+ targetBranch +'\' found in group: \'' + ourGroup + '\'', 'yellow')
    else:
        if mrFound == False:
            cprint('No \'open\' MR\'s that match our title filter: \'' + mrTitleFilter + '\' found in group: \'' + ourGroup + '\'', 'yellow')


def merge_update_base_tag_mrs(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, mergeWhat):
    print()
    cprint(dashes, 'cyan', attrs=['bold'])
    cprint(menuOptions[userOption], 'cyan', attrs=['bold'])
    cprint(dashes, 'cyan', attrs=['bold'])
    print()

    glObjectsList = get_gl_objects(gitUrl, myAuthToken, certFile)

    gl = glObjectsList[0]
    groupMrs = glObjectsList[1]
    mrFound = False
    numMRs = len(groupMrs)

    if numMRs == 0:
        cprint('No MR\'s in group: ' + ourGroup, 'yellow')

    numMRsMatchFilter = 0
    for groupMr in groupMrs:
        if groupMr.state == 'opened' and mrTitleFilter in groupMr.title:
            numMRsMatchFilter += 1

    cprint('\'' + str(numMRsMatchFilter) + '\' MR\'s found that match filter:', 'magenta', attrs=['bold'])
    cprint('MR state = \'opened\' && \''+ mrTitleFilter +'\' in MR title.', 'magenta')

    if mergeWhat == 'all':
        pass
    elif mergeWhat == 'develop':
        targetBranch = mergeWhat
    elif mergeWhat == 'master':
        targetBranch = mergeWhat
    else:
        pass

    for groupMr in groupMrs:
        if mergeWhat != 'all':
            if groupMr.state == 'opened' and mrTitleFilter in groupMr.title and groupMr.target_branch == targetBranch:
                mrFound = True
                project = gl.projects.get(groupMr.project_id, lazy=True)
                thisMR = project.mergerequests.get(groupMr.iid)

                print()
                cprint(stars, 'cyan', attrs=['bold'])
                print()
                cprint('attempting to merge MR:', 'cyan')
                cprint('MR URL: ' + str(thisMR.web_url), 'cyan')
                cprint('MR repo: ' + str(thisMR.references['full'].split('!')[0]), 'cyan')
                cprint('MR title: ' + str(thisMR.title), 'cyan')
                cprint('MR target branch: ' + str(thisMR.target_branch), 'cyan')

                if str(thisMR.pipeline['status']) == 'success':
                    cprint('MR pipeline status: ' + str(thisMR.pipeline['status']), 'green')
                elif str(thisMR.pipeline['status']) == 'running':
                    cprint('MR pipeline status: ' + str(thisMR.pipeline['status']), 'yellow')
                else:
                    cprint('MR pipeline status: ' + str(thisMR.pipeline['status']), 'red')

                if str(thisMR.merge_status) == 'can_be_merged':
                    cprint('MR merge status: ' + str(thisMR.merge_status), 'green')
                elif str(thisMR.merge_status) == 'checking':
                    cprint('MR merge status: ' + str(thisMR.merge_status), 'yellow')
                else:
                    cprint('MR merge status: ' + str(thisMR.merge_status), 'red')
                print()

                if thisMR.merge_status == 'can_be_merged' and thisMR.pipeline['status'] == 'success':
                    try:
                        thisMR.approve()
                        thisMR.merge()
                    except Exception as e:
                        cprint('Error encountered...', 'red')
                        cprint(str(e), 'red', attrs=['bold'])
                        if 'Unauthorized' in str(e):
                            cprint('You CAN NOT merge your own MR...', 'red')

                if thisMR.state == 'merged':
                    cprint('MR SUCCESSFULLY merged...', 'green')
        else:
            if groupMr.state == 'opened' and mrTitleFilter in groupMr.title:
                mrFound = True
                project = gl.projects.get(groupMr.project_id, lazy=True)
                thisMR = project.mergerequests.get(groupMr.iid)

                print()
                cprint(stars, 'cyan', attrs=['bold'])
                print()
                cprint('attempting to merge MR:', 'cyan')
                cprint('MR URL: ' + str(thisMR.web_url), 'cyan')
                cprint('MR repo: ' + str(thisMR.references['full'].split('!')[0]), 'cyan')
                cprint('MR title: ' + str(thisMR.title), 'cyan')
                cprint('MR target branch: ' + str(thisMR.target_branch), 'cyan')

                if str(thisMR.pipeline['status']) == 'success':
                    cprint('MR pipeline status: ' + str(thisMR.pipeline['status']), 'green')
                elif str(thisMR.pipeline['status']) == 'running':
                    cprint('MR pipeline status: ' + str(thisMR.pipeline['status']), 'yellow')
                else:
                    cprint('MR pipeline status: ' + str(thisMR.pipeline['status']), 'red')

                if str(thisMR.merge_status) == 'can_be_merged':
                    cprint('MR merge status: ' + str(thisMR.merge_status), 'green')
                elif str(thisMR.merge_status) == 'checking':
                    cprint('MR merge status: ' + str(thisMR.merge_status), 'yellow')
                else:
                    cprint('MR merge status: ' + str(thisMR.merge_status), 'red')
                print()

                if thisMR.merge_status == 'can_be_merged' and thisMR.pipeline['status'] == 'success':
                    try:
                        thisMR.approve()
                        thisMR.merge()
                    except Exception as e:
                        cprint('Error encountered...', 'red')
                        cprint(str(e), 'red', attrs=['bold'])
                        if 'Unauthorized' in str(e):
                            cprint('You CAN NOT merge your own MR...', 'red')

                if thisMR.state == 'merged':
                    cprint('MR SUCCESSFULLY merged...', 'green')

    if mergeWhat != 'all':
        if mrFound == False:
            cprint('No \'open\' MR\'s that match our title filter: \'' + mrTitleFilter + '\' and taget branch: \''+ targetBranch +'\' found in group: \'' + ourGroup + '\'', 'yellow')
    else:
        if mergeWhat == False:
            cprint('No \'open\' MR\'s that match our title filter: \'' + mrTitleFilter + '\' found in group: \'' + ourGroup + '\'', 'yellow')


def deploy_new_base_tag(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, targetBranch, buPolicyFileList, policyFilesBaseDir):
    print()
    cprint(dashes, 'cyan', attrs=['bold'])
    cprint(menuOptions[userOption], 'cyan', attrs=['bold'])
    cprint(dashes, 'cyan', attrs=['bold'])
    print()
    mrLabels = []

    if targetBranch == 'develop':
        mrLabels.append('Feature')
    elif targetBranch == 'master':
        mrLabels.append('Release')

    gl = establish_git_connection(gitUrl, myAuthToken, certFile)
    project = gl.projects.get(fnbBaseWrapperProjectNamespace)

    # get tags
    tags = project.tags.list()
    stringTagsList = []
    for tag in tags:
        tagName = tag.name
        stringTagsList.append(tagName)

    cprint('available tags for: ' + fnbBaseWrapperProjectNamespace, 'cyan', attrs=['bold'])

    while True:
        for stringTag in stringTagsList:
            cprint(stringTag, 'cyan')
        print()
        cprint('please select the NEW tag that you want to deploy.', 'magenta')
        print()
        userSelectedTag = input()
        if userSelectedTag not in stringTagsList:
            cprint('invalid tag selected... try again...', 'red', attrs=['bold'])
            print()
        else:
            break;

    print()
    cprint('updating base tag to: \'' + userSelectedTag + '\' for the below BU\'s:', 'cyan', attrs=['bold'])
    cprint(buPolicyFileList, 'cyan')

    if targetBranch == 'develop':
        for bu in buPolicyFileList:
            buProjectName = ourGroup+'/'+bu
            buProject = gl.projects.get(buProjectName)

            print()
            cprint(stars, 'cyan')
            cprint('attempting to update BU: \'' + bu + '\'', 'cyan')
            buPolicyFilesDir = policyFilesBaseDir + '/' + bu
            policyFileToUpdate = buPolicyFilesDir + '/' + policyFileName
            cprint('file: \'' + policyFileToUpdate + '\'', 'cyan')
            os.chdir(buPolicyFilesDir)
            os.system('git checkout ' + targetBranch)
            os.system('git pull origin ' + targetBranch)

            # Read in the file
            file = open(policyFileToUpdate, 'r')
            lines = file.readlines()

            newLinesList = []

            for line in lines:
                if baseWrapperCookbookCodeSnippet not in line:
                    newLinesList.append(line)
                elif baseWrapperCookbookCodeSnippet in line:
                    removedOldTagLine = line.split('tag:')[0]
                    newTagLine = removedOldTagLine + 'tag: ' + '\'' + userSelectedTag + '\'\n'
                    newLinesList.append(newTagLine)

            file.close()

            if len(newLinesList) > 0:
                file = open(policyFileToUpdate, 'w')
                file.writelines(newLinesList)
                cprint('file: \'' + policyFileToUpdate + '\' SUCCESSFULLY updated.', 'green')
                file .close()

            print()
            # push up git changes
            gitBranchName = yourFnum + '_' + mrTitleFilter + '_' + userSelectedTag + '_' + targetBranch
            os.system('git checkout -b ' + gitBranchName)
            os.system('git commit -am ' + gitBranchName)
            os.system('git push origin ' + gitBranchName)

            mr = buProject.mergerequests.create({'source_branch': gitBranchName,
                                       'target_branch': targetBranch,
                                       'title': gitBranchName,
                                       'labels': mrLabels,
                                       'remove_source_branch': True,
                                       'squash': True
                                       })
            if mr:
                print()
                cprint('MR SUCCESSFULLY created.', 'green')
                cprint('MR URL: ' + mr.web_url, 'cyan')

                # give gitlab chance to create pipelines
                print()
                # pipelines
                cprint('waiting for MR pipelines...', 'cyan')
                os.system('sleep 6')
                mrProjectObject = gl.projects.get(mr.project_id, lazy=True)

                # this gets the pipelines associated to the MR
                mrPipelines = mrProjectObject.pipelines.list(sha=str(mr.diff_refs['head_sha']))

                for mrPipeline in mrPipelines:
                    if mrPipeline.ref == gitBranchName:
                        cprint('cancelling non-detached pipeline.', 'magenta')
                        mrPipeline.cancel()
                        os.system('sleep 5')
                        mrPipelinesCheck = mrProjectObject.pipelines.list(sha=str(mr.diff_refs['head_sha']))
                        for mrPipelineCheck in mrPipelinesCheck:
                            if mrPipelineCheck.status == 'canceled':
                                cprint('SUCCESSFULLY canceled non-detached pipeline', 'green')
                print()


    elif targetBranch == 'master':
        for bu in buPolicyFileList:
            buProjectName = ourGroup+'/'+bu
            buProject = gl.projects.get(buProjectName)
            gitBranchName = yourFnum + '_' + mrTitleFilter + '_' + userSelectedTag + '_' + targetBranch

            print()
            cprint(stars, 'cyan')
            cprint('attempting to update BU: \'' + bu + '\'', 'cyan')
            buPolicyFilesDir = policyFilesBaseDir + '/' + bu
            os.chdir(buPolicyFilesDir)
            os.system('git checkout ' + targetBranch)
            os.system('git pull origin ' + targetBranch)
            os.system('git checkout -b ' + gitBranchName)
            pullDevelopCmd = 'git pull origin ' + developBranch
            pullDevelopOutput = getOScmdOutput(pullDevelopCmd)
            pullDevelopOutputLines = pullDevelopOutput.split('\n')
            mergeConflictFiles = []

            # get files that have a merge conflict:
            for line in pullDevelopOutputLines:
                if mergeConflictString in line:
                    splitLineToList = line.split(' ')
                    fileWithConflict = splitLineToList[-1]
                    mergeConflictFiles.append(fileWithConflict)

            cprint('files with merge conflicts:', 'yellow')
            for conflictFile in mergeConflictFiles:
                conflictFileToUpdate = buPolicyFilesDir + '/' + conflictFile
                cprint(conflictFileToUpdate, 'yellow')

                file = open(conflictFileToUpdate, 'r')
                lines = file.readlines()
                newLinesList = []

                cprint('Updating file to keep LATEST updates.', 'cyan')

                writeFlag = True
                for line in lines:
                    if line.startswith(beginningOfOldCodeForMergeConflict):
                        writeFlag = False
                    if writeFlag:
                        if line.startswith(endOfNewCodeForMergeConflict):
                            pass
                        else:
                            newLinesList.append(line)
                    if line.startswith(endOfOldCodeForMergeConflict):
                        writeFlag = True

                file.close()

                if len(newLinesList) > 0:
                    file = open(conflictFileToUpdate, 'w')
                    file.writelines(newLinesList)
                    cprint('file: \'' + conflictFileToUpdate + '\' SUCCESSFULLY updated.', 'green')
                    file .close()

            print()
            # push up git changes
            os.system('git commit -am ' + gitBranchName)
            os.system('git push origin ' + gitBranchName)

            mr = buProject.mergerequests.create({'source_branch': gitBranchName,
                                       'target_branch': targetBranch,
                                       'title': gitBranchName,
                                       'labels': mrLabels,
                                       'remove_source_branch': True,
                                       'squash': True
                                       })
            if mr:
                print()
                cprint('MR SUCCESSFULLY created.', 'green')
                cprint('MR URL: ' + mr.web_url, 'cyan')

                # give gitlab chance to create pipelines
                print()
                # pipelines
                cprint('waiting for MR pipelines...', 'cyan')
                os.system('sleep 6')
                mrProjectObject = gl.projects.get(mr.project_id, lazy=True)

                # this gets the pipelines associated to the MR
                mrPipelines = mrProjectObject.pipelines.list(sha=str(mr.diff_refs['head_sha']))

                for mrPipeline in mrPipelines:
                    if mrPipeline.ref == gitBranchName:
                        cprint('cancelling non-detached pipeline.', 'magenta')
                        mrPipeline.cancel()
                        os.system('sleep 5')
                        mrPipelinesCheck = mrProjectObject.pipelines.list(sha=str(mr.diff_refs['head_sha']))
                        for mrPipelineCheck in mrPipelinesCheck:
                            if mrPipelineCheck.status == 'canceled':
                                cprint('SUCCESSFULLY canceled non-detached pipeline', 'green')
                print()


# run the scripty...
userOption = display_menu(menuOptions)

if userOption == 1:
    targetBranch = 'develop'
    policyFilesBaseDir = developPolicyfilesBaseLocation
    buPolicyFileList = listdir(policyFilesBaseDir)
    deploy_new_base_tag(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, targetBranch, buPolicyFileList, policyFilesBaseDir)

elif userOption == 2:
    targetBranch = 'develop'
    policyFilesBaseDir = developPolicyfilesBaseLocation
    # get all projects in our group: 'ourGroup'
    gl = establish_git_connection(gitUrl, myAuthToken, certFile)

    cprint('getting valid projects for group: \'' + ourGroup + '\', please wait a couple seconds.', 'cyan')
    group = gl.groups.get(ourGroup)
    projects = group.projects.list(all=True)
    txtProjectsList = []
    for project in projects:
        txtProjectsList.append(project.name)

    selectedBUFailure = False
    while True:
        print()
        cprint('Please enter in ONLY the name/s of the BU project you want to the base tag for.', 'magenta')
        cprint('i.e.', 'magenta')
        cprint('iss', 'magenta')
        cprint('If you want to update multiple BU\'s, please enter each of them separated by a comma.', 'magenta')
        cprint('i.e.', 'magenta')
        cprint('iss, fx, mer', 'magenta')
        print()
        buPolicyFileList = []
        userSpecificBUListStr = input()

        if ',' in userSpecificBUListStr:
            for thisSpecificBU in userSpecificBUListStr.split(','):
                buPolicyFileList.append(thisSpecificBU.replace(' ', ''))
        else:
            buPolicyFileList.append(userSpecificBUListStr.replace(' ', ''))

        for userSpecificBU in buPolicyFileList:
            if userSpecificBU not in txtProjectsList:
                selectedBUFailure = True
                cprint('your selected BU: \'' + userSpecificBU + '\' is not a valid project in the \'' + ourGroup + '\' group.', 'red', attrs=['bold'])
                cprint('try again...', 'red')
            else:
                selectedBUFailure = False

        if selectedBUFailure == False:
            break

    deploy_new_base_tag(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, targetBranch, buPolicyFileList, policyFilesBaseDir)

elif userOption == 3:
    targetBranch = 'master'
    policyFilesBaseDir = masterPolicyfilesBaseLocation
    buPolicyFileList = listdir(policyFilesBaseDir)
    deploy_new_base_tag(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, targetBranch, buPolicyFileList, policyFilesBaseDir)

elif userOption == 4:
    targetBranch = 'master'
    policyFilesBaseDir = masterPolicyfilesBaseLocation
    # get all projects in our group: 'ourGroup'
    gl = establish_git_connection(gitUrl, myAuthToken, certFile)

    cprint('getting valid projects for group: \'' + ourGroup + '\', please wait a couple seconds.', 'cyan')
    group = gl.groups.get(ourGroup)
    projects = group.projects.list(all=True)
    txtProjectsList = []
    for project in projects:
        txtProjectsList.append(project.name)

    selectedBUFailure = False
    while True:
        print()
        cprint('Please enter in ONLY the name/s of the BU project you want to the base tag for.', 'magenta')
        cprint('i.e.', 'magenta')
        cprint('iss', 'magenta')
        cprint('If you want to update multiple BU\'s, please enter each of them separated by a comma.', 'magenta')
        cprint('i.e.', 'magenta')
        cprint('iss, fx, mer', 'magenta')
        print()
        buPolicyFileList = []
        userSpecificBUListStr = input()

        if ',' in userSpecificBUListStr:
            for thisSpecificBU in userSpecificBUListStr.split(','):
                buPolicyFileList.append(thisSpecificBU.replace(' ', ''))
        else:
            buPolicyFileList.append(userSpecificBUListStr.replace(' ', ''))

        for userSpecificBU in buPolicyFileList:
            if userSpecificBU not in txtProjectsList:
                selectedBUFailure = True
                cprint('your selected BU: \'' + userSpecificBU + '\' is not a valid project in the \'' + ourGroup + '\' group.', 'red', attrs=['bold'])
                cprint('try again...', 'red')
            else:
                selectedBUFailure = False

        if selectedBUFailure == False:
            break

    deploy_new_base_tag(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, targetBranch, buPolicyFileList, policyFilesBaseDir)

elif userOption == 5:
    viewWhat = 'all'
    view_update_base_tag_mrs(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, viewWhat)

elif userOption == 6:
    viewWhat = 'develop'
    view_update_base_tag_mrs(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, viewWhat)

elif userOption == 7:
    viewWhat = 'master'
    view_update_base_tag_mrs(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, viewWhat)

elif userOption == 8:
    mergeWhat = 'all'
    merge_update_base_tag_mrs(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, mergeWhat)

elif userOption == 9:
    mergeWhat = 'develop'
    merge_update_base_tag_mrs(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, mergeWhat)

elif userOption == 10:
    mergeWhat = 'master'
    merge_update_base_tag_mrs(gitUrl, myAuthToken, certFile, menuOptions, userOption, mrTitleFilter, mergeWhat)

else:
    cprint('invalid option...', 'red', attrs=['bold'])
    cprint('re-run the script...', 'red', attrs=['bold'])
    sys.exit()
