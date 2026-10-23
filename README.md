🔍 TraceLens AI

Explainable Compiler Error Detection, Code Analysis & AI-Assisted Learning for a Restricted Subset of C

TraceLens AI is an educational compiler and intelligent code-analysis system designed for a restricted subset of the C programming language.

Unlike traditional compilers that primarily report errors, TraceLens exposes the internal compilation pipeline and explains where an error occurred, which compiler phase detected it, why it occurred, and how it can be corrected.

The system combines deterministic Compiler Design techniques with Explainable AI (XAI), Retrieval-Augmented Generation (RAG), and an optional locally running LLM using Ollama.

Core principle: The compiler determines what is wrong. AI explains why.

✨ Key Features

Lexical analysis and token generation

Exact line and column tracking

Recursive-descent CFG parsing

Abstract Syntax Tree (AST) generation

Scoped symbol table

Semantic analysis

Phase-aware error classification

Beginner-friendly compiler diagnostics

Safe deterministic auto-fix

Three-Address Code (TAC) generation

Intermediate-code visualization

Basic code optimization

Compiler pipeline visualization

Retrieval-Augmented Generation (RAG)

AI Compiler Coach

Optional local LLM integration using Ollama

Analysis history

JSON analysis export

Automated test suite

🧠 Compiler Architecture

Source Code
    ↓
Lexical Analyzer
    ↓
Token Stream
    ↓
CFG / Recursive-Descent Parser
    ↓
Abstract Syntax Tree (AST)
    ↓
Semantic Analyzer
    ↕
Scoped Symbol Table
    ↓
Phase-Aware Diagnostic Engine
    ↓
Safe Auto-Fix Engine
    ↓
Intermediate Code Generation
    ↓
Three-Address Code (TAC)
    ↓
Basic Optimizer
    ↓
Compiler Knowledge Retrieval (RAG)
    ↓
AI Compiler Coach
    ↓
Optional Local LLM (Ollama)

🤖 AI Architecture

TraceLens follows a hybrid symbolic-AI architecture.

The LLM is not responsible for deciding whether source code is correct.

Instead:

Deterministic Compiler
        ↓
Verified Diagnostic Evidence
        ↓
Compiler Knowledge Retrieval
        ↓
RAG Context
        ↓
Local LLM
        ↓
Grounded Educational Explanation

Lexical, syntax, and semantic errors are detected using deterministic compiler algorithms.

The AI layer operates downstream and converts verified compiler evidence into easier, contextual explanations for students.

This architecture helps reduce hallucination because the LLM is not treated as the source of truth.

🔤 Lexical Analysis

The lexical analyzer converts source code into tokens such as:

KEYWORD
IDENTIFIER
INTEGER
FLOAT
CHARACTER
STRING
OPERATOR
DELIMITER

Each token contains its source position, including line and column information.

Example:

int total = 10;

can produce:

KEYWORD      int
IDENTIFIER   total
OPERATOR     =
INTEGER      10
DELIMITER    ;

Invalid characters are reported as lexical diagnostics.

🌳 Parsing & Abstract Syntax Tree

TraceLens uses a recursive-descent parser for its supported C grammar.

The parser validates token sequences according to grammar rules and constructs an Abstract Syntax Tree (AST).

Example:

total = a + b * 2;

can conceptually produce:

Assignment
├── Identifier: total
└── BinaryOp: +
    ├── Identifier: a
    └── BinaryOp: *
        ├── Identifier: b
        └── Integer: 2

The AST exposes the hierarchical structure of the program rather than only displaying raw source code.

📚 Symbol Table & Semantic Analysis

The semantic analyzer uses a scoped symbol table to track identifiers and their properties.

The symbol table stores information such as:

Name
Type
Scope
Declaration Location
Symbol Kind

Semantic analysis can identify problems such as:

Redeclaration of identifiers

Use of undeclared identifiers

Basic type incompatibilities

Invalid identifier usage

Scope-related errors

Function argument mismatches within the supported subset

🚨 Phase-Aware Diagnostics

TraceLens distinguishes between different compiler phases.

Lexical Error

int x = 10 @ 2;

The invalid character cannot form a supported token.

Syntax Error

int x = 10
int y = 20;

The tokens themselves are valid, but their arrangement violates the grammar.

Semantic Error

total = marks + bonus;

The statement may be syntactically valid, but identifiers such as total or bonus may not exist in the accessible symbol table.

Diagnostics include information such as:

Diagnostic Code
Compiler Phase
Source Location
Error Message
Failed Rule
Suggested Correction

⚙️ Three-Address Code

After successful front-end analysis, TraceLens generates an intermediate representation using Three-Address Code (TAC).

Example:

total = x + y * 2;

can be represented as:

t1 = y * 2
t2 = x + t1
total = t2

Control-flow constructs can use temporary variables, labels, conditional jumps, and unconditional jumps.

TAC provides a machine-independent representation between source-level analysis and later compiler stages.

🚀 Basic Optimization

TraceLens performs selected educational compiler optimizations on its intermediate representation.

Examples include:

Constant Folding

4 * 5

becomes:

20

Algebraic Simplification

x + 0

becomes:

x

The optimization layer is intentionally limited to safe transformations appropriate for the restricted-C educational scope.

🔧 Safe Auto-Fix

TraceLens includes deterministic corrections for selected errors.

For example, a safely identifiable missing semicolon may be automatically corrected.

Ambiguous semantic problems are not blindly modified. In such cases, TraceLens provides a suggestion and leaves the final decision to the user.

This follows a human-in-the-loop approach.

📖 Retrieval-Augmented Generation (RAG)

TraceLens contains a curated compiler knowledge base covering concepts such as:

Lexical Analysis
CFG Parsing
Syntax Errors
AST
Symbol Tables
Semantic Analysis
Type Checking
Three-Address Code
Optimization
Compiler Diagnostics

When an error is detected, the system retrieves relevant compiler knowledge using the diagnostic context.

The retrieved information is used to ground the AI explanation.

🧑‍🏫 AI Compiler Coach

The AI Compiler Coach transforms compiler diagnostics into educational explanations.

It can explain:

Which compiler phase detected the problem

What caused the problem

Which Compiler Design concept is involved

How the problem can be corrected

Why the error belongs to that compiler phase

What concept the student should revise

The deterministic compiler remains the source of truth.

🦙 Local LLM Integration

TraceLens supports an optional locally running LLM using Ollama.

A compatible Llama model can be used to generate grounded educational explanations without requiring the source code to be sent to a cloud LLM service.

Example setup:

ollama run llama3.2

Verify installed models using:

ollama list

If Ollama is unavailable, TraceLens can continue using its deterministic compiler analysis and grounded built-in explanation layer.

💻 Supported C Subset

TraceLens focuses on an intentionally restricted subset of C, including support for constructs such as:

int

float

char

Variable declarations

Assignments

Arithmetic expressions

Relational expressions

Logical expressions

if

if-else

while

for

Nested blocks

Functions within the supported grammar

Function parameters and calls within the supported grammar

return

The project does not claim to implement the complete ANSI C language.

Restricting the language allows the internal compiler algorithms and structures to remain transparent and suitable for educational use.

🖥️ Application Modules

The interface provides dedicated views for:

Dashboard
Pipeline
Tokens
AST
Symbol Table
Diagnostics
TAC
Optimization
AI Coach
History

Users can directly edit C code, analyze it, inspect intermediate compiler structures, and compare results.

📊 Analysis History

TraceLens maintains analysis history so that users can observe how diagnostics change as they correct their program.

Example:

Run 1 → 3 Errors
Run 2 → 1 Error
Run 3 → 0 Errors

This provides an additional learning mechanism for understanding the effect of code corrections.

📤 JSON Export

Compiler-analysis results can be exported in structured JSON format for future testing, evaluation, or integration.

Exported information can include:

Tokens

Diagnostics

Symbols

AST information

TAC

Optimized intermediate code

Analysis summary

🧪 Testing

The project contains an automated test suite covering representative cases including:

Valid programs

Lexical errors

Syntax errors

Undeclared identifiers

Redeclarations

Functions

if / while

for

Type-related cases

Function-call validation

Run the tests using:

py tests/test_suite.py

📂 Project Structure

TraceLens_100_Percent/
│
├── main.py
├── run_windows.bat
├── requirements.txt
├── README.md
│
├── src/
│   ├── analyzer.py
│   └── ai_engine.py
│
├── samples/
├── tests/
├── knowledge/
├── docs/
└── exports/

▶️ Running the Project

1. Clone the repository

git clone <your-repository-url>

2. Enter the project directory

cd TraceLens_100_Percent

3. Run TraceLens

On Windows:

py main.py

Alternatively, use:

run_windows.bat

The core compiler does not require the LLM to function.

🦙 Optional Ollama Setup

Install Ollama separately and verify:

ollama --version

Run/download the supported model:

ollama run llama3.2

Check installed models:

ollama list

Then start TraceLens and use the Ask Local LLM (Ollama) functionality from the AI section.

🎯 Project Objectives

TraceLens was designed to:

Demonstrate the major stages of a compiler front-end

Make compiler internals visible to students

Distinguish lexical, syntax, and semantic errors

Connect diagnostics to Compiler Design concepts

Generate intermediate representation

Demonstrate introductory compiler optimization

Provide deterministic and explainable corrections

Use AI without replacing compiler correctness

Provide grounded, beginner-friendly learning assistance

💡 What Makes TraceLens Different?

Traditional compiler workflow:

Code → Error Message

TraceLens:

Code
 ↓
Compiler Phase
 ↓
Internal Representation
 ↓
Diagnostic Evidence
 ↓
Failed Compiler Rule
 ↓
Suggested Correction
 ↓
Relevant Compiler Concept
 ↓
Grounded AI Explanation

TraceLens therefore acts not only as an error detector but also as a compiler-learning and visualization environment.

🔬 Key Concepts

The project demonstrates:

Compiler Front-End Design

Lexical Analysis

Context-Free Grammar

Recursive-Descent Parsing

Abstract Syntax Trees

Symbol Tables

Semantic Analysis

Intermediate Code Generation

Three-Address Code

Code Optimization

Explainable AI (XAI)

Retrieval-Augmented Generation (RAG)

Grounded Generation

Hybrid Symbolic-AI Architecture

Human-in-the-Loop Correction

Local Large Language Models

👩‍💻 Author

Bhavya Chopra

B.Tech — Computer Science and Engineering
Vellore Institute of Technology, Vellore

📌 Academic Context

TraceLens AI was developed as a Compiler Design Laboratory project.

The goal is educational: to demonstrate compiler phases and internal structures while improving the way students understand compiler diagnostics.

🔮 Future Enhancements

Although the defined restricted-C project scope is complete, possible future extensions include:

Larger C grammar coverage

Arrays and pointers

More advanced type checking

Additional intermediate representations

Control-flow graphs

Data-flow analysis

Additional optimization passes

Assembly/code generation

More advanced diagnostic ranking

Larger compiler knowledge base

Comparative evaluation with production compiler diagnostics

📄 License

This project was developed for academic and educational purposes.
