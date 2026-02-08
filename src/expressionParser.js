export function evaluateExpression(expr, variables) {
    // Uses the given variables (dict from name to value) to evaluate the given expression.
    // This expression can have +-*/(), identifiers and floats (or ints). BIDMAS is adheared to.
    
    const tokens = tokenize(expr);
    const substitutedTokens = substitute(tokens, variables);  // Since scope doesn't really exist, we can convert all identifiers to literals here
    const ast = parse(substitutedTokens);  // This is successful if it cleared the substitutedTokens array
    if (substitutedTokens.length !== 0) throw "Failed to parse full tokens array, did you close all brackets?";
    const result = execute(ast);
    
    return result;
}

export function getUsedSubstitionNames(expr) {
    // Gets the names of values that need to be substituted into expr.
    // Returns Set<string>.
    
    const tokens = tokenize(expr);
    const names = tokens.filter(tok => ((typeof tok === "string" || tok instanceof String) && !OPERATORS.has(tok)));
    
    return Object.freeze(new Set(names));
    
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
const LITERAL_CHARS = new Set("0123456789.");
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
            tokens.push(expr[i]);
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
            tokens.push(parseFloat(literal_chars.join("")));
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
            tokens.push(identifier_chars.join(""));
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

    return tokens;
}

function substitute(tokens, variables) {
    // Substitutes any identifiers in the given tokens array with the variables given.
    // If an identifier has no value in varaibles then an error is thrown.
    
    // Substitute
    const newTokens = tokens.map(tok => ((typeof tok === "string" || tok instanceof String) && !OPERATORS.has(tok)) ? variables[tok] : tok);
    // Find any (and their index) that are undefined (so no variable was found for them)
    const missing = newTokens.map((tok, i) => [tok, i]).filter(toki => toki[0] === undefined);
    // Error if any are missing
    if (missing.length > 0) throw "Variable not specified - "+ tokens[missing[0][1]];
    
    return newTokens;
}

function parse(tokens) {
    // Parses the given tokens into an AST.
    // This expects the only tokens to be literals (floats or ints) and operators (so no variables anymore).
    //
    // The returned AST is a tree formatted like this ["-", ["+", 3, 2], 2].
    // 
    // This will modify the given array.
    //                                                                                                                     ⌄
    // If an (un-opened (by this)) closing bracket is found, then this method will return without consuming it.  E.g. (1+2))/2
    
    if (tokens.length === 0) throw "Expected at least one token";

    let lhs = parsePrimary(tokens);
    while (tokens.length > 0) {
        if (tokens[0] === ")") break;  // If closing bracket then return without consuming
        let op = tokens.shift();
        let opPrecedence = OPERATORS_PRECEDENCE[op];
        if (opPrecedence === undefined) throw "Unexpected token " + op;  // Use precedence's keys as brackets can't come here.
        
        let rhs = parsePrimary(tokens);

        while (tokens.length > 0 && tokens[0] !== ")") {  // RHS may be an expression, e.g. a + 2/3  the 2/3 is the rhs
            let nextOp = tokens[0];
            let nextOpPrecedence = OPERATORS_PRECEDENCE[nextOp];
            if (nextOpPrecedence === undefined) throw "Unexpected token " + nextOp;  // Use precedence's keys as brackets can't come here.
            
            if (opPrecedence >= nextOpPrecedence) break;  // >= as if we have 3 - 2 - 1 then we want to do (3 - 2) - 1
            tokens.shift();  // Consume operator
            
            rhs = [nextOp, rhs, parsePrimary(tokens)];
        }

        lhs = [op, lhs, rhs];
    }
    
    return lhs;
}

function parsePrimary(tokens) {
    // Parses a literal or a bracket or unary operation, but not an identifier/variable.
    // This requires the literal to be a numeric.
    // This consumes the tokens.
    
    // Is it a bracket
    if (tokens[0] === "(") {
        tokens.shift();  // Consume opening bracket
        const parsed = parse(tokens);  
        if (tokens[0] !== ")") throw "Expected closing bracket, got " + tokens[0];
        tokens.shift(); // Consume closing bracket
        return parsed;
    }
    
    // Is it a unary operation?
    if ((tokens[0] === "+" || tokens[0] === "-") && tokens.length > 1) {  // +/- and then at least one more token
        const op = tokens.shift();  // Consume operator
        return [op, 0, parsePrimary(tokens)];  // -a = 0 - a and +a = 0 + a. Parse another primary in-case we have a double unary, e.g. --a
    }
    
    
    // It must be literal
    if (typeof tokens[0] !== "number") throw "Invalid token type, expected number";
    return tokens.shift();
}

function execute(ast) {
    // Computes the value of the ast and returns the result.
    // This expects a tree of integers/floats and operators, foramtted as this ["*", 1, ["+", 2, 5]].
    // This throws an error if an operation results in NaN.
    
    if (Array.isArray(ast)) {
        const lhs = execute(ast[1]);
        const rhs = execute(ast[2]);
        const ret = OPERATORS_FUNCTIONS[ast[0]](lhs, rhs);
        if (isNaN(ret)) throw "Operator resulted in NaN for " + ast + " lhs=" + lhs + " rhs=" + rhs;
        return ret;
    }
    return ast;
}
