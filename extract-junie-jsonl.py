import json
import re
import sys
import os

def unescape_description(text):
    text = text.replace('\\\\', '\\')
    text = text.replace('\\"', '"')
    text = text.replace('\\n', '\n')
    return text

def extract_descriptions(input_file, output_md):
    buffer = ""
    first_timestamp = None
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_md, 'w', encoding='utf-8') as outfile:
        for line in infile:
            buffer += line
            try:
                obj = json.loads(buffer)
                buffer = ""
                if (
                    "event" in obj and
                    obj["event"].get("type") == "AgentStateUpdatedEvent"
                ):
                    description = (
                        obj["event"]
                        .get("state", {})
                        .get("issue", {})
                        .get("description")
                    )
                    if description:
                        if first_timestamp is None:
                            first_timestamp = obj.get("timestampMs")
                        description = unescape_description(description)
                        outfile.write('---\n')
                        outfile.write(description)
                        outfile.write('\n\n')
            except json.JSONDecodeError:
                continue
    return first_timestamp

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.jsonl'):
            input_file = os.path.join(folder_path, filename)
            # Temporary output name, will be renamed after extracting timestamp
            output_md = os.path.splitext(input_file)[0] + '.md'
            print(f"Processing {input_file}")
            first_timestamp = extract_descriptions(input_file, output_md)
            if first_timestamp:
                new_output_md = os.path.join(
                    os.path.dirname(output_md),
                    f"{first_timestamp}_{os.path.basename(output_md)}"
                )
                os.rename(output_md, new_output_md)
                print(f"Renamed output to {new_output_md}")
            else:
                print(f"No description found in {input_file}, output file: {output_md}")

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "-f":
        process_folder(sys.argv[2])
    elif len(sys.argv) == 3:
        extract_descriptions(sys.argv[1], sys.argv[2])
    else:
        print("Usage:")
        print("  python script.py <input_file> <output_md>")
        print("  python script.py -f <folder>")
