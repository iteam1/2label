# Contributing to 2Label

Thank you for considering contributing to 2Label! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate when interacting with other contributors. Harassment or disrespectful behavior will not be tolerated.

## How to Contribute

There are several ways you can contribute to 2Label:

1. **Bug Reports**: Submit detailed bug reports via GitHub issues
2. **Feature Requests**: Suggest new features or improvements
3. **Documentation**: Improve or create documentation
4. **Code Contributions**: Submit pull requests with bug fixes or new features

## Getting Started

1. Fork the repository on GitHub
2. Clone your forked repository locally
3. Create a new branch for your changes
4. Make your changes
5. Push your changes to your fork
6. Submit a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/2label.git
cd 2label

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

## Pull Request Guidelines

1. Create a branch with a descriptive name
2. Keep changes focused and related
3. Include tests if applicable
4. Ensure your code passes all tests
5. Follow the code style used in the project
6. Write clear commit messages
7. Update documentation if needed

## Adding Support for New Annotation Formats

If you want to add support for a new annotation format:

1. Create a new conversion script in the `convert/` directory
2. Update the documentation in the README.md and docs directory
3. Add example usage in the documentation
4. Add tests for the new format

## Reporting Bugs

When reporting bugs, please include:

1. Description of the issue
2. Steps to reproduce
3. Expected vs. actual behavior
4. System information (OS, Python version, etc.)
5. Any relevant logs or screenshots

## Contact

If you have questions about contributing, please open an issue or contact the project maintainers.

Thank you for your contributions!
