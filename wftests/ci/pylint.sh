# set -x
pip install pylint

cd ../
git clone https://github.com/warriorframework/warriorframework.git pylint_warrior
cd pylint_warrior

if [[ "${TRAVIS_BRANCH}" == "master" ]] && [[ "${TRAVIS_PULL_REQUEST_BRANCH}" != release* ]]; then
    echo "Pull request shouldn't merge to master"
    exit 1
fi

git checkout "${TRAVIS_BRANCH}"
git checkout "${TRAVIS_PULL_REQUEST_BRANCH}"
echo "Merging ${TRAVIS_PULL_REQUEST_BRANCH} into ${TRAVIS_BRANCH}"
git merge --no-edit "${TRAVIS_BRANCH}"
git add .

git branch
# Displaying what .py files have changed
filelist=$(git --no-pager diff "${TRAVIS_BRANCH}" --name-only --diff-filter=d | grep ".py$\|warrior$")
if [[ "$filelist" ]]; then
    echo "$filelist" > filelist.txt
    python ../warriorframework/wftests/ci/pylint_checker.py filelist.txt .pylintrc "${TRAVIS_BRANCH}" "${TRAVIS_PULL_REQUEST_BRANCH}"
else
    echo "no .py file has changed in this commit, exiting"
fi
