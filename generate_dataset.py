import pandas as pd
import random
from collections import defaultdict

# Complaint templates for each department with varied descriptions
datasets = {
    'Electricity': {
        'High': [
            'live wire hanging near the main road causing electric shock hazard',
            'sparking from transformer in residential area near children',
            'electric pole fallen and live wires on ground floor',
            'short circuit in street light causing fire risk',
            'power outage in hospital during emergency situation',
            'critical live wire exposure threatening public safety',
            'emergency electrical hazard causing immediate danger',
            'dangerous high voltage transformer sparking dangerously',
        ],
        'Medium': [
            'street light not working on main road for 3 weeks',
            'frequent power tripping affecting daily operations',
            'voltage fluctuations damaging household appliances',
            'broken electric meter near market area',
            'dangling wires on telephone poles creating hazard',
            'electricity meter not recording consumption properly',
            'loose connection at transformer causing sparks intermittently',
            'power supply irregular and unstable in area',
            'electrical wire partially damaged needs immediate repair',
            'damaged transformer needs urgent maintenance and fixing',
        ],
        'Low': [
            'street light needs new bulb replacement',
            'light pole slightly tilted, needs straightening',
            'paint fading on electrical pole',
            'minor crack in transformer box',
            'dusty light fixtures need cleaning',
            'minor electrical maintenance required',
            'routine light repair and maintenance needed',
        ]
    },
    'Water': {
        'High': [
            'water leakage from main pipeline affecting entire neighborhood',
            'sewage overflow in residential area causing disease outbreak',
            'water supply stopped for more than 48 hours',
            'contaminated water supply causing health issues',
            'major water tank rupture flooding the area',
            'critical water scarcity affecting hospital and homes',
            'emergency sewage overflow creating hazardous condition',
        ],
        'Medium': [
            'water pipe leakage on street resulting in water waste',
            'water supply irregular, only few hours daily',
            'broken water tap wasting precious water resource',
            'water tank maintenance not done for months',
            'slight discoloration in drinking water',
            'water pressure very low in residential area',
            'drainage pipe choked causing water accumulation',
            'power supply irregular and unstable in area',
            'water pipe partially damaged causing wastage',
            'water supply intermittent requiring urgent action',
            'stagnant water accumulating due to pipe blockage',
        ],
        'Low': [
            'water meter needs servicing and calibration',
            'minor water pipe repair needed at street corner',
            'water tank needs paint refreshing',
            'old water line needs replacement soon',
            'water tap handle broken needs fixing',
            'routine water maintenance scheduled',
        ]
    },
    'Police/Traffic': {
        'High': [
            'vehicle theft reported, urgent investigation needed',
            'robbery incident on main street, criminal still at large',
            'accident with multiple injuries and vehicles involved',
            'assault case reported, victim in critical condition',
            'molestation incident reported by female citizen',
            'traffic accident with fatality near school',
            'reckless drunk driver causing accidents on highway',
            'critical crime incident requiring immediate response',
            'dangerous accident with severe injuries and casualties',
            'emergency traffic situation with multiple vehicle collision',
        ],
        'Medium': [
            'traffic signal malfunctioning at busy intersection causing congestion',
            'vehicles parked illegally blocking emergency access',
            'rash driving near school affecting student safety',
            'traffic noise pollution from horn usage',
            'stolen two wheeler reported in the area',
            'pickpocketing incidents in crowded market',
            'traffic violation with vehicles breaking red light',
            'accident scene without proper barricading setup',
            'vehicle collision on road needing intervention',
            'traffic congestion due to signal malfunction urgently needs fix',
        ],
        'Low': [
            'traffic signal light needs cleaning from dust',
            'road marking faded, lines need repainting',
            'traffic sign damaged needs replacement',
            'helmet not used by riders, awareness campaign needed',
            'parking space marking needs clarification',
            'routine traffic sign maintenance required',
        ]
    },
    'PWD': {
        'High': [
            'major pothole on main road causing accidents and vehicle damage',
            'road completely damaged affecting vehicle movement',
            'bridge foundation showing cracks, structural integrity at risk',
            'manhole cover missing creating dangerous pit',
            'severe subsidence on road near government building',
            'critical road damage causing traffic accident risk',
            'emergency road collapse threatening public safety',
            'severe pothole hazard causing vehicle damage and accidents',
        ],
        'Medium': [
            'multiple potholes on street requiring immediate repair',
            'sidewalk broken making it difficult for elderly and disabled',
            'road surface deteriorated with multiple cracks',
            'street divider damaged after vehicle collision',
            'footpath uneven causing frequent falls and injuries',
            'concrete pavement crumbling near market',
            'road surface uneven near school area',
            'damaged road surface needing urgent patching and repair',
            'broken sidewalk creating walking hazard for citizens',
            'pothole appearing on main street needs quick attention',
        ],
        'Low': [
            'road needs repainting of lane markings',
            'minor pothole needs filling in residential street',
            'street sign faded needs repainting',
            'road needs regular maintenance and sweeping',
            'asphalt patch needed on side street',
            'routine road marking and sign maintenance',
        ]
    },
    'Health Department': {
        'High': [
            'food poisoning outbreak in locality causing hospitalizations',
            'stray dogs attacking people in area, urgent animal control needed',
            'dead bird spreading disease, immediate disposal required',
            'dengue outbreak suspected, vector surveillance urgently needed',
            'unhygienic food preparation in restaurant causing health risk',
            'critical disease outbreak requiring emergency response',
            'emergency health hazard affecting multiple people',
            'severe food contamination causing widespread illness urgently',
        ],
        'Medium': [
            'mosquito breeding in stagnant water, dengue prevention needed',
            'stray dogs roaming creating nuisance and safety hazard',
            'food stall operating without proper hygiene license',
            'pharmacy selling expired medicines illegally',
            'malaria cases reported in residential area',
            'pest control needed for rat infestation urgently',
            'pest infestation near food storage area',
            'vector-borne disease indication requiring intervention and control',
            'mosquito breeding requiring immediate pest control action',
            'health hazard due to animals and insects present nearby',
        ],
        'Low': [
            'health center needs routine inspection and maintenance',
            'clinic needs equipment calibration',
            'health awareness poster placement needed',
            'sanitation training program for food vendors',
            'health checkup camp scheduling needed',
            'routine health facility maintenance required',
        ]
    },
    'Fire': {
        'High': [
            'building on fire with people trapped inside',
            'gas cylinder blast in residential building',
            'chemical fire in warehouse area',
            'explosion near petrol pump causing severe damage',
            'fire in dense residential area threatening multiple buildings',
            'critical fire emergency requiring immediate response',
            'emergency fire situation with potential casualties',
            'severe explosion hazard threatening surrounding buildings',
        ],
        'Medium': [
            'smoke coming from basement of office building',
            'fire extinguisher not available in government building',
            'fire alarm system not working in hospital',
            'electrical burning smell in residential complex',
            'fire safety audit failing in commercial area',
            'potential fire risk due to electrical issue detected',
            'fire hazard condition needing urgent attention and inspection',
            'burning smell indicating possible fire risk in building',
        ],
        'Low': [
            'fire safety signage needs replacement in mall',
            'fire exit door needs repair in office',
            'fire equipment maintenance and inspection due',
            'fire safety training needed for staff',
            'emergency light needs battery replacement',
            'routine fire safety equipment maintenance needed',
        ]
    },
    'Municipality': {
        'High': [
            'open dumping of waste creating health hazard in residential area',
            'encroachment blocking main road affecting public access',
            'garbage accumulation causing disease outbreak',
            'illegal construction on public land',
            'sewage treatment plant overflow causing environmental damage',
            'critical waste management crisis threatening public health',
            'emergency encroachment blocking essential services and access',
            'severe garbage accumulation causing environmental and health emergency',
        ],
        'Medium': [
            'garbage not collected for several days, piling up',
            'overflowing dustbin on street creating smell',
            'tree branches hanging dangerously near road',
            'park encroachment by unauthorized vendors',
            'street cleaning not done for weeks',
            'illegal billboard obstruction on public path',
            'public toilet not functioning for community',
            'waste accumulation needing urgent collection and disposal',
            'garbage piling requiring immediate cleanup action',
            'encroachment issue needing removal and enforcement action',
            'dustbin overflow creating nuisance and smell in area',
        ],
        'Low': [
            'park bench needs repainting and repair',
            'tree branches need pruning for maintenance',
            'park grass needs regular cutting and maintenance',
            'dustbin needs replacement in area',
            'public area beautification needed',
            'street sign installation for park entrance',
            'park fence needs minor repair and maintenance',
            'routine park maintenance and beautification required',
        ]
    }
}

# Generate balanced dataset
random.seed(42)
all_data = []

# Define target samples per category (balanced)
SAMPLES_PER_CATEGORY = 200  # Will give us more data

for dept, priorities in datasets.items():
    for priority, complaints in priorities.items():
        # Generate multiple variations of each complaint
        samples_needed = SAMPLES_PER_CATEGORY
        generated = 0
        
        while generated < samples_needed:
            for complaint in complaints:
                if generated >= samples_needed:
                    break
                
                # Add original
                all_data.append({
                    'text': complaint,
                    'label': dept,
                    'priority': priority
                })
                generated += 1
                
                if generated >= samples_needed:
                    break
                
                # Add variations with slight modifications
                variations = [
                    complaint.replace('needs', 'requires').replace('the', 'this'),
                    complaint.replace('area', 'locality').replace('urgent', 'immediate'),
                    f"Reported: {complaint}",
                    f"{complaint} Please take action",
                    complaint.replace('.', ', action required.'),
                    complaint.replace('and', '&'),
                ]
                
                for variation in variations:
                    if generated >= samples_needed:
                        break
                    all_data.append({
                        'text': variation,
                        'label': dept,
                        'priority': priority
                    })
                    generated += 1

# Shuffle the dataset
random.shuffle(all_data)

# Create DataFrame and save
df = pd.DataFrame(all_data)

print(f"📊 Dataset Generation Report:")
print(f"   Total rows: {len(df)}")
print(f"\n   Department distribution:")
print(f"{df['label'].value_counts().to_string()}")
print(f"\n   Priority distribution:")
print(f"{df['priority'].value_counts().to_string()}")

# Check balance
dept_counts = df['label'].value_counts()
prio_counts = df['priority'].value_counts()
min_dept = dept_counts.min()
max_dept = dept_counts.max()
balance_ratio = (min_dept / max_dept) * 100

print(f"\n   Department Balance Score: {balance_ratio:.2f}% (100% = perfectly balanced)")
print(f"   Min samples per department: {min_dept}")
print(f"   Max samples per department: {max_dept}")

# Save to CSV
df.to_csv('dataset.csv', index=False)
print(f"\n✅ Enhanced dataset saved to dataset.csv")

