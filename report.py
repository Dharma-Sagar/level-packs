from pathlib import Path

from level_packs import gen_vocab_report


onto = Path('content/ontos/A0')
out_path = Path('content/')
vocab_path = Path('content/level_vocab.xlsx')
tagged_path = Path('content/A0/5 to-tag/')
gen_vocab_report(onto, out_path, vocab_path, tagged_path)
