import argparse
import json
from pathlib import Path
from .rules import analyze

def main():
    parser=argparse.ArgumentParser(description='Review an extracted merger-agreement MAE definition. Offline; no API key.')
    parser.add_argument('file',nargs='?',type=Path,help='UTF-8 .txt containing the complete target MAE definition')
    parser.add_argument('--serve',action='store_true',help='Start local browser interface')
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    if args.serve:
        from .server import serve
        serve(args.port)
    elif args.file:
        try:
            print(json.dumps(analyze(args.file.read_text(encoding='utf-8-sig')),indent=2,ensure_ascii=False))
        except (ValueError,OSError) as exc:
            parser.error(str(exc))
    else:
        parser.error('Supply a clause file or --serve.')

if __name__=='__main__':
    main()
