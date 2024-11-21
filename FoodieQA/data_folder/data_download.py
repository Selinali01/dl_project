from datasets import load_dataset
import pandas as pd
from huggingface_hub import login
login("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")

ds = load_dataset("lyan62/FoodieQA")

# Combine all splits into a single DataFrame
all_data = pd.concat([pd.DataFrame(ds[split]) for split in ds.keys()])

# Save the combined DataFrame to a single CSV file
all_data.to_csv("foodieqa_combined.csv", index=False)

print("Entire dataset saved as foodieqa_combined.csv")