# Atlas Long-Term Memory System

Atlas is equipped with a long-term memory system that allows it to learn from past interactions and improve its performance over time.

## Overview

The memory system is managed by the `MemoryManager` class, which is responsible for:

1.  **Storing Memories**: Saving important information as memories.
2.  **Embedding Memories**: Converting memories into vector embeddings using the `LLMManager`.
3.  **Retrieving Memories**: Searching for and retrieving relevant memories based on the current goal.

## How It Works

The system leverages a local vector store (`ChromaDB`) to manage memories efficiently on the user's machine.

### Memory Storage

After the `MasterAgent` successfully executes a plan, it automatically creates a memory containing:
- The original goal.
- The successful plan that was executed.

This memory is then sent to the `MemoryManager`, which generates a vector embedding for it and stores it in the ChromaDB collection.

### Memory Retrieval

When the `MasterAgent` receives a new goal, it queries the `MemoryManager` before generating a new plan. The `MemoryManager` searches the vector store for memories that are semantically similar to the new goal.

If relevant memories are found, they are injected into the planning prompt given to the `MasterAgent`. This provides the agent with valuable context from past experiences, helping it create more effective and efficient plans.

### Plugin Interaction

Currently, direct interaction with the `MemoryManager` from plugins is not implemented. The memory system operates automatically in the background to assist the `MasterAgent`.

Future versions of Atlas may expose an API for plugins to read from or write to the long-term memory, allowing for even more powerful and context-aware extensions.
