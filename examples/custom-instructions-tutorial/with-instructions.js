/**
 * Example function generated WITH custom instructions
 * 
 * Notice the comprehensive documentation, validation, examples, and clear structure.
 * This follows the guidelines defined in copilot-instructions.md
 */

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
 *
 * @example
 * // returns null (invalid input - not a number)
 * areaOfCircle("invalid");
 */
function areaOfCircle(radius) {
  // Early return for invalid input (following the instruction)
  if (typeof radius !== "number" || isNaN(radius) || radius <= 0) {
    // Invalid input: radius must be a positive number
    return null;
  }

  // Calculate area using meaningful variable name
  const area = Math.PI * Math.pow(radius, 2);
  return area;
}

// Example usage demonstrating the function behavior
console.log("Valid inputs:");
console.log(areaOfCircle(5));    // 78.53981633974483
console.log(areaOfCircle(10));   // 314.1592653589793

console.log("\nInvalid inputs:");
console.log(areaOfCircle(-2));   // null
console.log(areaOfCircle(0));    // null
console.log(areaOfCircle("5"));  // null
