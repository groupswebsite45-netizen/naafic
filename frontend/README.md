# Frontend - Hawlwadaag School Management System

Vue 3 + TypeScript single-page application for **Hawlwadaag Primary and Secondary School** administrative and authentication portal.

## Technology Stack

- **Framework**: Vue 3 (Composition API `<script setup>`)
- **Language**: TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router 4 (with client-side authentication guards)
- **HTTP Client**: Axios (with Bearer token interceptor and 401 response handling)
- **Styling**: Vanilla Modern Scoped CSS + CSS Design Tokens

## Folder Structure

```
frontend/
├── public/                  # Static assets & school-icon.svg
├── src/
│   ├── assets/              # Design tokens and global CSS styles
│   │   └── styles/
│   │       ├── variables.css
│   │       └── main.css
│   ├── components/          # Reusable UI components
│   │   ├── admin/           # AdminHeader, AdminSidebar
│   │   └── common/          # AppButton, InputField, StatusBadge
│   ├── constants/           # Centralized school branding (branding.ts)
│   ├── layouts/             # App layouts (AuthLayout, AdminLayout)
│   ├── router/              # Route definitions & navigation guards
│   ├── services/            # Axios API client, authService, adminService
│   ├── stores/              # Pinia auth store (useAuthStore)
│   ├── types/               # TypeScript interfaces & types (auth, user, admin)
│   ├── views/               # Page views (LoginView, DashboardView, ProfileView, SettingsView)
│   ├── App.vue              # Root Vue Component
│   └── main.ts              # Application Bootstrap
├── .env.example
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Centralized School Branding

All institution branding (School Name, Motto, Campus Location, Contact Info, Theme Colors, and Logos) are centralized in:
`src/constants/branding.ts`

Any future modifications to branding should be made in this file.

## Setup & Running

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default:
```env
VITE_API_BASE_URL="http://localhost:8000/api/v1"
```

### 3. Start Development Server
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

### 4. Build for Production
```bash
npm run build
```
The compiled output will be generated in `dist/`.
