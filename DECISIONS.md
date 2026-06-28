# Architectural Decisions

## Database & Persistence
- **SQLite**: Maintained as the primary relational database to avoid Docker dependencies on the host machine. We will use Alembic for proper schema migrations.
- **Redis**: Deferred. We will use in-memory caching and Python queues for the crawler tasks to maintain a zero-dependency local setup.

## Backend Structure
- **Modular Python Monolith**: The backend is organized into domain-specific modules (`engine`, `knowledge`, `crawler`) rather than a single `main.py` file to support the complex pipeline required by the new Agentic prompt.

## Frontend
- **Vite + React**: Maintained over a complete Next.js rewrite. The current SPA architecture is perfectly capable of rendering complex dashboards (using Recharts) and dynamic Markdown. Avoiding a rewrite allows us to focus entirely on the core AI engineering while still delivering a premium UI.

## Web Searching
- **DuckDuckGo API**: Selected as the default unauthenticated scraping provider for the `DataSourcer` to bypass API quota limits, enabling the system to fulfill the strict citation requirements without external paid API keys.
