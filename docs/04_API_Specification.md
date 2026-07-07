# 04 - API Specification

> **Project:** AI Resume Analyzer & Job Match Platform
> **Version:** v1

---

# Purpose

This document defines all REST API endpoints, request/response standards, authentication, validation, and error handling.

Base URL:

```
/api/v1
```

All APIs must return JSON.

---

# API Standards

- RESTful API Design
- JSON Request/Response
- JWT Authentication
- Versioned APIs
- Proper HTTP Status Codes
- Input Validation
- Consistent Error Responses

---

# Authentication

Protected endpoints require:

```
Authorization: Bearer <JWT_TOKEN>
```

Public Endpoints:

- Register
- Login
- Forgot Password
- Reset Password

All other endpoints require authentication.

---

# Authentication APIs

## Register

```
POST /auth/register
```

Request

```json
{
  "full_name": "",
  "email": "",
  "password": ""
}
```

Response

```
201 Created
```

---

## Login

```
POST /auth/login
```

Returns

- Access Token
- Refresh Token
- User Details

---

## Logout

```
POST /auth/logout
```

---

## Profile

```
GET /users/profile
```

---

## Update Profile

```
PUT /users/profile
```

---

# Resume APIs

## Upload Resume

```
POST /resumes/upload
```

Supports:

- PDF
- DOCX

---

## Get Resumes

```
GET /resumes
```

---

## Resume Details

```
GET /resumes/{id}
```

---

## Delete Resume

```
DELETE /resumes/{id}
```

---

# Resume Analysis

## Analyze Resume

```
POST /analysis/{resume_id}
```

Returns

- ATS Score
- Resume Score
- Skills
- Experience
- Education
- Suggestions

---

## Analysis History

```
GET /analysis/history
```

---

## Analysis Details

```
GET /analysis/{id}
```

---

# Job Matching

## Match Resume

```
POST /jobs/match
```

Request

```json
{
  "resume_id": "",
  "job_description": ""
}
```

Returns

- Match %
- Missing Skills
- Matching Skills
- Required Keywords

---

## Match History

```
GET /jobs/history
```

---

# AI Assistant

## Resume Review

```
POST /ai/review
```

---

## Generate Cover Letter

```
POST /ai/cover-letter
```

---

## Improve Summary

```
POST /ai/summary
```

---

## Improve Projects

```
POST /ai/projects
```

---

## Interview Questions

```
POST /ai/interview
```

---

# Dashboard

## Dashboard Overview

```
GET /dashboard
```

Returns

- Total Resumes
- Average ATS Score
- Latest Reports
- Recent Matches
- Activity Summary

---

# Admin APIs

## Get Users

```
GET /admin/users
```

---

## System Analytics

```
GET /admin/analytics
```

---

## Upload Statistics

```
GET /admin/uploads
```

---

## System Logs

```
GET /admin/logs
```

---

# Response Format

Success

```json
{
  "success": true,
  "message": "Request successful",
  "data": {}
}
```

Error

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": []
}
```

---

# HTTP Status Codes

| Code | Meaning |
|------|---------|
|200|Success|
|201|Created|
|204|Deleted|
|400|Bad Request|
|401|Unauthorized|
|403|Forbidden|
|404|Not Found|
|409|Conflict|
|422|Validation Error|
|429|Too Many Requests|
|500|Internal Server Error|

---

# Validation Rules

- Validate every request.
- Reject unsupported file types.
- Maximum upload size: 10 MB.
- Sanitize user input.
- Validate email format.
- Enforce strong passwords.
- Reject malformed JSON.

---

# API Security

- JWT Authentication
- HTTPS Only
- Rate Limiting
- CORS Protection
- Secure Headers
- Input Sanitization
- File Validation

---

# API Versioning

Current Version

```
/api/v1
```

Future versions

```
/api/v2
/api/v3
```

Older versions should remain backward compatible when possible.

---

# Acceptance Criteria

- REST compliant
- Proper status codes
- Consistent JSON responses
- Complete validation
- Secure endpoints
- Well documented
- Production ready

---

# Agent Instructions

The AI coding agent must:

- Implement all endpoints under `/api/v1`.
- Follow REST principles strictly.
- Validate every request using Pydantic.
- Return consistent response formats.
- Never expose sensitive information.
- Protect private endpoints with JWT.
- Document endpoints using FastAPI OpenAPI/Swagger.
- Write clean, modular API controllers.