import logging
import re 
from typing import Optional, Dict, Any

# Get a logger instance specifically for this module.
# The __name__ variable will be 'string_utils' when this module is imported.
logger = logging.getLogger(__name__)

# --- Utility for Strict Expense Parsing ---
def parse_expense_text_strict(text: str) -> Optional[Dict[str, Any]]:
  """
  Parses expense text strictly for the format: "/new <amount> for <description>"
  Returns None if the format does not match.
  """
  text = text.strip()

  # Must start with "/new "
  if not text.lower().startswith('/new '):
    return None

  # Remove '/new ' prefix
  content = text[5:].strip()

  # Regex to find:
  # 1. An amount: \d+(?:\.\d{1,2})?
  # 2. Followed by "for" (case-insensitive): \s+for\s+
  # 3. Followed by a description: (.*)
  # Using re.IGNORECASE for "for"
  match = re.match(r'^(?P<amount>\d+(?:\.\d{1,2})?)\s+for\s+(?P<description>.+)$', content, re.IGNORECASE)

  if match:
    try:
      amount = float(match.group('amount'))
      description = match.group('description').strip()
      # Default category for now, as user wants strict parsing only
      category = "Uncategorized"

      return {
        "amount": amount,
        "description": description,
        "category": category
      }
    except ValueError:
      logger.warning(f"Failed to convert matched amount '{match.group('amount')}' to float.")
      return None # Indicate parsing failure
  
  else:
    return None # Format did not match strict pattern