'''
Module voor het lezen, schrijven en vinden van .sol bestanden.
Vereist: pyamf (pip install pyamf)
'''
import os
from pathlib import Path
from pyamf import sol

def read_sol(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Bestand niet gevonden: {path}")
    if os.path.getsize(path) == 0:
        raise ValueError("Het bestand is leeg.")
    
    with open(path, 'rb') as f:
        raw_lso = sol.load(f)
    
    # Converteer naar een standaard dict voor makkelijkere verwerking in GUI.
    # Dit is een basisconversie; mogelijk verfijning nodig voor specifieke AMF types.
    lso_dict = {}
    if hasattr(raw_lso, 'items'): # Controleer of het op een dictionary lijkt
        for k, v in raw_lso.items():
            if hasattr(v, '__dict__') and not isinstance(v, type):
                try:
                    # Probeer een diepe conversie voor geneste objecten
                    lso_dict[k] = {ki: vi for ki, vi in v.__dict__.items() if not ki.startswith('_')}
                except Exception:
                    lso_dict[k] = str(v) # Fallback naar string representatie
            elif isinstance(v, list):
                new_list = []
                for item in v:
                    if hasattr(item, '__dict__') and not isinstance(item, type):
                        try:
                            new_list.append({ki: vi for ki, vi in item.__dict__.items() if not ki.startswith('_')})
                        except Exception:
                            new_list.append(str(item))
                    else:
                        new_list.append(item)
                lso_dict[k] = new_list
            else:
                lso_dict[k] = v
    else:
        # Als raw_lso geen items heeft (bijv. een simpele waarde of een lijst op root niveau),
        # probeer het direct te gebruiken of als string.
        # Dit scenario is minder gebruikelijk voor .sol bestanden die game saves bevatten.
        if isinstance(raw_lso, list):
            # Als het een lijst is, moeten we een manier vinden om het in de GUI te representeren.
            # Voor nu, verpakken we het in een dict met een generieke key.
            # Dit zou aangepast kunnen worden afhankelijk van hoe je dit wilt tonen.
            return {'_root_list_data': raw_lso} 
        # Mogelijk andere types hier afhandelen indien nodig
        return {'_root_value': str(raw_lso)} # Fallback

    return lso_dict

def write_sol(path, data):
    with open(path, 'wb') as f:
        sol.save(data, f)

def find_jacksmith_sol_folder():
    """Zoekt naar de Jacksmith .sol bestanden map."""
    appdata_path = os.getenv('APPDATA')
    if appdata_path:
        expected_path = Path(appdata_path) / 'com.flipline.jacksmith' / 'Local Store' / '#SharedObjects'
        if expected_path.is_dir():
            return expected_path
    return None # Geeft None terug als het niet automatisch gevonden is
