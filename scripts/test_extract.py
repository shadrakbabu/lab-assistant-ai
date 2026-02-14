import pdfplumber
from src.experiment_extractor import ExperimentExtractor
from src.procedure_parser import ProcedureParser

pfile='uploads/LAB MANUAL PDF FOR TESTING.pdf'
with pdfplumber.open(pfile) as pdf:
    text='\n'.join((p.extract_text() or '') for p in pdf.pages)
    ex=ExperimentExtractor()
    pp=ProcedureParser()
    exps=ex.extract_experiments(text)
    print('FOUND', len(exps), 'EXPS')
    for e in exps:
        print(e)
    # choose exp 7
    target = None
    for e in exps:
        if e['number']=='7':
            target=e
            break
    if not target:
        print('Exp 7 not found')
    else:
        sp = target.get('start_page')
        ep = target.get('end_page')
        print('target', target)
        if sp and ep:
            # pages are 1-based in the manual listing
            pages_text = '\n'.join((pdf.pages[i].extract_text() or '') for i in range(sp-1, min(ep, len(pdf.pages))))
            print('\n---- PAGES EXTRACT PREVIEW ----')
            print(pages_text[:2000])
            steps = pp.extract_procedures(pages_text)
            print('\n---- PARSED STEPS ----')
            for s in steps:
                print(s)
        else:
            print('No page range for exp 7')
