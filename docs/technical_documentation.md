# API Documentation - CloudSync API v2.0

## Overview

CloudSync API is a RESTful API that enables developers to integrate cloud storage functionality into their applications. This documentation covers authentication, endpoints, request/response formats, and best practices.

## Base URL

```
https://api.cloudsync.com/v2
```

## Authentication

### API Keys

All API requests require authentication using API keys. You can generate API keys from your dashboard.

**Authentication Header:**
```
Authorization: Bearer YOUR_API_KEY
```

### OAuth 2.0

For user-specific operations, use OAuth 2.0 authentication.

**Authorization URL:**
```
https://auth.cloudsync.com/oauth/authorize
```

**Token URL:**
```
https://auth.cloudsync.com/oauth/token
```

**Scopes:**
- `storage:read` - Read access to stored files
- `storage:write` - Write access to stored files
- `storage:delete` - Delete files
- `user:profile` - Access user profile information
- `sharing:manage` - Manage file sharing

## Rate Limiting

- **Free Tier**: 100 requests per hour
- **Pro Tier**: 1,000 requests per hour
- **Enterprise**: Custom limits

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1699564800
```

## Endpoints

### File Management

#### Upload File

Upload a new file to cloud storage.

**Endpoint:** `POST /files/upload`

**Request:**
```bash
curl -X POST https://api.cloudsync.com/v2/files/upload \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/file.pdf" \
  -F "folder_id=folder_123" \
  -F "is_public=false"
```

**Parameters:**
- `file` (required) - The file to upload
- `folder_id` (optional) - Destination folder ID
- `is_public` (optional) - Make file publicly accessible
- `tags` (optional) - Comma-separated tags

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "file_id": "file_abc123",
    "name": "file.pdf",
    "size": 1048576,
    "mime_type": "application/pdf",
    "url": "https://cdn.cloudsync.com/files/abc123",
    "created_at": "2024-11-15T10:30:00Z",
    "modified_at": "2024-11-15T10:30:00Z"
  }
}
```

#### Get File

Retrieve file metadata and download URL.

**Endpoint:** `GET /files/{file_id}`

**Request:**
```bash
curl -X GET https://api.cloudsync.com/v2/files/file_abc123 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "file_id": "file_abc123",
    "name": "file.pdf",
    "size": 1048576,
    "mime_type": "application/pdf",
    "url": "https://cdn.cloudsync.com/files/abc123",
    "download_url": "https://cdn.cloudsync.com/download/abc123?token=xyz",
    "thumbnail_url": "https://cdn.cloudsync.com/thumbnails/abc123",
    "is_public": false,
    "folder_id": "folder_123",
    "tags": ["important", "work"],
    "created_at": "2024-11-15T10:30:00Z",
    "modified_at": "2024-11-15T10:30:00Z",
    "accessed_at": "2024-11-16T08:15:00Z"
  }
}
```

#### Delete File

Permanently delete a file.

**Endpoint:** `DELETE /files/{file_id}`

**Request:**
```bash
curl -X DELETE https://api.cloudsync.com/v2/files/file_abc123 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

#### List Files

List all files in your storage or a specific folder.

**Endpoint:** `GET /files`

**Query Parameters:**
- `folder_id` (optional) - Filter by folder
- `limit` (optional) - Results per page (default: 50, max: 100)
- `offset` (optional) - Pagination offset
- `sort` (optional) - Sort by: `name`, `size`, `created_at`, `modified_at`
- `order` (optional) - Order: `asc` or `desc`
- `search` (optional) - Search in file names

**Request:**
```bash
curl -X GET "https://api.cloudsync.com/v2/files?limit=10&sort=created_at&order=desc" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "file_abc123",
        "name": "document.pdf",
        "size": 1048576,
        "mime_type": "application/pdf",
        "created_at": "2024-11-15T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 150,
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
  }
}
```

### Folder Management

#### Create Folder

Create a new folder.

**Endpoint:** `POST /folders`

**Request:**
```bash
curl -X POST https://api.cloudsync.com/v2/folders \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Documents",
    "parent_id": null,
    "color": "#FF5733"
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "folder_id": "folder_123",
    "name": "My Documents",
    "parent_id": null,
    "color": "#FF5733",
    "file_count": 0,
    "size": 0,
    "created_at": "2024-11-16T09:00:00Z"
  }
}
```

### Sharing

#### Create Share Link

Create a shareable link for a file.

**Endpoint:** `POST /files/{file_id}/share`

**Request:**
```bash
curl -X POST https://api.cloudsync.com/v2/files/file_abc123/share \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "expires_at": "2024-12-31T23:59:59Z",
    "password": "secret123",
    "max_downloads": 10
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "share_id": "share_xyz789",
    "url": "https://cloudsync.com/s/xyz789",
    "expires_at": "2024-12-31T23:59:59Z",
    "download_count": 0,
    "max_downloads": 10,
    "password_protected": true
  }
}
```

### User Management

#### Get User Info

Get information about the authenticated user.

**Endpoint:** `GET /user/me`

**Request:**
```bash
curl -X GET https://api.cloudsync.com/v2/user/me \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "user_456",
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "pro",
    "storage_used": 5368709120,
    "storage_limit": 107374182400,
    "created_at": "2023-01-15T10:00:00Z"
  }
}
```

## Webhooks

Set up webhooks to receive real-time notifications about events.

### Event Types

- `file.uploaded` - New file uploaded
- `file.deleted` - File deleted
- `file.shared` - File shared
- `folder.created` - New folder created
- `storage.limit_reached` - Storage limit reached

### Webhook Payload

```json
{
  "event": "file.uploaded",
  "timestamp": "2024-11-16T10:30:00Z",
  "data": {
    "file_id": "file_abc123",
    "name": "document.pdf",
    "size": 1048576,
    "user_id": "user_456"
  }
}
```

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid API key",
    "details": "The provided API key is not valid or has expired"
  }
}
```

### Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## Best Practices

### 1. Error Handling

Always implement proper error handling:

```python
import requests

response = requests.get(
    'https://api.cloudsync.com/v2/files',
    headers={'Authorization': f'Bearer {api_key}'}
)

if response.status_code == 200:
    data = response.json()
    # Process data
elif response.status_code == 429:
    # Handle rate limiting
    retry_after = response.headers.get('Retry-After')
    # Wait and retry
else:
    # Handle other errors
    error = response.json()
    print(f"Error: {error['error']['message']}")
```

### 2. Pagination

Always paginate when retrieving large lists:

```python
offset = 0
limit = 100
all_files = []

while True:
    response = requests.get(
        f'https://api.cloudsync.com/v2/files?offset={offset}&limit={limit}',
        headers={'Authorization': f'Bearer {api_key}'}
    )
    data = response.json()
    all_files.extend(data['data']['files'])
    
    if not data['data']['pagination']['has_more']:
        break
    
    offset += limit
```

### 3. Webhook Verification

Verify webhook signatures to ensure authenticity:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## SDKs

Official SDKs are available for:

- **Python**: `pip install cloudsync-sdk`
- **JavaScript**: `npm install @cloudsync/sdk`
- **Ruby**: `gem install cloudsync`
- **PHP**: `composer require cloudsync/sdk`

### Python SDK Example

```python
from cloudsync import CloudSyncClient

client = CloudSyncClient(api_key='YOUR_API_KEY')

# Upload file
file = client.files.upload(
    file_path='/path/to/file.pdf',
    folder_id='folder_123'
)

# List files
files = client.files.list(limit=10)

# Create share link
share = client.files.create_share(
    file_id=file.id,
    expires_at='2024-12-31T23:59:59Z'
)
```

## Support

- **Documentation**: https://docs.cloudsync.com
- **Support Email**: api-support@cloudsync.com
- **Status Page**: https://status.cloudsync.com
- **Community Forum**: https://community.cloudsync.com

## Changelog

### Version 2.0 (November 2024)
- Added folder color customization
- Improved upload performance
- Added webhook support
- New sharing options

### Version 1.5 (June 2024)
- Added file tagging
- Improved search functionality
- Added thumbnail generation

### Version 1.0 (January 2024)
- Initial release

