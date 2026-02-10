# Path-Specific Custom Instructions Example

This example demonstrates how to use **path-specific custom instructions** that apply only to certain files or directories.

## 📋 What This Example Demonstrates

Path-specific instructions allow you to:
- Apply different coding standards to different parts of your codebase
- Use language-specific guidelines (Python vs JavaScript)
- Enforce framework-specific patterns in certain directories
- Maintain consistency within specific modules

## 🎯 How Path-Specific Instructions Work

Path-specific instructions use a special frontmatter with an `applyTo` field:

```markdown
---
applyTo: "python-code/**/*.py"
---

# Python-Specific Instructions

When writing Python code, always:
- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions
- Use docstrings with Google style format
- Prefer `pathlib` over `os.path`
```

## 📁 Example Structure

This example shows two different instruction sets:

1. **`python.instructions.md`** - Applies to all Python files in `python-code/`
2. **`javascript.instructions.md`** - Applies to all JavaScript files in `javascript-code/`

Each instruction file affects only its targeted files, demonstrating how you can maintain different standards for different parts of your codebase.

## 🚀 Testing This Example

### In VS Code, Visual Studio, or JetBrains IDEs:

1. Open this directory in your IDE with GitHub Copilot enabled
2. Create a new Python file in `python-code/`
3. Ask Copilot to generate a function
4. Notice it follows Python-specific guidelines (type hints, Google docstrings)
5. Create a new JavaScript file in `javascript-code/`
6. Ask Copilot to generate a function
7. Notice it follows JavaScript-specific guidelines (JSDoc, arrow functions)

### With GitHub Copilot Coding Agent:

The coding agent automatically respects path-specific instructions when working on files matching the `applyTo` pattern.

## 📝 Instruction Files

- **`python.instructions.md`** - Python coding standards
- **`javascript.instructions.md`** - JavaScript coding standards
- **`python-code/example.py`** - Example Python file following the instructions
- **`javascript-code/example.js`** - Example JavaScript file following the instructions

## 🔍 Key Differences

### Python Instructions Emphasize:
- Type hints (`def func(x: int) -> str:`)
- Google-style docstrings
- pathlib for file operations
- List comprehensions
- Context managers

### JavaScript Instructions Emphasize:
- JSDoc comments
- Arrow functions and const/let
- Async/await patterns
- Destructuring
- Modern ES6+ syntax

## 💡 Use Cases for Path-Specific Instructions

1. **Multi-language repositories**: Different rules for different languages
2. **Legacy vs modern code**: Stricter rules for new code, relaxed for legacy
3. **Framework-specific patterns**: React patterns in `src/components/`, Node.js in `src/api/`
4. **Test code**: Different standards for test files
5. **Documentation**: Special rules for documentation generation

## 🎓 Learning Points

1. **Granular control**: Apply different standards to different parts of your codebase
2. **Scaling strategy**: Start with repository-wide, add path-specific as needed
3. **Priority order**: Path-specific instructions override repository-wide instructions
4. **Pattern matching**: Use glob patterns to target specific files/directories

## 📚 Additional Resources

- [GitHub Copilot Path-Specific Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions)
- Repository-wide instructions: `.github/copilot-instructions.md`
- Simple tutorial: `../custom-instructions-tutorial/`

---

**Note**: Path-specific instructions are currently supported in **VS Code**, **Visual Studio**, **JetBrains IDEs**, and **GitHub Copilot coding agent**.
