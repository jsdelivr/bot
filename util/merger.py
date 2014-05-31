from git import Repo
import pystache

class GitMerger():
    """
        merges a pull request by the request of a collab
    """
    def __init__():
        pass

    template = pystache.compile(open("templates/pr-issue.tpl"))

    def should_merge(self, comment, requester):
        return any(self.merge_re.match(line) for line in comment.splitlines()) and \
            any(requester == collab.login for collab in self.repo.iter_collaborators())

    def merge(self, number, requester, comment=""):
        if not self.should_merge(comment, requester): return
        
        pr = self.get_pull(number)

        repo = Repo(self.config["path_to_repo"])

        repo.git.checkout("master")
        repo.git.pull("origin", "master")

        #for merging
        remote = repo.create_remote("temp", "https://github.com/{0}/{1}.git".format(*pr.head.repo))
        repo.git.fetch(remote, pr.head.ref)
        #akin: git checkout -b temp-merge temp/<branch> --track
        branch_name = "{0}/{1}".format(remote.name, pr.head.ref)
        repo.git.checkout("temp-merge", branch_name, b=True, track=True)
        branch = repo.active_branch

        #soft reset/squash it
        repo.head.reset("HEAD~{0}".format(pr.commits - 1), index=False, working_tree=False)

        with open("templates/merge-pull-request.tpl") as f:
            commit_msg = pystache.render(f.read(), pr)
        repo.index.commit(commit_msg)

        repo.git.checkout("master")
        repo.git.merge(branch)

        #clean up
        branch.delete()
        repo.delete_remote(remote)

        repo.origin.push(force=True)