Notes for backend ops:
- SECRET_KEY must be set in production .env or as environment variable.
- Do NOT commit .env; .gitignore contains .env entries.
- MongoDB connection should use a dedicated user with limited privileges, not the admin user.
- Use TLS for database and API endpoints.
