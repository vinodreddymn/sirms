# Frontend Features

## Technology and application shell

The frontend is a React 19 + TypeScript + Vite single-page application. It uses React Router, Axios, Framer Motion, Lucide icons, shared modal/form/table components, and toast notifications.

- Axios attaches the stored JWT access token to requests and redirects to `/login` on a `401` response.
- A route guard requires an `access_token` in local storage for all application pages.
- The main layout provides sidebar navigation, top-level search input, and a local logout action.

## Implemented screens and user actions

### Authentication

- Login form posts credentials to `/auth/login` and saves the returned access token.
- Protected routes redirect unauthenticated users to login.
- Logout removes the local access token and returns to login. It does not call the backend logout endpoint.

### Asset management

- Asset register supports server-backed pagination, sorting, filter controls, text search, field/register view modes, refresh, and CSV export.
- Asset summary metrics are loaded from the backend.
- Create and edit flows load projects and dependent asset classifications, including category -> subcategory -> model filtering.
- Asset forms load dynamic specification definitions and location position choices.
- Asset detail page loads a selected asset; list cards and rows navigate to its detail route.
- Asset detail page shows its O&M timeline and provides a replacement dialog that submits the faulty-to-spare replacement workflow.
- Location autocomplete searches live backend locations after the user enters at least two characters.

### Master data and specifications

- Master-data screen lists and creates/edits 22 configured lookup categories, including asset, incident, location, and stock-related lookups.
- Dynamic-specification screen lists and creates/edits specification definitions with category/subcategory scoping, data type, unit, required flag, and display order.

### Infrastructure

- Location tree loads the live hierarchy and shows location-type-aware icons and node statistics.
- Users can create/edit locations with parent selection, coordinates, and remarks.
- Position sub-panel lists position slots for a selected location and supports create/edit operations.

### Stock

- Stock ledger loads and displays live stock transactions with type-specific iconography and quantity sign/color treatment.

## Current frontend gaps and placeholders

- Dashboard cards use hard-coded values (`1,248`, `24`, and `7`); they do not call the live dashboard summary API.
- Incidents and maintenance routes render placeholder text only.
- Stock has no create-transaction form; its button displays a “coming soon” toast.
- Global search input has no connected search behavior.
- The displayed topbar user (`Admin`) and avatar are static rather than sourced from `/auth/me`.
- Login stores only the access token; refresh-token lifecycle, backend logout, dashboard/notification preferences, uploads, reporting, and most backend workflows have no frontend UI.
- The replacement dialog currently accepts a spare asset UUID; a searchable spare picker and repair/field-note forms remain to be built.

## Route map

| Route | Current screen |
| --- | --- |
| `/login` | Login |
| `/` | Static dashboard |
| `/master` | Lookup management |
| `/master/specifications` | Dynamic specification definitions |
| `/assets` | Asset register and create/edit modal |
| `/assets/:id` | Asset details |
| `/infrastructure` | Location tree and position management |
| `/stock` | Stock transaction ledger |
| `/incidents` | Placeholder |
| `/maintenance` | Placeholder |

## Main source locations

- Routes: `frontend/src/App.tsx`
- Shared layout/API client: `frontend/src/layouts/MainLayout.tsx`, `frontend/src/services/api.ts`
- Feature pages: `frontend/src/features/`
