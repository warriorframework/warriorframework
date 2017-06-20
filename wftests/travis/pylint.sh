# set -v
# ls -l
pip install pylint
git checkout master
if [[ $(git --no-pager diff --name-only master "${TRAVIS_COMMIT}"  | grep -v 'OSS' | grep '.py$') ]]; then
    echo "List of .py files that have changed in this commit"
    git --no-pager diff --name-only master "${TRAVIS_COMMIT}"  | grep -v 'OSS' | grep '.py$'
else
    echo "no .py file has changed in this commit, exiting"
    exit 0;
fi
git --no-pager diff --name-only master "${TRAVIS_COMMIT}"  | grep -v 'OSS' | grep '.py$' | xargs pylint || true
git checkout "${TRAVIS_COMMIT}" ;
git --no-pager diff --name-only "${TRAVIS_COMMIT}" master  | grep -v 'OSS' | grep '.py$'
git --no-pager diff --name-only "${TRAVIS_COMMIT}" master  | grep -v 'OSS' | grep '.py$' | xargs pylint | tee pylint_result.txt || true

grep "Your code has been rated" pylint_result.txt > score.txt
grep "Module" pylint_result.txt > filename.txt

sed -i -e 's/\** Module//g' filename.txt
sed -i -e 's/Your code//g' score.txt
paste -d "^" filename.txt score.txt | column -t -s "^" | tee summary.txt

set +x
echo "Files that doesn't meet the pylint score requirement (>5 with score increase)"
status="pass"
while read -r line;
do 
    line_status="pass"
    num1=$(grep -oP "at \K[0-9\.\-]*" <<< "$line");
    num2="5";
    echo "$num1"
    echo "$num2"
    echo "$num1 < $num2" | bc
    if [[ $(echo "$num1 < $num2" | bc) -ne 0 ]] ; then
        echo "score lower than 5: $num1"
        status="fail"
        line_status="fail"
    fi
    
    num3=$(grep -oP "previous run.*/10, \K[0-9\.\-+]*" <<< "$line" | tr -d "+")
    num4="0"
    echo "$num3"
    echo "$num4"
    echo "$num3 < $num4"
    if [[ $(echo "$num3 < $num4" | bc) -ne 0 ]] ; then
        echo "score decrease: $num3"
        status="fail"
        line_status="fail"
    fi

    if [ "$line_status" = "fail" ]; then
        filename=$(grep -oP "[^\s]{2,}" <<< "$line" | head -1)
        echo "$filename ($num1, $num3)"
    fi
done < summary.txt

if [ "$status" = "fail" ] ; then
    exit 1;
else
    exit 0;
fi