# Your First Custom Instructions - Tutorial Example

This example demonstrates how to use GitHub Copilot custom instructions to improve code generation, based on [GitHub's official tutorial](https://docs.github.com/en/copilot/tutorials/customization-library/custom-instructions/your-first-instructions).

## 📋 What This Example Demonstrates

This tutorial shows:
1. How custom instructions change code generation behavior
2. The difference between code **without** and **with** custom instructions
3. A practical example of function writing guidelines

## 🎯 The Custom Instructions

The instructions in this example tell GitHub Copilot to always:
- Add descriptive JSDoc comments
- Include input validation
- Use early returns for error conditions
- Add meaningful variable names
- Include at least one example usage in comments

## 📁 Files in This Example

- **`copilot-instructions.md`** - The custom instructions file
- **`without-instructions.js`** - Example function generated WITHOUT custom instructions
- **`with-instructions.js`** - Example function generated WITH custom instructions
- **`README.md`** - This file

## 🚀 How to Test This Example

### Option 1: Using GitHub Copilot Chat

1. Open GitHub Copilot Chat (in your IDE or at [github.com/copilot](https://github.com/copilot))
2. Navigate to this directory
3. Ask: `Create a JavaScript function that calculates the area of a circle`
4. Compare the result with the examples in this directory

### Option 2: Using Path-Specific Instructions in Your IDE

1. Ensure you have GitHub Copilot enabled in VS Code, Visual Studio, or JetBrains
2. Open this directory in your IDE
3. Create a new JavaScript file
4. Start typing a function comment like: `// Function to calculate rectangle area`
5. Let Copilot suggest the implementation
6. Notice how it follows the instructions (JSDoc, validation, examples, etc.)

## 📊 Before and After Comparison

### Without Custom Instructions

The generated function is functional but minimal:

```javascript
function areaOfCircle(radius) {
    if (typeof radius !== 'number' || radius < 0) {
        throw new Error('Radius must be a non-negative number');
    }
    return Math.PI * radius * radius;
}
```

### With Custom Instructions

The generated function includes:
- ✅ Comprehensive JSDoc comments
- ✅ Input validation with early returns
- ✅ Multiple example usages
- ✅ Meaningful variable names
- ✅ Clear error handling

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

## 🎓 Learning Points

1. **Custom instructions are powerful**: A few simple guidelines dramatically improve code quality
2. **Instructions persist**: Once set, they apply to all interactions
3. **JSDoc improves usability**: Functions become self-documenting
4. **Validation is critical**: Good functions handle edge cases
5. **Examples help understanding**: Usage examples in comments clarify intent

## 🔧 Customizing for Your Project

You can adapt these instructions to your project's needs:

```markdown
When writing functions, always:
- Follow [Your Style Guide] conventions
- Use TypeScript types for type safety
- Include error handling for network requests
- Log important operations with [Your Logger]
- Write unit tests using [Your Test Framework]
```

## 📚 Additional Resources

- [About customizing GitHub Copilot responses](https://docs.github.com/en/copilot/concepts/response-customization)
- [Configure custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions)
- [Awesome GitHub Copilot Customizations](https://github.com/github/awesome-copilot)

## 💡 Next Steps

After mastering basic custom instructions, explore:
1. **Path-specific instructions**: Different rules for different directories
2. **Organization-wide instructions**: Shared guidelines across repositories
3. **Prompt files**: Reusable prompts for specific tasks
4. **Advanced patterns**: Combining multiple instruction types

---

**Note**: This is a simplified example for learning. For production use, consider adding more comprehensive guidelines specific to your codebase, as demonstrated in the main `.github/copilot-instructions.md` file at the repository root.
