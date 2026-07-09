import subprocess
import glob
import os

def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def main():
    print("🚀 Rebuilding Git History with Individual Commits...")
    
    # 1. Erase the commit history (keeps the .git folder and your remote intact!)
    run_cmd(["git", "update-ref", "-d", "HEAD"])
    
    # 2. Unstage everything so we can start fresh
    subprocess.run(["git", "rm", "-rf", "--cached", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Stage everything
    run_cmd(["git", "add", "-A"])
    
    # 4. Find all the personalized READMEs we generated
    generated_readmes = glob.glob("*.README.md")
    for folder in ["backend", "src", "public"]:
        folder_readme = os.path.join(folder, "README.md")
        if os.path.exists(folder_readme):
            generated_readmes.append(folder_readme)
            
    # 5. UNSTAGE the personalized READMEs so they aren't in the main commit
    for readme in generated_readmes:
        subprocess.run(["git", "rm", "--cached", readme], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    # 6. Make the first big commit with the actual code
    run_cmd(["git", "commit", "-m", "feat: TrustScope v2.0 Enterprise Codebase"])
    
    # 7. Now, loop through every personalized README and commit it individually!
    for readme in generated_readmes:
        run_cmd(["git", "add", readme])
        
        # Make a pretty commit message based on the file name
        if readme.endswith(".README.md"):
            clean_name = readme.replace(".README.md", "")
        else:
            clean_name = os.path.dirname(readme) + " directory"
            
        run_cmd(["git", "commit", "-m", f"docs: add comprehensive documentation for {clean_name}"])

    # 8. Force push this beautiful new history to GitHub
    print("\n📦 Pushing new commit history to GitHub...")
    run_cmd(["git", "push", "-u", "origin", "main", "--force"])
    print("\n✅ Done! Check your GitHub, you will have a beautiful list of individual commits!")

if __name__ == "__main__":
    main()
