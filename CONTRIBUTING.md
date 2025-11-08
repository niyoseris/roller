# Contributing to Agentic Trend Video Creator

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/agentic/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (OS, Python version)
   - Relevant logs or screenshots

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and why it would be useful
3. Include examples or mockups if possible

### Pull Requests

1. **Fork the repository**
```bash
git clone https://github.com/yourusername/agentic.git
cd agentic
```

2. **Create a feature branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make your changes**
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation as needed

4. **Test your changes**
```bash
# Run the application
python3 main.py

# Test specific features
python3 tests/test_*.py
```

5. **Commit your changes**
```bash
git add .
git commit -m "feat: Add amazing feature"
```

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

6. **Push and create PR**
```bash
git push origin feature/amazing-feature
```

Then open a Pull Request on GitHub with:
- Clear title and description
- Reference any related issues
- Screenshots/videos if UI changes

## Development Setup

1. **Install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Add your API keys to .env
```

3. **Run locally**
```bash
python3 main.py
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Comment complex logic

## Testing

- Test manually with dashboard at `http://localhost:5001`
- Verify video creation works
- Check logs for errors
- Test with different trend inputs

## Documentation

- Update README.md if adding major features
- Add comments to complex code
- Update docs/ folder if needed
- Include examples in docstrings

## Questions?

- Open an issue for discussion
- Check existing issues and PRs
- Read the full documentation in README.md

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers
- Celebrate contributions

Thank you for contributing! 🚀
