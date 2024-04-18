import spacy
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_community.llms import Ollama
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Pydantic model to represent each item and its match
class ItemMatch(BaseModel):
    #item: str = Field(description="The item from the first list")
    match: Optional[str] = Field(None, description="The matching term from the list")
    #match: str = Field(description="The matching item from the second list. None if no match")

# Initialize the LLM model (Ollama)
#model = Ollama(model="nous-hermes2",temperature=0)
#model = Ollama(model="nous-hermes:13b-q4_0", temperature=0)
#model = Ollama(model="codellama", temperature=0)
#model = Ollama(model="mistral", temperature=0)
#model = Ollama(model="llama2", temperature=0)
model = Ollama(model="wizardlm2:7b", temperature=0)
model = Ollama(model="llama3", temperature=0)

def filter_by_similarity(items: List[str], term: str, threshold: float = 0.3) -> List[str]:
    term_doc = nlp(term)
    return [item for item in items if nlp(item).similarity(term_doc) > threshold]

def find_matches(first_list: List[str], second_list: List[str]) -> List[ItemMatch]:
    matches = []
    # Use a copy of the second list to manipulate without altering the original list outside the function
    available_matches = second_list.copy()
    
    for item in first_list:
        if not available_matches:
            print("No more matches available in second list.")
            break
        # Filter the second list to include only semantically similar items 
        filtered_list = filter_by_similarity(available_matches, item)
        
        # Filter by keywords (optional)
        #words = item.split()
        #filtered_list = [
        #    match_item for match_item in second_list
        #    if any(word.lower() in match_item.lower() for word in words)
        #]

        # Formulate the prompt query for the language model
        #query = f"Find the best semantic match for '{item}' from this list: {', '.join(filtered_list)}, if any. If no match set as None"
        #filtered_list = available_matches
        #quoted_items = [f'\'{term}\'' for term in filtered_list]
        quoted_items = [f'\'{term}\'' for term in available_matches]
        query = f"Find the best semantic match for the term '{item}' from the following list: {', '.join(quoted_items)}. If no match set as 'None'. Ouput as JSON"
        print('Matching:',item) 
        #print(query)
        # Set up the parser to convert model output to Pydantic object
        parser = PydanticOutputParser(pydantic_object=ItemMatch)
        
        # Define the prompt template
        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        
        # Create a chain of operations: prompt template -> model -> parser
        chain = prompt | model | parser
        #print(chain)
        # Invoke the chain with the provided query
        result = chain.invoke({"query": query})
        print(result)
        # Check the result and remove the match from available matches if it's found
        if result.match and result.match in available_matches:
            print('Match found!\n', item,'<--->', result.match)
            matches.append(result)
            # Remove the match from the list of available matches
            available_matches.remove(result.match)
            print('--------------')
        else:
            print('No match found')
            # Append without a match or if the match is not in the available list
            matches.append(ItemMatch(match=None))
            print('---------------')

    return matches

# Lists of items and potential matches
#first_list = ['apple', 'carrot', 'car','Broccoli','Mango','Spinach']
#second_list = ['fruit', 'vegetable','meat']

first_list = [
    "Dose 1 (non-radiation)",
    "Status (stts_name)",
    "Barcode",
    "Chronic exposure duration (Hours) unit",
    "Linear Energy Transfer  (in water) (keV/micron)",
    "Particle energies  (in order of administration)",
    "Time between exposures (for multiple particle)",
    "Particle charge(s)  (in order of administration)",
    "Ionizing radiation  (in order of administration)",
    "Dose 3 (non-radiation)",
    "Dose 2 (non-radiation)",
    "Age at irradiation",
    "ALSDA biospecimen ID",
    "Sample name",
    "Section",
    "Type (cntp_name)",
    "Id",
    "Payload ID (rdrc_name)",
    "Project",
    "Sponsor",
    "<SLIMSGUID>",
    "Category (cntp_name)",
    "Derivation count"
]

second_list = [
    "Timestamp",
    "PI name",
    "PI Institution",
    "Phone number",
    "Email",
    "NSRL run #",
    "Grant number",
    "Species/Type",
    "Number of subjects for experimental group",
    "Subject unique identifiers for this experimental group separated by comma followed by a space (EX. 112, 113, 114, 115)",
    "Treatment 1 dose",
    "Treatment 1 dose units",
    "Do you have another treatment?",
    "Treatment 2 dose",
    "Treatment 2 dose units",
    "Do you have another treatment? .1",
    "Treatment 3 dose",
    "Treatment 3 dose units",
    "(Non-Irradiated Control) Were mice sacrificed at a specific timepoint?",
    "Sham model?",
    "(Acute) Age at exposure (Weeks)",
    "Number of particle types",
    "Ionizing radiation",
    "Particle energies",
    "Energy unit",
    "(Acute) Were mice sacrificed at a specific timepoint?",
    "Sham model?",
    "Radiation beam type.1",
    "(Chronic) Age at exposure (Weeks)",
    "Ionizing Radiation",
    "Time between exposures (Hour).1",
    "Particle energies.1",
    "Energy unit .1",
    "Total absorbed dose per particle type.1",
    "Total absorbed dose units .1",
    "Absorbed dose rate .1",
    "Absorbed dose rate unit  .1",
    "(Chronic) Were mice sacrificed at a specific timepoint?",
    "Sham model? .1",
    "Radiation beam type.2",
    "(Fractionated) Age at exposure (Weeks)",
    "Number of particle types.1",
    "Ionizing radiation",
    "Time between fractions unit",
    "Particle energies.2",
    "Absorbed dose rate .2",
    "Absorbed dose rate unit  .2",
    "(Fractionated) Were mice sacrificed at a specific timepoint?",
    "****Time point of sacrifice post-irradiation units",
    "Date of euthanasia",
    "***Time point of sample collection post-irradiation treatment",
    "***Time point of sample collection post-irradiation units",
    "Date of sample collection",
    "Biospecimen type",
    "Status of samples (Available, Not-available)",
    "Box Information for Shipment (Number, barcode, etc.) separated by comma to match the order of your input for the 'Subject unique identifier' field, (EX. 112, 113, 114, 115)",
    "Cage number (s) separated by comma to match the order of your input for the 'Subject unique identifier' field, (EX. 112, 113, 114, 115)",
    "Unnamed: 85",
    "Subject unique identifiers for this experimental group separated by comma followed by a space (EX. 112, 113, 114, 115).1",
    "Cage number (s) separated by comma to match the order of your input for the 'Subject unique identifier' field, (EX. 112, 113, 114, 115).1"
]


# Find matches using the LLM model
match_results = find_matches(first_list, second_list)
print(first_list)
print('-------')
print(match_results)

# Print the results

