import shutil
import os

FEATURE_NAME = 'Develop'
WORKSPACE = ''

PR_SOURCE_BRANCH_PARAMETER = "GITHUB_PR_SOURCE_BRANCH"
WORKSPACE_PARAMETER = 'WorkSpace'

if PR_SOURCE_BRANCH_PARAMETER in os.environ:
	FEATURE_NAME = os.environ[PR_SOURCE_BRANCH_PARAMETER]

WORKSPACE = os.environ[WORKSPACE_PARAMETER]
srcFolder = r"Carwale/bin"
releaseFolder = r"C:/Release/"
des = os.path.join(releaseFolder,FEATURE_NAME,'bin')


def clean_folder(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.normpath(os.path.join(src, item))
        d = os.path.normpath(os.path.join(dst, item))
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

clean_folder(des)
copytree(os.path.normpath(os.path.join(WORKSPACE,srcFolder)), des)