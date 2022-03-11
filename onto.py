from pathlib import Path
from level_packs.onto.leavedonto import OntoManager

master = Path('content/ontos/A0_onto.yaml')
om = OntoManager(master)
# om.recompose_ontos_from_master(overwrite=True)
om.onto1.convert2xlsx()