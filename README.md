# Semantic-Matching-with-LLM

## Overview
This tool utilizes Large Language Models (LLMs) and fuzzy matching to perform semantic matching between two distinct lists of terms. LangChain with Ollama are used for generating language model-based suggestions and `fuzzywuzzy` for fuzzy string matching to refine these suggestions based on similarity thresholds. The project is flexible and can work with different open LLM models; currently, it uses the "wizardlm2" model from Microsoft.


## Dependencies
- Python 3.8 or higher
- Pydantic
- LangChain's
- Ollama
- fuzzywuzzy

## Installation

Ensure you have Python installed, then run the following commands to set up the project environment:

```bash
# Install necessary libraries
pip install pydantic langchain-community fuzzywuzzy

#
# Overview
"Semantic-Matching-with-LLM" is a Python project designed to perform semantic matching between two lists of terms by leveraging Language Learning Models (LLMs) and fuzzy matching. Utilizing the advanced capabilities of LangChain's Ollama model, which is based on the open-source "wizardlm2" LLM from Microsoft, the project effectively suggests matches and refines these suggestions with fuzzy string matching to ensure high similarity between matched terms.

## Dependencies
- Python 3.8 or higher
