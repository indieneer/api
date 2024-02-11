#!/bin/bash

# TBD: description

set -o errexit
set -o nounset

# First, check for git in $PATH
hash git 2>/dev/null || { echo >&2 "Git required, not installed.  Aborting build number update script."; exit 0; }

# Use the latest tag for short version (expected tag format "n[.n[.n]]")
LATEST_TAG=$(git describe --tags --abbrev=0)
COMMIT_COUNT_SINCE_TAG=$(git rev-list --count ${LATEST_TAG}..)
if [ $LATEST_TAG = "start" ]
  then LATEST_TAG=0
fi
if [ $COMMIT_COUNT_SINCE_TAG = 0 ]; then
  SHORT_VERSION="$LATEST_TAG"
else
  # increment final digit of tag and append "d" + commit-count-since-tag
  # e.g. commit after 1.0 is 1.1d1, commit after 1.0.0 is 1.0.1d1
  # this is the bit that requires /bin/bash

  OLD_IFS=$IFS
  IFS="."
  VERSION_PARTS=($LATEST_TAG)
  LAST_PART=$((${#VERSION_PARTS[@]}-1))

  # at least temporarily, we disable the automatic increment of the last digit of the version
  # in the last tag.
  # as we are early in development/test, we are happy to upload an indeterminate number of builds
  # to the same version e.g. 0.1.1
  # this means that to change the short version you must create a new tag e.g. 0.1.2 or 0.2.0 after 0.1.1 etc
  # VERSION_PARTS[$LAST_PART]=$((${VERSION_PARTS[${LAST_PART}]}+1))

  # note that app store / testflight does not allow :CFBundleShortVersionString to be
  # anything other than x.y.z with x,y,z integers
  # so we are no longer appending the "d<commit count since last tag>"
  # SHORT_VERSION="${VERSION_PARTS[*]}d${COMMIT_COUNT_SINCE_TAG}"
  SHORT_VERSION="${VERSION_PARTS[*]}d${COMMIT_COUNT_SINCE_TAG}"
  IFS=$OLD_IFS
fi

# output
echo "SHORT_VERSION=$SHORT_VERSION" >> $GITHUB_OUTPUT

# For debugging:
echo "LATEST_TAG: $LATEST_TAG"
echo "COMMIT_COUNT_SINCE_TAG: $COMMIT_COUNT_SINCE_TAG"
echo "SHORT VERSION: $SHORT_VERSION"