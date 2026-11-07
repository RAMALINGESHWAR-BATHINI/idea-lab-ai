from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
prs = Presentation(r'C:\Users\pc\Downloads\Awareness_program_PPT_23_09_2026.pptx')
slide = prs.slides[1]
texts = []
for s in slide.shapes:
    if s.has_text_frame and s.text.strip():
        texts.append((s.left, s.top, s.text.strip()[:40]))
counter = [0]
def walk(shape, path=''):
    if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        for s in shape.shapes:
            walk(s, path)
    elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
        counter[0]+=1
        # nearest text
        best = min(texts, key=lambda t: abs(t[0]-shape.left)+abs(t[1]-shape.top))
        print('img %d at (%d,%d) -> nearest: %s' % (counter[0], shape.left, shape.top, best[2]))
for s in slide.shapes:
    walk(s)
