# set -x
TRAVIS_BRANCH=develop
TRAVIS_PULL_REQUEST_BRANCH=feature/WAR-1336
# pip install pylint

# rm -rf ../pylint_warrior
cd ../
# git clone https://github.com/warriorframework/warriorframework.git pylint_warrior
cd pylint_warrior
# git checkout "${TRAVIS_BRANCH}"
# git checkout "${TRAVIS_PULL_REQUEST_BRANCH}"
# echo "Merging ${TRAVIS_BRANCH} into ${TRAVIS_PULL_REQUEST_BRANCH}"
# git merge --no-edit "${TRAVIS_BRANCH}"
# git add .

# git branch
# Displaying what .py files have changed
filelist=$(git --no-pager diff "${TRAVIS_BRANCH}" --name-only | grep ".py$")
if [[ "$filelist" ]]; then
    echo "List of .py files that have changed in this commit"
    echo "$filelist"
    echo ""
    echo "$filelist" > filelist.txt
    python ../warriorframework/wftests/ci/pylint_checker.py filelist.txt .pylintrc "${TRAVIS_BRANCH}" "${TRAVIS_PULL_REQUEST_BRANCH}"
else
    echo "no .py file has changed in this commit, exiting"
fi

exit 0;