from flask import Flask, render_template, request
from urllib.parse import urlparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import run_scan
app=Flask(__name__,template_folder='templates')
@app.route('/',methods=['GET','POST'])
def index():
    results=[]; report_path=None; error=None; target=''
    if request.method=='POST':
        target=request.form.get('url','').strip()
        try:
            p=urlparse(target)
            if p.scheme not in ('http','https') or not p.netloc: raise ValueError('URL không hợp lệ.')
            results,report_path=run_scan(target)
        except Exception as exc: error=str(exc)
    return render_template('index.html',results=results,report_path=report_path,error=error,target=target)
if __name__=='__main__': app.run(host='127.0.0.1',port=5001,debug=False)
