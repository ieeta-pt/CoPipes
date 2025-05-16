# Supabase Authentication Setup Guide

This document provides instructions for setting up and configuring the authentication system in this project, which uses Supabase for backend authentication.

## Table of Contents

1. [Supabase Setup](#supabase-setup)
2. [Environment Variables](#environment-variables)
3. [Database Setup](#database-setup)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Testing](#testing)

## Supabase Setup

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Create a new project in Supabase
3. Note down your project URL and API keys from the project settings 

## Environment Variables

Add the following environment variables to your environment:

### Backend (.env file in backend directory)

```
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
JWT_SECRET_KEY=your-secret-key-for-jwt-signing
```

### Frontend (.env.local file in frontend directory)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Setup

### Run the Migration Script

1. Log in to your Supabase dashboard
2. Go to the SQL Editor
3. Create a new query and paste the contents of the `backend/api/migrations/create_auth_tables.sql` file
4. Run the query to create the necessary tables and policies

## Backend Setup

1. Install the required packages:

```bash
cd backend/api
pip install -r requirements.txt
```

2. Start the backend server:

```bash
cd backend/api
uvicorn main:app --reload
```

## Frontend Setup

1. Install the required packages:

```bash
cd frontend
npm install
```

2. Start the frontend development server:

```bash
npm run dev
```

## Authentication Flow

This project implements a token-based authentication system with JWT:

1. **Registration**: Users register with email and password
2. **Login**: Users login and receive an access token and refresh token
3. **Authentication**: The access token is used to authenticate requests
4. **Token Refresh**: When the access token expires, the refresh token is used to get a new one
5. **Logout**: The refresh token is invalidated on logout

## Security Considerations

1. JWT tokens are signed with a secret key
2. Passwords are hashed using bcrypt
3. Refresh tokens are stored in a secure table with RLS policies
4. Access tokens have a short expiration time (30 minutes)
5. Refresh tokens are periodically cleaned up

## Protected Routes

The following routes are protected and require authentication:

### Backend
- All workflow-related routes (`/api/workflows/*`)
- Upload route (`/api/upload`)
- Airflow DAG routes (`/api/get_dags`)

### Frontend
- Dashboard page
- Workflow pages
- Profile page

## Testing

To test the authentication system:

1. Register a new user
2. Login with the registered credentials
3. Try accessing protected routes
4. Test token refresh by waiting for token expiration
5. Test logout functionality 