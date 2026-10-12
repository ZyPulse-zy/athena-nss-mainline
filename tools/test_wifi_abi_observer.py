"""Run actual observer functions with bounded payload/lifecycle fixtures; no kernel I/O."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]/'code/controller/native'
source=(root/'wifi-abi-observer.c').read_text()
functions=source[source.index('static bool shape_matches'):source.index('static void expiration')]
fixture=(root/'test-wifi-abi-observer.c').read_text().replace('/* SOURCE_FUNCTIONS */',functions)
with tempfile.TemporaryDirectory() as folder:
 p=Path(folder);(p/'test.c').write_text(fixture)
 subprocess.run(['cc','-std=gnu11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
