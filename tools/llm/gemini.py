"""Send a text task to Gemini (Google AI Studio free tier) and write the answer to a file. For TEXT jobs only:
captions, hashtags, analytics tables from screenshots, summaries. Code, renders and final decisions stay with Claude.
The key is read from the environment variable GEMINI_API_KEY (Windows user variable on the PC). Never put the key in a file in the repo.
Note: on the free tier Google may use prompts to improve its products; do not send anything private.

  python tools/llm/gemini.py "task text" [--file a.md --file shot.jpg ...] [--out answer.md] [--model gemini-2.5-flash]
  python tools/llm/gemini.py --list          (shows the model names this key can use)
Only the standard library is used (no pip install)."""
import os, sys, json, base64, argparse, mimetypes, urllib.request, urllib.error
API='https://generativelanguage.googleapis.com/v1beta'
def call(url,body=None):
    key=os.environ.get('GEMINI_API_KEY')
    if not key: sys.exit('GEMINI_API_KEY is not set (set it as a Windows user environment variable, then open a NEW terminal).')
    req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json','x-goog-api-key':key})
    try:
        with urllib.request.urlopen(req,timeout=180) as r: return json.load(r)
    except urllib.error.HTTPError as e: sys.exit(f'HTTP {e.code}: {e.read().decode(errors="replace")[:800]}')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('task',nargs='?'); ap.add_argument('--file',action='append',default=[]); ap.add_argument('--out')
    ap.add_argument('--model',default=os.environ.get('GEMINI_MODEL','gemini-2.5-flash')); ap.add_argument('--list',action='store_true'); a=ap.parse_args()
    if a.list:
        for m in call(f'{API}/models').get('models',[]):
            if 'generateContent' in m.get('supportedGenerationMethods',[]): print(m['name'].split('/')[-1])
        return
    if not a.task: sys.exit('give a task text')
    parts=[{'text':a.task}]
    for f in a.file:
        mt=mimetypes.guess_type(f)[0] or 'text/plain'
        if mt.startswith('text') or f.endswith(('.md','.py','.json','.txt','.csv')):
            parts.append({'text':f'\n--- file: {os.path.basename(f)} ---\n'+open(f,encoding='utf-8').read()})
        else: parts.append({'inline_data':{'mime_type':mt,'data':base64.b64encode(open(f,'rb').read()).decode()}})
    r=call(f'{API}/models/{a.model}:generateContent',{'contents':[{'parts':parts}]})
    try: text=''.join(p.get('text','') for p in r['candidates'][0]['content']['parts'])
    except (KeyError,IndexError): sys.exit('no answer: '+json.dumps(r)[:800])
    if a.out: open(a.out,'w',encoding='utf-8').write(text); print('written',a.out)
    else: print(text)
if __name__=='__main__': main()
