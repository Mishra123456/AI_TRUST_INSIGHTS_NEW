import subprocess
import os

def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)

def main():
    print("🚀 Rebuilding Git History with Personalized Commits For Every File...")
    
    # 1. Erase the single giant commit history
    run_cmd(["git", "update-ref", "-d", "HEAD"])
    subprocess.run(["git", "rm", "-rf", "--cached", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Dictionary mapping each file/folder to a beautiful, personalized commit message
    commits = {
        "backend": "feat: implement machine learning pipeline and FastAPI backend",
        "src": "feat: build luxury React dashboard components and styling",
        "public": "asset: add static public assets and screenshots",
        "package.json": "chore: configure frontend NPM dependencies and scripts",
        "package-lock.json": "chore: lock frontend dependencies",
        "tailwind.config.ts": "style: define luxury enterprise gradient design system",
        "vite.config.ts": "chore: configure Vite bundler and path aliases",
        "components.json": "chore: initialize shadcn/ui configuration",
        "index.html": "feat: setup main HTML entry point",
        "eslint.config.js": "chore: enforce strict TypeScript linting rules",
        "tsconfig.json": "chore: setup root TypeScript configuration",
        "tsconfig.app.json": "chore: configure React browser TypeScript environment",
        "tsconfig.node.json": "chore: configure Vite Node.js build environment",
        "Dockerfile": "ci: create production multi-stage Dockerfile for Hugging Face Spaces",
        ".gitignore": "chore: ignore virtual environments and node modules",
        "README.md": "docs: write comprehensive TrustScope documentation",
        "bun.lockb": "chore: lock bun dependencies"
    }
    
    # Loop through the dictionary and commit each file individually
    for path, message in commits.items():
        if os.path.exists(path):
            run_cmd(["git", "add", path])
            run_cmd(["git", "commit", "-m", message])
            
    # Add any leftover files that weren't in the list
    subprocess.run(["git", "add", "-A"], stdout=subprocess.DEVNULL)
    
    # Check if there are uncommitted changes (leftover files)
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if status.stdout.strip():
        run_cmd(["git", "commit", "-m", "chore: add remaining configuration files"])

    print("\n📦 Pushing new personalized commit history to GitHub...")
    subprocess.run(["git", "push", "-u", "origin", "main", "--force"])
    print("\n✅ Done! Check your GitHub, EVERY file now has a different commit message next to it!")

if __name__ == "__main__":
    main()
