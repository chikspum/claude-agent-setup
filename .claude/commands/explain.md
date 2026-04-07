# /explain $ARGUMENTS

Explain how a specific part of the codebase works.

The user will pass a file path, function name, module, or concept as $ARGUMENTS.

Steps:
1. Find the relevant code (search if needed)
2. Read it thoroughly, including callers and callees
3. Explain:
   - **What** it does (1-2 sentences)
   - **How** it works (step by step, referencing line numbers)
   - **Why** it exists (what problem it solves, what calls it)
   - **Diagram** if there are complex interactions (use ASCII)

Keep explanations concise. Adapt depth to the complexity of the code — simple utility functions get a short answer, complex systems get diagrams and flow descriptions.
