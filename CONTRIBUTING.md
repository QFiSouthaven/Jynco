# Contributing to Video Foundry

Thank you for your interest in contributing to Video Foundry! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Jynco.git`
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/QFiSouthaven/Jynco.git
cd Jynco

# Copy environment template
cp .env.example .env

# Start services with Docker
docker-compose up --build

# Run tests
cd tests
pip install -r requirements.txt
pytest -v
```

## Code Style

### Python (Backend & Workers)
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Run `black` for formatting
- Use `flake8` for linting

### TypeScript/React (Frontend)
- Follow ESLint rules
- Use functional components
- Add TypeScript types
- Use meaningful variable names

### Git Commits
- Use clear, descriptive commit messages
- Reference issues when applicable
- Format: `Add feature X` or `Fix bug in Y`

## Testing

All contributions should include tests:

### Backend Tests
```bash
cd tests
pytest tests/e2e/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Pull Request Process

1. **Update Documentation**: If you change functionality, update relevant docs
2. **Add Tests**: Include tests for new features
3. **Pass CI**: Ensure all checks pass
4. **Describe Changes**: Write a clear PR description
5. **Link Issues**: Reference related issues

## Pull Request Template

```markdown
## Description
[Describe your changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Local testing completed
- [ ] Unit tests added/updated
- [ ] E2E tests added/updated
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No breaking changes (or documented)
```

## Reporting Issues

### Bug Reports
Include:
- Video Foundry version
- Operating system
- Docker version
- Steps to reproduce
- Expected vs actual behavior
- Logs/screenshots

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Impact on existing features

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

## Questions?

- Open an issue for discussion
- Join community discussions
- Review existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Video Foundry! 🎬
