"""Offline checks of imports, data, the native AI and a spawned worker."""
import argparse
import importlib.metadata
import json
import multiprocessing as mp
import os
from pathlib import Path
import struct
import sys
import tempfile

def dependencies():
    wanted={'pygame-ce':'2.5.8','numpy':'2.5.3','numba':'0.67.0','Pillow':'12.3.0','llvmlite':'0.49.0'}
    actual={name:importlib.metadata.version(name) for name in wanted}
    if actual != wanted:raise RuntimeError('Dependencies do not match requirements: '+str(actual))
    import pygame,numpy,numba,PIL,llvmlite
    return actual

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dependencies',action='store_true');args=parser.parse_args()
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
    report=dict(python=sys.version,platform=sys.platform,bits=struct.calcsize('P')*8)
    if report['bits']!=64:raise RuntimeError('Use the 64-bit runtime')
    from desktop_start import configure_runtime
    configure_runtime();report['dependencies']=dependencies()
    if args.dependencies:print(json.dumps(report));return
    from engine import Game,Storage
    from puzzles import LEVELS
    from rescue import practice_challenges
    from typography import families,Face
    report['puzzles']=len(LEVELS);report['rescue_practice']=len(practice_challenges())
    assert report['puzzles']==12 and report['rescue_practice']==3
    report['fonts']=families()
    face=Face(18,'title');text='经典能力远征绝境重生'
    assert all(m is not None for m in face.native.get_metrics(text)), 'Chinese font is missing'
    from platform_paths import user_root,InstanceLock
    user_root().mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='2048-check-',dir=user_root()) as folder:
        path=Path(folder)/'save.json';g=Game(17);g.move('left');s=Storage(path)
        assert s.save(g,{}) and Game.restore(Storage(path).data['game']).snapshot()==g.snapshot()
        with InstanceLock(Path(folder)/'game.lock'):pass
    from ai import worker
    ctx=mp.get_context('spawn');requests=ctx.Queue();results=ctx.Queue();process=ctx.Process(target=worker,args=(requests,results));process.start()
    try:
        token,ready=results.get(timeout=90);assert ready.get('ready'),ready
        board=[2,2,4,8]+[0]*12;requests.put((13,board,.025))
        token,result=results.get(timeout=30);assert token==13 and result.get('direction'),result
        report['ai']=dict(backend=result['backend'],direction=result['direction'],nodes=result['nodes'])
    finally:
        requests.put(None);process.join(timeout=3)
        if process.is_alive():process.terminate();process.join(timeout=2)
        requests.close();results.close()
    report['status']='PASS'
    destination=user_root()/'logs';destination.mkdir(parents=True,exist_ok=True)
    (destination/'diagnostics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True,indent=2))
    print('Saved diagnostics:',destination/'diagnostics.json')

if __name__=='__main__':
    mp.freeze_support();main()
