/**
 * Example function generated WITHOUT custom instructions
 * 
 * This is a typical output when Copilot has no specific guidelines.
 * It's functional but lacks comprehensive documentation and examples.
 */

function areaOfCircle(radius) {
    if (typeof radius !== 'number' || radius < 0) {
        throw new Error('Radius must be a non-negative number');
    }
    return Math.PI * radius * radius;
}

// Basic usage
console.log(areaOfCircle(5)); // 78.53981633974483
