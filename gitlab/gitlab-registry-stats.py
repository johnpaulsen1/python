#!/usr/bin/env python3

import os
import json
import argparse
import math

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


BASE_DIR = '/opt/git-registry/docker/registry/v2'

print("Getting All Repository Projects:")
for proj in listAllRepositoryProjects(BASE_DIR):
    revs = listProjectRevisions(proj)
    tags = listProjectTags(proj)
    currentRevs = list(map(lambda x: x['current'], tags))
    orphanedRevs = list(filter(lambda x: x not in currentRevs, revs))
    totalSize = 0
    orphanedTotalSize = 0

    for rev in revs:
        revSize = getRevisionSize(BASE_DIR, rev)
        totalSize += revSize
        if rev not in currentRevs:
            orphanedTotalSize += revSize

    print(">> {}: \n {} revisions, \n {} orphaned revisions, \n {} tags, \n {} total size, \n {} orphans size)".format(
        proj,
        len(revs),
        len(orphanedRevs),
        len(tags),
        convertSize(totalSize),
        convertSize(orphanedTotalSize)
        ))
    print("*"*50)
