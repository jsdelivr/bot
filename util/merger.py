import pystache, re
from subprocess import call
import os

class GitMerger():
    """
        merges a pull request by the request of a collab
    """
    def __init__(self):
        self.merge_re = re.compile(self.config["merge_re"], re.IGNORECASE)

    def check_comment(self, number, comment, requester):
        user = self.gh.user(requester)
        lines = comment.splitlines()
        print number
        print requester
        if any(self.merge_re.match(line) for line in lines) and \
            any(user == collab for collab in self.repo.iter_collaborators()):

            self.squash_merge(number, self.get_number_commits(comment))

    def rebase(self, number):
        pr = self.get_pull(number)
        issue = self.repo.issue(number)

        with open("templates/rebase.tpl") as f:
            msg = pystache.render(f.read(), pr)
        issue.create_comment(msg)

    def squash_merge(self, number):
        """
           Merge and squash the commits of a pull request if the requester is allowed

           Merges in 1-2 commits depending if fast-forward is necessary

           @param number int pull number
        """
        pr = self.get_pull(number)
        issue = self.repo.issue(pr.number)

        if pr.commits <= 1:
            issue.create_comment("I'm afraid I can't do that.")
            return

        message = "%s\nCloses #%d" % (pr.title, number)
        DEVNULL = open(os.devnull, 'r+b', 0)
        
        status = call(['./scripts/squash-and-merge.sh',
            self.config["path_to_repo"],
            self.config["repo_remote"],
            self.config["repo_branch"],
            str(number),
            message
        ])
        # ], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

        if status != 200: #success
            issue.create_comment("Sorry! I've failed you :(")