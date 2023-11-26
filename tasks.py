from invoke import task


@task
def lint(c):
    print("Checking code styling...")
    c.run("flake8 --exclude=.venv .")
    c.run("black --check --exclude='.venv/' .")


@task
def spellcheck(c):
    print("Running spell check...")
    c.run("codespell --skip=.venv .")


@task(pre=[lint, spellcheck])
def test(c):
    print("Testing the project...")


@task
def lintfix(c):
    print("Linting code...")
    c.run("black --exclude='.venv/' .")
