from pathlib import Path

from level_packs import gen_vocab_report


onto = Path('content/ontos/A0')
out_path = Path('content/')
gen_vocab_report(onto, out_path)
