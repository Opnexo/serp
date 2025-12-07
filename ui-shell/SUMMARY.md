# SERP UI Shell - Summary

## Overview

The SERP UI Shell is a NextJS 15 frontend application that provides:

- **Modern Stack**: NextJS 15 with App Router, React 19, TypeScript 5.7, Tailwind CSS 3.4
- **Module System**: Dynamic loading of module UI components
- **Permission-Based UI**: Show/hide features based on user permissions
- **Ribbon Interface**: Microsoft Office-style toolbar
- **State Management**: TanStack Query v5 (server) + Zustand v5 (client)
- **Authentication**: JWT-based auth with session management

## Project Structure

```
ui-shell/
├── src/
│   ├── app/                      # NextJS App Router
│   │   ├── (auth)/              # Login/logout routes
│   │   ├── (protected)/         # Protected routes with shell
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Home page
│   │   └── globals.css          # Global styles
│   │
│   ├── components/
│   │   ├── Shell/               # Application shell
│   │   ├── Ribbon/              # Ribbon toolbar
│   │   ├── Providers.tsx        # Context providers
│   │   └── ui/                  # Base UI components
│   │
│   ├── lib/
│   │   ├── auth/                # Authentication system
│   │   ├── permissions/         # Permission checking
│   │   ├── modules/             # Module registry & loader
│   │   ├── api/                 # API client & endpoints
│   │   └── utils.ts             # Utility functions
│   │
│   └── types/                   # TypeScript type definitions
│
├── public/                      # Static assets
├── package.json
├── next.config.js
├── tailwind.config.js
└── tsconfig.json
```

## Key Features

### 1. Authentication System

- JWT-based authentication with automatic token refresh
- Login/logout pages
- AuthGuard for protected routes
- Session persistence in localStorage

**Location**: `src/lib/auth/`

### 2. Permission System

- Role-based access control (RBAC)
- Permission gates for conditional rendering
- Integration with user permissions from backend

**Location**: `src/lib/permissions/`

### 3. Module System

- Dynamic module loading at runtime
- Module registry for route and UI registration
- Module loader for lazy component imports

**Location**: `src/lib/modules/`

### 4. Ribbon Toolbar

- Microsoft Office-style interface
- Tab-based navigation
- Button groups with actions
- Permission-based button visibility

**Location**: `src/components/Ribbon/`

### 5. Shell Layout

- Main application wrapper
- Persistent ribbon toolbar
- Content area with routing

**Location**: `src/components/Shell/`

## Getting Started

### Installation

```bash
cd ui-shell
npm install
```

### Development

```bash
# Start dev server (http://localhost:3000)
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

### Production Build

```bash
npm run build
npm start
```

## Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_AUTH_STORAGE_KEY=serp_auth_token
```

## API Integration

### Endpoints Configuration

All API endpoints are defined in `src/lib/api/endpoints.ts`:

- `/api/auth/*` - Authentication
- `/api/users/*` - User management
- `/api/modules/*` - Module discovery

### API Client

The `apiClient` in `src/lib/api/client.ts` provides:

- Automatic token injection
- Error handling and transformation
- Request/response interceptors
- Typed request functions (get, post, put, patch, del)

## Module Integration

Modules register their UI components:

```typescript
// module/UI/registry.ts
export const registry = {
  moduleId: "my-module",
  moduleName: "My Module",
  ribbon: {
    tabId: "my-tab",
    tabLabel: "My Module",
    groups: [
      {
        groupId: "actions",
        groupLabel: "Actions",
        buttons: [
          {
            buttonId: "create",
            label: "Create",
            icon: "Plus",
            permission: "my_module:create",
            action: { type: "navigate", route: "/my-module/create" },
          },
        ],
      },
    ],
  },
  routes: [
    {
      routeId: "list",
      path: "/my-module",
      permission: "my_module:list",
      component: () => import("./views/List"),
    },
  ],
  permissions: ["my_module:create", "my_module:list"],
};
```

## Styling

### Tailwind CSS

Custom theme with CSS variables for easy customization:

- Light/dark mode support
- Design tokens for colors, spacing, typography
- Utility classes for rapid development

### Component Library

Base UI components in `src/components/ui/`:

- Button
- Card (with Header, Content, Footer)
- More components can be added as needed

## State Management

### Server State (TanStack Query)

For data fetching, caching, and synchronization:

```typescript
const { data, isLoading } = useQuery({
  queryKey: ['users'],
  queryFn: () => get('/api/users'),
});
```

### Client State (Zustand)

For UI state and temporary data:

```typescript
const useStore = create((set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
```

## TypeScript Types

All types are defined in `src/types/`:

- `auth.ts` - Authentication types
- `module.ts` - Module system types
- `permission.ts` - Permission types
- `api.ts` - API response types

## Next Steps

1. **Install dependencies**: `npm install`
2. **Configure environment**: Copy `.env.example` to `.env.local`
3. **Start backend**: Ensure serp-shell is running on port 8000
4. **Start frontend**: `npm run dev`
5. **Access app**: http://localhost:3000

## Architecture Notes

- **App Router**: Uses NextJS 14 App Router (not Pages Router)
- **Server Components**: Default components are Server Components
- **Client Components**: Use `'use client'` directive when needed
- **Route Groups**: `(auth)` and `(protected)` for layout control
- **Dynamic Routes**: `[...slug]` for module route handling

## Dependencies

### Production
- next ^15.1.0
- react ^19.0.0
- @tanstack/react-query ^5.62.0
- zustand ^5.0.2
- axios ^1.7.9
- lucide-react ^0.468.0
- tailwind-merge ^2.5.5

### Development
- typescript ^5.7.2
- tailwindcss ^3.4.16
- eslint ^9.16.0

## License

MIT License - See LICENSE file for details
