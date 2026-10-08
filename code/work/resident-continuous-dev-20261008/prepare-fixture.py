from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'resident-normal-dev-i-20261008/fixture.mjs').read_text()
s=s.replace("import {materialize,read,save,stopRequest} from '../resident-dev-20261007/materialize.mjs';", "import {read,save,stopRequest} from '../resident-dev-20261007/materialize.mjs';\nimport {materializeFixture as materialize,requireOwnedUpload} from './fixture-materialize.mjs';")
s=s.replace("import {requireOwnedUpload} from '../v42-counter-window/owned-load-policy.mjs';\n", '')
s=s.replace("from './normal-reader.mjs'", "from '../resident-normal-dev-i-20261008/normal-reader.mjs'")
s=s.replace("import('./normal-policy.mjs')", "import('../resident-normal-dev-i-20261008/normal-policy.mjs')")
s=s.replace('clientSeconds:180,serverSeconds:250', 'clientSeconds:360,serverSeconds:450')
s=s.replace('remainingSeconds>=160', 'remainingSeconds>=300').replace('reserve160 unchanged', 'finite simulation reserve300 required')
s=s.replace('+182000', '+362000').replace('+212000', '+392000').replace('+272000', '+472000').replace('+202000', '+382000')
s=s.replace('Original independent210-second client guard', 'Finite independent390-second client guard')
(root/'fixture.mjs').write_text(s)
print('Separate finite simulation fixture prepared locally')
