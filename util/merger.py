from git import Repo
import pystache, re

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

            merge(number, self.get_number_commits(comment))

    def rebase(self, number):
        pr = self.get_pull(number)
        issue = self.repo.issue(number)

        with open("templates/rebase.tpl") as f:
            msg = pystache.render(f.read(), pr)
        issue.create_comment(msg)

    def merge(self, number):
        """
           Merge and squash the commits of a pull request if the requester is allowed

           Merges in 2-3 commits depending if fast-forward is necessary

           @param number int pull number
           @param requester str github login
           @param comment str check if comment is requesting a merge 
        """
        
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
            repo.git.rebase("master")

            with open("templates/merge-pull-request.tpl") as f:
                commit_msg = pystache.render(f.read(), pr)
                print commit_msg
            # repo.index.commit(commit_msg)

            # repo.git.checkout("master")
            # repo.git.merge(branch)

            # repo.remotes.origin.push("master")

        except Exception,e:
            issue = self.repo.issue(pr.number)
            issue.create_comment("Could not automatically squash and merge the pull request: {0}".format(str(e)))
        finally:
            try:
                #clean up
                repo.delete_remote(remote)
                repo.git.branch(branch, D=True) #delete branch
            except: pass
