import pandas as pd

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

third_list = [
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
# Convert the list into a DataFrame
df = pd.DataFrame(first_list, columns=["Column Headers"])
df2 = pd.DataFrame(second_list, columns=["GT Headers"])
df3 = pd.DataFrame(third_list, columns=["Column Headers2"])
# Write the DataFrame to an Excel file
df.to_excel("column_headers.xlsx", index=False)
df2.to_excel("gt_headers.xlsx", index=False)
df3.to_excel("column_headers2.xlsx", index=False)

print("Excel file created successfully.")
