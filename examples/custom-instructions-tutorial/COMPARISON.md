# Quick Comparison: Custom Instructions Impact

## Side-by-Side Comparison

### 📦 Without Custom Instructions

```javascript
function areaOfCircle(radius) {
    if (typeof radius !== 'number' || radius < 0) {
        throw new Error('Radius must be a non-negative number');
    }
    return Math.PI * radius * radius;
}
```

**Characteristics:**
- ❌ No JSDoc documentation
- ❌ No usage examples
- ❌ Minimal error messages
- ❌ Basic variable names
- ✅ Functional implementation

---

### 🎯 With Custom Instructions

```javascript
/**
 * Calculates the area of a circle given its radius.
 *
 * @param {number} radius - The radius of the circle. Must be a positive number.
 * @returns {number|null} The area of the circle, or null if the input is invalid.
 *
 * @example
 * // returns 78.53981633974483
 * areaOfCircle(5);
 *
 * @example
 * // returns null (invalid input)
 * areaOfCircle(-2);
 */
function areaOfCircle(radius) {
  if (typeof radius !== "number" || isNaN(radius) || radius <= 0) {
    // Invalid input: radius must be a positive number
    return null;
  }

  const area = Math.PI * Math.pow(radius, 2);
  return area;
}
```

**Characteristics:**
- ✅ Complete JSDoc documentation
- ✅ Multiple usage examples
- ✅ Clear error messages
- ✅ Descriptive variable names
- ✅ Early return pattern
- ✅ Self-documenting code

---

## Impact Metrics

| Feature | Without | With | Improvement |
|---------|---------|------|-------------|
| Lines of code | 6 | 18 | +200% (documentation) |
| JSDoc comments | 0 | 1 full | ✅ Complete |
| Usage examples | 0 | 2 | ✅ Multiple scenarios |
| Error handling clarity | Basic | Enhanced | ✅ More robust |
| Code readability | Fair | Excellent | ✅ Self-documenting |
| Maintainability | Medium | High | ✅ Easier to understand |

---

## The Custom Instructions

The simple instructions that caused this transformation:

```markdown
When writing functions, always:
- Add descriptive JSDoc comments
- Include input validation
- Use early returns for error conditions
- Add meaningful variable names
- Include at least one example usage in comments
```

---

## Key Takeaways

1. **Small instructions, big impact**: 5 simple guidelines transform code quality
2. **Documentation matters**: JSDoc makes code self-explanatory
3. **Examples are valuable**: Usage examples clarify expected behavior
4. **Validation is essential**: Good error handling prevents bugs
5. **Consistency wins**: Instructions ensure uniform code across your project

---

## Try It Yourself

1. Copy `copilot-instructions.md` to your project root
2. Ask Copilot to generate a function
3. Compare with functions generated without instructions
4. Customize the instructions for your coding standards

---

**Remember**: Custom instructions are a powerful tool to ensure consistent, high-quality code generation across your entire project!
