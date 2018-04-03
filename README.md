# warriorframework
http://warriorframework.org

Warrior Framework is an open source automation framework designed to enable anyone to automate their testing, processes, and repetitive tasks by simplifying the complex process of building an automation infrastructure. As a keyword and data driven framework, Warrior’s infrastructure is built to maximize on re-usability of  built in keywords. In addition, Warrior’s app based platform provides the users with native apps to easily implement their automation needs, while providing the user with the ability to customize their own workflow apps.

1. Clone warriorframework
$ git clone https://github.com/warriorframework/warriorframework.git
2. go to warriorframework directory
$cd warriorframework
3. To check the list of versions available, execute "git tag --list" command <br/>
$ git tag --list <br />
warior-3.1.0 <br/>
warior-3.1.1 <br/>
warior-3.2.0 <br/>
warior-3.3.0 <br/>
$
3. To Check the current version you are at, execute "git branch" command <br/>
$ git branch <br/>
\* master <br/>
$
- \* indicates the active version.
- In the above example master is the active version.
- If the active version is master it means you are not using a standard release version of warrior framework and hence it may
not be a stable tested version.
4. To switch to a specific version from master, execute 'git checkout <version_name>' command. <br/>
$ git checkout warrior-3.3.0 <br/>
Note: checking out 'warrior-3.3.0'.
You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by performing another checkout.
If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -b with the checkout command again. Example:
git checkout -b <new-branch-name>
HEAD is now at 146313d... reduce command timeout, wait after timeout=60
$
5. Execute git branch command to verify the active version. <br/>
$ git branch <br/>
\* (HEAD detached at warrior-3.3.0) <br/>
master <br/>
$
- \* indicates the active version.
6. Switch from one version to another (current=warrior-3.3.0, switch to warrior-3.2.0) <br/>
$ git checkout warrior-3.2.0 <br/>
Previous HEAD position was 146313d... reduce command timeout, wait after timeout=60
HEAD is now at ecb6373... WAR-180, handle nd prompt on timeout
$
$ git branch <br/>
\* (HEAD detached at warrior-3.2.0) \
master <br/>
$
7. Switch to master branch again. <br/>
$ git checkout master <br/>
Previous HEAD position was ecb6373... WAR-180, handle nd prompt on timeout
Switched to branch 'master'
Your branch is up-to-date with 'origin/master'.
$ <br/>
$ <br/>
$ git branch <br/>
* master <br/>
$ 
