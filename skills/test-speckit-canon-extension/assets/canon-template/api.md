# Public API

## List Todos

The system exposes a Todo collection capability that returns the available Todo items as a list.

Each returned Todo includes:

- `id`
- `title`
- `completed`

## Get Todo

The system exposes a Todo detail capability that returns one Todo by identifier.

When the identifier matches an existing Todo, the response returns that Todo using the canonical Todo fields. When the identifier does not match an existing Todo, the response returns a not-found outcome.
