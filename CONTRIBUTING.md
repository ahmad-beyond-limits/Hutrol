# Contributing to Hutrol

First off, thank you for considering contributing to Hutrol! It's people like you that make Hutrol such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check if there's already an [issue](https://github.com/ahmad-beyond-limits/Hutrol/issues) for it. If not, feel free to open a new one!

## Setting up your environment

1. Fork the repository on GitHub.
2. Clone your fork locally.
3. Install dependencies using `uv` (the lightning-fast Python package manager):
   ```bash
   uv sync
   ```
4. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes in the `src/` directory.
3. Test your changes locally to ensure everything works (including the CLI commands).

## Building the Executable

If you modify the CLI or core logic and need to test the `.exe` build:
```bash
uv run pyinstaller --onefile --name hutrol src/human/cli/main.py
```
To generate the Windows Installer, compile `scripts/build_installer.iss` using Inno Setup.

## Submitting a Pull Request

1. Commit your changes with clear, descriptive commit messages.
2. Push your branch to your fork on GitHub.
3. Open a Pull Request against the `main` branch of the original repository.
4. Provide a clear description of the problem you've solved or the feature you've added.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms. Let's build a welcoming and inclusive community together!
