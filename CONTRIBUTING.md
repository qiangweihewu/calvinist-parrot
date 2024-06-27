# Contribute to the Calvinist Parrot project

## How to set up the project

### Prerequisites

You will need to have the following installed on your machine:

- [Docker](https://www.docker.com/products/docker-desktop/)

### Environment variables

You will need access to the database. Please connect me for credentials to a test database. Please see the `.env.example` file for the environment variables that need to be set. Once you have those, rename it to `.env` and put it in the app folder.

For the Google Application Credentials, please connect with me so I can create your service account and give you the JSON file. Once you have it, please put it in the `app/.secret/` folder.

### Running the tests

In the app folder, run the following command to run the tests.

    .\test_parrot.bat

## Contributing to the Project

Before you begin, make sure to fork the project. Go to the project's GitHub page and click the `fork` button:
[Project Page](https://github.com/Jegama/calvinist-parrot)

### Setting Up Your Local Repository

1. **Clone your forked repository** to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/calvinist-parrot.git
   cd calvinist-parrot
   ```

2. **Add the original repository as a remote** to pull future updates:
   ```bash
   git remote add upstream https://github.com/Jegama/calvinist-parrot.git
   ```

3. **Fetch the latest updates** from the original repository:
   ```bash
   git fetch upstream
   ```

4. **Create a new branch** for your changes:
   ```bash
   git checkout -b mychange upstream/master
   ```

### Making Changes
1. Make your changes to the code.

2. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Describe your changes here"
   ```

### Submitting Changes
1. **Push your changes** to your fork:
   ```bash
   git push origin mychange
   ```

2. Go to your fork on GitHub. You should see a `Compare & pull request` button. Click it to create a pull request.

   - When creating the pull request, you can choose to allow maintainers to make edits. This is helpful if they need to make minor adjustments before merging.

### Updating Your Branch
If you need to make more changes after your initial commit:
1. Make the changes locally.

2. **Amend your previous commit** if you want to keep it as a single commit (optional):
   ```bash
   git add .
   git commit --amend --no-edit
   ```

3. **Force push** your changes (since you've amended the commit):
   ```bash
   git push -f origin mychange
   ```

### Keeping Your Fork Updated
To keep your fork up to date with the original repository:
1. **Fetch updates** from the upstream:
   ```bash
   git fetch upstream
   ```

2. **Merge updates into your master branch**:
   ```bash
   git checkout master
   git merge upstream/master
   ```

3. **Push updates to your fork**:
   ```bash
   git push origin master
   ```

**Note:** It’s important to regularly sync your fork, especially before starting a new change.
