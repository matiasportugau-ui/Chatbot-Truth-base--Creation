---
applyTo: "javascript-code/**/*.js"
---

# JavaScript-Specific Custom Instructions

When writing JavaScript code in this directory, always:

## Documentation
- Use JSDoc comments for all functions and classes
- Include parameter types, return types, and examples
- Document any side effects or async behavior

## Modern JavaScript
- Use `const` and `let`, never `var`
- Prefer arrow functions for callbacks and pure functions
- Use async/await instead of raw Promises for async operations
- Use destructuring for objects and arrays
- Use template literals instead of string concatenation

## Error Handling
- Use try/catch for async operations
- Return meaningful error objects
- Validate inputs at function boundaries
- Use early returns to avoid deep nesting

## Code Organization
- Keep functions small and focused (single responsibility)
- Use meaningful variable and function names
- Group related functionality together
- Export explicit named exports, avoid default exports

## Example Function Format

```javascript
/**
 * Fetches user data from the API and processes it.
 * 
 * @param {string} userId - The unique identifier for the user
 * @param {Object} options - Configuration options
 * @param {boolean} options.includeMetadata - Whether to include metadata
 * @returns {Promise<Object>} Processed user data object
 * @throws {Error} If user is not found or API request fails
 * 
 * @example
 * const user = await fetchUserData('user123', { includeMetadata: true });
 * console.log(user.name); // 'John Doe'
 */
const fetchUserData = async (userId, { includeMetadata = false } = {}) => {
  if (!userId || typeof userId !== 'string') {
    throw new Error('Valid userId string is required');
  }

  try {
    const response = await fetch(`/api/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`User not found: ${userId}`);
    }

    const data = await response.json();
    
    return includeMetadata 
      ? data 
      : { name: data.name, email: data.email };
  } catch (error) {
    throw new Error(`Failed to fetch user: ${error.message}`);
  }
};
```
