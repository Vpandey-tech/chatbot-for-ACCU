
"""
Deep Search module for the Mechanical Engineering Chatbot.
Provides advanced knowledge search capabilities using open-source tools.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import os
import random
import string
import time
from datetime import datetime
import traceback
import numpy as np
import faiss
import wikipedia
import requests
import trafilatura
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Suppress urllib3 debug logs to reduce noise
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Ensure NLTK resources are available
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.error(f"Error downloading NLTK resources: {str(e)}")

# Engineering knowledge domains
ENGINEERING_DOMAINS = {
    "materials": [
        "material science", "steel", "aluminum", "composite", "metal", "alloy",
        "properties", "strength", "hardness", "ductility", "heat treatment"
    ],
    "manufacturing": [
        "manufacturing", "machining", "cnc", "casting", "forging", "welding",
        "3d printing", "additive manufacturing", "tooling", "process"
    ],
    "design": [
        "design", "cad", "modeling", "simulation", "analysis", "fea",
        "drawing", "tolerance", "gdt", "dimensioning"
    ],
    "standards": [
        "standard", "regulation", "code", "iso", "astm", "din", "ansi", "asme",
        "certification", "compliance", "quality"
    ],
    "mechanical_systems": [
        "mechanism", "machine", "component", "system", "drive", "gear", "bearing",
        "shaft", "coupling", "chain", "belt", "friction", "lubrication"
    ]
}

class DeepSearchEngine:
    """Advanced search engine for mechanical engineering knowledge."""
    
    def __init__(self):
        """Initialize the search engine."""
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.index = None
        self.documents = []
        self.stop_words = set(stopwords.words('english'))
        
        # Build initial index
        self._build_initial_index()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, wikipedia.exceptions.WikipediaException))
    )
    def _fetch_wikipedia_summary(self, term: str) -> str:
        """Fetch Wikipedia summary for a term with retry logic."""
        return wikipedia.summary(term, sentences=3, auto_suggest=False)
    
    def _build_initial_index(self):
        """Build the initial document index from stored knowledge."""
        try:
            # Add known information about engineering domains
            domain_descriptions = []
            for domain, keywords in ENGINEERING_DOMAINS.items():
                description = f"{domain}: {', '.join(keywords)}"
                domain_descriptions.append(description)
            
            # Get Wikipedia snippets for engineering terms
            engineering_terms = [
                "Mechanical engineering", "Material science", "Manufacturing engineering",
                "Computer-aided design", "Computer-aided manufacturing", "3D printing",
                "Finite element analysis", "CNC machining", "Engineering materials",
                "Engineering tolerances", "Machine design", "Mechanical systems"
            ]
            
            wiki_snippets = []
            for term in engineering_terms:
                try:
                    # Fetch summary with retry
                    snippet = self._fetch_wikipedia_summary(term)
                    wiki_snippets.append(f"{term}: {snippet}")
                    logger.info(f"Successfully fetched Wikipedia snippet for {term}")
                    time.sleep(1)  # Delay to avoid rate limiting
                except Exception as e:
                    logger.error(f"Failed to fetch Wikipedia snippet for {term}: {str(e)}")
                    continue  # Skip failed term and continue
            
            # Combine all documents
            self.documents = domain_descriptions + wiki_snippets
            
            # Build the index
            if self.documents:
                self._update_index()
                logger.info(f"Initial search index built with {len(self.documents)} documents")
            else:
                logger.warning("No documents available to build initial search index")
        
        except Exception as e:
            logger.error(f"Error building initial search index: {str(e)}")
    
    def _update_index(self):
        """Update the search index with current documents."""
        if not self.documents:
            return
        
        try:
            # Create document vectors
            X = self.vectorizer.fit_transform(self.documents)
            X_dense = X.toarray().astype(np.float32)
            
            # Build Faiss index for fast similarity search
            dimension = X_dense.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(X_dense)
        except Exception as e:
            logger.error(f"Error updating search index: {str(e)}")
    
    def search_similar_documents(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search for documents similar to the query.
        
        Args:
            query: The search query
            top_k: Maximum number of results to return
            
        Returns:
            List of similar documents
        """
        if not self.index or not self.documents:
            return []
        
        try:
            # Process query
            query_vec = self.vectorizer.transform([query]).toarray().astype(np.float32)
            
            # Search the index
            D, I = self.index.search(query_vec, min(top_k, len(self.documents)))
            
            # Return matched documents
            results = [self.documents[i] for i in I[0] if i < len(self.documents)]
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def extract_domain_knowledge(self, query: str) -> Dict[str, Any]:
        """
        Extract domain-specific knowledge from a query.
        
        Args:
            query: The user's query
            
        Returns:
            Dictionary with domain knowledge
        """
        knowledge = {}
        
        # Identify the relevant domains
        domain_scores = {}
        query_lower = query.lower()
        
        for domain, keywords in ENGINEERING_DOMAINS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            # Get the highest-scoring domain
            primary_domain = max(domain_scores.items(), key=lambda x: x[1])[0]
            knowledge["primary_domain"] = primary_domain
            
            # Get other relevant domains
            other_domains = [d for d, s in domain_scores.items() if d != primary_domain and s > 0]
            if other_domains:
                knowledge["related_domains"] = other_domains
        
        return knowledge
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """
        Extract technical engineering terms from text.
        
        Args:
            text: Input text
            
        Returns:
            List of technical terms
        """
        terms = []
        
        try:
            # Tokenize text
            words = word_tokenize(text.lower())
            
            # Filter stop words
            filtered_words = [w for w in words if w.isalpha() and w not in self.stop_words]
            
            # Check words against engineering domains
            all_keywords = []
            for domain, keywords in ENGINEERING_DOMAINS.items():
                all_keywords.extend(keywords)
            
            # Extract technical terms
            terms = [word for word in filtered_words if word in all_keywords]
            
            # Add compound terms (multi-word technical terms)
            compound_terms = []
            for domain, keywords in ENGINEERING_DOMAINS.items():
                for keyword in keywords:
                    if " " in keyword and keyword in text.lower():
                        compound_terms.append(keyword)
            
            # Combine results
            all_terms = terms + compound_terms
            
            # Remove duplicates and return
            return list(set(all_terms))
        
        except Exception as e:
            logger.error(f"Error extracting technical terms: {str(e)}")
            return terms
    
    def search_web_for_engineering_knowledge(self, query: str) -> str:
        """
        Search the web for mechanical engineering knowledge (simulated/cached).
        
        Args:
            query: The search query
            
        Returns:
            String with relevant information
        """
        # This function simulates web search with cached/pre-downloaded content
        # In a real implementation, you could use trafilatura to fetch real content
        
        # Extract key terms
        technical_terms = self.extract_technical_terms(query)
        
        if not technical_terms:
            return "No relevant engineering information found."
        
        # Basic simulated "web knowledge"
        cached_knowledge = {
            "cnc": "CNC (Computer Numerical Control) machining is a manufacturing process where pre-programmed software controls the movement of factory tools and machinery. The process can control a range of complex machinery from grinders and lathes to mills and routers.",
            "3d printing": "3D printing or additive manufacturing is the process of making three-dimensional solid objects from a digital file. The creation of a 3D printed object is achieved using additive processes, where an object is created by laying down successive layers of material.",
            "steel": "Steel is an alloy of iron with typically a few percent of carbon to improve its strength and fracture resistance. Many other elements may be present or added to produce different properties. Common types include carbon steel, alloy steel, tool steel, stainless steel, and weathering steel.",
            "aluminum": "Aluminum is a lightweight, corrosion-resistant metal used extensively in aerospace, construction, and consumer products. It offers excellent strength-to-weight ratio, good thermal and electrical conductivity, and high recyclability.",
            "tolerances": "Engineering tolerances are specified allowable variations in dimensions, properties, or conditions. They define the acceptable limits of variation to ensure parts fit and function properly. Precision machining typically works with tolerances measured in thousandths of an inch or hundredths of a millimeter.",
            "heat treatment": "Heat treatment is a group of industrial, thermal, and metalworking processes used to alter the physical, and sometimes chemical, properties of a material. Common heat treatment methods include annealing, case hardening, precipitation strengthening, tempering, carburizing, normalizing, and quenching.",
            "material selection": "Material selection in mechanical engineering involves choosing the optimal material for a specific application based on properties like strength, weight, corrosion resistance, cost, manufacturability, and environmental impact.",
            "gcode": "G-code is the common name for the programming language that controls CNC machines. It tells the motors where to move, how fast to move, and what path to follow. The most common g-code commands include G00 (rapid positioning), G01 (linear interpolation), G02/G03 (circular interpolation), and M codes for machine functions.",
            "fanuc": "FANUC is a leading manufacturer of factory automation solutions, including CNC systems, robots, and production machinery. Their CNC controllers are widely used in manufacturing industries worldwide, especially for machine tools like lathes, mills, and machining centers."
        }
        
        # Collect relevant information
        information = []
        for term in technical_terms:
            # Check if we have information on this term
            for keyword, info in cached_knowledge.items():
                if term in keyword or keyword in term:
                    information.append(info)
        
        if not information:
            return "No specific engineering information found for your query."
        
        # Combine and return
        return "\n\n".join(information)
    
    def enhance_query_with_knowledge(self, query: str) -> Dict[str, Any]:
        """
        Enhance a query with domain knowledge and search results.
        
        Args:
            query: The user's query
            
        Returns:
            Dictionary with enhanced knowledge
        """
        result = {
            "original_query": query,
            "technical_terms": [],
            "domain_knowledge": {},
            "search_results": [],
            "web_knowledge": ""
        }
        
        try:
            # Extract technical terms
            result["technical_terms"] = self.extract_technical_terms(query)
            
            # Get domain knowledge
            result["domain_knowledge"] = self.extract_domain_knowledge(query)
            
            # Search similar documents
            result["search_results"] = self.search_similar_documents(query, top_k=3)
            
            # Get web knowledge if needed
            if result["technical_terms"]:
                result["web_knowledge"] = self.search_web_for_engineering_knowledge(query)
            
            return result
        
        except Exception as e:
            logger.error(f"Error enhancing query: {str(e)}")
            return result
    
    def get_enhanced_response(self, query: str, base_response: str) -> str:
        """
        Enhance a base response with deep knowledge search.
        
        Args:
            query: The user's query
            base_response: The initial response
            
        Returns:
            Enhanced response
        """
        try:
            # Get enhanced knowledge
            knowledge = self.enhance_query_with_knowledge(query)
            
            # Check if we have useful technical information
            if not knowledge["technical_terms"] and not knowledge["web_knowledge"]:
                return base_response
            
            # Prepare enhancement text
            enhancement = ""
            
            # Add domain-specific information if available
            if knowledge["web_knowledge"]:
                enhancement += "\n\nAdditional technical information:\n" + knowledge["web_knowledge"]
            
            # Combine with original response
            if enhancement:
                return base_response + enhancement
            else:
                return base_response
            
        except Exception as e:
            logger.error(f"Error generating enhanced response: {str(e)}")
            return base_response