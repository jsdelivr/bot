from git import Repo
import pystache, re

class GitMerger():
    """
        merges a pull request by the request of a collab
    """
    def __init__(self):
        self.merge_re = re.compile(self.config["merge_re"], re.IGNORECASE)

    def should_merge(self, comment, requester):
        return any(self.merge_re.match(line) for line in comment.splitlines()) and \
            any(requester == collab.login for collab in self.repo.iter_collaborators())

    def get_number_commits(self, comment):
        matches = [self.merge_re.match(line) for line in comment.splitlines()]
        match = next(match for match in matches if match is not None)
        return int(match.groups()[0])

    def merge(self, number, requester, comment=""):
        """
           Merge and squash the commits of a pull request if the requester is allowed

           Merges in 2-3 commits depending if fast-forward is necessary

           @param number int pull number
           @param requester str github login
           @param comment str check if comment is requesting a merge 
        """
        if not self.should_merge(comment, requester): return False
        
        pr = self.get_pull(number)
        repo = Repo(self.config["path_to_repo"])

        repo.git.checkout("master")
        repo.git.pull("origin", "master")

        try:
            #for merging
            remote = repo.create_remote("temp", "https://github.com/{0}/{1}.git".format(*pr.head.repo))
            repo.git.fetch(remote, pr.head.ref)
            #akin: git checkout -b temp-merge temp/<branch> --track
            branch_name = "{0}/{1}".format(pr.user.login, pr.head.ref)
            branch_location = "{0}/{1}".format(remote.name, pr.head.ref)
            repo.git.checkout(branch_name, branch_location, b=True, track=True)
            branch = repo.active_branch

            #soft reset/squash it
            reset_commits = max(0, pr.commits - self.get_number_commits(comment))
            repo.git.reset("HEAD~{0}".format(reset_commits), soft=True)

            with open("templates/merge-pull-request.tpl") as f:
                commit_msg = pystache.render(f.read(), pr)
            repo.index.commit(commit_msg)

            repo.git.checkout("master")
            repo.git.merge(branch)

            repo.remotes.origin.push("master")

        except Exception,e:
            issue = self.repo.issue(pr.number)
            issue.create_comment("Could not automatically squash and merge the pull request: {0}".format(str(e)))
        finally:
            try:
                #clean up
                repo.delete_remote(remote)
                repo.git.branch(branch, D=True) #delete branch
            except: pass
