# Semantic-Matching-with-LLM

## Overview
This tool utilizes a Large Language Model (LLM) and fuzzy matching to perform semantic matching between two distinct lists of terms. LangChain with Ollama are used for generating language model-based suggestions and `fuzzywuzzy` for fuzzy string matching to refine these suggestions based on similarity thresholds. The project is flexible and can work with different open LLM models; currently, it uses the "wizardlm2" model from Microsoft.


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
```

## Example 
### Example command-line usage
```bash
$ python3 match.py
Matching: Dose 1 (non-radiation)
LLM Match: Treatment 1 dose
Match found!
 Dose 1 (non-radiation) <---> Treatment 1 dose
--------------
Matching: Status (stts_name)
LLM Match: Status of samples (Available, Not-available)
Match found!
 Status (stts_name) <---> Status of samples (Available, Not-available)
--------------
```
