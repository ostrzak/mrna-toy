"""Arc-length layouts for one captive RNA strip; independent of FreeCAD.

Closed: narrow drive peak, broad flank bends, and a longer underside return.
Open: the same short engagement and shoulder bends, with free hanging tails.
These are inextensible nominal CAD layouts, not a TPU deformation simulation.
"""
import math

PITCH = .72 * math.pi
CELLS = 110
LENGTH = CELLS * PITCH
TOP_HALF, TOP_RADIUS, BOTTOM_RADIUS = 9.0, 33.0, 33.0
WIDTH = 2*(TOP_HALF+TOP_RADIUS)
BOTTOM_HALF = WIDTH/2-BOTTOM_RADIUS
VERTICAL = (LENGTH-2*TOP_HALF-2*BOTTOM_HALF-math.pi*(TOP_RADIUS+BOTTOM_RADIUS))/2
HEIGHT = TOP_RADIUS+VERTICAL+BOTTOM_RADIUS
RADIUS = min(TOP_RADIUS,BOTTOM_RADIUS)
QUARTER = math.pi*TOP_RADIUS/2
BOTTOM_QUARTER = math.pi*BOTTOM_RADIUS/2
RNA_PER_STEP = 3*PITCH
TRAVEL = 22*RNA_PER_STEP
# Keep the rack phase integral when the material length has an odd number
# of pitches. The open end reserves differ by one pitch; travel is unchanged.
JOIN_HOME = math.floor((LENGTH-TRAVEL)/(2*PITCH)+1e-9)*PITCH
S = (TOP_HALF, TOP_HALF+QUARTER, TOP_HALF+QUARTER+VERTICAL,
     TOP_HALF+QUARTER+VERTICAL+BOTTOM_QUARTER,
     TOP_HALF+QUARTER+VERTICAL+BOTTOM_QUARTER+2*BOTTOM_HALF,
     TOP_HALF+QUARTER+VERTICAL+2*BOTTOM_QUARTER+2*BOTTOM_HALF,
     TOP_HALF+QUARTER+2*VERTICAL+2*BOTTOM_QUARTER+2*BOTTOM_HALF,
     TOP_HALF+2*QUARTER+2*VERTICAL+2*BOTTOM_QUARTER+2*BOTTOM_HALF)


def closed(s):
    s %= LENGTH
    t, r, h, b, rb = TOP_HALF, TOP_RADIUS, HEIGHT, BOTTOM_HALF, BOTTOM_RADIUS
    if s < S[0]: return -s, 0.0, 0.0
    if s < S[1]:
        a=(s-S[0])/r
        return -t-r*math.sin(a), r*(1-math.cos(a)), a
    if s < S[2]: return -WIDTH/2, r+s-S[1], math.pi/2
    if s < S[3]:
        a=(s-S[2])/rb
        return -b-rb*math.cos(a), h-rb+rb*math.sin(a), math.pi/2+a
    if s < S[4]: return -b+s-S[3], h, math.pi
    if s < S[5]:
        a=(s-S[4])/rb
        return b+rb*math.sin(a), h-rb+rb*math.cos(a), math.pi+a
    if s < S[6]: return WIDTH/2, h-rb-(s-S[5]), 3*math.pi/2
    if s < S[7]:
        a=(s-S[6])/r
        return t+r*math.cos(a), r-r*math.sin(a), 3*math.pi/2+a
    return t-(s-S[7]), 0.0, 2*math.pi


def opened(s):
    """Signed distance through the straight front; tails preserve arc length."""
    u=abs(s)
    if u <= TOP_HALF: return -s, 0.0, 0.0
    side=1 if s > 0 else -1
    a=min(math.pi/2,(u-TOP_HALF)/TOP_RADIUS)
    x=-side*(TOP_HALF+TOP_RADIUS*math.sin(a))
    v=TOP_RADIUS*(1-math.cos(a))+max(0,u-TOP_HALF-QUARTER)
    return x,v,side*a


def layout(material, feed, is_closed):
    q=JOIN_HOME+material+feed
    return closed(q) if is_closed else opened(q-LENGTH)


def _f(x): return format(x,'.16g')


def _piece(cases, last):
    for condition,value in reversed(cases): last=f'({condition} ? {value} : {last})'
    return last


def expressions(variable='GuideDistance'):
    """FreeCAD scalar expressions: (u, v, accumulated tangent turn)."""
    s=variable; t=_f(TOP_HALF); r=_f(TOP_RADIUS); h=_f(HEIGHT)
    b=_f(BOTTOM_HALF); rb=_f(BOTTOM_RADIUS)
    bounds=[_f(x) for x in S]
    a=lambda k:f'(({s}-{bounds[k]})/{rb if k in (2,4) else r} * 1 rad)'
    c=lambda k:f'{s} < {bounds[k]}'
    cu=_piece([(c(0),f'-{s}'),(c(1),f'-{t}-{r}*sin({a(0)})'),
        (c(2),_f(-WIDTH/2)),(c(3),f'-{b}-{rb}*cos({a(2)})'),
        (c(4),f'-{b}+{s}-{bounds[3]}'),(c(5),f'{b}+{rb}*sin({a(4)})'),
        (c(6),_f(WIDTH/2)),(c(7),f'{t}+{r}*cos({a(6)})')],
        f'{t}-({s}-{bounds[7]})')
    cv=_piece([(c(0),'0'),(c(1),f'{r}*(1-cos({a(0)}))'),
        (c(2),f'{r}+{s}-{bounds[1]}'),(c(3),f'{h}-{rb}+{rb}*sin({a(2)})'),
        (c(4),h),(c(5),f'{h}-{rb}+{rb}*cos({a(4)})'),
        (c(6),f'{h}-{rb}-({s}-{bounds[5]})'),(c(7),f'{r}-{r}*sin({a(6)})')],'0')
    ct=_piece([(c(0),'0'),(c(1),f'({s}-{bounds[0]})/{r}'),
        (c(2),_f(math.pi/2)),(c(3),f'{_f(math.pi/2)}+({s}-{bounds[2]})/{rb}'),
        (c(4),_f(math.pi)),(c(5),f'{_f(math.pi)}+({s}-{bounds[4]})/{rb}'),
        (c(6),_f(3*math.pi/2)),(c(7),f'{_f(3*math.pi/2)}+({s}-{bounds[6]})/{r}')],_f(2*math.pi))
    a=f'(min({_f(math.pi/2)},max(0,(abs({s})-{t})/{r})) * 1 rad)'
    ou=f'abs({s}) <= {t} ? -{s} : ({s} > 0 ? -1 : 1)*({t}+{r}*sin({a}))'
    ov=f'abs({s}) <= {t} ? 0 : {r}*(1-cos({a}))+max(0,abs({s})-{t}-{_f(QUARTER)})'
    ot=f'abs({s}) <= {t} ? 0 : ({s} > 0 ? 1 : -1)*min({_f(math.pi/2)},(abs({s})-{t})/{r})'
    # Semicolons avoid FreeCAD's locale-sensitive decimal-comma parsing.
    return tuple(f'Motion.StrandClosed ? ({a}) : ({b})'.replace(',',';')
                 for a,b in [(cu,ou),(cv,ov),(ct,ot)])
