# replit-code-jam-9

## to install:
get **GitHub Desktop** and open this repository in the desktop app. this will allow you to create a local repository, with
all of your changes still locally tracked.

make sure you have python installed, and navigate to the directory where you cloned the repo.

you can set up a virtual environment with the following commands:
```
$ python -m venv env
```
on Windows: 
```
$ env\Scripts\activate
```
on Mac/Unix:
```
$ source env/bin/activate
```
after that, you can install all the necessary packages and run the webserver:
```
$ python -m pip install poetry
$ poetry install
$ set FLASK_APP=tutorona && set FLASK_ENV=development
$ flask run
```
## creating a branch
on GitHub Desktop, you can make a new branch easily. make sure when you're developing features and committing code the commits
go to your branch-- this way everyone can work on separate features.

when you're ready to commit, add a commit message and description to explain your changes.

when you're ready to merge the branch, go to the branch tab and click create pull request. you'll be able to submit a pull
request for review and add some info about your changes

**NEVER** push your changes right to master or merge to master, make sure you use pull requests.
