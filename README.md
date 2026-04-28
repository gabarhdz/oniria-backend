# Oniria Backend

Backend API for **Oniria**, a mental health and sleep-focused platform built with **Django**, **Django REST Framework**, **JWT authentication**, **WebSockets**, and **AI-assisted services**.

It supports:

- user accounts and profile management
- psychologist applications and psychologist profiles
- custom forms and due tests assigned to patients
- community spaces with posts, replies, likes, and dislikes
- direct chat between users and psychologists
- real-time notifications
- AI-powered conversation and dream-related assistance

## Project Overview

Oniria is designed around two main user flows:

1. A regular user can create an account, join communities, post content, receive notifications, chat with a psychologist, and answer assigned forms.
2. A psychologist can manage their public profile, create forms and questions, assign due tests to patients, and review submitted responses.

The backend is organized into domain apps:

- `apps/users`: user model, profile updates, psychologist flags
- `apps/psychologists`: psychologist profiles, applications, forms, questions, answers, assigned tests
- `apps/community`: communities and posts
- `apps/chat`: private conversations and messages
- `apps/notifications`: notification center and WebSocket notifications
- `apps/dreams`: AI endpoint for prompt-based dream support

## Tech Stack

- Python
- Django 5
- Django REST Framework
- Djoser + SimpleJWT
- Django Channels + Daphne
- MySQL
- DeepSeek API
- ChromaDB

## Main Capabilities

### Authentication

- JWT-based login and refresh flow
- account creation through Djoser and custom user serializer
- current-user profile endpoint

### Psychologist Workflow

- psychologist application review flow
- psychologist public directory
- form builder with reusable questions
- due test assignment for patients
- form response review with computed total score

### Community

- create and browse communities
- create posts and replies
- join or leave communities
- like and dislike posts
- AI moderation before publishing a post

### Messaging and Notifications

- conversation creation between user and psychologist
- message listing and unread counters
- WebSocket support for chat and notifications
- REST notification inbox with mark-as-read actions

### AI Features

- prompt-based AI chat endpoint
- dream-related AI endpoint
- optional PDF ingestion into ChromaDB for retrieval context

## Repository Structure

```text
.
├── apps/
│   ├── users/
│   ├── psychologists/
│   ├── community/
│   ├── chat/
│   ├── notifications/
│   └── dreams/
├── backendExpo/
├── services/
├── pdfs/
├── manage.py
└── requirements.txt
```

## Local Setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root.

```env
SECRET_KEY=your-django-secret-key

DB_NAME=oniria_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_PASSWORD=your-email-password

DEEPSEEK_API_KEY=your-deepseek-api-key

CHROMADB_API_KEY=
CHROMADB_HOST=api.trychroma.com
CHROMADB_TENANT=
CHROMADB_DATABASE=
```

Notes:

- `DEEPSEEK_API_KEY` is required for AI chat, moderation, and dream endpoints.
- `CHROMADB_*` values are optional unless you want retrieval context from a hosted ChromaDB instance.
- The project is currently configured for **MySQL**.

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

Base URL:

```text
http://127.0.0.1:8000/
```

## Authentication Guide

The API uses **Bearer JWT tokens** for protected endpoints.

Example header:

```http
Authorization: Bearer <access_token>
```

Typical auth flow:

1. Register a user.
2. Obtain JWT tokens.
3. Send the access token in protected requests.
4. Refresh the token when needed.

## Environment Notes

- `DEBUG` is enabled in the current settings file.
- CORS is configured for local frontend development on `localhost:5173`.
- Media uploads are enabled for profile pictures and community images.
- Channels currently use `InMemoryChannelLayer`, which is convenient for development but not ideal for production scale.

## API Guide

All routes below are mounted from `backendExpo/urls.py`.

### Auth Endpoints

Provided by Djoser and SimpleJWT under `/api/auth/`.

Common routes:

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `POST` | `/api/auth/users/` | Register a new user | No |
| `GET` | `/api/auth/users/me/` | Get authenticated account from Djoser | Yes |
| `POST` | `/api/auth/jwt/create/` | Obtain access and refresh tokens | No |
| `POST` | `/api/auth/jwt/refresh/` | Refresh access token | No |
| `POST` | `/api/auth/jwt/verify/` | Verify a token | No |

### Users

Base path: `/api/users/`

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/users/` | List all users | No |
| `POST` | `/api/users/` | Create user with optional profile image | No |
| `GET` | `/api/users/me/` | Get current authenticated user | Yes |
| `PUT/PATCH` | `/api/users/me/` | Update current user profile | Yes |
| `GET` | `/api/users/<user_id>/` | Get a specific user | Yes |
| `PUT/PATCH` | `/api/users/<user_id>/` | Update own user record | Yes |
| `PATCH` | `/api/users/create-psychologist/` | Mark a user as psychologist | Yes, superuser only |
| `GET` | `/api/users/psychologist/` | List users flagged as psychologists | Yes |
| `GET` | `/api/users/psychologist/<user_id>/` | Get one user flagged as psychologist | Yes |

Important user fields:

- `username`
- `email`
- `description`
- `profile_pic`
- `profile_pic_url`
- `is_psychologist`
- `date_joined`

Password rule in the serializer:

- minimum 12 characters
- at least 1 uppercase letter
- at least 1 number
- at least 1 special character

### Psychologists

Base path: `/api/psychologists/`

#### Public Directory and Profile

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/psychologists/psychologists/` | List psychologist profiles | No |
| `GET` | `/api/psychologists/psychologist/<user_id>/` | Get one psychologist profile | No |
| `GET` | `/api/psychologists/psychologist/profile/me/` | Get own psychologist profile | Yes |
| `PUT/PATCH` | `/api/psychologists/psychologist/profile/me/` | Update own psychologist profile | Yes |
| `POST` | `/api/psychologists/psychologist/upload-profile-pic/` | Upload psychologist profile image | Yes |

#### Applications

ViewSet base path: `/api/psychologists/applications/`

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/psychologists/applications/` | List own applications, or all if admin | Yes |
| `POST` | `/api/psychologists/applications/` | Submit psychologist application | Yes |
| `GET` | `/api/psychologists/applications/my_application/` | Get latest application from current user | Yes |
| `GET` | `/api/psychologists/applications/pending/` | List pending applications | Yes, admin only |
| `POST` | `/api/psychologists/applications/<id>/review/` | Approve or reject application | Yes, admin only |
| `DELETE` | `/api/psychologists/applications/<id>/cancel/` | Cancel own pending application | Yes |

Application payload fields:

- `university_name`
- `professional_description`
- `credentials_document`

Review payload fields:

- `action`: `approve` or `reject`
- `rejection_reason`: required when rejecting

#### Forms and Questions

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/psychologists/forms/` | List forms created by current psychologist | Yes |
| `POST` | `/api/psychologists/forms/` | Create a form | Yes |
| `GET` | `/api/psychologists/forms/<id>/` | Get form detail | Yes |
| `PUT` | `/api/psychologists/forms/<id>/` | Update form | Yes |
| `DELETE` | `/api/psychologists/forms/<id>/` | Delete form | Yes |
| `GET` | `/api/psychologists/questions/` | List questions | Yes |
| `POST` | `/api/psychologists/questions/` | Create a question | Yes |
| `GET` | `/api/psychologists/questions/<id>/` | Get question detail | Yes |
| `PUT` | `/api/psychologists/questions/<id>/` | Update question | Yes |
| `DELETE` | `/api/psychologists/questions/<id>/` | Delete question | Yes |

Form creation uses `questions_ids` in the serializer.

Example form payload:

```json
{
  "title": "Sleep Quality Intake",
  "description": "Initial screening form",
  "questions_ids": [
    "question-uuid-1",
    "question-uuid-2"
  ]
}
```

Example question payload:

```json
{
  "question_text": "How many hours did you sleep last night?",
  "min_value": 0,
  "max_value": 10
}
```

#### Answers and Form Responses

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `POST` | `/api/psychologists/answers/` | Create one answer record directly | Yes |
| `GET` | `/api/psychologists/form-response/` | List all form responses | Yes |
| `POST` | `/api/psychologists/form-response/` | Submit a filled form with answers | Yes |
| `GET` | `/api/psychologists/form-response/<id>/` | Get one response | Yes |
| `GET` | `/api/psychologists/my-form-responses/` | Get responses for forms created by current psychologist | Yes |
| `GET` | `/api/psychologists/patient-responses/<patient_id>/` | Get one patient’s responses to current psychologist’s forms | Yes |

Example form response payload:

```json
{
  "form": "form-uuid",
  "due_test": "due-test-uuid",
  "answers": [
    {
      "question": "question-uuid-1",
      "value": 7
    },
    {
      "question": "question-uuid-2",
      "value": 4
    }
  ]
}
```

Behavior:

- creates a `form_response`
- creates the nested `answer` records
- computes `total_score`
- marks the linked due test as completed when `due_test` is provided

#### Due Tests

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/psychologists/assign-due-tests/` | List due tests assigned by current psychologist | Yes |
| `POST` | `/api/psychologists/assign-due-tests/` | Assign a due test to a patient | Yes |
| `GET` | `/api/psychologists/due-tests/<id>/` | Get due test detail | Yes |
| `PUT` | `/api/psychologists/due-tests/<id>/` | Update due test | Yes |
| `DELETE` | `/api/psychologists/due-tests/<id>/` | Delete due test | Yes |
| `GET` | `/api/psychologists/my-due-tests/` | List pending due tests for current patient | Yes |

Example due test payload:

```json
{
  "patient": "user-uuid",
  "form": "form-uuid",
  "date": "2026-05-15T18:00:00Z",
  "description": "Please complete this before the next session"
}
```

Notes:

- only users marked as psychologists can assign tests
- each due test gets a generated 6-digit `access_code`

#### PDF Training

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `POST` | `/api/psychologists/ai-training/` | Process a PDF and send chunks to the knowledge pipeline | Not explicitly restricted in this view |

Expected field:

- `pdfFile`

### Communities

Base path: `/api/communities/`

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/communities/` | List communities | Depends on permission class behavior |
| `POST` | `/api/communities/` | Create a community | Requires authenticated owner in practice |
| `GET` | `/api/communities/<name>/` | Search similar communities by name | No explicit auth in view |
| `GET` | `/api/communities/specific/<id>/` | Get one community | Depends on permission class behavior |
| `PUT` | `/api/communities/specific/<id>/` | Update a community | Owner-controlled |
| `DELETE` | `/api/communities/specific/<id>/` | Delete a community | Owner-controlled |
| `PATCH` | `/api/communities/join/<id>/` | Join or leave a community | Yes |

Community creation supports:

- `name`
- `description`
- optional file upload: `profile_image`

### Posts

Community post routes live under the same `/api/communities/` prefix.

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/communities/post/` | List all posts | No explicit auth in view |
| `POST` | `/api/communities/post/` | Create a post or reply | Uses current authenticated user |
| `GET` | `/api/communities/post/<id>/` | Get one post | Owner/read-only permission class |
| `PUT` | `/api/communities/post/<id>/` | Update a post | Owner only |
| `DELETE` | `/api/communities/post/<id>/` | Delete a post | Owner only |
| `GET` | `/api/communities/post/community/<community_id>/` | List posts from one community | No explicit auth in view |
| `PATCH` | `/api/communities/post/like/<id>/` | Toggle like | Yes |
| `PATCH` | `/api/communities/post/dislike/<id>/` | Toggle dislike | Yes |

Example post payload:

```json
{
  "title": "My sleep routine this week",
  "text": "I started journaling before bed and noticed fewer interruptions.",
  "community": "community-uuid"
}
```

Example reply payload:

```json
{
  "title": "Re: My sleep routine this week",
  "text": "That routine worked for me too.",
  "community": "community-uuid",
  "parent_post": "parent-post-uuid"
}
```

Notes:

- post content is checked by the DeepSeek moderation service before creation
- liking or disliking removes the opposite reaction if it already exists

### Chat

Base path: `/api/chat/`

This prefix contains two different APIs:

1. a direct AI chat endpoint
2. a REST router for user-to-psychologist conversations

#### AI Chat Endpoint

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `POST` | `/api/chat/` | Send a message to the AI service | Yes |

Example payload:

```json
{
  "message": "I had a dream about being lost in a city. What could that symbolize?"
}
```

#### Conversation Routes

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/chat/conversations/` | List conversations for current user | Yes |
| `POST` | `/api/chat/conversations/` | Create or reuse conversation with a psychologist | Yes |
| `GET` | `/api/chat/conversations/<id>/` | Get one conversation | Yes |
| `GET` | `/api/chat/conversations/<id>/messages/` | List messages in a conversation | Yes |
| `POST` | `/api/chat/conversations/<id>/mark_as_read/` | Mark other user’s messages as read | Yes |
| `GET` | `/api/chat/conversations/unread_count/` | Get unread message count | Yes |
| `GET` | `/api/chat/messages/` | Read-only list of accessible messages | Yes |
| `GET` | `/api/chat/messages/<id>/` | Read one message | Yes |

Example conversation creation payload:

```json
{
  "psychologist_id": "psychologist-user-uuid",
  "initial_message": "Hello, I would like to schedule an introductory conversation."
}
```

### Notifications

Base path: `/api/notifications/`

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `GET` | `/api/notifications/` | List the latest notifications for the current user | Yes |
| `GET` | `/api/notifications/<id>/` | Get one notification | Yes |
| `PATCH` | `/api/notifications/<id>/` | Mark one notification as read | Yes |
| `DELETE` | `/api/notifications/<id>/` | Delete one notification | Yes |
| `POST` | `/api/notifications/mark-all-read/` | Mark all unread notifications as read | Yes |
| `GET` | `/api/notifications/unread-count/` | Get unread notification count | Yes |
| `DELETE` | `/api/notifications/clear-all/` | Delete all read notifications | Yes |

### Dreams

Base path: `/api/dreams/`

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `POST` | `/api/dreams/ai/basic/` | Send a prompt to the dream AI service | Inherits default authentication |

Example payload:

```json
{
  "prompt": "I dreamed that I was falling and then suddenly woke up."
}
```

## WebSocket Guide

The project also exposes WebSocket endpoints through Django Channels.

| Route | Purpose |
|---|---|
| `ws/notifications/` | Real-time notifications |
| `ws/chat/<conversation_id>/` | Real-time chat messages for a conversation |

Implementation notes:

- WebSockets are wired in `backendExpo/asgi.py`
- a JWT middleware is used for WebSocket authentication
- development currently uses `InMemoryChannelLayer`

## Example Development Flow

### User Journey

1. Register a user with `/api/auth/users/` or `/api/users/`.
2. Log in with `/api/auth/jwt/create/`.
3. Load profile data with `/api/users/me/`.
4. Join communities and create posts.
5. Start a conversation with a psychologist.
6. Receive notifications and complete assigned forms.

### Psychologist Journey

1. Submit a psychologist application.
2. After approval, update psychologist profile.
3. Create questions.
4. Build forms from those questions.
5. Assign due tests to patients.
6. Review completed responses and total scores.

## Known Implementation Notes

- The codebase mixes English and Spanish names in routes, comments, and responses.
- Some endpoints rely on custom permission classes whose exact behavior should be validated during QA.
- `apps/notifications/serializers.py` references `obj.community.profile_image.url`, while the model stores `profile_image_base64`; this area may need cleanup if notification community images are used.
- The AI training endpoint is not visibly protected in the view and should be reviewed before production use.
- Channels use in-memory transport for development; Redis would be the better production path.

## Admin

Admin panel:

```text
/admin/
```

The project includes `django-unfold` for the admin UI.

## Requirements Summary

To run the full project locally, you will typically need:

- Python 3.11+
- MySQL
- virtualenv
- DeepSeek API access
- optional ChromaDB configuration for retrieval features

## License

No license file is currently included in this repository.
