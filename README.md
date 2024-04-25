# Semantic-Matching-with-LLM

## Overview
This project utilizes Large Language Models (LLMs) and fuzzy matching to perform semantic matching between two distinct lists of terms. LangChain with Ollama are used for generating language model-based suggestions and `fuzzywuzzy` for fuzzy string matching to refine these suggestions based on similarity thresholds.

## Dependencies
- Python 3.8 or higher
- Pydantic
- LangChain's LLMs (langchain_community)
- fuzzywuzzy

## Installation

Ensure you have Python installed, then run the following commands to set up the project environment:

```bash
# Install necessary libraries
pip install spacy pydantic langchain-community fuzzywuzzy

# Download the necessary spaCy model
python -m spacy download en_core_web_md
