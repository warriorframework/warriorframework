cd ./projects
git checkout develop pj_framework_tests.xml
cd ../suites
git checkout develop ts_framework_tests.xml
cd framework_tests/
git checkout develop ts_framework_tests.xml
cd ../
cd ../testcases/framework_tests/
cd cond_var/

git checkout develop cond_var.xml
git checkout develop error.xml
git checkout develop fail.xml
git checkout develop pass.xml
cd ../

cd manual_verification_tests/
git checkout develop tc_runmode_rup_single_step.xml
cd ..
git checkout develop tc_no_impact_onerror_goto_verification.xml
cd ..
git push 

