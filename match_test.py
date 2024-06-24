from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_community.llms import Ollama
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from fuzzywuzzy import fuzz

# Pydantic model to represent each item and its match
class ItemMatch(BaseModel):
    match: Optional[str] = Field(None, description="The matching term from the list")

# Initialize the LLM model (Ollama)
#wizardlm2:7b
model = Ollama(model="wizardlm2:7b", base_url="http://localhost:11434/", temperature=0)

def find_best_fuzzy_match(target, candidates, threshold=90):
    """
    Finds the best fuzzy match for a target string among a list of candidate strings.

    Args:
        target (str): The string to match against the candidates.
        candidates (list of str): A list of strings to be evaluated as potential matches.
        threshold (int): The minimum similarity score to consider a match valid.

    Returns:
        tuple: A tuple containing the best match and its similarity score, or None if no valid match is found.
    """
    best_match = None
    highest_similarity = 0

    for candidate in candidates:
        similarity = fuzz.partial_ratio(target, candidate)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = candidate

    return best_match, highest_similarity
    

def find_matches(first_list: List[str], second_list: List[str], progress_signal) -> List[ItemMatch]:
    matches = []
    #Kayvon: Dict of matches of item -> best match
    dict_matches = {}
    # Use a copy of the second list to manipulate without altering the original list outside the function
    available_matches = second_list.copy()
    #total items in first_list
    total_items = len(first_list)
    processed_items = 0
    for item in first_list:
        if not available_matches:
            print("No more matches available in second list.")
        
        quoted_items = [f'\'{term}\'' for term in available_matches]
        query = f"Find the best semantic match for the term '{item}' from the following list: {', '.join(quoted_items)}. If no match set as 'None'. Ouput as JSON"
        print('Matching:',item) 
        
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
        
        # Invoke the chain with the provided query
        result = chain.invoke({"query": query})
        print('LLM Match:', result.match) 
        
        # Check the result and remove the match from available matches if it's found
        if result.match:
            threshold = 90
            match_result = find_best_fuzzy_match(result.match, available_matches, threshold)
            best_match, score = match_result
            if score >= threshold:
                print('Match found!\n', item, '<--->', best_match)
                dict_matches[item] = best_match #Kayvon: Dict of matches of best match -> item
                matches.append(ItemMatch(match=best_match))
                available_matches.remove(best_match)
                print('--------------')
            else:
                print(f'"{result.match}" not in list. Skipping...')
                print('---------------')
                matches.append(ItemMatch(match=None))
        else:
            print('No match found')
            # Append without a match or if the match is not in the available list
            matches.append(ItemMatch(match=None))
            print('---------------')
        processed_items += 1
        progress = int((processed_items / total_items) * 100)
        progress_signal.emit(progress)
    return matches, dict_matches

#Example 
#List of terms that need matching
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

#List of potential matches
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
if __name__ == "__main__":
    match_results = find_matches(first_list, second_list)



