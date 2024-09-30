/**
 * Validates a SQL string by cleaning it and ensuring it adheres to specific command structures.
 *
 * @param {string} sql - The SQL query to validate.
 * @returns {boolean} - Returns true if the SQL is valid, otherwise false.
 */
export const isValidSql = (sql: string) => {
  try {
    if (!sql?.length) {
      return false;
    }

    // Step 1: Remove duplicated spaces and line breaks
    const cleanedSql = sql
      .split(/\s+/) // Split by any whitespace (space, tab, newline)
      .join(" ") // Join with single space
      .trim(); // Remove leading and trailing spaces

    // Step 2: Check for balanced parentheses
    if (!areParenthesesBalanced(cleanedSql)) {
      return false;
    }

    // Step 3: Identify the SQL command
    const commandMatch = cleanedSql.match(
      /^(SELECT|INSERT INTO|CREATE TABLE)\b/i,
    );
    if (!commandMatch) {
      return false; // Command not allowed
    }

    const command = commandMatch[1].toUpperCase();

    // Step 4: Perform command-specific validations
    switch (command) {
      case "SELECT":
        return validateSelect(cleanedSql);
      case "INSERT INTO":
        return validateInsert(cleanedSql);
      case "CREATE TABLE":
        return validateCreateTable(cleanedSql);
      default:
        return false; // Unsupported command
    }
  } catch (e) {
    console.log("parse error:", e);
    return false;
  }
};

/**
 * Checks if all parentheses in the string are balanced.
 *
 * @param {string} str - The string to check.
 * @returns {boolean} - True if balanced, else false.
 */
const areParenthesesBalanced = (str: string) => {
  const stack = [];
  for (let char of str) {
    if (char === "(") {
      stack.push(char);
    } else if (char === ")") {
      if (stack.length === 0) {
        return false; // Closing parenthesis without matching opening
      }
      stack.pop();
    }
  }
  return stack.length === 0; // All opened parentheses are closed
};

/**
 * Validates a SELECT statement.
 *
 * Ensures it contains a FROM clause and, if present, a LIMIT clause with a valid integer.
 *
 * @param {string} sql - The cleaned SQL SELECT statement.
 * @returns {boolean} - True if valid, else false.
 */
const validateSelect = (sql: string) => {
  // Regular expression to match SELECT statements
  // Captures fields, table, and optional LIMIT
  const selectRegex = /^SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+LIMIT\s+(\d+))?;?$/i;
  const match = sql.match(selectRegex);
  if (!match) return false;

  const fields = match[1].trim();
  const table = match[2].trim();
  const limit = match[3];

  // 1. Ensure at least one field is selected (not empty)
  if (!fields) return false;

  // Optionally, ensure fields are valid (e.g., not just '*')
  // Depending on requirements, you might want to allow '*'
  // Here, we'll allow '*' as it's a valid selection
  if (fields === "*") {
    // '*' is allowed
  } else {
    // Ensure that fields are properly listed
    const fieldList = fields.split(",").map((f) => f.trim());
    if (fieldList.length === 0) return false;
    // Optionally, check for valid field names
    // For simplicity, we'll assume any non-empty string is valid
    for (let field of fieldList) {
      if (!/^\w+$/i.test(field)) return false;
    }
  }

  // 2. Ensure exactly one table is specified in FROM
  if (!table || !/^\w+$/i.test(table)) return false;

  // 3. Validate LIMIT if present
  if (limit !== undefined) {
    const limitValue = parseInt(limit, 10);
    if (isNaN(limitValue) || limitValue < 0) return false;
  }

  return true;
};

/**
 * Validates an INSERT statement.
 *
 * Ensures the number of columns matches the number of values.
 *
 * @param {string} sql - The cleaned SQL INSERT statement.
 * @returns {boolean} - True if valid, else false.
 */
const validateInsert = (sql: string) => {
  // Regular expression to capture table name, columns, and values
  const insertRegex =
    /^INSERT INTO\s+[\w]+\s*\(([^)]+)\)\s+VALUES\s*\(([^)]+)\);?$/i;
  const match = sql.match(insertRegex);
  if (!match) {
    return false; // Invalid INSERT statement format
  }

  const columns = match[1].split(",").map((col) => col.trim());
  const values = match[2].split(",").map((val) => val.trim());

  if (columns.length !== values.length) {
    return false; // Number of columns does not match number of values
  }

  // Optionally, you can add more validations for column names and value formats

  return true;
};

/**
 * Validates a CREATE TABLE statement.
 *
 * Ensures that each column has a name and a type.
 *
 * @param {string} sql - The cleaned SQL CREATE TABLE statement.
 * @returns {boolean} - True if valid, else false.
 */
const validateCreateTable = (sql: string): boolean => {
  // Regular expression to capture table name and columns
  const createTableRegex = /^CREATE TABLE\s+(\w+)\s*\(([^)]+)\);?$/i;
  const match = sql.match(createTableRegex);
  if (!match) {
    return false; // Invalid CREATE TABLE statement format
  }

  const table = match[1].trim();
  const columnsPart = match[2].trim();

  // 1. Ensure table name is valid
  if (!table || !/^\w+$/i.test(table)) return false;

  // 2. Split column definitions by comma
  const columns = columnsPart.split(",").map((col) => col.trim());

  if (columns.length === 0) {
    return false; // No columns defined
  }

  // 3. Define allowed base data types and complex types
  const allowedBaseTypes = ["INT", "STRING", "FLOAT"];

  const allowedComplexTypes = ["LIST"];

  // 4. Validate each column definition
  for (let column of columns) {
    // Regular expression to capture column name and type
    // Supports complex types like list[float]
    const columnRegex = /^(\w+)\s+([\w]+(?:\s*\[\s*\w+\s*\])?)$/i;
    const colMatch = column.match(columnRegex);
    if (!colMatch) {
      return false; // Column definition is invalid
    }

    const colName = colMatch[1].trim();
    const colType = colMatch[2].trim().toUpperCase();

    // Ensure column name is valid
    if (!/^\w+$/i.test(colName)) return false;

    // Check if type is a base type
    if (allowedBaseTypes.includes(colType)) {
      continue;
    }

    // Check for complex types like LIST[FLOAT]
    const complexTypeMatch = colType.match(/^(\w+)\s*\[\s*(\w+)\s*\]$/);
    if (complexTypeMatch) {
      const baseType = complexTypeMatch[1].trim();
      const innerType = complexTypeMatch[2].trim();

      if (!allowedComplexTypes.includes(baseType)) return false;
      if (!allowedBaseTypes.includes(innerType)) return false;
    } else {
      return false; // Type is neither a base type nor a supported complex type
    }
  }

  return true;
};
