# GitHub Copilot Custom Instructions Examples

This directory contains practical, hands-on examples demonstrating GitHub Copilot's custom instructions feature.

## 📚 Available Examples

### 1. 🎯 [Your First Custom Instructions](./custom-instructions-tutorial/)

**Perfect for beginners!** Learn how custom instructions transform code generation.

- **What you'll learn**: The basics of custom instructions and their impact
- **Language**: JavaScript
- **Complexity**: ⭐ Beginner
- **Time**: 10 minutes

**Includes**:
- Simple function writing instructions
- Before/after code comparison
- Working examples you can run with Node.js
- Side-by-side impact analysis

👉 **[Start here](./custom-instructions-tutorial/README.md)** if you're new to custom instructions!

---

### 2. 🎨 [Path-Specific Instructions](./path-specific-instructions-example/)

**For intermediate users** working with multi-language codebases.

- **What you'll learn**: How to apply different rules to different parts of your codebase
- **Languages**: Python and JavaScript
- **Complexity**: ⭐⭐ Intermediate
- **Time**: 15 minutes

**Includes**:
- Python-specific coding standards (type hints, pathlib, Google docstrings)
- JavaScript-specific patterns (JSDoc, async/await, ES6+)
- Working examples in both languages
- Glob pattern matching demonstrations

👉 **[Explore this example](./path-specific-instructions-example/README.md)** to learn advanced patterns!

---

## 🚀 Quick Start

### Running the Examples

1. **Clone this repository**:
   ```bash
   git clone https://github.com/matiasportugau-ui/Chatbot-Truth-base--Creation.git
   cd Chatbot-Truth-base--Creation/examples
   ```

2. **Choose an example**:
   ```bash
   # For the basic tutorial
   cd custom-instructions-tutorial
   node test-functions.js
   
   # For path-specific examples
   cd path-specific-instructions-example
   python3 python-code/example.py
   node javascript-code/example.js
   ```

3. **Experiment with GitHub Copilot**:
   - Open the examples in your IDE with GitHub Copilot enabled
   - Try modifying the instruction files
   - Create new files and watch Copilot adapt to the instructions

---

## 📖 Learning Path

Follow this recommended order:

1. **Start with basics**: Begin with the [custom instructions tutorial](./custom-instructions-tutorial/)
2. **See the impact**: Review the before/after comparison
3. **Test locally**: Run the example files to see them work
4. **Go advanced**: Explore [path-specific instructions](./path-specific-instructions-example/)
5. **Apply to your project**: Adapt the patterns to your own codebase

---

## 🎓 Key Concepts Covered

### Custom Instructions
- ✅ What are custom instructions?
- ✅ How do they affect code generation?
- ✅ Where to place instruction files?
- ✅ How to write effective instructions?

### Repository-Wide Instructions
- ✅ Single file at repository root
- ✅ Applies to entire codebase
- ✅ Best for universal coding standards

### Path-Specific Instructions
- ✅ Multiple instruction files with `applyTo` patterns
- ✅ Different rules for different directories
- ✅ Language-specific or framework-specific guidelines
- ✅ Glob pattern matching

---

## 💡 Use Cases

### When to Use Repository-Wide Instructions
- Establishing team-wide coding standards
- Defining documentation requirements
- Setting security practices
- Standardizing error handling

### When to Use Path-Specific Instructions
- Multi-language repositories (Python + JavaScript)
- Different frameworks in different directories
- Stricter rules for production vs. test code
- Legacy code vs. modern code standards

---

## 📚 Additional Resources

### Documentation
- [GitHub Copilot Custom Instructions Guide](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions)
- [Response Customization Concepts](https://docs.github.com/en/copilot/concepts/response-customization)
- [Awesome Copilot Customizations](https://github.com/github/awesome-copilot)

### Repository Resources
- Main custom instructions: [`../.github/copilot-instructions.md`](../.github/copilot-instructions.md)
- Setup guide: [`../.github/COPILOT_SETUP.md`](../.github/COPILOT_SETUP.md)

---

## 🤝 Contributing

Have a great example to share? Contributions are welcome!

1. Create a new directory in `examples/`
2. Include a comprehensive README
3. Add working code examples
4. Test everything thoroughly
5. Update this index file
6. Submit a pull request

---

## 🆘 Need Help?

- Check the README in each example directory
- Review the code comments in example files
- Consult the main repository documentation
- Open an issue if you find problems

---

## ⚡ Quick Tips

1. **Start simple**: Begin with repository-wide instructions
2. **Test frequently**: Try generating code to see the impact
3. **Iterate**: Refine instructions based on results
4. **Be specific**: Clear, concrete guidelines work best
5. **Include examples**: Show Copilot what you want

---

**Happy coding with GitHub Copilot!** 🚀

The examples in this directory demonstrate best practices based on [GitHub's official tutorial](https://docs.github.com/en/copilot/tutorials/customization-library/custom-instructions/your-first-instructions) and real-world usage patterns.
