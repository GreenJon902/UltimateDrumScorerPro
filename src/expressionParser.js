export function evaluateExpression(expr, variables) {
    // Uses the given variables (dict from name to value) to evaluate the given expression.
    // This expression can have +-*/(), identifiers and floats (or ints). BIDMAS is adheared to.
    
    const tokens = tokenize(expr);
    const substitutedTokens = substitute(tokens, variables);  // Since scope doesn't really exist, we can convert all identifiers to literals here
    const ast = parse(substitutedTokens);
    if (substitutedTokens.length !== 0) throw "Failed to parse full tokens array";
    const result = execute(ast);
    
    return result;
}

const OPERATORS_PRECEDENCE = {  // Maps from operator (single-character) to precedence number (higher means do first). Only contains operators with precedence.
    "+": 0,
    "*": 1,
    "/": 2,
    "-": 0
}

const OPERATORS_FUNCTIONS = {  // Maps from operator (single-character) to function used to evaluate it. Only contains binary operators
    "+": (a, b) => a + b,
    "*": (a, b) => a * b,
    "/": (a, b) => a / b,
    "-": (a, b) => a - b
}

const OPERATORS = new Set("()+/-*");  // Contains all operators (single-characters).
const LITERAL_CHARS = new Set("123456789.");
const IDENTIFIER_CHARS = new Set("abcdefghijklmnopqrstuvwxyz_");

function tokenize(expr) {
    // Splits the given expression into tokens and ensures each token is valid.
    // Returns an array of tokens "<literal>", "+", "-", "/", "*", "(", ")", "<identifier>".
    // This supports only floats or ints as literals.
    
    let i=0;
    const tokens = [];
    while (i < expr.length) {
        // Is token at i an operator
        if (OPERATORS.has(expr[i])) {
            tokens.append(expr[i]);
            i++;
            continue;
        }
        
        // Is token at i a literal
        if (LITERAL_CHARS.has(expr[i])) {
            // Find whole literal
            const literal_chars = [];
            while (i < expr.length && LITERAL_CHARS.has(expr[i])) {
                literal_chars.push(expr[i]);
                i++;
            }
            
            // Convert to float
            tokens.add(parseFloat(literal_chars.join("")));
            continue;
        }
        
        // Is token at i an identifier
        if (IDENTIFIER_CHARS.has(expr[i])) {
            // Find whole identifier
            const identifier_chars = [];
            while (i < expr.length && IDENTIFIER_CHARS.has(expr[i])) {
                identifier_chars.push(expr[i]);
                i++;
            }
            
            // Convert to string
            tokens.add(identifier_chars.join(""));
            continue;
        }
        
        // Is character at i whitespace
        if (expr[i] === " ") {
            i++;
            continue;
        }
        
        // Nothing matched so error
        throw "Failed to tokenize expression";
    }
}

function substitute(tokens, variables) {
    // Substitutes any identifiers in the given tokens array with the variables given.
    // If an identifier has no value in varaibles then an error is thrown.
    
    // Substitute
    const newTokens = tokens.map(tok => ((typeof tok === "string" || tok instanceof String) && !OPERATORS.has(tok)) ? variables[tok] : tok);
    // Throw error if any are undefined (so identifier not in variables)
    if (newTokens.filter(tok => tok === undefined)) throw "Variable not specified";
    
    return newTokens;
}

function parse(tokens) {
    // Parses the given tokens into an AST.
    // This expects the only tokens to be literals (floats or ints) and operators.
    //
    // The returned AST is a tree formatted like this ["-", ["+", 3, 2], 2].
    // 
    // This will modify the given array.
    
    if (tokens.length === 0) throw "Expected at least one token";

    let lhs = parseLiteralOrBracket(tokens);
    while (tokens.length > 0) {
        let op = tokens.shift();
        if (op === ")") break;
        let opPrecedence = OPERATORS_PRECEDENCE[op];
        if (opPrecedence === undefined) throw "Unexpected token";  // Use precedence's keys as brackets can't come here.
        
        let rhs = parseLiteralOrBracket(tokens);

        while (tokens.length > 0 && tokens[0] !== ")") {
            let nextOp = tokens[0];
            let nextOpPrecedence = OPERATORS_PRECEDENCE[op];
            if (nextOpPrecedence === undefined) throw "Unexpected token";  // Use precedence's keys as brackets can't come here.
            
            if (opPrecedence > nextOpPrecedence) break;
            tokens.shift();  // Consume operator
            
            let rhs = [nextOp, rhs, parseLiteralOrBracket(tokens)];
        }

        lhs = [op, lhs, rhs];
    }
    
    return lhs;
}

function parseLiteralOrBracket(tokens) {
    // Parses a literal or a bracket.
    // This requires the literal to be a numeric.
    // This consumes the tokens.
    
    // Is it a bracket
    if (tokens[0] === "(") return parse(tokens);  // This consumes the closing bracket for us
    
    // It must be literal
    if (typeof tokens[0] !== "number") throw "Invalid token type, expected number";
    return tokens.shift();
}

function execute(ast) {
    // Computes the value of the ast and returns the result.
    // This expects a tree of integers/floats and operators, foramtted as this ["*", 1, ["+", 2, 5]].
    
    if (Array.isArray(ast)) return OPERATORS_FUNCTIONS[ast[0]](execute(ast[1]), execute(ast[2]));
    return ast;
}
