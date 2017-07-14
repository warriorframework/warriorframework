set -x
# ls -l
pip install pylint

git config --replace-all remote.origin.fetch +refs/heads/*:refs/remotes/origin/*
git fetch origin develop
git checkout FETCH_HEAD

git branch
# Displaying what .py files have changed
if [[ $(git --no-pager diff --name-only FETCH_HEAD "${TRAVIS_COMMIT}"  | grep -v 'OSS' | grep -v 'conf.py' | grep '.py$') ]]; then
    echo "List of .py files that have changed in this commit"
    git --no-pager diff --name-only FETCH_HEAD "${TRAVIS_COMMIT}"  | grep -v 'OSS' | grep -v 'conf.py' | grep '.py$'
else
    echo "no .py file has changed in this commit, exiting"
    exit 0;
fi
# Do pylint on develop and the latest commit, output result to pylint_result.txt
git --no-pager diff --name-only FETCH_HEAD "${TRAVIS_COMMIT}"  | grep -v 'OSS' | grep -v 'conf.py' | grep '.py$' | xargs -L 1 pylint || true
git checkout "${TRAVIS_COMMIT}" ;
git --no-pager diff --name-only "${TRAVIS_COMMIT}" FETCH_HEAD  | grep -v 'OSS' | grep -v 'conf.py' | grep '.py$'
git --no-pager diff --name-only "${TRAVIS_COMMIT}" FETCH_HEAD  | grep -v 'OSS' | grep -v 'conf.py' | grep '.py$' | xargs -L 1 pylint | tee pylint_result.txt || true

# Match filename and score into summary.txt
grep "Your code has been rated" pylint_result.txt > score.txt
grep "Module" pylint_result.txt > filename.txt

sed -i -e 's/\** Module//g' filename.txt
sed -i -e 's/Your code//g' score.txt
paste -d "^" filename.txt score.txt | column -t -s "^" | tee summary.txt

# Check if there is an increase 
set +x
echo "Files that doesn't meet the pylint score requirement (>5 with score increase)"
status="pass"
while read -r line;
do 
    line_status="pass"
    echo "$line"
    num1=$(grep -oP "at \K[0-9\.\-]*" <<< "$line");
    num2="5";
    if [[ $(echo "$num1 < $num2" | bc) -ne 0 ]] ; then
        echo "score lower than 5: $num1"
        status="fail"
        line_status="fail"
    fi
    
    num3=$(grep -oP "previous run.*/10, \K[0-9\.\-+]*" <<< "$line" | tr -d "+")
    num4="0"
    if [[ $(echo "$num3 < $num4" | bc) -ne 0 ]] ; then
        echo "score decrease: $num3"
        status="fail"
        line_status="fail"
    fi

    if [[ "$line_status" = "fail" ]]; then
        filename=$(grep -oP "[^\s]{2,}" <<< "$line" | head -1)
        echo "$filename ($num1, $num3)"
    fi
done < summary.txt

if [ "$status" = "fail" ] ; then
    exit 1;
else
    exit 0;
fi