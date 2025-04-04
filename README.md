# Edit this
Initialized with pyinit using the "basic" project package.<br>
This package is recommended for simple cli programs or libraries.<br>


## Suggested workflow:

### Edit pyproject.toml 
* Edit your info and add a description
* Add any known dependencies you are going to use
* If your project doesn't need a cli command, remove the project.scripts entry

### Install to virtual environment
* You can do it manually or use the instal-dev script
* The script installs with the -e option, allowing you to edit the program without reinstallation
* The script also installs the necessary testing components, pytest / flake8 / mypy / tox

### Initialize git and set upstream
* Create an empty repository on github
* git init
* git add .
* git commit -m 'Initial Commit'
* git remote add origin url-to-repository
* git push -u origin main

### Start coding
* To get started quickly, you can put your code in the init or main files
* It's good practice to get used to testing.
* You can run the run_tests.sh script or create your own.
* You can also use tools like ptw which runs tests when it detects a change in afile.
* Lastly you can run tox. The basic configuration tests the last 3 python versions.
* It's recommended to run tox before commiting to main. Tox is slow as it installs whole environments.

Suggestion for beginners:<br>
Getting used to tests can be annoying. Perhaps you may not know what to test<br>
Everytime you get the urge to use the print function to debug the output of a<br>
function, turn it into test. This will not only test the functionality, but it<br>
will also check if you have setup your imports correctly, which is necessary<br>
if you want others to use your program. 


# description
...

# Installation:
Download the repo or use the git clone command<br>
CD into the created folder.<br>
pip install .

# Documenation
rantevou -h