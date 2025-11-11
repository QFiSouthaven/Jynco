# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Video Foundry, please report it by emailing the maintainers or opening a private security advisory on GitHub.

**Please do not report security vulnerabilities through public GitHub issues.**

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Security Best Practices

When deploying Video Foundry:

1. **Never commit `.env` files** - Use environment variables
2. **Rotate secrets regularly** - Change API keys and passwords periodically
3. **Use strong SECRET_KEY** - Generate with `openssl rand -hex 32`
4. **Enable HTTPS** - Always use SSL/TLS in production
5. **Limit CORS origins** - Only allow trusted domains
6. **Update dependencies** - Keep all packages up to date
7. **Use IAM roles** - For AWS, use roles instead of access keys when possible
8. **Monitor logs** - Watch for suspicious activity

## Known Security Considerations

- Default Docker credentials (`postgres:password`, `guest:guest`) are for local development only
- Mock AI adapter is for testing - use real API keys in production
- SECRET_KEY must be changed from default value in production
- RabbitMQ and Redis should be behind a firewall in production

## Disclosure Policy

We follow responsible disclosure practices. Security researchers should:
1. Report issues privately
2. Allow reasonable time for fixes
3. Avoid disclosing details publicly until patched

Thank you for helping keep Video Foundry secure!
