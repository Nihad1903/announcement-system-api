# Announcement Management Platform — API Documentation

> **Base URL:** `http://localhost:8000/api/v1`
>
> **Content-Type:** `application/json` (except file uploads: `multipart/form-data`)
>
> **Authentication:** Bearer token via `Authorization: Bearer <access_token>` header

---

## 1. Response Envelope Formats

### Success (non-paginated)

```json
{
  "status": "success",
  "message": "Human-readable message",
  "data": { ... }
}
```

### Success (paginated list)

```json
{
  "status": "success",
  "data": {
    "count": 42,
    "total_pages": 5,
    "current_page": 1,
    "next": "http://localhost:8000/api/v1/announcements/?page=2",
    "previous": null,
    "results": [ ... ]
  }
}
```

### Error

```json
{
  "status": "error",
  "message": "Validation error.",
  "errors": {
    "field_name": ["Error message 1", "Error message 2"],
    "other_field": ["Error message"]
  }
}
```

### HTTP Status Codes Used

| Code  | Meaning                                |
| ----- | -------------------------------------- |
| `200` | Success                                |
| `201` | Created                                |
| `204` | No Content (successful delete)         |
| `400` | Bad Request / Validation Error         |
| `401` | Unauthorized (missing/invalid token)   |
| `403` | Forbidden (insufficient role)          |
| `404` | Not Found                              |
| `405` | Method Not Allowed                     |
| `429` | Too Many Requests (rate limited)       |
| `500` | Internal Server Error                  |

---

## 2. Authentication & Users

### 2.1 Login

```
POST /api/v1/auth/login/
```

**Auth:** None

**Request Body:**

```json
{
  "username": "manager",
  "password": "manager123"
}
```

**Response `200`:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "manager",
    "email": "manager@example.com",
    "first_name": "System",
    "last_name": "Manager",
    "role": "manager",
    "date_joined": "2026-03-04T09:25:00Z"
  }
}
```

**Error `401`:**

```json
{
  "status": "error",
  "message": "Authentication failed.",
  "errors": {
    "detail": "No active account found with the given credentials"
  }
}
```

---

### 2.2 Register

```
POST /api/v1/auth/register/
```

**Auth:** None

**Request Body:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

| Field              | Type   | Required | Notes                                  |
| ------------------ | ------ | -------- | -------------------------------------- |
| `username`         | string | Yes      | Unique                                 |
| `email`            | string | Yes      | Unique (case-insensitive)              |
| `password`         | string | Yes      | Min 8 chars, Django password validation |
| `password_confirm` | string | Yes      | Must match `password`                  |
| `first_name`       | string | Yes      |                                        |
| `last_name`        | string | Yes      |                                        |
| `role`             | string | No       | `"user"` (default) or `"manager"`      |

**Response `201`:**

```json
{
  "status": "success",
  "message": "Registration successful.",
  "data": {
    "user": {
      "id": 3,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user",
      "date_joined": "2026-03-04T10:00:00Z"
    },
    "tokens": {
      "refresh": "eyJ...",
      "access": "eyJ..."
    }
  }
}
```

---

### 2.3 Refresh Token

```
POST /api/v1/auth/token/refresh/
```

**Auth:** None

**Request Body:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200`:**

```json
{
  "access": "eyJ_new_access_token...",
  "refresh": "eyJ_new_refresh_token..."
}
```

> **Note:** Refresh tokens are rotated — each refresh call returns a NEW refresh token. The old one is blacklisted.

---

### 2.4 Logout

```
POST /api/v1/auth/logout/
```

**Auth:** Bearer token required

**Request Body:**

```json
{
  "refresh": "eyJ_the_refresh_token_to_blacklist..."
}
```

**Response `200`:**

```json
{
  "status": "success",
  "message": "Logged out successfully."
}
```

---

### 2.5 Get Profile

```
GET /api/v1/auth/profile/
```

**Auth:** Bearer token required

**Response `200`:**

```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "id": 1,
    "username": "manager",
    "email": "manager@example.com",
    "first_name": "System",
    "last_name": "Manager",
    "role": "manager",
    "date_joined": "2026-03-04T09:25:00Z"
  }
}
```

---

### 2.6 Change Password

```
PUT /api/v1/auth/change-password/
```

**Auth:** Bearer token required

**Request Body:**

```json
{
  "old_password": "currentPassword123",
  "new_password": "NewStrongPass456!",
  "new_password_confirm": "NewStrongPass456!"
}
```

**Response `200`:**

```json
{
  "status": "success",
  "message": "Password changed successfully."
}
```

---

### 2.7 List Users (Manager Only)

```
GET /api/v1/auth/users/
```

**Auth:** Bearer token required (role: `manager`)

**Response `200`:** Paginated list

```json
{
  "status": "success",
  "data": {
    "count": 2,
    "total_pages": 1,
    "current_page": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "username": "manager",
        "email": "manager@example.com",
        "first_name": "System",
        "last_name": "Manager",
        "role": "manager",
        "is_active": true,
        "date_joined": "2026-03-04T09:25:00Z"
      },
      {
        "id": 2,
        "username": "user",
        "email": "user@example.com",
        "first_name": "Regular",
        "last_name": "User",
        "role": "user",
        "is_active": true,
        "date_joined": "2026-03-04T09:25:00Z"
      }
    ]
  }
}
```

---

## 3. Departments

### 3.1 List Departments

```
GET /api/v1/departments/
```

**Auth:** Bearer token required

**Query Parameters:**

| Param       | Type   | Description                              |
| ----------- | ------ | ---------------------------------------- |
| `search`    | string | Search in `name`, `description`          |
| `ordering`  | string | `name`, `created_at`, `-name`, `-created_at` |
| `page`      | int    | Page number (default: 1)                 |
| `page_size` | int    | Items per page (default: 10, max: 100)   |

**Response `200`:** Paginated list

```json
{
  "status": "success",
  "data": {
    "count": 5,
    "total_pages": 1,
    "current_page": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Finance",
        "description": "Finance and Accounting department",
        "is_active": true,
        "announcement_count": 0,
        "created_at": "2026-03-04T09:25:00Z",
        "updated_at": "2026-03-04T09:25:00Z"
      },
      {
        "id": 2,
        "name": "HR",
        "description": "Human Resources department",
        "is_active": true,
        "announcement_count": 3,
        "created_at": "2026-03-04T09:25:00Z",
        "updated_at": "2026-03-04T09:25:00Z"
      }
    ]
  }
}
```

---

### 3.2 Get Department Detail

```
GET /api/v1/departments/{id}/
```

**Auth:** Bearer token required

**Response `200`:**

```json
{
  "id": 1,
  "name": "IT",
  "description": "Information Technology department",
  "is_active": true,
  "announcement_count": 5,
  "created_at": "2026-03-04T09:25:00Z",
  "updated_at": "2026-03-04T09:25:00Z"
}
```

---

### 3.3 Create Department (Manager Only)

```
POST /api/v1/departments/
```

**Auth:** Bearer token required (role: `manager`)

**Request Body:**

```json
{
  "name": "Legal",
  "description": "Legal and Compliance department",
  "is_active": true
}
```

| Field         | Type    | Required | Notes                                  |
| ------------- | ------- | -------- | -------------------------------------- |
| `name`        | string  | Yes      | Max 100 chars, unique (case-insensitive) |
| `description` | string  | No       | Defaults to `""`                       |
| `is_active`   | boolean | No       | Defaults to `true`                     |

**Response `201`:**

```json
{
  "id": 6,
  "name": "Legal",
  "description": "Legal and Compliance department",
  "is_active": true,
  "announcement_count": 0,
  "created_at": "2026-03-04T10:30:00Z",
  "updated_at": "2026-03-04T10:30:00Z"
}
```

---

### 3.4 Update Department (Manager Only)

```
PUT /api/v1/departments/{id}/
```

**Auth:** Bearer token required (role: `manager`)

**Request Body:** Same fields as create (all required for PUT).

For partial update use:

```
PATCH /api/v1/departments/{id}/
```

(only include fields you want to change)

**Response `200`:** Same as detail response.

---

### 3.5 Delete Department (Manager Only)

```
DELETE /api/v1/departments/{id}/
```

**Auth:** Bearer token required (role: `manager`)

**Response `204`:** No content (success)

**Error `400`** (if linked to announcements):

```json
{
  "status": "error",
  "message": "Validation error.",
  "errors": {
    "detail": "Cannot delete department that has linked announcements. Remove or reassign announcements first."
  }
}
```

---

## 4. Announcement Types

### 4.1 List Announcement Types

```
GET /api/v1/announcement-types/
```

**Auth:** Bearer token required

**Query Parameters:**

| Param       | Type   | Description                              |
| ----------- | ------ | ---------------------------------------- |
| `search`    | string | Search in `name`, `description`          |
| `ordering`  | string | `name`, `created_at`, `-name`, `-created_at` |
| `page`      | int    | Page number                              |
| `page_size` | int    | Items per page (default: 10, max: 100)   |

**Response `200`:** Paginated list

```json
{
  "status": "success",
  "data": {
    "count": 5,
    "total_pages": 1,
    "current_page": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Event",
        "description": "Event announcements",
        "is_active": true,
        "announcement_count": 2,
        "created_at": "2026-03-04T09:25:00Z",
        "updated_at": "2026-03-04T09:25:00Z"
      }
    ]
  }
}
```

---

### 4.2 Get Announcement Type Detail

```
GET /api/v1/announcement-types/{id}/
```

**Auth:** Bearer token required

**Response `200`:**

```json
{
  "id": 1,
  "name": "General",
  "description": "General announcements",
  "is_active": true,
  "announcement_count": 10,
  "created_at": "2026-03-04T09:25:00Z",
  "updated_at": "2026-03-04T09:25:00Z"
}
```

---

### 4.3 Create Announcement Type (Manager Only)

```
POST /api/v1/announcement-types/
```

**Auth:** Bearer token required (role: `manager`)

**Request Body:**

```json
{
  "name": "Newsletter",
  "description": "Company newsletter updates",
  "is_active": true
}
```

| Field         | Type    | Required | Notes                                  |
| ------------- | ------- | -------- | -------------------------------------- |
| `name`        | string  | Yes      | Max 100 chars, unique (case-insensitive) |
| `description` | string  | No       | Defaults to `""`                       |
| `is_active`   | boolean | No       | Defaults to `true`                     |

**Response `201`:** Same as detail response.

---

### 4.4 Update Announcement Type (Manager Only)

```
PUT /api/v1/announcement-types/{id}/
PATCH /api/v1/announcement-types/{id}/
```

**Auth:** Bearer token required (role: `manager`)

**Response `200`:** Same as detail response.

---

### 4.5 Delete Announcement Type (Manager Only)

```
DELETE /api/v1/announcement-types/{id}/
```

**Auth:** Bearer token required (role: `manager`)

**Response `204`:** No content

**Error `400`** (if linked):

```json
{
  "status": "error",
  "message": "Validation error.",
  "errors": {
    "detail": "Cannot delete announcement type that has linked announcements. Remove or reassign announcements first."
  }
}
```

---

## 5. Announcements

### 5.1 List Announcements

```
GET /api/v1/announcements/
```

**Auth:** Bearer token required

**Visibility Rules:**

- **Users (role=user):** Only see announcements with `status=active`
- **Managers (role=manager):** See all announcements (active + inactive), excluding soft-deleted

**Query Parameters:**

| Param            | Type     | Description                                         | Example                                  |
| ---------------- | -------- | --------------------------------------------------- | ---------------------------------------- |
| `department`     | int      | Filter by department ID                             | `?department=1`                          |
| `type`           | int      | Filter by announcement type ID                      | `?type=2`                                |
| `status`         | string   | Filter by status (`active` / `inactive`) — managers only | `?status=active`                    |
| `created_after`  | datetime | Announcements created on/after this date            | `?created_after=2026-01-01T00:00:00Z`   |
| `created_before` | datetime | Announcements created on/before this date           | `?created_before=2026-12-31T23:59:59Z`  |
| `search`         | string   | Keyword search in `title` and `description`         | `?search=policy update`                  |
| `ordering`       | string   | Sort field (prefix `-` for descending)              | `?ordering=-created_at`                  |
| `page`           | int      | Page number (default: 1)                            | `?page=2`                                |
| `page_size`      | int      | Items per page (default: 10, max: 100)              | `?page_size=20`                          |

**Ordering options:** `created_at`, `-created_at`, `updated_at`, `-updated_at`, `title`, `-title`

**Filters can be combined:**

```
GET /api/v1/announcements/?department=1&type=2&search=policy&ordering=-created_at&page=1&page_size=5
```

**Response `200`:** Paginated list

```json
{
  "status": "success",
  "data": {
    "count": 25,
    "total_pages": 5,
    "current_page": 1,
    "next": "http://localhost:8000/api/v1/announcements/?page=2",
    "previous": null,
    "results": [
      {
        "id": 10,
        "title": "New Leave Policy Update",
        "image": "http://localhost:8000/media/announcements/images/2026/03/policy.jpg",
        "status": "active",
        "type": 4,
        "type_name": "Policy Update",
        "department": 2,
        "department_name": "HR",
        "created_by_name": "System Manager",
        "created_at": "2026-03-04T10:00:00Z",
        "updated_at": "2026-03-04T10:00:00Z"
      }
    ]
  }
}
```

> **Note:** The list response is **lightweight** — no `description` field. Fetch the detail endpoint for full content.

---

### 5.2 Get Announcement Detail

```
GET /api/v1/announcements/{id}/
```

**Auth:** Bearer token required

**Response `200`:**

```json
{
  "id": 10,
  "title": "New Leave Policy Update",
  "description": "We are updating the annual leave policy effective April 1, 2026. All employees are entitled to...",
  "image": "http://localhost:8000/media/announcements/images/2026/03/policy.jpg",
  "status": "active",
  "type": {
    "id": 4,
    "name": "Policy Update",
    "description": "Policy and procedure updates",
    "is_active": true,
    "announcement_count": 3,
    "created_at": "2026-03-04T09:25:00Z",
    "updated_at": "2026-03-04T09:25:00Z"
  },
  "department": {
    "id": 2,
    "name": "HR",
    "description": "Human Resources department",
    "is_active": true,
    "announcement_count": 8,
    "created_at": "2026-03-04T09:25:00Z",
    "updated_at": "2026-03-04T09:25:00Z"
  },
  "created_by": 1,
  "created_by_name": "System Manager",
  "created_at": "2026-03-04T10:00:00Z",
  "updated_at": "2026-03-04T10:00:00Z"
}
```

> **Note:** Detail response returns **full nested objects** for `type` and `department`, plus the full `description`.

---

### 5.3 Create Announcement (Manager Only)

```
POST /api/v1/announcements/
```

**Auth:** Bearer token required (role: `manager`)

**Content-Type:** `multipart/form-data` (if uploading image) or `application/json` (no image)

**Request Body:**

```json
{
  "title": "System Maintenance Scheduled",
  "description": "The system will undergo maintenance on March 10, 2026 from 2:00 AM to 6:00 AM UTC.",
  "type": 5,
  "department": 1,
  "status": "active",
  "image": null
}
```

| Field         | Type   | Required | Notes                                   |
| ------------- | ------ | -------- | --------------------------------------- |
| `title`       | string | Yes      | Min 3 chars, max 255 chars              |
| `description` | string | Yes      | Min 10 chars                            |
| `type`        | int    | Yes      | AnnouncementType ID (FK)                |
| `department`  | int    | Yes      | Department ID (FK)                      |
| `status`      | string | No       | `"active"` (default) or `"inactive"`    |
| `image`       | file   | No       | JPG/JPEG/PNG/GIF/WEBP, max 5MB         |

**For file upload, use `multipart/form-data`:**

```
Content-Type: multipart/form-data

title: System Maintenance Scheduled
description: The system will undergo maintenance...
type: 5
department: 1
status: active
image: [binary file data]
```

**Response `201`:** Returns the **detail format** (with nested type/department objects):

```json
{
  "id": 11,
  "title": "System Maintenance Scheduled",
  "description": "The system will undergo maintenance on March 10, 2026 from 2:00 AM to 6:00 AM UTC.",
  "image": null,
  "status": "active",
  "type": {
    "id": 5,
    "name": "Maintenance",
    "description": "System maintenance notices",
    "is_active": true,
    "announcement_count": 1,
    "created_at": "2026-03-04T09:25:00Z",
    "updated_at": "2026-03-04T09:25:00Z"
  },
  "department": {
    "id": 1,
    "name": "IT",
    "description": "Information Technology department",
    "is_active": true,
    "announcement_count": 5,
    "created_at": "2026-03-04T09:25:00Z",
    "updated_at": "2026-03-04T09:25:00Z"
  },
  "created_by": 1,
  "created_by_name": "System Manager",
  "created_at": "2026-03-04T11:00:00Z",
  "updated_at": "2026-03-04T11:00:00Z"
}
```

---

### 5.4 Update Announcement (Manager Only)

```
PUT /api/v1/announcements/{id}/
```

**Auth:** Bearer token required (role: `manager`)

**Full update — all fields required.**

For partial update:

```
PATCH /api/v1/announcements/{id}/
```

Only include the fields you want to change:

```json
{
  "status": "inactive"
}
```

```json
{
  "title": "Updated Title Here",
  "description": "Updated description with at least 10 characters."
}
```

**Response `200`:** Returns the **detail format** (with nested type/department objects).

---

### 5.5 Delete Announcement (Manager Only)

```
DELETE /api/v1/announcements/{id}/
```

**Auth:** Bearer token required (role: `manager`)

**Response `204`:** No content

> **Note:** This performs a **soft delete** — the announcement is marked as `is_deleted=true` and no longer appears in any API response, but remains in the database.

---

## 6. Authentication Flow Guide

### Initial Setup

```
1. POST /api/v1/auth/login/  →  Store both `access` and `refresh` tokens
2. Use `access` token in all subsequent requests:
   Authorization: Bearer <access_token>
```

### Token Refresh (when access token expires)

```
1. Catch HTTP 401 response
2. POST /api/v1/auth/token/refresh/  with { "refresh": "<refresh_token>" }
3. Store the NEW access AND refresh tokens (rotation is enabled)
4. Retry the original failed request with the new access token
```

### Token Lifetime

| Token   | Lifetime   | Configurable via                          |
| ------- | ---------- | ----------------------------------------- |
| Access  | 60 minutes | `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` env var |
| Refresh | 7 days     | `JWT_REFRESH_TOKEN_LIFETIME_DAYS` env var |

### JWT Claims (decoded access token payload)

```json
{
  "token_type": "access",
  "exp": 1741089600,
  "iat": 1741086000,
  "jti": "unique-token-id",
  "user_id": 1,
  "username": "manager",
  "role": "manager"
}
```

> The `role` claim is available in the JWT payload for client-side role checks without an extra API call.

---

## 7. Role-Based Access Summary

| Endpoint                             | `user` role        | `manager` role |
| ------------------------------------ | :----------------: | :------------: |
| `POST /auth/login/`                  | ✅                 | ✅             |
| `POST /auth/register/`              | ✅                 | ✅             |
| `POST /auth/token/refresh/`         | ✅                 | ✅             |
| `POST /auth/logout/`                | ✅                 | ✅             |
| `GET /auth/profile/`                | ✅                 | ✅             |
| `PUT /auth/change-password/`        | ✅                 | ✅             |
| `GET /auth/users/`                  | ❌ 403             | ✅             |
| `GET /announcements/`               | ✅ (active only)   | ✅ (all)       |
| `GET /announcements/{id}/`          | ✅ (active only)   | ✅             |
| `POST /announcements/`              | ❌ 403             | ✅             |
| `PUT/PATCH /announcements/{id}/`    | ❌ 403             | ✅             |
| `DELETE /announcements/{id}/`       | ❌ 403             | ✅             |
| `GET /departments/`                 | ✅                 | ✅             |
| `GET /departments/{id}/`            | ✅                 | ✅             |
| `POST /departments/`                | ❌ 403             | ✅             |
| `PUT/PATCH /departments/{id}/`      | ❌ 403             | ✅             |
| `DELETE /departments/{id}/`         | ❌ 403             | ✅             |
| `GET /announcement-types/`          | ✅                 | ✅             |
| `GET /announcement-types/{id}/`     | ✅                 | ✅             |
| `POST /announcement-types/`         | ❌ 403             | ✅             |
| `PUT/PATCH /announcement-types/{id}/` | ❌ 403           | ✅             |
| `DELETE /announcement-types/{id}/`  | ❌ 403             | ✅             |

---

## 8. Rate Limiting

| Client Type          | Limit              |
| -------------------- | ------------------ |
| Anonymous (no token) | 100 requests/hour  |
| Authenticated user   | 1000 requests/hour |

When exceeded, response is `429`:

```json
{
  "status": "error",
  "message": "Request was throttled. Expected available in 58 seconds.",
  "errors": {
    "detail": "Request was throttled. Expected available in 58 seconds."
  }
}
```

---

## 9. Seeded Test Accounts

| Username  | Password     | Role      |
| --------- | ------------ | --------- |
| `manager` | `manager123` | `manager` |
| `user`    | `user12345`  | `user`    |

### Seeded Departments

| ID | Name       |
| -- | ---------- |
| 1  | IT         |
| 2  | HR         |
| 3  | Marketing  |
| 4  | Finance    |
| 5  | Operations |

### Seeded Announcement Types

| ID | Name          |
| -- | ------------- |
| 1  | General       |
| 2  | Urgent        |
| 3  | Event         |
| 4  | Policy Update |
| 5  | Maintenance   |

> **Note:** Seeded IDs may vary. Use the GET list endpoints to fetch actual IDs.

---

## 10. Image Upload Notes

- Accepted formats: `jpg`, `jpeg`, `png`, `gif`, `webp`
- Max file size: **5 MB**
- Images are served at: `{BASE_URL}/media/announcements/images/YYYY/MM/filename.ext`
- When returned in JSON, `image` is a full URL string or `null`
- To **remove** an existing image on update, send `"image": null` or `"image": ""`

---

## 11. Common Validation Error Shapes

**Field-level errors:**

```json
{
  "status": "error",
  "message": "Validation error.",
  "errors": {
    "title": ["This field is required."],
    "description": ["Description must be at least 10 characters long."],
    "email": ["A user with this email already exists."]
  }
}
```

**Non-field errors:**

```json
{
  "status": "error",
  "message": "Validation error.",
  "errors": {
    "non_field_errors": ["Passwords do not match."]
  }
}
```

**Permission denied:**

```json
{
  "status": "error",
  "message": "Permission denied.",
  "errors": {
    "detail": "Only managers can modify this resource."
  }
}
```

**Not found:**

```json
{
  "status": "error",
  "message": "Resource not found.",
  "errors": {
    "detail": "Not found."
  }
}
```
