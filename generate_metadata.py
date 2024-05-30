import json
from datetime import datetime

# Read the template
with open('metadata_template.json', 'r') as template_file:
    template = template_file.read()

# Fill in the template
date = datetime.utcnow().strftime('%Y-%m-%d')
metadata_content = template.replace('{{date}}', date)

# Write the filled template to metadata.json
with open('metadata.json', 'w') as metadata_file:
    metadata_file.write(metadata_content)
