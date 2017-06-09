git fetch
git checkout develop

#Remove all existing package .rst files.
rm -rf docs/source/Actions*rst
rm -rf docs/source/Framework*rst
rm -rf docs/build/*

#Rebuild package .rst files to make sure it reflect
sphinx-apidoc -f -o  docs/source  warrior/Actions
sphinx-apidoc -f -o  docs/source  warrior/Framework

git config --global user.email "warriorframework.docs@gmail.com"
git config --global user.name "wf-docs"
# please refer to https://docs.travis-ci.com/user/encryption-keys
# to see how to generate the encryption key
git remote add origin-docs https://$GITHUB_TOKEN@github.com/warriorframework/warriorframework.git

git add -A
git commit -m "[skip ci] Update warriorframework rst documents for readthedoc"
git config --list
git push -u origin-docs develop