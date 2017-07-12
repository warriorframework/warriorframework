set -x
# ls -l
pip install pylint

cd ../
git clone https://github.com/warriorframework/warriorframework.git pylint_warrior
cd pylint_warrior
git checkout develop

git branch
# Displaying what .py files have changed
filelist=$(git --no-pager diff --name-only develop "${TRAVIS_PULL_REQUEST_BRANCH}"  | grep -v 'OSS' | grep -v 'conf.py' | grep '.py$')
if [[ $filelist ]]; then
    echo "List of .py files that have changed in this commit"
    echo $filelist
else
    echo "no .py file has changed in this commit, exiting"
    exit 0;
fi

# Do pylint on develop and the latest commit, output result to pylint_result.txt
echo $filelist | xargs -L 1 pylint || true
git checkout "${TRAVIS_PULL_REQUEST_BRANCH}" ;
echo $filelist
echo $filelist | xargs -L 1 pylint | tee pylint_result.txt || true

# Match filename and score into summary.txt
grep "Your code has been rated" pylint_result.txt > score.txt
grep "Module" pylint_result.txt > filename.txt

sed -i -e 's/\** Module//g' filename.txt
sed -i -e 's/Your code//g' score.txt
paste -d "^" filename.txt score.txt | column -t -s "^" | tee summary.txt

# Check if there is an increase 
# set +x
echo "Files that doesn't meet the pylint score requirement (>5 with score increase)"
status="pass"
while read -r line;
do 
    line_status="pass"
    # echo "$line"
    num1=$(grep -oP "at \K[0-9\.\-]*" <<< "$line");
    num2="5";
    if [[ $(echo "$num1 < $num2" | bc) -ne 0 ]] ; then
        echo "score lower than 5: $num1"
        status="fail"
        line_status="fail"
    fi
    
    num3=$(grep -oP "previous run.*/10, \K[0-9\.\-+]*" <<< "$line" | tr -d "+":-0)
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