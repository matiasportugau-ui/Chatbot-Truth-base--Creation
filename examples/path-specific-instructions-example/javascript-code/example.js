/**
 * Example JavaScript file demonstrating path-specific custom instructions.
 * 
 * This file follows the JavaScript-specific guidelines defined in javascript.instructions.md
 */

/**
 * Fetches data from an API endpoint with error handling.
 * 
 * @param {string} url - The API endpoint URL
 * @param {Object} options - Fetch options
 * @param {number} options.timeout - Request timeout in milliseconds (default: 5000)
 * @returns {Promise<Object>} The parsed JSON response
 * @throws {Error} If request fails or times out
 * 
 * @example
 * const data = await fetchWithTimeout('/api/users');
 * console.log(data.users.length);
 */
const fetchWithTimeout = async (url, { timeout = 5000 } = {}) => {
  if (!url || typeof url !== 'string') {
    throw new Error('Valid URL string is required');
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    
    throw new Error(`Fetch failed: ${error.message}`);
  }
};

/**
 * Processes an array of items with async operations.
 * 
 * @param {Array<Object>} items - Items to process
 * @param {Function} processor - Async function to process each item
 * @returns {Promise<Array<Object>>} Processed items
 * @throws {Error} If any item fails to process
 * 
 * @example
 * const enrichedUsers = await processItems(
 *   users,
 *   async (user) => ({ ...user, timestamp: Date.now() })
 * );
 */
const processItems = async (items, processor) => {
  if (!Array.isArray(items)) {
    throw new Error('Items must be an array');
  }

  if (typeof processor !== 'function') {
    throw new Error('Processor must be a function');
  }

  try {
    const results = await Promise.all(
      items.map((item, index) => 
        processor(item, index).catch(err => {
          throw new Error(`Failed to process item ${index}: ${err.message}`);
        })
      )
    );
    
    return results;
  } catch (error) {
    throw new Error(`Batch processing failed: ${error.message}`);
  }
};

/**
 * Filters and transforms user data.
 * 
 * @param {Array<Object>} users - Array of user objects
 * @param {Object} filters - Filter criteria
 * @param {boolean} filters.activeOnly - Include only active users
 * @param {number} filters.minAge - Minimum age filter
 * @returns {Array<Object>} Filtered and transformed user data
 * 
 * @example
 * const activeAdults = filterUsers(allUsers, { activeOnly: true, minAge: 18 });
 * console.log(activeAdults.map(u => u.displayName));
 */
const filterUsers = (users, { activeOnly = false, minAge = 0 } = {}) => {
  if (!Array.isArray(users)) {
    throw new Error('Users must be an array');
  }

  return users
    .filter(user => !activeOnly || user.isActive)
    .filter(user => user.age >= minAge)
    .map(({ id, name, email, age, isActive }) => ({
      userId: id,
      displayName: name,
      contactEmail: email,
      userAge: age,
      status: isActive ? 'active' : 'inactive'
    }));
};

/**
 * Creates a debounced version of a function.
 * 
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 * 
 * @example
 * const debouncedSearch = debounce((query) => {
 *   console.log('Searching for:', query);
 * }, 300);
 * 
 * debouncedSearch('hello'); // Only executes after 300ms of inactivity
 */
const debounce = (func, delay) => {
  if (typeof func !== 'function') {
    throw new Error('First argument must be a function');
  }

  if (typeof delay !== 'number' || delay < 0) {
    throw new Error('Delay must be a non-negative number');
  }

  let timeoutId = null;

  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Calculates statistics for an array of numbers.
 * 
 * @param {Array<number>} numbers - Array of numbers to analyze
 * @returns {Object} Statistics object with min, max, average, and sum
 * @throws {Error} If array is empty or contains non-numbers
 * 
 * @example
 * const stats = calculateStats([1, 2, 3, 4, 5]);
 * // { min: 1, max: 5, average: 3, sum: 15, count: 5 }
 */
const calculateStats = (numbers) => {
  if (!Array.isArray(numbers) || numbers.length === 0) {
    throw new Error('Input must be a non-empty array');
  }

  if (!numbers.every(n => typeof n === 'number' && !isNaN(n))) {
    throw new Error('All elements must be valid numbers');
  }

  const sum = numbers.reduce((acc, n) => acc + n, 0);
  const count = numbers.length;

  return {
    min: Math.min(...numbers),
    max: Math.max(...numbers),
    average: sum / count,
    sum,
    count
  };
};

// Example usage
if (typeof module !== 'undefined' && require.main === module) {
  console.log('JavaScript Custom Instructions Example');
  console.log('='.repeat(40));

  // Test calculateStats
  const numbers = [10, 20, 30, 40, 50];
  const stats = calculateStats(numbers);
  console.log('\nNumber statistics:');
  console.log(`  Numbers: ${numbers.join(', ')}`);
  console.log(`  Min: ${stats.min}`);
  console.log(`  Max: ${stats.max}`);
  console.log(`  Average: ${stats.average}`);
  console.log(`  Sum: ${stats.sum}`);

  // Test filterUsers
  const users = [
    { id: 1, name: 'Alice', email: 'alice@example.com', age: 25, isActive: true },
    { id: 2, name: 'Bob', email: 'bob@example.com', age: 17, isActive: false },
    { id: 3, name: 'Charlie', email: 'charlie@example.com', age: 30, isActive: true }
  ];
  
  const activeAdults = filterUsers(users, { activeOnly: true, minAge: 18 });
  console.log('\nFiltered users (active, 18+):');
  activeAdults.forEach(u => console.log(`  - ${u.displayName} (${u.userAge})`));

  // Test debounce
  console.log('\nDebounce example:');
  const debouncedLog = debounce((msg) => console.log(`  Debounced: ${msg}`), 100);
  debouncedLog('This will be logged');
  console.log('  Setup complete (debounced function will execute after delay)');
}

// Export functions for use in other modules
module.exports = {
  fetchWithTimeout,
  processItems,
  filterUsers,
  debounce,
  calculateStats
};
