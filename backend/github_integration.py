import os
from github import Github, Auth
from github.GithubException import GithubException

def open_playbook_pr(
    repo_name: str, 
    branch_name: str, 
    file_path: str, 
    new_content: str, 
    pr_title: str, 
    pr_body: str
) -> str:
    """
    Creates a new branch, updates the playbook file, and opens a PR.
    Returns the URL of the created PR.
    
    Args:
        repo_name: Full repository name (e.g., "owner/repo")
        branch_name: Name of the branch to create for the PR
        file_path: Path to the file to update (e.g., "playbooks/incident_response.md")
        new_content: The updated content for the file
        pr_title: Title of the pull request
        pr_body: Body/description of the pull request
    
    Returns:
        str: URL of the created pull request
    
    Raises:
        ValueError: If GITHUB_TOKEN is not set
        RuntimeError: If PR creation fails
    """
    # Fail fast if we forgot the token during the hackathon
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("CRITICAL: GITHUB_TOKEN environment variable is missing.")

    # Use the new Auth.Token method (PyGithub 2.x)
    auth = Auth.Token(token)
    g = Github(auth=auth)
    
    try:
        repo = g.get_repo(repo_name)
        main_branch = repo.get_branch("main")
        
        # 1. Create a new branch (handle case where we are testing and it already exists)
        try:
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
            print(f"✅ Created new branch: {branch_name}")
        except GithubException as e:
            if e.status == 422:  # 422 usually means reference already exists
                print(f"⚠️  Branch {branch_name} already exists. Attempting to update existing branch.")
            else:
                raise

        # 2. Get the existing file so we have its SHA (required by GitHub API to update)
        try:
            contents = repo.get_contents(file_path, ref="main")
            repo.update_file(
                path=contents.path, 
                message=f"Automated playbook update: {file_path}", 
                content=new_content, 
                sha=contents.sha, 
                branch=branch_name
            )
            print(f"✅ Updated file: {file_path}")
        except GithubException as e:
            if e.status == 404:
                # Fallback: if the file doesn't exist, create it
                repo.create_file(
                    path=file_path, 
                    message=f"Create {file_path}", 
                    content=new_content, 
                    branch=branch_name
                )
                print(f"✅ Created new file: {file_path}")
            else:
                raise

        # 3. Create the Pull Request
        pr = repo.create_pull(
            title=pr_title, 
            body=pr_body, 
            head=branch_name, 
            base="main"
        )
        print(f"✅ Pull Request created: {pr.html_url}")
        return pr.html_url
        
    except Exception as e:
        raise RuntimeError(f"Failed to open GitHub PR: {str(e)}")
