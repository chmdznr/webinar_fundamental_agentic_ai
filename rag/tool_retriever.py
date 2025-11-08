"""
RAG Tool Retriever for AgenKampus

This module implements the "Librarian" concept - using ChromaDB and semantic search
to find the most relevant tools for a given user query.

Think of it this way:
- Without RAG: Agent sees ALL 1000 tools → Overwhelming, slow, expensive
- With RAG: Agent sees only TOP 3 most relevant tools → Fast, focused, efficient

Educational Demo:
- We only have 4 tools, but this scales to hundreds or thousands
- Demonstrates semantic similarity search using embeddings
- Shows how AI can intelligently select which tools to use
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class ToolRetriever:
    """
    Retrieves relevant tools using semantic search over tool descriptions.

    Architecture:
    1. Load tool descriptions from JSON
    2. Generate embeddings using sentence-transformers
    3. Store embeddings in ChromaDB (vector database)
    4. For queries: embed query → find similar tool descriptions → return tools
    """

    def __init__(
        self,
        tool_descriptions_path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: str = "tool_descriptions",
        persist_directory: Optional[str] = None
    ):
        """
        Initialize the tool retriever.

        Args:
            tool_descriptions_path: Path to JSON file with tool metadata
            embedding_model: HuggingFace model name for embeddings
            collection_name: ChromaDB collection name
            persist_directory: Directory to store ChromaDB data
        """
        # Setup paths
        if tool_descriptions_path is None:
            script_dir = Path(__file__).parent
            tool_descriptions_path = script_dir / "tool_descriptions.json"

        if persist_directory is None:
            script_dir = Path(__file__).parent
            persist_directory = script_dir / "chroma_db"

        self.tool_descriptions_path = Path(tool_descriptions_path)
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name

        # Load tool descriptions
        print(f"📚 Loading tool descriptions from {self.tool_descriptions_path}")
        with open(self.tool_descriptions_path, 'r') as f:
            self.tools = json.load(f)
        print(f"   Loaded {len(self.tools)} tools")

        # Initialize embedding model
        print(f"🤖 Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print(f"   ✓ Embedding model ready (dimension: {self.embedding_model.get_sentence_embedding_dimension()})")

        # Initialize ChromaDB
        print(f"💾 Initializing ChromaDB at {self.persist_directory}")
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Tool descriptions for semantic search"}
        )

        # Index tools if collection is empty
        if self.collection.count() == 0:
            print("📝 Indexing tools (first run)...")
            self._index_tools()
        else:
            print(f"   ✓ Found {self.collection.count()} indexed tools")

    def _create_searchable_text(self, tool: Dict[str, Any]) -> str:
        """
        Create rich searchable text from tool metadata.

        Combines description, keywords, and examples to create a comprehensive
        text representation that captures all aspects of the tool.

        Args:
            tool: Tool metadata dictionary

        Returns:
            Combined searchable text
        """
        parts = [
            f"Tool: {tool['name']}",
            f"Description: {tool['description']}",
            f"Category: {tool['category']}",
            f"Keywords: {', '.join(tool['keywords'])}",
            f"Examples: {' | '.join(tool.get('examples', []))}"
        ]

        return " ".join(parts)

    def _index_tools(self):
        """
        Index all tools into ChromaDB with embeddings.

        Process:
        1. Create searchable text for each tool
        2. Generate embeddings using sentence-transformers
        3. Store in ChromaDB with metadata
        """
        documents = []
        metadatas = []
        ids = []

        for tool in self.tools:
            # Create rich searchable text
            searchable_text = self._create_searchable_text(tool)
            documents.append(searchable_text)

            # Store metadata
            metadatas.append({
                "name": tool["name"],
                "server": tool["server"],
                "category": tool["category"],
                "description": tool["description"][:200]  # Truncate for storage
            })

            # Unique ID
            ids.append(tool["name"])

        # Generate embeddings
        print("   Generating embeddings...")
        embeddings = self.embedding_model.encode(
            documents,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()

        # Add to ChromaDB
        print("   Adding to ChromaDB...")
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(f"   ✓ Indexed {len(documents)} tools successfully")

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant tools for a query.

        Args:
            query: User's question or request
            top_k: Number of tools to retrieve
            score_threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of tool metadata dictionaries with similarity scores

        Example:
            >>> retriever = ToolRetriever()
            >>> tools = retriever.retrieve("What time is it?", top_k=2)
            >>> print(tools[0]['name'])
            get_waktu_saat_ini
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True
        ).tolist()

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Process results
        retrieved_tools = []

        for idx in range(len(results['ids'][0])):
            tool_name = results['ids'][0][idx]
            distance = results['distances'][0][idx]

            # Convert distance to similarity score (cosine similarity)
            # ChromaDB returns L2 distance, convert to similarity
            # For normalized vectors: similarity ≈ 1 - (distance² / 2)
            similarity = 1 - (distance ** 2 / 2)

            # Skip if below threshold
            if similarity < score_threshold:
                continue

            # Find full tool data
            tool_data = next((t for t in self.tools if t['name'] == tool_name), None)

            if tool_data:
                retrieved_tools.append({
                    **tool_data,
                    'similarity_score': similarity,
                    'retrieval_rank': idx + 1
                })

        return retrieved_tools

    def get_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get full tool metadata by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool metadata dictionary or None if not found
        """
        return next((t for t in self.tools if t['name'] == tool_name), None)

    def list_all_tools(self) -> List[str]:
        """
        Get list of all available tool names.

        Returns:
            List of tool names
        """
        return [tool['name'] for tool in self.tools]

    def demo_retrieval(self, queries: List[str], top_k: int = 3):
        """
        Demonstrate retrieval for multiple queries.

        Educational helper for testing and visualization.

        Args:
            queries: List of test queries
            top_k: Number of results per query
        """
        print("\n" + "="*80)
        print("🔍 RAG TOOL RETRIEVAL DEMO")
        print("="*80)

        for query in queries:
            print(f"\n📝 Query: \"{query}\"")
            print("-" * 80)

            results = self.retrieve(query, top_k=top_k)

            if not results:
                print("   ⚠️ No tools found")
                continue

            for idx, tool in enumerate(results, 1):
                print(f"\n   {idx}. {tool['name']} (Similarity: {tool['similarity_score']:.3f})")
                print(f"      Server: {tool['server']}")
                print(f"      Category: {tool['category']}")
                print(f"      Description: {tool['description'][:100]}...")


def main():
    """
    Test the RAG retriever with example queries.
    """
    print("🚀 Initializing ToolRetriever...")
    print()

    retriever = ToolRetriever()

    print("\n" + "="*80)
    print("✅ ToolRetriever initialized successfully!")
    print("="*80)

    # Demo queries
    test_queries = [
        "What time is it now?",
        "Calculate 10 times 5",
        "Who is the advisor of Agus Setiawan?",
        "Show me courses for Rini Wijaya",
        "Siapa dosen pembimbing Rini?",
        "Hitung 2+2"
    ]

    retriever.demo_retrieval(test_queries, top_k=2)

    print("\n" + "="*80)
    print("✅ Demo completed!")
    print("="*80)


if __name__ == "__main__":
    main()
