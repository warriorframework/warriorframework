The best place to look for any Warrior related information would be the Warrior User guide available under Warrior directory "Warrior/Docs/Warrior_user_guide"

This is the directory to hold information on the Systems and its details related to your test.


Input data file seperates Data from the logic and makes your Cases/Suites/Project more Manageble. 
Moreover, there are multiple ways to call/reference a Data file in Warrior.  
Below are the ways to call/reference data files to  cases/Suites in the order of priority.

1. Command line option "-datafile" can reference the executed item with the Input_data_file  
./Warrior <Case/Suite/Project>  -datafile  Data_file(Data/) "Mapping Data file to case/site/project at run time with flag -datafile"

2. Every Suite Step can reference a Input_data_file to a Case.
Suite_file(Suites/) ----> Data_file(Data/)       "Data file is referenced in Suite_file xml at case level. Each Case in Suite's Step is mapped to one Data file"

3. Suite Global level can reference an Input_data_file to all the Cases in the Suite.
Suite_file(Suites/) ----> Data_file(Data/)       "Data file is referenced in Suite_file xml at global level. All Case in Suite is mapped to one Data file" 

4. A Testcase can reference to a Input_data_file.
Automation_Case_file(Testcases/) ----> Data_file(Data/)     "Data file is referenced in Case_file xml"




