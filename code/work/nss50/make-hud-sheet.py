"""Pixel crops for scientific evidence review; never generate or alter HUD values."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
mapping=Path(sys.argv[1]);data=json.loads(mapping.read_text(encoding='utf-8'))
out=mapping.parent/(mapping.stem+'-review')
out.mkdir(exist_ok=False)
for phase in data['phaseMaps']:
    frames=phase['frames']
    if not frames:
        continue
    sheet=Image.new('RGB',(640,240*len(frames)),(18,22,30))
    draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(frames):
        with Image.open(f['file']) as im:
            assert im.size==(f['width'],f['height'])
            assert im.width>=1900 and im.height>=1000
            roi=im.crop((im.width-280,0,im.width,100)).resize((560,200))
            sheet.paste(roi,(40,i*240+30))
        draw.text((12,i*240+8),f"{phase['phase']} | {Path(f['file']).parent.name}/{Path(f['file']).name} | central={f['atLeastOneSecondFromBothPhaseBoundaries']}",fill='white')
    sheet.save(out/(phase['phase']+'-hud.png'))
    thumbs=Image.new('RGB',(640,210*((len(frames)+1)//2)),(18,22,30))
    td=ImageDraw.Draw(thumbs)
    for i,f in enumerate(frames):
        x=(i%2)*320;y=(i//2)*210
        with Image.open(f['file']) as im:
            im.thumbnail((320,180));thumbs.paste(im,(x,y+25))
        td.text((x+4,y+5),f"{phase['phase']} {Path(f['file']).name}",fill='white')
    thumbs.save(out/(phase['phase']+'-full-context.png'))
print(json.dumps({'output':str(out),'purpose':'Actual archived pixel evidence review only','phases':len(data['phaseMaps'])}))
