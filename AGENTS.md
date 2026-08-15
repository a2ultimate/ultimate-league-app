# Agent Instructions

This repository contains the A2U Ultimate Frisbee league web application, with a Django 4.2 backend and webpack-managed frontend assets.

## Essential Commands

Run the test suite from `src/`:

```bash
APP_RUNMODE=dev DJANGO_SETTINGS_MODULE=ultimate.settings.test python manage.py test
```

Build production frontend assets from `src/static/`:

```bash
npm run build
```

## Task-Specific Guides

- [Development environment and local servers](docs/agent-guides/development.md)
- [Testing](docs/agent-guides/testing.md)
- [Production updates](docs/agent-guides/deployment.md)
