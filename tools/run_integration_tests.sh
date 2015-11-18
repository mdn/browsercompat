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
  rm -f $DATABASE_NAME
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
  echo "Done."
}
trap cleanup_local EXIT

# Generate a random string
gen_rand_string () {
    local length=$1
    if [ -z $length ]; then length=10; fi
    python -c "\
import string, random;\
chars = string.ascii_uppercase + string.ascii_lowercase + string.digits;\
print ''.join(random.SystemRandom().choice(chars) for _ in range($length));\
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
user = User(username=username, email=email, is_superuser=is_superuser, is_staff=is_superuser);\
user.set_password(password);\
user.save();\
change_group = Group.objects.get(name='change-resource');\
delete_group = Group.objects.get(name='delete-resource');\
user.groups.add(change_group);\
user.groups.add(delete_group);\
" | python manage.py shell --plain
}

#
# Parse command line
#
DOC_MODE="verify"
WITH_CELERY=0
VERBOSITY=1
while getopts ":cghqv" opt; do
  case $opt in
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

#
# Setup the documentation database, server
#

# Change to project root
SCRIPT_DIR=`dirname "$BASH_SOURCE"`
cd "$SCRIPT_DIR/.."

# Set Django environment variables
DATABASE_URL="sqlite:///$DATABASE_NAME"
unset MEMCACHE_SERVERS
if [ $WITH_CELERY -eq 0 ]; then
    unset REDIS_URL
    unset CELERY_RESULT_BACKEND
    unset BROKER_URL
    export CELERY_ALWAYS_EAGER=1
else
    REDIS_DB=7
    export REDIS_URL="redis://localhost/$REDIS_DB"
    export CELERY_RESULT_BACKEND=$REDIS_URL
    export BROKER_URL=$REDIS_URL
    export CELERY_ALWAYS_EAGER=0
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
python manage.py migrate --verbosity=$VERBOSITY

# Add the documentation user
create_user $DOC_USER_NAME $DOC_USER_EMAIL $DOC_USER_PASSWORD 0

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
tools/upload_data.py \
    --api=$DOC_API_URL \
    --user=$DOC_USER_NAME \
    --password=$DOC_USER_PASSWORD \
    --data=docs/resources/ \
    --noinput

# If tools/resources.py changes resource creation order,
# uncomment this command to refresh resources
# tools/download_data.py \
#     --api=$DOC_API_URL \
#     --data=docs/resources/

# Make the documentation requests
tools/integration_requests.py\
    --api=$DOC_API_URL \
    --mode=$DOC_MODE \
    --user=$DOC_USER_NAME \
    --password=$DOC_USER_PASSWORD
