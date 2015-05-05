#!/bin/bash
set -e

## $1 is path to repo
## $2 is remote
## $3 is branch
## $4 is the pr number
## $5 is the new commit message

# Requires git-extras (https://github.com/tj/git-extras)

echo $1
echo $2
echo $3
echo $4
echo $5

cd "$1"

# Resync with remote
git fetch $2
git checkout $3
git reset --hard $2/$3

# Checkout and update
git pr $4 $2
git rebase $3

# Squash
COUNT="$(git missing $3 | wc -l)"
git reset --soft HEAD~$(expr $COUNT>0?$COUNT-1:0)
git add -A
git commit --amend -m "$5"

# merge into branch
git merge-into $3

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
git checkout $3
git branch -D $BRANCH

# Finish up
# git push $2 $3
exit 200