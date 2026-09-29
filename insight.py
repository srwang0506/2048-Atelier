"""Inspectable board facts; search scores are never presented as probabilities."""
from engine import DIRECTIONS,slide,can_move

NAMES={'left':'向左','up':'向上','right':'向右','down':'向下'}

def immediate_loss(after):
    """Exact probability of no legal move after the next 90/10 random spawn."""
    empty=[i for i,v in enumerate(after) if not v]
    if not empty:return float(not can_move(after))
    if len(empty)>1:return 0.
    probability=0.
    for value,weight in ((2,.9),(4,.1)):
        board=after[:];board[empty[0]]=value
        if not can_move(board):probability+=weight
    return probability

def analyze_moves(board):
    choices={}
    for direction in DIRECTIONS:
        after,gain,_,merges=slide(board,direction)
        if after==board:continue
        high=max(after)
        choices[direction]=dict(board=after,gain=gain,merges=len(merges),
            empty=max(0,after.count(0)-1),loss=immediate_loss(after),
            corner=any(after[i]==high for i in (0,3,12,15)))
    return choices

def explain(board,result,choices):
    direction=result.get('direction')
    if direction not in choices:return '已经没有可走的方向'
    move=choices[direction]
    if len(choices)==1:return '当前只有这一个方向可走'
    if move['loss']>0:return f"下一次落子后结束的风险为 {move['loss']:.0%}，建议深入分析"
    if any(v['loss']>0 for v in choices.values()):return '避开下一次落子就可能结束的方向'
    if move['empty']>board.count(0):return f"落子后保留 {move['empty']} 个空格，给后续合并留空间"
    if max(board)>=128 and move['corner']:return '最大数字保留在角落，后续更容易整理'
    if move['merges']:return f"合并 {move['merges']} 组，落子后还剩 {move['empty']} 个空格"
    return f"整理数字位置，落子后保留 {move['empty']} 个空格"

def enrich(board,result):
    result=dict(result);choices=analyze_moves(board)
    # A finite heuristic must never prefer certain immediate defeat to a move
    # that can survive. This also protects unusual, very high-valued positions.
    safe=[(d,v) for d,v in result.get('values',[]) if d in choices and choices[d]['loss']<1]
    if safe and choices.get(result.get('direction'),{}).get('loss')==1:
        result['direction']=max(safe,key=lambda pair:pair[1])[0];result['survival_guard']=True
    result['choices']=choices;result['board']=board[:]
    result['explanation']=explain(board,result,choices)
    return result
