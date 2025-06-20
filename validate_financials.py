import sys
import json

TOLERANCE = 0.001 # Allow a small tolerance for floating-point rounding

if len(sys.argv) != 2:
  print("Usage: python validate_financials.py <json_file>")
  sys.exit(1)

filename = sys.argv[1]

with open(filename, 'r') as f:
  data = json.load(f)

def parse_value(val):
  """Converts string to float, handles negatives and missing values."""
  try:
    return round(float(val), 2)
  except Exception:
    return 0.0

def check_rollups(node, path=''):
  """Recursively verifies that each node's value equals the sum of its 
  children's values."""
  errors = []
  node_name = node.get('name', 'Unknown')
  node_value = parse_value(node.get('value', 0))
  current_path = f"{path}/{node_name}"

  items = node.get('items', [])
  if items:
    children_sum = sum(parse_value(child.get('value', 0)) for child in items)

    if abs(children_sum - node_value) > TOLERANCE:
      errors.append({
        'path': current_path,
        'expected': node_value,
        'calculated': children_sum,
        'difference': round(children_sum - node_value, 2)
      })
    # Recurse into children
    for child in items:
      errors.extend(check_rollups(child, current_path))
  return errors

# Check all top-level balance sheet sections
errors = []
for section in ['assets', 'liabilities', 'equity']:
  if section in data:
    errors.extend(check_rollups(data[section], path=section.upper()))

# Print results
if errors:
  print("Discrepancies found:")
  for err in errors:
    print(f"Path: {err['path']}, Expected: {err['expected']}, "
          f"Calculated: {err['calculated']}, Difference: {err['difference']}")
else:
  print("All roll-ups match.")