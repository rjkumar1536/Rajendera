
import git
import sys
def main(argv):
	if len(argv) < 1:
		print "Incorrect Command format missing arguments"
		exit(-1)
	REPO_LOCATION =argv[0]
	repo = git.Repo(REPO_LOCATION)
	commit_data=[]
	commits_list = list(repo.iter_commits())
	commit = commits_list[0]
	commit_data.append(str(commit).split(" ")[0])
	commit_data.append(str(commit.author).split(" ")[0])
	commit_data.append(str(commit.message))
	details=str(commit_data).strip('[]')
	details=details.replace("<","")
	details=details.replace(">","")
	print "Commit_Details:"+details


if __name__ == '__main__':
	main(sys.argv[1:])
