// Use the exact historical hardware payload; only the controller's baseline changes.
import {verifyPreparation} from './session-binding.mjs';
import {beginStage as historicalBegin} from '../nss105/module-stage.mjs';
export {uploadStage,readStage,waitStageUndo} from '../nss105/module-stage.mjs';
export async function beginStage(...args){verifyPreparation();return historicalBegin(...args);}
