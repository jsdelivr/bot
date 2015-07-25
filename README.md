jsDelivr bot
=============

The bot which validates and comments on PRs, squashs commits and merges submissions.

### Why

Couple reasons: we wanted something even faster than **@jimaek** (he usually took a about a minute whereas the bot is under a second), bigger than **@jimaek** (checks more things than a human can), better than **@jimaek** (can squash commits before merging), and stronger than **@jimaek** (the bot defers to other mods for help if unsure) =D

#### Why not travis/jenkins etc

Could of be done, but it would have been much, much slower to validate and be difficult to support issue comment hooks (actions when a mod wants a pr squashed) and auto merging. The nice thing about bot is it only interacts with the Github API and avoids cloning the repo most of the time.

### How

Born out of a drunk weekend adventure to replace **@jimaek** with the github API, github3.py, and the jsDelivr API

### Usage

Note: squashing requires [`git-extras`](https://github.com/tj/git-extras)

```sh
pip install -r requirements.txt
```

Adjust `config.yml` as necessary (tokens, user name, repo clone path, etc)

Run server on port 9000
```sh
./run.py

#Background
nohup ./run.py &
```

```sh
./cli <pull-request-number>
```
