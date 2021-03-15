# Polaris Contributing Guide

### ML for exploring and analyzing telemetry data from the SatNOGS network and beyond :rocket:

Thank you for considering and taking the time to contribute! We're very glad that you'll will help us to improve Polaris :)

We also suggest that it would be best to try Polaris before contributing to it, here's our [getting started guide](https://docs.polarisml.space/en/latest/using/getting_started_with_polaris.html).

## Prerequisites
---
You’ll need to have a few things before we can start:

- You need Linux or Unix-like environment or Windows(7+) with Python 3.6 - 3.8, but support is limited for Windows.
  
- You’ll need to be comfortable installing Python packages – we strongly recommend using `venv` to create a separate environment for Polaris. If you haven’t done this before, [this guide should help you out.](https://docs.python.org/3.8/library/venv.html)
- You’ll need to be comfortable with the CLI.
- You’ll need a good network connection, so you can download telemetry quickly.
- [Git](https://git-scm.com/) installed on OS.
- Attitude to never give up.

## Setting up Local Development Enviornment
---
1. ### **Forking repository**:
   - Firstly you have to make your own copy of project. For that you have to fork the repository.
   - Kindly wait till it gets forked.
   - After that copy will look like `<your-user-name>/polaris` forked from ` librespacefoundation/Polaris/polaris`.
   - For more information click [here](https://docs.gitlab.com/ee////user/project/working_with_projects.html).

2. ### **Clone repository**:
   - Now you have your own copy of project. Here you have to start your work.
   - Go to desired location on your computer where you want to set-up the project.
   - Open `terminal` on your OS. you can learn more [here](https://docs.gitlab.com/ee/gitlab-basics/start-using-git.html).
   - Type the command git clone <your-fork-url>.git and hit enter.
   - Wait for few seconds till the project gets copied.
   ```console
      $ git clone https://gitlab.com/librespacefoundation/polaris/polaris.git
      Cloning into 'polaris'...
      remote: Counting objects: 179, done.
      remote: Total 179 (delta 0), reused 0 (delta 0), pack-reused 179
      Receiving objects: 100% (179/179), 24.07 KiB | 0 bytes/s, done.
      Resolving deltas: 100% (79/79), done.
      Checking connectivity... done
   ```

3. ### **Adding LSF's repo as alternate remote**:
   - Now you have to set up remote repositories.
   - Type `git remote -v` in terminal to list remote connections to your repo.
   - It will show something like this:
   ```console
    origin  https://gitlab.com/<your-user-name>/polaris.git (fetch)
    origin  https://gitlab.com/<your-user-name>/polaris.git (push)
    ``` 

   - Now type the command `git remote add upstream https://gitlab.com/librespacefoundation/polaris/polaris.git` this will set upstream as main directory.
   - Again type in command `git remote -v` to check if remote has been set up correctly.
   - It should show something like this:

   ```console
    origin  https://gitlab.com/Jeevan-Kiran-Lenka/polaris.git (fetch)
    origin  https://gitlab.com/Jeevan-Kiran-Lenka/polaris.git (push)
    upstream        https://gitlab.com/librespacefoundation/polaris/polaris.git (fetch)
    upstream        https://gitlab.com/librespacefoundation/polaris/polaris.git (push)
    ```
    - You can learn more about `remote` [here](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes)

4. ### **Creating a branch**:

    - While submitting an MR to polaris, it is highly recommended that changes are made to a separate branch on your fork rather than on the master branch.

    - `git branch` will list all the branches in the repository
    ```console
    $ git branch
    * master
    ```

    - Now type `git branch <your-branch-name>`, for example
    ```console
    $ git branch jeevan
    ```
   
   - You can check the created branch by `git branch`
   ```console
   $ git branch
   * master
     jeevan
   ```

   - But still if you start editing the edits will go to the main branch. To change the path of the edits type in `git checkout <your-branch-name>`
   ```console
   $ git checkout jeevan
     Switched to branch 'jeevan'
   ```

   - Now you are ready to do the desired changes.
 
 ## How to Report Bugs
 ---

 Please open a [new issue in the appropriate GitLab repository](https://gitlab.com/librespacefoundation/polaris/polaris/-/issues) with steps to reproduce the problem you're experiencing. 

 Any additional detail you can submit, such as *screenshots*, *text output*, and *both your expected and actual results* will help us to understand your request.

 ## How to Request Enhancements
 ---

 First, please refer to the applicable [GitLab repository](https://gitlab.com/librespacefoundation/polaris/polaris) and search the [repository's GitLab issues](https://gitlab.com/librespacefoundation/polaris/polaris/-/issues) to make sure your idea has not been (or is not still) considered. 

 Then, please [create a new issue in the Gitlab repository](https://gitlab.com/librespacefoundation/polaris/polaris/-/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=) describing your enhancement.

 Any additional detail you can submit, such as *step-by-step descriptions*, *specific examples*, *screenshots or mockups*, and *reasoning* will help us to understand your request.
