# Description: command line python script to create a new repository on github based on contents of directory it's passed, and populate a readme and the github description, based on a comment in the source file. used for initial repo and upload setup
import os
import sys
import github
import re

# GitHub credentials
GITHUB_TOKEN = "your_token_here"
GITHUB_USERNAME = "your_username_here"
COMMITTER_NAME = "your_commit_name_here"
COMMITTER_EMAIL = "your_commit_email_here"


def create_git_repo(folder_name):
    # Change directory to the specified folder
    os.chdir(folder_name)
    
    # Initialize a new Git repository if it doesn't exist
    if not os.path.exists('.git'):
        os.system("git init")
    else:
        print("Git repository already exists.")

def get_repo_description(script_file):
    description = "Default repository description"
    
    with open(script_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        # Handle Python files
        if script_file.endswith('.py'):
            for line in lines:
                if line.startswith("# Description:"):
                    description = line.strip()
                    break
        
        # Handle HTML files
        elif script_file.endswith('.html'):
            for line in lines:
                match = re.match(r'<!--\s*Description:\s*(.*?)\s*-->', line)
                if match:
                    description = match.group(1).strip()
                    break

    return description

def find_script_file(folder_name):
    # Search for Python or HTML script files within the specified folder
    for file in os.listdir(folder_name):
        if file.endswith('.py') or file.endswith('.html'):
            return os.path.join(folder_name, file)
    return None

def create_readme(description, folder_name):
    # Remove leading '#' from the description (for Python files)
    description = description.lstrip("#").strip()
    
    readme_content = f"""
# {folder_name}

{description}
"""
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(readme_content.strip())
    print("README.md created.")

def upload_to_github(repo_name, description, folder_name):
    # Connect to GitHub
    g = github.Github(GITHUB_TOKEN)
    user = g.get_user()

    # Check if repository already exists
    try:
        repo = user.get_repo(repo_name)
        print(f"Repository {repo_name} already exists on GitHub.")
    except github.GithubException:
        # Create a new repository on GitHub with the description
        print(f"Creating repository {repo_name} on GitHub with description: {description}")
        repo = user.create_repo(repo_name, description=description)
        print(f"Created repository {repo_name} on GitHub.")

    # Add all files (except .bak files) to the staging area
    for file in os.listdir('.'):
        if os.path.isfile(file) and not file.endswith('.bak'):
            os.system(f"git add {file}")

    # Commit
    os.system(f'git -c user.name="{COMMITTER_NAME}" -c user.email="{COMMITTER_EMAIL}" commit -m "Updated script"')

    # Set the branch to main and add remote origin if it doesn't exist
    os.system(f"git branch -M main")
    os.system(f"git remote get-url origin || git remote add origin https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git")

    # Push to GitHub
    push_result = os.system("git push -u origin main")

    if push_result != 0:
        print(f"Error: Failed to push some refs to 'https://github.com/{GITHUB_USERNAME}/{repo_name}.git'")

    print("Uploaded script to GitHub")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_name>")
        sys.exit(1)

    folder_name = sys.argv[1]
    repo_name = os.path.basename(folder_name)  # Use the folder name as the repository name

    # Convert the relative path to an absolute path
    folder_path = os.path.abspath(folder_name)

    # Create a new Git repository or reinitialize existing one
    create_git_repo(folder_path)

    # Find the script file within the specified folder (either Python or HTML)
    script_file = find_script_file(folder_path)
    if script_file is None:
        print(f"No Python or HTML script file found in the '{folder_name}' folder.")
        sys.exit(1)

    # Extract repository description from the script file
    repo_description = get_repo_description(script_file)

    # Create README.md with the repository description
    create_readme(repo_description, os.path.basename(folder_path))

    # Upload to GitHub
    upload_to_github(repo_name, repo_description, folder_path)
