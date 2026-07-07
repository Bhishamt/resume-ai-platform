# 08 - Security Guidelines

> **Project:** AI Resume Analyzer & Job Match Platform
> **Version:** 1.0

---

# Purpose

This document defines the minimum security standards for the application. Every feature must follow these guidelines.

---

# Security Principles

- Secure by Default
- Least Privilege
- Defense in Depth
- Zero Trust
- Never Trust User Input

---

# Authentication

- JWT Access Token
- Refresh Token
- Secure Logout
- Password Reset
- Session Expiration

---

# Authorization

Roles

- Guest
- User
- Admin

Users can access only their own resources.

Admins have elevated permissions.

---

# Password Policy

Minimum requirements:

- 8+ characters
- Uppercase
- Lowercase
- Number
- Special Character

Passwords must be hashed using **bcrypt**.

Never store plain text passwords.

---

# Input Validation

Validate:

- Email
- Password
- File uploads
- Form inputs
- JSON payloads
- URL parameters

Reject invalid requests.

---

# File Upload Security

Allowed Types

- PDF
- DOCX

Maximum Size

- 10 MB

Validate:

- MIME type
- Extension
- File size

Reject executable files.

---

# API Security

- JWT Authentication
- HTTPS Only
- Rate Limiting
- CORS Protection
- Request Validation
- Response Validation

---

# Data Protection

- Encrypt sensitive data
- Never expose internal IDs unnecessarily
- Protect user privacy
- Use secure database connections

---

# Environment Variables

Store securely:

- Database URL
- JWT Secret
- API Keys
- SMTP Credentials

Never commit secrets to Git.

---

# Error Handling

Do not expose:

- Stack traces
- SQL errors
- API keys
- Internal paths

Return user-friendly error messages.

---

# Logging

Log:

- Login attempts
- Failed authentication
- File uploads
- Admin actions
- API failures

Never log:

- Passwords
- JWT tokens
- API keys
- Personal sensitive data

---

# Dependencies

- Keep packages updated
- Remove unused dependencies
- Scan for vulnerabilities regularly

---

# Security Checklist

Before deployment:

- JWT configured
- Password hashing enabled
- HTTPS enforced
- Environment variables configured
- Input validation complete
- File upload secured
- Rate limiting enabled
- CORS configured

---

# Acceptance Criteria

- No hardcoded secrets
- Secure authentication
- Protected API endpoints
- Safe file uploads
- Validated user input
- Production-ready security

---

# Agent Instructions

The AI coding agent must:

- Follow OWASP best practices.
- Never hardcode secrets.
- Validate all user input.
- Protect all private routes.
- Hash passwords with bcrypt.
- Use environment variables for sensitive data.
- Secure file uploads and API endpoints.