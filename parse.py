import os
import pandas as pd

jsonl_file = open("leads.jsonl", "w")
main_folder = "Lead Cache"  # unzipped folder with all subfolders (should remove MACOSx folder to avoid duplicates just in case)

lead_count = 0
skipped_files = []
read_files = []

for root, dirs, files in os.walk(main_folder):
    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(root, file)
            df = pd.read_csv(file_path)

            if "insight" in df.columns:
                read_files.append(file)

                leads_array = []    # store all leads for this file
                insight_array = []  # store all insights this file

                for _, row in df.iterrows():
                    lead = {}
                    insight = ""
                    for col_name, value in row.items():  # iterate through row, column names can vary from csv to csv
                        if col_name == "insight":
                            insight = value
                        else:
                            lead[col_name] = value if not pd.isna(value) else "Information Not Available"

                    if insight == "":
                        raise Exception("No Insight Found For File: " + file)

                    leads_array.append(lead)
                    insight_array.append(insight)

                if len(insight_array) != len(leads_array):
                    raise Exception("Mismatch between Insight Array and Lead Array")

                print("Parsing " + str(len(leads_array)) + " leads from file " + file)

                for i in range(len(leads_array)):
                    lead_count += 1
                    jsonl_file.write('{"messages": [')

                    complete_lead_file = ", ".join(
                        f"Lead {i + 1}: [" + ", ".join(f"{key}: {value}" for key, value in lead.items()) + "]"      # enumerated to act as a seperator for the entire file of leads
                        for i, lead in enumerate(leads_array)
                    )
                    jsonl_file.write(
                        f"{{\"role\":\"system\", \"content\":\"Here is the complete lead file: [{complete_lead_file}]\"}},")

                    individual_lead_data = ", ".join(f"{key}: {value}" for key, value in leads_array[i].items())
                    jsonl_file.write(f"{{\"role\":\"user\", \"content\":\"Individual Lead Data: {{{individual_lead_data}}}\"}},")

                    assistant_message = f"Based on the Individual Lead Data and the whole file, the insight is {insight_array[i]}"
                    jsonl_file.write(f"{{\"role\":\"assistant\", \"content\":\"{assistant_message}\"}}]}}")

                    jsonl_file.write("\n")
            else:
                skipped_files.append(file)

jsonl_file.close()

print("Total leads (With Insights) Parsed: " + str(lead_count))
print("Skipped CSV files: " + str(len(skipped_files)))
print("Read files: " + str(len(read_files)))