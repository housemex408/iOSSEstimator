import subprocess
import os
import argparse
import sys as sys
sys.path.append(os.path.abspath(__file__))
import Utilities as utils
import Constants as c

parser = argparse.ArgumentParser(description='Github Repo ETL')
parser.add_argument("--p")
args = parser.parse_args()
key = args.p[1:]
repo = key.split('/')[1]
# repo = "angular"

# get list of tags
workingDirectory = "../{repo}".format(repo = repo)
outputDirectory = "../iROIEstimatorMetrics/{repo}".format(repo = repo)
tempDirectory = "{outputDirectory}/temp".format(outputDirectory = outputDirectory)
versionsFile = "{outputDirectory}/{repo}_versions.csv".format(outputDirectory = outputDirectory, repo = repo)
commitsFile = "{outputDirectory}/{repo}_all_commits.csv".format(outputDirectory = outputDirectory, repo = repo)
versionMetricsFile = "{outputDirectory}/{repo}_version_metrics.csv".format(outputDirectory = outputDirectory, repo = repo)
versionCommitsFile = "{outputDirectory}/{repo}_version_commits.csv".format(outputDirectory = outputDirectory, repo = repo)
versionCommitsMsgFile = "{outputDirectory}/{repo}_version_commits_msg.csv".format(outputDirectory = outputDirectory, repo = repo)

def create_directory(name):
  try:
    os.mkdir(name)
  except OSError as error:
      print(error)

create_directory(outputDirectory)
create_directory(tempDirectory)

#get all versions
versions = open(versionsFile, "w")
header = 'Key,Version,Date\n'
versions.write(header)
versions.close()
getTags = "git for-each-ref --format '%(refname:lstrip=2) %(creatordate:short)' refs/tags  --sort=creatordate | awk 'BEGIN {{OFS=\",\";}} {{print \"{key}\", $1, $2}}' >> {versionsFile}".format(key = key, versionsFile = versionsFile)
process = subprocess.run([getTags], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)
msg = process.stderr.strip()
print(msg)

tags = open(versionsFile, 'r')
data_analysis = open(versionMetricsFile, "w")
header = 'Key,Version,NT,NO,E_Module,E_Line,T_Module,T_Line,Date'
data_analysis.write(header)

versionCommits = open(versionCommitsFile, "w")
header = 'Key,Version,SHA,E_Module,E_Line\n'
versionCommits.write(header)
versionCommits.close()

versionCommitsMsg = open(versionCommitsMsgFile, "w")
header = 'Key,Version,SHA,Message\n'
versionCommitsMsg.write(header)
versionCommitsMsg.close()

class Tag(object):
    def __init__(self, row):
      self.version = row[1].strip()
      self.release_date = row[2].strip()
      self.print_template = 'Version: {version}, Release Date: {release_date}'
    def print(self):
        msg = self.print_template.format(version=self.version, release_date=self.release_date)
        print(msg)

seperator = ","

# skip the header line
tags.readline()
fromTag = Tag(tags.readline().split(seperator))
toTag = Tag(tags.readline().split(seperator))

fromTag.print()
toTag.print()

while True:
    toVersion = toTag.version
    Release_Date = toTag.release_date
    fromVersion = fromTag.version

    versionRange = "'{fromV}'..'{toV}'".format(toV=toVersion, fromV=fromVersion)
    print(versionRange)

    changeLog = '{tempDirectory}/{repo}_{filename}_changelog.txt'.format(tempDirectory = tempDirectory, repo = repo, filename=toVersion)

    # Get the change log for the current versionRange
    getChangeLog = 'git log --pretty="%h - %s (%an)" {range} > {outputFile}'.format(range=versionRange, outputFile=changeLog)
    process = subprocess.run([getChangeLog], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)

    # get commits between two tags
    getVersionCommits = "git log {range} --pretty='@%H' --stat  | grep -v \| |  tr '\n' ' '  |  tr '@' '\n' | awk 'BEGIN {{OFS=\",\";}} {{print \"{key}\",\"{toVersion}\", $1, $2, $5 + $7}}' >> {versionCommitsFile}".format(range = versionRange, key = key, toVersion = toVersion, versionCommitsFile = versionCommitsFile)
    process = subprocess.run([getVersionCommits], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)

    # get commit messages between two tags
    getVersionCommitMsgs = "git log {range} --pretty='%H %f' | awk 'BEGIN {{OFS=\",\";}} {{print \"{key}\",\"{toVersion}\", $1, $2}}' >> {versionCommitsMsgFile}".format(range = versionRange, key = key, toVersion = toVersion, versionCommitsMsgFile = versionCommitsMsgFile)
    process = subprocess.run([getVersionCommitMsgs], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)

    # Get corrective tasks
    getNT = 'grep -Ec "fix|bug|defect" {outputFile}'.format(outputFile=changeLog)

    #print(getCorrectiveTasks)

    process = subprocess.run([getNT], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    NT = process.stdout.strip()
    msg = 'NT: {NT}'.format(NT=NT)
    print(msg)

    # Get other tasks
    getNO = 'grep -Ecv "fix|bug|defect" {outputFile}'.format(outputFile=changeLog)

    #print(getOtherTasks)

    process = subprocess.run([getNO], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    NO = process.stdout.strip()
    msg = 'NO: {NO}'.format(NO=NO)
    print(msg)

    # Get files modified / added / deleted
    getEModule = "git diff --shortstat " + versionRange + " | awk '{print $1}'"

    #print(getEModule)

    process = subprocess.run([getEModule], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)
    E_Module = process.stdout.strip()
    msg = 'E_Module: {E_Module}'.format(E_Module=E_Module)
    print(msg)

    # Get LOC modified / added / deleted
    getELine = "git diff --shortstat " + versionRange + " | awk '{print $4 + $6}'"

    #print(getELine)

    process = subprocess.run([getELine], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)
    E_Line = process.stdout.strip()
    msg = 'E_Line: {E_Line}'.format(E_Line=E_Line)
    print(msg)

    # Checkout tags/toVersion
    checkoutTag = "git checkout tags/" + toVersion + " --force"
    print(checkoutTag)
    process = subprocess.run([checkoutTag], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)
    print(process.stdout.strip())

    # Get total files up to this version
    getTotalFiles = "git ls-files --exclude-standard | wc -l | awk '{print $1 }'"
    process = subprocess.run([getTotalFiles], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)
    T_Module = process.stdout.strip()
    msg = 'T_Module: {T_Module}'.format(T_Module=T_Module)
    print(msg)

    # Get total LOC up to this version
    getTotalLOC = "git grep ^ | wc -l | awk '{print $1 }'"
    process = subprocess.run([getTotalLOC], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=workingDirectory)
    T_Line = process.stdout.strip()
    msg = 'T_Line: {T_Line}'.format(T_Line=T_Line)
    print(msg)

    # Create a line item
    template = '\n{key},{toVersion},{NT},{NO},{E_Module},{E_Line},{T_Module},{T_Line},{Release_Date}'
    line = template.format(key=key,toVersion=toVersion, NT=NT, NO=NO, E_Module=E_Module, E_Line=E_Line, T_Module=T_Module, T_Line=T_Line, Release_Date=Release_Date)
    data_analysis.write(line)
    print(line)

    fromTag = toTag
    nextLine = tags.readline()

    if not nextLine:
        break

    toTag = Tag(nextLine.split(seperator))

tags.close()
data_analysis.close()

