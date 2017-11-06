# warriorframework
http://warriorframework.org

Warrior Framework is an open source automation framework designed to enable anyone to automate their testing, processes, and repetitive tasks by simplifying the complex process of building an automation infrastructure. As a keyword and data driven framework, Warrior’s infrastructure is built to maximize on re-usability of  built in keywords. In addition, Warrior’s app based platform provides the users with native apps to easily implement their automation needs, while providing the user with the ability to customize their own workflow apps.

1. Clone warriorframework
$ git clone https://github.com/warriorframework/warriorframework.git
2. go to warriorframework directory
$cd warriorframework
3. To check the list of versions available, execute "git tag --list" command
$ git tag --list \n
warior-3.1.0 \n
warior-3.1.1 \n
warior-3.2.0 \n
warior-3.3.0 \n
$
3. To Check the current version you are at, execute "git branch" command
$ git branch\n
\* master
$
- \* indicates the active version.
- In the above example master is the active version.
- If the active version is master it means you are not using a standard release version of warrior framework and hence it may
not be a stable tested version.
4. To switch to a specific version from master, execute 'git checkout <version_name>' command.
$ git checkout warrior-3.3.0
Note: checking out 'warrior-3.3.0'.
You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by performing another checkout.
If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -b with the checkout command again. Example:
git checkout -b <new-branch-name>
HEAD is now at 146313d... reduce command timeout, wait after timeout=60
$
5. Execute git branch command to verify the active version.
$ git branch \n
\* (HEAD detached at warrior-3.3.0) \n
master \n
$
- \* indicates the active version.
6. Switch from one version to another (current=warrior-3.3.0, switch to warrior-3.2.0)
$ git checkout warrior-3.2.0
Previous HEAD position was 146313d... reduce command timeout, wait after timeout=60
HEAD is now at ecb6373... WAR-180, handle nd prompt on timeout
$
$ git branch \n
\* (HEAD detached at warrior-3.2.0) \
master \n
$
7. Switch to master branch again.
$ git checkout master
Previous HEAD position was ecb6373... WAR-180, handle nd prompt on timeout
Switched to branch 'master'
Your branch is up-to-date with 'origin/master'.
$ \n
$ \n
$ git branch \n
* master \n
$ 
