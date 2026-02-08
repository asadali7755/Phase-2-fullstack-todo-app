# Quickstart Guide: Frontend Application for Todo Full-Stack Web Application

## Prerequisites
- Node.js 18+
- npm or yarn package manager
- Git
- Access to the backend API (FastAPI server running)

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Environment Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### 3. Environment Variables
Create `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/v1
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret-for-development
```

### 4. Better Auth Configuration
Configure Better Auth in `frontend/lib/auth.ts`:
```typescript
import { betterAuth } from "better-auth/react";

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000",
  // Add other auth configurations as needed
});
```

## Running the Application

### Development Mode
```bash
cd frontend
npm run dev
# or
yarn dev
```

Application will be available at `http://localhost:3000`

### Production Mode
```bash
cd frontend
npm run build
npm run start
# or
yarn build
yarn start
```

## Key Components and Usage

### Authentication Components
- **SignInForm**: Handles user sign-in functionality
- **SignUpForm**: Handles user registration functionality
- **ProtectedRoute**: Wrapper component for protecting routes that require authentication

### Todo Components
- **TodoList**: Displays the list of todos for the authenticated user
- **TodoCard**: Individual todo item display with completion toggle
- **TodoForm**: Form for creating and updating todos

### Hooks
- **useAuth**: Hook for accessing authentication state and functions
- **useTodos**: Hook for managing todo operations (fetch, create, update, delete)

### API Client
The API client is located in `lib/api-client.ts` and automatically attaches JWT tokens to authenticated requests.

## Project Structure
```
frontend/
├── app/
│   ├── (auth)/              # Authentication pages
│   │   ├── sign-in/
│   │   │   └── page.tsx
│   │   └── sign-up/
│   │       └── page.tsx
│   ├── dashboard/           # Main dashboard page
│   │   └── page.tsx
│   ├── globals.css          # Global styles
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Home page
├── components/              # Reusable UI components
│   ├── auth/
│   │   ├── SignInForm.tsx
│   │   └── SignUpForm.tsx
│   ├── todo/
│   │   ├── TodoCard.tsx
│   │   ├── TodoList.tsx
│   │   └── TodoForm.tsx
│   ├── ui/                  # Base UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── LoadingSpinner.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── ProtectedRoute.tsx
├── lib/                     # Utilities and services
│   ├── auth.ts              # Better Auth configuration
│   ├── api-client.ts        # API client with JWT handling
│   └── utils.ts             # Utility functions
├── hooks/                   # Custom React hooks
│   ├── useTodos.ts
│   └── useAuth.ts
├── types/                   # TypeScript type definitions
│   └── index.ts
├── tests/                   # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── public/                  # Static assets
└── package.json             # Project dependencies
```

## Testing

### Run Unit Tests
```bash
cd frontend
npm run test
# or
yarn test
```

### Run Integration Tests
```bash
cd frontend
npm run test:integration
# or
yarn test:integration
```

### Run E2E Tests
```bash
cd frontend
npm run test:e2e
# or
yarn test:e2e
```

## API Integration

### Making Authenticated Requests
The API client automatically attaches JWT tokens to requests:

```typescript
import { apiClient } from '@/lib/api-client';

// This will automatically include the JWT token in the Authorization header
const response = await apiClient.get('/todos');
```

### Error Handling
The API client includes built-in error handling:

```typescript
try {
  const response = await apiClient.get('/todos');
  console.log(response.data);
} catch (error) {
  // Error handling is built into the client
  console.error('Failed to fetch todos:', error);
}
```

## Environment Configuration

### Development
- `NEXT_PUBLIC_API_BASE_URL`: Points to your local backend (e.g., `http://localhost:8000/v1`)
- `NEXT_PUBLIC_BACKEND_URL`: Backend base URL for auth (e.g., `http://localhost:8000`)

### Production
- `NEXT_PUBLIC_API_BASE_URL`: Points to your production backend API
- `NEXT_PUBLIC_BACKEND_URL`: Production backend base URL for auth