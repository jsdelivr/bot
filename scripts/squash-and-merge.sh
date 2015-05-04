#!/bin/bash

## $1 is path
## $2 is remote
## $3 is branch
## $4 is the pr number
## $5 is the number of commits
## $6 is the new commit message

# Requires git-extras (https://github.com/tj/git-extras)

cd $1

# Resync with remote
git fetch $2
git checkout $3
git reset --hard $2/$3

# Checkout and squash
git pr $4 $2
git rebase $2
git reset --soft HEAD~$(expr $5 - 1)
git add -A
git commit --amend -m $6

# merge into branch
git merge-into $3

BRANCH = git rev-parse --abbrev-ref HEAD
git checkout $3
git branch -D $BRANCH

git push $2 $3

# echo ${PWD##*/}
