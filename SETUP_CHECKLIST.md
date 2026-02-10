# Post-Template Setup Checklist

After running `setup_template.py`, use this checklist to complete your project setup:

## Immediate Tasks

- [ ] Run `uv sync` to install dependencies
- [ ] Review and test: `uv run pytest`
- [ ] Check linting: `uv run ruff check .`

## Documentation

- [ ] Update `README.md` with your project description
- [ ] Update the "Features" section
- [ ] Update the "Project Structure" section with your package names
- [ ] Update "Package Contents" section to describe your packages
- [ ] Update links and repository URLs

## Configuration Files

- [ ] Review each `packages/*/pyproject.toml`:
  - [ ] Update `description` field
  - [ ] Add proper `authors` and `license`
  - [ ] Review dependencies
- [ ] Review `.github/workflows/*.yml`:
  - [ ] Update Python versions if needed
  - [ ] Configure any secrets for publishing
- [ ] Update `LICENSE` file if not using MIT

## Git & GitHub

- [ ] Initialize git: `git init` (if not already done)
- [ ] Add files: `git add .`
- [ ] Make first commit: `git commit -m "Initial commit"`
- [ ] Create repository on GitHub
- [ ] Push to GitHub: `git push -u origin main`
- [ ] Mark repository as a template in GitHub Settings (optional)

## Development

- [ ] Remove sample packages or customize them:
  - [ ] Delete `packages/my-library` or customize it
  - [ ] Delete `packages/my-app` or customize it
  - [ ] Delete `packages/my-cli` or customize it
- [ ] Add your first package using the instructions in `README.md`
- [ ] Write tests for your packages
- [ ] Set up package publishing (see "Publishing a Package" in README.md)

## GitHub Actions & Publishing (Optional)

- [ ] Set up PyPI trusted publishing:
  - [ ] Create PyPI account if needed
  - [ ] Go to PyPI Settings → Token management
  - [ ] Create "GitHub" publisher for each package
  - [ ] See [PyPI docs](https://docs.pypi.org/trusted-publishers/)
- [ ] Configure GitHub Actions to have permission to publish

## Cleanup

- [ ] Delete this checklist when complete
- [ ] Delete `setup_template.py` (already removed by setup script)
- [ ] Delete `TEMPLATE.md` if you don't need template instructions

## Testing

- [ ] [ ] Create a test file: `uv run pytest`
- [ ] [ ] Verify linting passes: `uv run ruff check . && uv run ruff format --check .`
- [ ] [ ] Test adding a new package following README instructions
- [ ] [ ] Test importing packages between each other

## Documentation

- [ ] [ ] Write a CONTRIBUTING.md if you plan to accept contributions
- [ ] [ ] Add CHANGELOG.md for tracking releases
- [ ] [ ] Create a CODE_OF_CONDUCT.md if accepting contributions

That's it! Your Python monorepo is ready to use. Happy coding!
