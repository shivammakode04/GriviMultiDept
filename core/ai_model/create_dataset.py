import pandas as pd
import random

# Minimal balanced dataset focused on quality examples
data = []

complaints = {
    'Electricity': {
        'High': ['live wire on road', 'sparking transformer', 'electric pole down', 'short circuit fire risk', 'hospital power outage'],
        'Medium': ['street light off', 'power tripping', 'meter broken', 'dangling wire', 'loose connection'],
        'Low': ['bulb replacement', 'pole tilt', 'paint fading', 'crack in box', 'dusty fixture']
    },
    'Water': {
        'High': ['water pipeline rupture', 'sewage overflow disease', 'water supply cut', 'contaminated water', 'tank rupture flood'],
        'Medium': ['water pipe leak', 'irregular supply hours', 'tap broken', 'tank not maintained', 'water discolored'],
        'Low': ['meter servicing', 'minor repair', 'tank paint', 'old line replace', 'tap handle fix']
    },
    'Police/Traffic': {
        'High': ['vehicle theft urgent', 'robbery incident', 'accident multiple injuries', 'assault victim', 'molestation reported'],
        'Medium': ['signal broken jam', 'illegal parking', 'rash driving school', 'noise pollution', 'two wheeler stolen'],
        'Low': ['signal light dirty', 'mark lines faded', 'sign damaged', 'helmet awareness', 'parking mark']
    },
    'PWD': {
        'High': ['major pothole accident', 'road damage traffic', 'bridge crack structural', 'manhole cover missing', 'road subsidence'],
        'Medium': ['potholes repair', 'sidewalk broken', 'road cracked', 'divider damaged', 'path uneven falls'],
        'Low': ['lane marking repaint', 'minor pothole', 'sign faded', 'maintenance sweep', 'asphalt patch']
    },
    'Health Department': {
        'High': ['food poison outbreak', 'dog attack animal', 'dead bird disease', 'dengue outbreak vector', 'food unhygienic'],
        'Medium': ['mosquito breeding', 'stray dogs nuisance', 'food stall license', 'pharmacy expired', 'malaria cases'],
        'Low': ['health inspection', 'clinic calibration', 'health awareness', 'sanitation training', 'health checkup']
    },
    'Fire': {
        'High': ['building fire trapped', 'gas cylinder blast', 'chemical fire warehouse', 'explosion petrol pump', 'fire residential'],
        'Medium': ['smoke basement', 'no fire extinguisher', 'alarm not working', 'electrical burning', 'fire safety audit'],
        'Low': ['safety sign replace', 'exit door repair', 'equipment maintenance', 'fire safety training', 'light battery']
    },
    'Municipality': {
        'High': ['open dump hazard', 'encroachment road', 'garbage outbreak', 'illegal construction', 'sewage overflow'],
        'Medium': ['garbage not collected', 'dustbin overflow', 'tree branches danger', 'park encroachment', 'street clean'],
        'Low': ['bench repair', 'tree pruning', 'grass cutting', 'dustbin replace', 'beautification']
    }
}

for dept, priorities in complaints.items():
    for priority, complaint_list in priorities.items():
        for complaint in complaint_list:
            # Add original
            data.append({'text': complaint, 'label': dept, 'priority': priority})
            # Add variations
            data.append({'text': f'{complaint} urgent', 'label': dept, 'priority': priority})
            data.append({'text': f'{complaint} reported', 'label': dept, 'priority': priority})
            data.append({'text': f'Issue: {complaint}', 'label': dept, 'priority': priority})

random.seed(42)
random.shuffle(data)

df = pd.DataFrame(data)
df.to_csv('dataset.csv', index=False)

print(f'✅ Dataset created: {len(df)} rows')
print(f'\nDepartment distribution:')
print(df['label'].value_counts())
print(f'\nPriority distribution:')
print(df['priority'].value_counts())
