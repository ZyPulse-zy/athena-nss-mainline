from pathlib import Path
r=Path('work/v40-five-sim');s=Path('work/v39-five-sim/analyze-hardware.py').read_text().replace('work/v39-five-sim','work/v40-five-sim').replace('3206','3254')
with (r/'analyze-hardware.py').open('x',encoding='utf8') as f:f.write(s)
print('Analysis prepared from the prior explicit five-flow contract; actual hardware required.')
