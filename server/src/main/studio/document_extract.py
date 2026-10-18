"""Bounded subprocess: PDF parsing cannot consume the Studio RAM budget."""
import json
import resource
import sys
from pathlib import Path


def main():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(20,20))
    path=Path(sys.argv[1])
    if path.suffix.lower()=='.pdf':
        from pypdf import PdfReader
        reader=PdfReader(path)
        if reader.is_encrypted:
            raise ValueError('Use an unlocked PDF')
        parts=[]
        for index,page in enumerate(reader.pages[:100]):
            parts.append(f'\n[Page {index+1}]\n'+(page.extract_text() or ''))
            if sum(map(len,parts))>=120000:
                break
        text='\n'.join(parts)
        truncated=len(reader.pages)>len(parts) or len(text)>120000
    else:
        text=path.read_text(encoding='utf-8-sig',errors='replace')
        truncated=len(text)>120000
    if not text.strip():
        raise ValueError('No readable text was found; scanned PDFs need OCR before upload')
    print(json.dumps({'text':text[:120000],'truncated':truncated},ensure_ascii=False))


if __name__=='__main__':
    main()
