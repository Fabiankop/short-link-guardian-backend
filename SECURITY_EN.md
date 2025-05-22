# Security Rules for the Project

## 1. SQL Injection Prevention

- **Always use SQLAlchemy ORM**: Never build SQL queries using string concatenation.
- **Use parameters in queries**: Use `select(Model).where(Model.column == parameter)` instead of string interpolation.
- **Validate and sanitize inputs**: All inputs must be validated using Pydantic.
- **Avoid dynamic queries**: Do not generate SQL queries based on unvalidated inputs.

## 2. Authentication and Authorization

- **Store passwords with hash**: Use bcrypt for secure storage.
- **Implement JWT with short expiration time**: Tokens should not last more than 30 minutes.
- **Verification for each endpoint**: Use dependency decorators to validate permissions.
- **Clear separation of roles**: Implement role-based restrictions for all actions.
- **Session invalidation**: Allow token revocation in case of compromise.

## 3. Data Validation

- **Validate all inputs**: Use Pydantic models to validate every input.
- **Limit input sizes**: Establish clear limits to prevent DoS attacks.
- **Sanitize URLs**: Especially validate and sanitize received URLs.
- **Data format validation**: Apply strict rules for emails, codes, and other formats.

## 4. Protection Against Common Web Attacks

- **Implement CORS correctly**: Restrict allowed origins.
- **Prevent XSS**: Do not allow HTML rendering from user inputs.
- **Defense against CSRF**: Implement anti-CSRF tokens for sensitive operations.
- **HTTP security headers**: Configure Content-Security-Policy, X-XSS-Protection, etc.

## 5. Sensitive Data Management

- **Do not store unnecessary sensitive data**: Minimize stored information.
- **Encrypt sensitive data**: Use strong algorithms to encrypt sensitive information.
- **Environment variables for secrets**: Never include secrets in the code.
- **Data retention policy**: Delete data that is no longer needed.

## 6. Rate Limiting

- **Limit requests by IP**: Prevent API abuse.
- **Stricter restrictions for sensitive endpoints**: Enhanced protection for login/registration.
- **Monitor suspicious patterns**: Detect and block anomalous behaviors.

## 7. Logging and Monitoring

- **Log authentication attempts**: Especially failed ones.
- **Audit sensitive changes**: Log modifications to important data.
- **Do not include sensitive information in logs**: Never log passwords or tokens.
- **Active security monitoring**: Implement alerts for anomalous behaviors.

## 8. Deployment Security

- **Regular updates**: Keep all dependencies updated.
- **Vulnerability scanning**: Use tools like Safety or Snyk.
- **Secure secrets management**: Use services like Vault for secrets.
- **Mandatory HTTPS**: Never allow connections without TLS.

## 9. Redirections and Short URLs

- **Validate all URLs before redirecting**: Avoid redirections to malicious sites.
- **Limit allowed domains**: Restrict to known and secure domains.
- **Scan URLs against blacklists**: Verify against phishing databases.
- **Monitor abuse patterns**: Detect attempts to use the service for phishing.

## 10. Error Handling

- **Do not expose sensitive information in errors**: Use generic messages for clients.
- **Detailed error logging**: Maintain detailed logs only internally.
- **Consistent responses**: Maintain similar response times to prevent timing attacks.

## Technical Implementation

### SQL Injection Prevention

```python
# CORRECT: Use ORM
result = await db.execute(select(User).where(User.email == email))

# INCORRECT: Never do this
result = await db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### Secure Authentication

```python
# CORRECT: Store passwords with hash
hashed_password = pwd_context.hash(password)

# CORRECT: Verify passwords
is_valid = pwd_context.verify(plain_password, hashed_password)
```

### Validation with Pydantic

```python
class URLCreate(BaseModel):
    original_url: HttpUrl  # Automatic URL validation

    @validator('original_url')
    def validate_url(cls, v):
        # Custom additional validation
        if "malicious-domain.com" in str(v):
            raise ValueError("URL not allowed")
        return v
```

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security Considerations](https://docs.sqlalchemy.org/en/14/core/engines.html#engine-disposal)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
