from datetime import datetime
import json
import os

from config import OUTPUT_DIR


def write_file(filename, content, output_dir=OUTPUT_DIR):
    """Writes content to a text file."""
    try:
        full_path = os.path.join(output_dir, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[INFO][write_file] content saved to '{full_path}'")
        return full_path
    except Exception as e:
        print(f"[ERROR][write_file] writing writing to file '{filename}': {e}")
        return None

def save_results(data, minute_id, step, format="json", output_dir=OUTPUT_DIR):
    """
    Saves results to a file with appropriate naming.
    """
    timestamp = generate_timestamp()
    filename = f"{minute_id}_{step}_{timestamp}.{format}"

    if format == "json":
        try:
            content = json.dumps(data, indent=2, ensure_ascii=False)
        except:
            content = str(data)
    else:
        content = str(data)

    return write_file(filename, content, output_dir=output_dir)

def generate_timestamp():
    """Generates a timestamp string for filenames."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")