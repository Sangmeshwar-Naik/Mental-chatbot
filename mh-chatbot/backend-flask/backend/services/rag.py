"""
RAG (Retrieval Augmented Generation) Service
Provides evidence-based mental health resources and CBT/DBT techniques
"""
from typing import List, Dict, Optional
import os


class RAGService:
    """
    RAG service for mental health resources
    Uses vector database to retrieve relevant information
    """
    
    def __init__(self):
        self.vector_db = None
        self.is_initialized = False
        self._initialize_vector_db()
    
    def _initialize_vector_db(self):
        """Initialize vector database (Chroma or FAISS)"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Initialize Chroma client
            self.vector_db = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            # Get or create collection
            try:
                self.collection = self.vector_db.get_collection("mental_health_resources")
            except:
                self.collection = self.vector_db.create_collection("mental_health_resources")
                self._seed_initial_data()
            
            self.is_initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize vector DB: {e}")
            self.is_initialized = False
    
    def _seed_initial_data(self):
        """Seed database with initial mental health resources"""
        initial_resources = [
            {
                "content": "Cognitive Behavioral Therapy (CBT): Identify negative thought patterns and challenge them with evidence. Ask yourself: What evidence supports this thought? What evidence contradicts it?",
                "category": "CBT",
                "techniques": ["thought_challenging", "cognitive_restructuring"]
            },
            {
                "content": "Dialectical Behavior Therapy (DBT) - Distress Tolerance: TIPP technique - Temperature (cold water on face), Intense exercise, Paced breathing, Progressive muscle relaxation.",
                "category": "DBT",
                "techniques": ["distress_tolerance", "crisis_survival"]
            },
            {
                "content": "Mindfulness breathing: Find a comfortable position. Breathe in for 4 counts, hold for 4, breathe out for 6. Focus on the sensation of breath entering and leaving your body.",
                "category": "mindfulness",
                "techniques": ["breathing", "relaxation"]
            },
            {
                "content": "Grounding technique for anxiety: 5-4-3-2-1 method. Notice 5 things you see, 4 things you can touch, 3 things you hear, 2 things you smell, 1 thing you taste.",
                "category": "anxiety",
                "techniques": ["grounding", "sensory_awareness"]
            },
            {
                "content": "Sleep hygiene: Maintain consistent sleep schedule, avoid screens 1 hour before bed, keep bedroom cool and dark, limit caffeine after 2pm.",
                "category": "self_care",
                "techniques": ["sleep", "routine"]
            },
            {
                "content": "Depression management: Break tasks into smaller steps, celebrate small wins, maintain social connections even when you don't feel like it, establish daily routine.",
                "category": "depression",
                "techniques": ["behavioral_activation", "routine"]
            },
            {
                "content": "Emotional regulation: RAIN technique - Recognize the emotion, Allow it to be present, Investigate with curiosity, Nurture yourself with compassion.",
                "category": "emotional_regulation",
                "techniques": ["mindfulness", "self_compassion"]
            },
            {
                "content": "Self-care checklist: Have you eaten today? Had water? Taken medications? Gotten sunlight? Moved your body? Reached out to someone? Been kind to yourself?",
                "category": "self_care",
                "techniques": ["basic_needs", "wellness"]
            }
        ]
        
        # Add to vector database
        for i, resource in enumerate(initial_resources):
            self.collection.add(
                documents=[resource["content"]],
                metadatas=[{"category": resource["category"], "techniques": ",".join(resource["techniques"])}],
                ids=[f"resource_{i}"]
            )
    
    def search_resources(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Search for relevant mental health resources
        
        Args:
            query: User's message or query
            n_results: Number of results to return
        
        Returns:
            List of relevant resources
        """
        if not self.is_initialized:
            return self._get_fallback_resources()
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            resources = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    resources.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'relevance_score': 1 - results['distances'][0][i] if results.get('distances') else 0.5
                    })
            
            return resources
        
        except Exception as e:
            print(f"Error searching vector DB: {e}")
            return self._get_fallback_resources()
    
    def _get_fallback_resources(self) -> List[Dict]:
        """Fallback resources when vector DB is unavailable"""
        return [
            {
                'content': "Remember to practice self-care: ensure you're eating regularly, staying hydrated, and getting adequate sleep.",
                'metadata': {'category': 'self_care'},
                'relevance_score': 0.5
            },
            {
                'content': "Try the 5-4-3-2-1 grounding technique when feeling anxious: Notice 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
                'metadata': {'category': 'anxiety'},
                'relevance_score': 0.5
            }
        ]
    
    def get_cbt_technique(self, thought_pattern: str) -> Dict:
        """Get CBT technique for specific thought pattern"""
        techniques = {
            "catastrophizing": "Challenge catastrophic thinking: What's the worst that could happen? What's the most likely outcome? How would you cope?",
            "all_or_nothing": "Challenge black-and-white thinking: Are there shades of gray? What's a more balanced perspective?",
            "overgeneralization": "Challenge overgeneralizations: Is this always true? Can you think of exceptions?",
            "mental_filter": "Broaden your perspective: What positive things are you filtering out? What's the complete picture?"
        }
        
        return {
            'technique': techniques.get(thought_pattern, "Identify the thought, examine the evidence, find alternatives."),
            'category': 'CBT'
        }


# Singleton instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service singleton"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
