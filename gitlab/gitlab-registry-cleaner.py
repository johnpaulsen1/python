#!/usr/bin/env python3
import os
import json
import argparse
import math
from datetime import datetime
import dateutil.parser
import time
import sys

def convertSize(size_bytes):
    if (size_bytes == 0):
        return '0B'
    size_name = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes/p, 2)
    return '{} {}'.format(s, size_name[i])

def listAllRepositoryProjects(BASE_DIR):
    projects = []
    layers_stop_dir = "_layers"
    uploads_stop_dir = "_uploads"
    manifest_stop_dir = "_manifests"

    # traverse base directory, and list directories as dirs
    for root, dirs, files in os.walk("{}/repositories".format(BASE_DIR)):
        if layers_stop_dir in dirs:
            dirs.remove(layers_stop_dir)
        if uploads_stop_dir in dirs:
            dirs.remove(uploads_stop_dir)
        if manifest_stop_dir in dirs:
            projects.append(root)
            dirs.remove(manifest_stop_dir)
    return projects

def listProjectRevisions(project):
    return os.listdir("{}/_manifests/revisions/sha256/".format(project))

def listProjectTags(project):
    tags = []
    tags_path = "{}/_manifests/tags".format(project)

    if os.path.exists(tags_path):
        for tag in os.listdir(tags_path):
            tagData = { 'name' : tag, 'revs' : [], 'current' : '' }

            tag_index_path = "{}/_manifests/tags/{}/index/sha256".format(project, tag)
            if os.path.exists(tag_index_path):
                for rev in os.listdir(tag_index_path):
                    tagData['revs'].append(rev)

            tag_link_path = "{}/_manifests/tags/{}/current/link".format(project, tag)
            if os.path.exists(tag_link_path):
                with open(tag_link_path, 'r') as cur:
                    tagData['current'] = cur.read().split(':')[1]
            tags.append(tagData)
    return tags

def getRevisionSize(BASE_DIR, revision):
    revision_data_path = "{}/blobs/sha256/{}/{}/data".format(BASE_DIR, revision[:2], revision)
    if not os.path.isfile(revision_data_path):
        return 0

    if os.path.exists(revision_data_path):
        with open(revision_data_path, 'r') as cur:
            revData = json.load(cur)
            size = 0
            if "layers" in revData:
                for l in revData['layers']:
                    size += l['size']

                size += revData['config']['size']
    return size

def timedelta_total_seconds(timedelta):
    timeDelta = ((timedelta.microseconds + 0.0 +
                    (timedelta.seconds + timedelta.days * 24 * 3600) *
                    10 ** 6) / 10 ** 6)
    return timeDelta

def getRevisionDate(BASE_DIR, revision):
    revision_data_path = "{}/blobs/sha256/{}/{}/data".format(BASE_DIR, revision[:2], revision)
    if not os.path.isfile(revision_data_path):
        return 0

    if os.path.exists(revision_data_path):
        with open(revision_data_path, 'r') as cur:
            revData = json.load(cur)
            if "config" in revData:
                confRevData = revData['config']
                if "digest" in confRevData:
                    config = revData['config']['digest'].split(':')[1]
                    revision_conf_data_path = "{}/blobs/sha256/{}/{}/data".format(BASE_DIR, config[:2], config)
                    if os.path.exists(revision_conf_data_path):
                        with open(revision_conf_data_path, 'r') as conf:
                            confData = json.load(conf)
                            revDate = timedelta_total_seconds(dateutil.parser.parse(confData['created']).replace(tzinfo=None) - datetime(1970, 1, 1))
                            return revDate
                    else:
                        return None
                else:
                    return None
            else:
                return None

def selector(x):
    return x[2]

def removeRevision(project, tag, revision):
    indexRevisionDir = "{}/_manifests/tags/{}/index/sha256/{}".format(project, tag, revision)
    indexRevisionFile = indexRevisionDir + "/link"
    tagDir = "{}/_manifests/tags/{}".format(project, tag)
    tagIndexDir = tagDir + "/index"
    tagCurrentDir = tagIndexDir + "/current"
    tagShaDir = tagIndexDir + "/sha256"
    tagFile = tagCurrentDir + "/link"
    revisionShaDir = "{}/_manifests/revisions/sha256/{}".format(project, revision)
    revisionShaLinkFile = revisionShaDir + "/link"

    tagDirLessIndex = tagDir + "/current"
    revisionFileLessIndex = tagDirLessIndex + "/link"

    if os.path.isfile(revisionFileLessIndex):
        try:
            os.remove(revisionFileLessIndex)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(revisionFileLessIndex, str(e)))

        try:
            os.rmdir(tagDirLessIndex)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(tagDirLessIndex, str(e)))

    if os.path.isfile(indexRevisionFile):
        try:
            os.remove(indexRevisionFile)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(indexRevisionFile, str(e)))

        try:
            os.rmdir(indexRevisionDir)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(indexRevisionDir, str(e)))


    if os.path.exists(tagDir):
        try:
            os.remove(tagFile)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(tagFile, str(e)))

        try:
            os.rmdir(tagShaDir)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(tagShaDir, str(e)))

        try:
            os.rmdir(tagIndexDir)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(tagIndexDir, str(e)))

        try:
            os.rmdir(tagCurrentDir)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(tagCurrentDir, str(e)))

        try:
            os.rmdir(tagDir)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(tagDir, str(e)))


    if os.path.isfile(revisionShaLinkFile):
        try:
            os.remove(revisionShaLinkFile)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(revisionShaLinkFile, str(e)))

        try:
            os.rmdir(revisionShaDir)
        except Exception as e:
            print("removal of: {}, failed with error: {}".format(revisionShaDir, str(e)))


    indexRevisionDirExists = os.path.exists(indexRevisionDir)
    tagDirExists = os.path.exists(tagDir)
    revisionShaDirExists = os.path.exists(revisionShaDir)

    print()
    if indexRevisionDirExists == False and tagDirExists == False and revisionShaDirExists == False:
        print("Tag: '{}' - Revision: '{}' successfully removed".format(tag, revision))
        print()


# BASE_DIR = '/opt/git-registry/docker/registry/v2'
# KEEP_COUNT=5
# DRY_RUN=True

parser = argparse.ArgumentParser(description="Clean gitlab registry tags by date they were created, keeps '-k | --keep' newest tags")
parser.add_argument('--dry-run', '-d', help='Only prints what will be removed',
                    dest='dry_run', action='store_true')
parser.add_argument('--keep', '-k', type=int,
                    help='Number of newest revisions to keep')
parser.add_argument('--base-dir', '-b',
                    help='Base directory of gitlab registry (ending with registry/v2')

try:
    parser.set_defaults(dry_run=DRY_RUN, keep=KEEP_COUNT, base_dir=BASE_DIR)
except:
    pass

args = parser.parse_args()
BASE_DIR = args.base_dir
KEEP_COUNT = args.keep
DRY_RUN = args.dry_run

if args.dry_run is None or args.keep is None:
    print("defaults not set, please run this progam with '-h' for a help guide.")
    print("i.e.")
    print(os.path.abspath(__file__), "-h")
    sys.exit(1)

if not os.path.isdir(str(BASE_DIR)) or BASE_DIR is None:
    print("Base directory: '{}' of gitlab registry DOES NOT EXISTS!".format(BASE_DIR))
    sys.exit(1)

print("Searching Through All Repository Projects...")
for proj in listAllRepositoryProjects(BASE_DIR):
    revs = listProjectRevisions(proj)
    tags = listProjectTags(proj)
    revsList = list()
    for tag in tags:
        for rev in tag['revs']:
            revsList.append([ tag['name'], rev, getRevisionDate(BASE_DIR, rev) ])
    revsList = list(reversed(sorted(revsList, key=selector)))

    print(">> Project: {} \n   ({} marked for removal out of {})".format(proj, max(0, len(revsList) - KEEP_COUNT), len(revsList)))

    for i in range(len(revsList)):
        tag, rev, created = revsList[i]
        if i < KEEP_COUNT and created != 0:
            if created is not None:
                print(">>> Kept Back: Tag: {} - Revision: {} (created on {})".format(tag, rev[:12], datetime.fromtimestamp(created).strftime("%d-%m-%Y")))
        else:
            if created is not None:
                print(">>> Marked for Removal: Tag: {} - Revision: {} (created on {})".format(tag, rev[:12], datetime.fromtimestamp(created).strftime("%d-%m-%Y")))
                if not DRY_RUN:
                    # print("...REMOVAL TIME...")
                    # time.sleep(2)
                    # print(";-)")
                    removeRevision(proj, tag, rev)
    print("*"*50)
    print()


if not DRY_RUN:
  print("!!!!! Please Run gitlab garbage collector !!!!!")
