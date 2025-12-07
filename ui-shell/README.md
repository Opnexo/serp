# SERP UI Shell

NextJS 14+ frontend application shell for the SimpleERP (SERP) system.

## Features

- **NextJS 15 App Router**: Modern routing with server components and React 19
- **TypeScript 5.7**: Full type safety with latest features
- **Tailwind CSS 3.4**: Utility-first styling
- **Module System**: Dynamic module loading
- **Permission-Based UI**: Show/hide based on user permissions
- **Ribbon Toolbar**: Microsoft Office-style interface
- **TanStack Query v5**: Server state management
- **Zustand v5**: Client state management

## Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Update API URL in .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
ui-shell/
├── src/
│   ├── app/                  # NextJS App Router
│   │   ├── (auth)/          # Authentication routes
│   │   ├── (protected)/     # Protected routes with shell
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   └── globals.css      # Global styles
│   │
│   ├── components/          # React components
│   │   ├── Shell/          # Shell components
│   │   ├── Ribbon/         # Ribbon toolbar
│   │   ├── ModuleLoader/   # Dynamic module loading
│   │   ├── Providers/      # Context providers
│   │   └── ui/             # Base UI components
│   │
│   ├── lib/                 # Core libraries
│   │   ├── auth/           # Authentication
│   │   ├── permissions/    # Permission system
│   │   ├── modules/        # Module registry & loader
│   │   ├── api/            # API client
│   │   └── utils/          # Utilities
│   │
│   └── types/               # TypeScript types
│
├── public/                  # Static assets
└── package.json
```

## Module Integration

Modules register their UI components and routes:

```typescript
// my-module/UI/registry.ts
export const registry = {
  moduleId: "my-module",
  moduleName: "My Module",
  ribbon: {
    tabId: "my-tab",
    tabLabel: "My Module",
    groups: [...],
  },
  routes: [...],
  permissions: [...],
};
```

## Architecture

- **Shell**: Main application layout with ribbon toolbar
- **Module Loader**: Dynamically loads module UI components
- **Permission Gate**: Conditionally renders based on user permissions
- **Route Guard**: Protects routes requiring authentication/permissions
- **API Client**: Axios-based client with interceptors

## License

MIT License - See LICENSE file for details
