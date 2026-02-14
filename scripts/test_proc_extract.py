import re
from src.pdf_processor import extract_text_from_pdf, extract_pages
from src.experiment_extractor import ExperimentExtractor
from src.procedure_parser import ProcedureParser

pfile='uploads/LAB MANUAL PDF FOR TESTING.pdf'
text = extract_text_from_pdf(pfile)
pages = extract_pages(pfile)
ex=ExperimentExtractor()
pp=ProcedureParser()
exps=ex.extract_experiments(text)
# pick exp 6 and 7 to test
for target_num in ('6','7'):
    target = next((e for e in exps if e['number']==target_num), None)
    print('\n=== Exp', target_num, 'found ->', bool(target))
    if not target:
        continue
    sp=target.get('start_page')
    ep=target.get('end_page')
    page_texts = [p['text'] or '' for p in pages if p['page_num']>=sp and p['page_num']<=ep]
    sec='\n'.join(page_texts)
    # procedure heuristic
    proc_match = re.search(r'(Procedure(?:s)?[:\s\n]|Experimental Procedure[:\s\n]|Procedure of the Experiment[:\s\n])', sec, re.IGNORECASE)
    if proc_match:
        start = proc_match.start()
        end_match = re.search(r'\n\s*(Theory|Observation|Viva Questions|Precautions|Result|Introduction)\b', sec[start:], re.IGNORECASE)
        if end_match:
            sec = sec[start:start+end_match.start()]
        else:
            sec = sec[start:]
    steps=pp.extract_procedures(sec)
    print('pages',sp,ep,'section len',len(sec),'steps',len(steps))
    for s in steps[:6]:
        print(s)
