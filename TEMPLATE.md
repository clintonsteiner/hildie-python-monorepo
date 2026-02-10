# Using This as a GitHub Template

This is a GitHub template for creating new Python monorepos with `uv` workspaces.

## Quick Setup

### Option 1: Using the Setup Script (Recommended)

1. Click "Use this template" on GitHub to create a new repository
2. Clone your new repository
3. Run the setup script:
   ```bash
   python setup_template.py
   ```
4. Follow the prompts to customize your project

### Option 2: Manual Setup

1. Click "Use this template" on GitHub
2. Clone your new repository
3. Replace the following in all files:
   - `my-library` → your library name
   - `my-app` → your app name
   - `my-cli` → your CLI name
   - `Developer` → your name
   - `dev@example.com` → your email
   - `MIT` → your license

## After Using the Template

1. Update `README.md` with your project description
2. Update package descriptions in each `pyproject.toml`
3. Customize the GitHub Actions workflows if needed
4. Update the LICENSE file
5. Remove the sample packages and add your own

## Adding Your First Package

Follow the instructions in the README.md under "Creating a New Package".

## Important Files to Customize

- `README.md` - Project overview
- `pyproject.toml` - Root workspace config and authors
- `packages/*/pyproject.toml` - Individual package metadata
- `.github/workflows/*.yml` - CI/CD configuration
- `LICENSE` - License file (if not MIT)

## Next Steps

1. Read the full `README.md` for detailed documentation
2. Check `QUICKSTART.md` for common commands
3. Customize the workflow files in `.github/workflows/`
4. Add your own packages to `packages/`
