#!/bin/bash
# Record a deployment to Heroku

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -e  # Exit on non-zero status from command
set -u  # Unset variables are error
set -o pipefail  # Fail on non-zero exit in a pipe
IFS=$'\n\t'  # Stricter for loops

# Defaults from environment
API_KEY=${NEW_RELIC_API_KEY:-}
APP_ID=${NEW_RELIC_DEPLOY_APP_ID:-}
BRANCH=${NEW_RELIC_BRANCH:-remotes/browsercompat/master}
DEPLOY_USER=${NEW_RELIC_DEPLOYER:-}
FAKE=0

usage () {
  local errnum=${1:-0}
  echo "Record a deployment in New Relic. Usage:"
  echo "${0##/} [-a APP_NAME] [-b BRANCH] [-i APP_ID] [-k API_KEY] [-u USER] [-f]"
  echo " -b BRANCH - Branch that was deployed (default remotes/browsercompat/master)"
  echo " -i APP_ID - The New Relic app ID (default \$NEW_RELIC_DEPLOY_APP_ID)"
  echo " -k API_KEY - The New Relic API key (default \$NEW_RELIC_API_KEY)"
  echo " -u USER - The deployment user (default is commit author)"
  echo " -f - Fake deployment (dry run)"
  exit $errnum
}

while getopts "b:i:k:u:f" opt; do
    case $opt in
        b)
            BRANCH="$OPTARG"
            ;;
        i)
            APP_ID="$OPTARG"
            ;;
        f)
            FAKE=1
            ;;
        k)
            API_KEY="$OPTARG"
            ;;
        u)
            DEPLOY_USER="$OPTARG"
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage 1
            ;;
    esac
done

FAILED=0
if [ -z "$API_KEY" ]; then
    echo "** Must set API key"
    FAILED=1
fi

if [ -z "$APP_ID" ]; then
    echo "** Must set app ID"
    FAILED=1
fi

if [ $FAILED -ne 0 ]; then
    usage $FAILED
fi

DESCRIPTION=`git log $BRANCH -n1 --pretty=format:%s`
REVISION=`git log $BRANCH -n1 --pretty=format:%H`

if [ -z ${DEPLOY_USER:-} ]; then
    DEPLOY_USER=`git log $BRANCH -n1 --pretty=format:%an`
fi

if [ $FAKE -eq 0 ]; then
    curl -H "x-api-key:$API_KEY" \
        -d "deployment[application_id]=$APP_ID" \
        -d "deployment[user]=$DEPLOY_USER" \
        -d "deployment[revision]=$REVISION" \
        -d "deployment[description]=$DESCRIPTION" \
        https://api.newrelic.com/deployments.xml -v
else
    echo curl -H "x-api-key:$API_KEY" \
        -d "deployment[application_id]=$APP_ID" \
        -d "deployment[user]=$DEPLOY_USER" \
        -d "deployment[revision]=$REVISION" \
        -d "deployment[description]=$DESCRIPTION" \
        https://api.newrelic.com/deployments.xml -v
fi
