import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Load the Excel files
df1 = pd.read_excel('slims.xlsx', header=2)
df2 = pd.read_excel('btsc.xlsx')

# Extract column names
columns_file1 = df1.columns.tolist()
columns_file2 = df2.columns.tolist()

threshold = 80

# Store all potential matches and scores
all_potential_matches = []
for col1 in columns_file1:
    for col2 in columns_file2:
        score = fuzz.ratio(col1, col2)  # Using fuzz.ratio for direct comparison
        all_potential_matches.append((col1, col2, score))

# Filter to keep only matches above the threshold
matches_above_threshold = [match for match in all_potential_matches if match[2] >= threshold]

# Sort matches to prioritize highest scores
matches_above_threshold.sort(key=lambda x: x[2], reverse=True)

# Select the best match for each column, ensuring unique matches in df2
best_matches = {}
used_df2_cols = set()
for col1, col2, score in matches_above_threshold:
    if col1 not in best_matches and col2 not in used_df2_cols:
        best_matches[col1] = (col2, score)
        used_df2_cols.add(col2)

# Identify unmatched columns in df1
#unmatched_df1_cols = [col for col in columns_file1 if col not in best_matches]
#print(unmatched_df1_cols)
#print('-------')
# Identify extra columns in df2 not used in best matches
#extra_df2_cols = [col for col in columns_file2 if col not in used_df2_cols]
#print(extra_df2_cols)

# Create a DataFrame for match results
match_results = [(col1, col2, score, "Above Threshold" if score >= threshold else "Below Threshold")
                 for col1, (col2, score) in best_matches.items()]
match_results_df = pd.DataFrame(match_results, columns=['Column in File1', 'Best Match in File2', 'Similarity Score', 'Match Status'])

#Logic


# Add unmatched columns with a status of "Below Threshold"
for col1 in columns_file1:
    if col1 not in best_matches:
        match_results_df = pd.concat([match_results_df, pd.DataFrame([[col1, "No Match Found", 0, "Below Threshold"]],
                                                                      columns=match_results_df.columns)])


# Re-sort the DataFrame to have all entries sorted by their score
match_results_df.sort_values(by='Similarity Score', ascending=False, inplace=True)

# Now, prepare new_df2 based on best_matches and df2_extra for unmatched df2 columns
new_df2 = pd.DataFrame(columns=columns_file1)
for col1 in columns_file1:
    if col1 in best_matches:
        col2, _ = best_matches[col1]
        new_df2[col1] = df2[col2]
    else:
        new_df2[col1] = pd.NA

# Identify extra columns in df2 not used in best matches
extra_columns = [col for col in columns_file2 if col not in used_df2_cols]
df2_extra = df2[extra_columns]


# Export to Excel with multiple sheets
with pd.ExcelWriter('matched_columns_report.xlsx') as writer:
    new_df2.to_excel(writer, sheet_name='Matched Data', index=False)
    df2_extra.to_excel(writer, sheet_name='Extra Columns', index=False)
    match_results_df.to_excel(writer, sheet_name='Match Scores', index=False)

print("Matching completed. Results are in 'matched_columns_report.xlsx'.")

