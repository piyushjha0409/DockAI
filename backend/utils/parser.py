import re


def parse_autodock_results(content):
    """
    Parse AutoDock Vina output file content and extract the results table
    into a list of dictionaries.
    """
    # Find the table section - starts with header line containing 'mode'
    table_pattern = r"mode \|   affinity.*?Writing output \.\.\. done\."
    table_match = re.search(table_pattern, content, re.DOTALL)

    if not table_match:
        return {"error": "Could not find results table in the provided file"}

    table_text = table_match.group(0)

    # Skip the header and separator lines
    lines = table_text.strip().split("\n")[3:]  # Skip first 3 lines

    results = []
    for line in lines:
        # Check if the line actually contains data (to handle the "Writing output ... done." line)
        if not re.match(r"\s*\d+\s+", line):
            continue

        # Extract data from each line using regex
        # Format:   1         -8.6      0.000      0.000
        match = re.match(r"\s*(\d+)\s+(-?\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", line)
        if match:
            mode, affinity, rmsd_lb, rmsd_ub = match.groups()
            results.append(
                {
                    "mode": int(mode),
                    "affinity": float(affinity),
                    "rmsd_lb": float(rmsd_lb),
                    "rmsd_ub": float(rmsd_ub),
                }
            )

    return results
