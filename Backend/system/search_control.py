import os
import re

def search_with_regex(pattern, path=".", case_sensitive=False):
    """
    Search for a regex pattern in files within the given path.
    """
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = re.findall(pattern, content, flags)
                        if matches:
                            results.append(f"Found in {file_path}: {matches}")
                except Exception as e:
                    continue  # Skip files that can't be read
    except Exception as e:
        return f"Error during search: {str(e)}"

    if results:
        return "\n".join(results)
    else:
        return "No matches found."