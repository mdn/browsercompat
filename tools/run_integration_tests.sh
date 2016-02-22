#!/bin/bash
# Make requests against an API server for documentation, integration testing

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -e  # Exit on non-zero status from command
set -u  # Unset variables are error
set -o pipefail  # Fail on non-zero exit in a pipe
IFS=$'\n\t'  # Stricter for loops

# Debugging
# set -x  # Print trace of simple commands and their arguments
# set -v  # Print shell input lines as they are read

#
# Functions
#

# Display usage
REDIS_DB=7
usage () {
  local errnum=${1:-0}
  echo "Make requests against a local API server with known data. Usage:"
  echo "${0##/} [-g] [-h]"
  echo " -a - The API version (default v1)"
  echo " -c - Run with Celery and local Redis (database $REDIS_DB)."
  echo " -g - Generate documentation samples. If omitted, then tests"
  echo "      responses against documentation samples."
  echo " -h - This usage statement."
  echo " -q - Show less output."
  echo " -v - Show more output."
  exit $errnum
}


# Cleanup on exit
DJANGO_PID=
CELERY_PID=
DATABASE_NAME="integration.sqlite3"
cleanup_local () {
  echo "Cleaning up..."
  if [ ! -z $DJANGO_PID ]
  then
    echo "Killing Django ($DJANGO_PID)"
    kill -TERM $DJANGO_PID
    DJANGO_PID=
  fi
  if [ ! -z $CELERY_PID ]
  then
    echo "Killing Celery ($CELERY_PID)"
    kill -TERM $CELERY_PID
    CELERY_PID=
    echo "Flushing Redis DB $REDIS_DB"
    redis-cli -n $REDIS_DB flushdb
  fi
  rm -f $DATABASE_NAME
  echo "Done."
}
trap cleanup_local EXIT

# Generate a random string
gen_rand_string () {
    local length=$1
    if [ -z $length ]; then length=10; fi
    python -c "\
from __future__ import print_function;\
import string, random;\
chars = string.ascii_uppercase + string.ascii_lowercase + string.digits;\
print(''.join(random.SystemRandom().choice(chars) for _ in range($length)));\
"
}

# Create a Django user
create_user () {
    local username=$1
    local email=$2
    local password=$3
    local is_superuser=$4
    echo "\
from django.contrib.auth.models import User, Group;\
username='$username';
email='$email';\
password='$password';\
is_superuser=('$is_superuser' == '1');\
user = User(username=username, email=email, is_superuser=is_superuser, \
  is_staff=is_superuser);\
user.set_password(password);\
user.save();\
change_group = Group.objects.get(name='change-resource');\
delete_group = Group.objects.get(name='delete-resource');\
user.groups.add(change_group);\
user.groups.add(delete_group);\
" | python manage.py shell --plain
}

# Create an OAuth2 public implicit app and related token
create_oauth2_app_and_token () {
    local username=$1
    local app_name=$2
    local client_id=$3
    local client_secret=$4
    local token=$5
    local redirect_uris='http://localhost:8000/about/'
    local client_type='public'
    local authorization_grant_type='implicit'
    echo "\
from django.contrib.auth.models import User;\
from oauth2_provider.models import AccessToken, Application;\
from datetime import datetime, timedelta;\
username='$username';
app_name='$app_name';\
client_id='$client_id';\
client_secret='$client_secret';\
redirect_uris='$redirect_uris';\
client_type='$client_type';\
authorization_grant_type='$authorization_grant_type';\
token='$token';\
user = User.objects.get(username=username);\
assert user, 'User not found';\
expire_time=datetime.now() + timedelta(seconds=300);\
scope='read write';\
app = Application.objects.create(\
  user=user, client_id=client_id, client_secret=client_secret, \
  redirect_uris=redirect_uris, client_type=client_type, \
  authorization_grant_type=authorization_grant_type, \
  name=app_name, skip_authorization=True);\
access_token = AccessToken.objects.create(\
  user=user, token=token, application=app, expires=expire_time, scope=scope);\
" | python manage.py shell --plain
}

#
# Parse command line
#
DOC_MODE="verify"
API_VERSION="v1"
WITH_CELERY=0
VERBOSITY=1
API_VERSION="v1"
while getopts ":a:cghqv" opt; do
  case $opt in
    a)
      API_VERSION=$OPTARG
      DATABASE_NAME="integration-${API_VERSION}.sqlite3"
      ;;
    c)
      WITH_CELERY=1
      ;;
    g)
      DOC_MODE="generate"
      ;;
    h)
      usage
      ;;
    v)
      VERBOSITY=2
      ;;
    q)
      VERBOSITY=0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage 1
      ;;
  esac
done


#
# Script parameters
#
DOC_API_HOSTNAME="127.0.0.1:8081"
DOC_API_SCHEME="http"
DOC_API_URL="${DOC_API_SCHEME}://${DOC_API_HOSTNAME}"
DOC_USER_NAME=user
DOC_USER_PASSWORD=$(gen_rand_string 10)
DOC_USER_EMAIL="user@example.com"
DOC_APP_NAME="TestApp $(gen_rand_string 7)"
DOC_CLIENT_ID=$(gen_rand_string 10)
DOC_CLIENT_SECRET=$(gen_rand_string 20)
DOC_TOKEN=$(gen_rand_string 30)

#
# Setup the documentation database, server
#

# Change to project root
SCRIPT_DIR=`dirname "$BASH_SOURCE"`
cd "$SCRIPT_DIR/.."

# Set Django environment variables
export DATABASE_URL="sqlite:///$DATABASE_NAME"
unset MEMCACHE_SERVERS
if [ $WITH_CELERY -eq 0 ]; then
    unset REDIS_URL
    unset CELERY_RESULT_BACKEND
    unset BROKER_URL
    export CELERY_ALWAYS_EAGER=1
    export USE_CACHE=0
else
    REDIS_DB=7
    export REDIS_URL="redis://localhost/$REDIS_DB"
    export CELERY_RESULT_BACKEND=$REDIS_URL
    export BROKER_URL=$REDIS_URL
    export CELERY_ALWAYS_EAGER=0
    export USE_CACHE=1
    echo "Flushing Redis DB $REDIS_DB"
    redis-cli -n $REDIS_DB flushdb
fi

if [ $VERBOSITY -gt 1 ]; then
    export DJANGO_DEBUG=1
else
    export DJANGO_DEBUG=0
    export ALLOWED_HOSTS="*"
    export EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
fi

# Create an empty database
rm -f $DATABASE_NAME
python manage.py migrate --verbosity=$VERBOSITY --noinput

# Add the documentation user
create_user $DOC_USER_NAME $DOC_USER_EMAIL $DOC_USER_PASSWORD 0

# Generate an OAuth2 token
create_oauth2_app_and_token $DOC_USER_NAME $DOC_APP_NAME $DOC_CLIENT_ID \
    $DOC_CLIENT_SECRET $DOC_TOKEN

# Startup documentation server
python manage.py runserver $DOC_API_HOSTNAME --noreload --verbosity=$VERBOSITY &
DJANGO_PID=$!
found=0
while [ $found -eq 0 ]
do
    sleep 2
    curl -s "$DOC_API_URL/api/v1/" > /dev/null
    if [ $? == 0 ]
    then
        echo "Server is running."
        found=1
    else
        echo "Server is not running yet..."
    fi
done

# Start the celery worker
if [ $WITH_CELERY -eq 1 ]; then
    celery -A wpcsite.celery worker --loglevel=info &
    CELERY_PID=$!
    sleep 2
fi

# Add the documentation resources
# TODO: change when upload_data.py can work with v2 API
tools/upload_data.py \
    --api=$DOC_API_URL \
    --user=$DOC_USER_NAME \
    --password=$DOC_USER_PASSWORD \
    --data=docs/v1/resources/ \
    --noinput

# If tools/resources.py changes resource creation order,
# uncomment this command to refresh resources
# tools/download_data.py \
#     --api=$DOC_API_URL \
#     --data=docs/v1/resources/

# Make the documentation requests
tools/integration_requests.py\
    --api=$DOC_API_URL \
    --apiversion=$API_VERSION \
    --mode=$DOC_MODE \
    --token=$DOC_TOKEN \
    --raw="docs/$API_VERSION/raw" \
    --cases="docs/$API_VERSION/doc_cases.json"
