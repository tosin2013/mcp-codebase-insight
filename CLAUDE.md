# TechPath Project Guidelines

## Build & Test Commands
- **Python**: `make install-dev` (setup), `make start` (run server), `make check` (all checks)
- **Python Tests**: `make test` or `pytest tests/test_file.py::test_function_name` (single test)
- **Frontend**: `cd project && npm run dev` (development), `npm run build` (production)
- **Frontend Tests**: `cd project && npm test` or `npm test -- -t "test name pattern"` (single test)
- **Linting**: `make lint` (Python), `cd project && npm run lint` (TypeScript/React)
- **Formatting**: `make format` (Python), `prettier --write src/` (Frontend)

## Code Style Guidelines
- **Python**: Black (88 chars), isort for imports, type hints required
- **TypeScript**: 2-space indent, semicolons, strong typing with interfaces
- **Imports**: Group by external then internal, alphabetize
- **React**: Functional components with hooks, avoid class components
- **Types**: Define interfaces in separate files when reused
- **Naming**: camelCase for JS/TS variables, PascalCase for components/types, snake_case for Python
- **Error Handling**: Try/catch in async functions, propagate errors with descriptive messages
- **Comments**: Document complex logic, interfaces, and function parameters/returns
- **Testing**: Unit test coverage required, mock external dependencies