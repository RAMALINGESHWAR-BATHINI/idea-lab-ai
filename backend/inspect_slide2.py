from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Emu
prs = Presentation(r'C:\Users\pc\Downloads\Awareness_program_PPT_23_09_2026.pptx')
slide = prs.slides[1]
for shape in slide.shapes:
    if shape.shape_type == MSO_SHAPE_TYPE.PICTURE or shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        # find nearest text
        nearest = None
        for t in slide.shapes:
            if t.has_text_frame and t.text.strip():
                dx = abs(t.left - shape.left)
                dy = abs(t.top - shape.top)
                if nearest is None or (dx+dy) < nearest[0]:
                    nearest = (dx+dy, t.text.strip()[:60])
        print(f'IMG/GROUP at ({shape.left},{shape.top}) size {shape.width}x{shape.height} -> nearest text: {nearest[1] if nearest else None}')
    elif shape.has_text_frame and shape.text.strip():
        print(f'TEXT at ({shape.left},{shape.top}): {shape.text.strip()[:60]}')
