---
applyTo: "**/*.{ts,tsx,js,jsx}"
---

# TypeScript/JavaScript Development Standards

## Purpose

These instructions guide Copilot code review for TypeScript and JavaScript files.
This includes the Panelin agents SDK and any frontend components.

## Type Safety (TypeScript)

- Avoid using `any` type—use `unknown` or specific types instead
- Use strict null checks (no `null` or `undefined` without explicit handling)
- Define interfaces for all object shapes

```typescript
// Avoid
function processData(data: any) {
    return data.value;
}

// Prefer
interface DataShape {
    value: string;
}

function processData(data: DataShape): string {
    return data.value;
}
```

## Naming Conventions

- Use PascalCase for types, interfaces, and classes
- Use camelCase for variables, functions, and methods
- Use UPPER_CASE for constants
- Use descriptive, intention-revealing names

```typescript
// Avoid
const d = new Date();
const x = users.filter(u => u.active);

// Prefer
const currentDate = new Date();
const activeUsers = users.filter(user => user.isActive);
```

## Modern TypeScript/JavaScript Patterns

- Use optional chaining (`?.`) and nullish coalescing (`??`)
- Prefer `const` over `let`; never use `var`
- Use arrow functions for callbacks and short functions
- Use async/await instead of raw Promises

```typescript
// Avoid
const name = user && user.profile && user.profile.name;
let count = value !== null && value !== undefined ? value : 0;

// Prefer
const name = user?.profile?.name;
const count = value ?? 0;
```

## Error Handling

- Always handle promise rejections
- Use try/catch with async/await
- Provide meaningful error messages

```typescript
// Avoid
async function fetchData() {
    const response = await fetch(url);
    return response.json();
}

// Prefer
async function fetchData(): Promise<DataType> {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        return response.json();
    } catch (error) {
        console.error('Failed to fetch data:', error);
        throw error;
    }
}
```

## React-Specific (for .tsx/.jsx files)

- Use functional components with hooks
- Keep components small and focused (under 200 lines)
- Type all props and state explicitly
- Use proper event types

```typescript
// Prefer
interface ButtonProps {
    label: string;
    onClick: () => void;
    disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false }) => {
    return (
        <button onClick={onClick} disabled={disabled}>
            {label}
        </button>
    );
};
```

## Security

- Never hardcode API keys or credentials
- Validate and sanitize user inputs
- Use parameterized queries to prevent injection attacks
- Escape user content when rendering HTML

## Testing

- Write unit tests for critical functions
- Use descriptive test names
- Test edge cases and error conditions
