# GitHub submission setup

Run these commands from this directory after installing/testing the project:

```bash
git init
git add .
git commit -m "Add arithmetic coding replication implementation"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Before pushing, verify:

```bash
python -m unittest discover -s tests -v
python arithmetic_coding_replication.py
```

Do not commit `.venv/`, Python cache files, IDE settings, or other generated development artifacts; these are covered by `.gitignore`.
