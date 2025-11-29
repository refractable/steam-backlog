# Contributing to Backpile

Thanks for your interest in contributing! This document outlines how to get started.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/refractable/backpile.git
   cd backpile
   ```
3. Install dependencies:
   ```bash
   pip install requests rich
   ```
4. Set up your config by running `python main.py` and following the setup wizard

## Development

### Project Structure

```
main.py                 # Entry point
backlog/
  __init__.py           # Package constants
  api.py                # Steam API functions
  cache.py              # Local data storage
  cli.py                # Command-line interface
  display.py            # Output formatting
  export.py             # CSV/JSON export
  utils.py              # Helper functions
```

### Running the Tool

```bash
python main.py --help
python main.py --sync
python main.py --stats
```

### Code Style

- Use [Black](https://github.com/psf/black) for formatting (88 char line length)
- Use meaningful variable and function names
- Add docstrings to new functions
- Keep functions focused and reasonably sized

## How to Contribute

### Reporting Bugs

- Check existing issues first to avoid duplicates
- Use the Bug Report template
- Include steps to reproduce, expected vs actual behavior, and error messages

### Suggesting Features

- Use the Feature Request template
- Explain the use case and why it would be useful
- Be open to discussion on implementation

### Submitting Changes

1. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Test your changes thoroughly
4. Commit with clear messages:
   ```bash
   git commit -m "Add feature: description of what it does"
   ```
5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Open a Pull Request with a clear description of your changes

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Update the README if adding new commands or features
- Test with your own Steam library before submitting
- Be responsive to feedback and questions

## Ideas for Contributions

Here are some areas where contributions would be welcome:

- **New filters** - additional ways to filter the library
- **Sorting options** - new sort criteria
- **Display improvements** - better formatting or new views
- **Documentation** - improve README, add examples
- **Bug fixes** - check the issues tab
- **Tests** - add unit tests

## Questions?

Open an issue with the Question template if you're unsure about anything.
