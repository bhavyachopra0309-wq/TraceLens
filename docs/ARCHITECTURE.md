# Architecture

Source → Lexer → Token Stream → Recursive-Descent CFG Parser → AST → Semantic Analyzer ↔ Scoped Symbol Table → Diagnostics/Safe Fix → TAC → Optimizer → RAG Retriever → AI Compiler Coach → Optional Ollama LLM.

**Guardrail:** deterministic compiler algorithms decide correctness. AI is downstream and explanatory only.
