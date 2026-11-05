"""Check binary review STLs independently of FreeCAD; never repair the mesh."""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct


def check(path):
    data=path.read_bytes()
    if len(data)<84:raise ValueError('Not a binary STL')
    facets=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*facets:raise ValueError('Unexpected binary STL size')
    vertices={};edges=Counter();orientation=Counter()
    degenerate=0;nonfinite=0;signed_volume=0.0
    for item in struct.iter_unpack('<12fH',memoryview(data)[84:]):
        points=[tuple(item[k:k+3]) for k in (3,6,9)]
        if not all(math.isfinite(v) for p in points for v in p):
            nonfinite+=1;continue
        ids=[vertices.setdefault(p,len(vertices)) for p in points]
        if len(set(ids))<3:degenerate+=1
        a,b,c=points
        signed_volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+
                        a[1]*(b[2]*c[0]-b[0]*c[2])+
                        a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        if len(set(ids))==3 and sum(x*x for x in cross)==0:degenerate+=1
        for x,y in ((ids[0],ids[1]),(ids[1],ids[2]),(ids[2],ids[0])):
            edge=(min(x,y),max(x,y));edges[edge]+=1
            orientation[edge]+=1 if x<y else -1
    boundaries=sum(n==1 for n in edges.values())
    nonmanifold=sum(n>2 for n in edges.values())
    inconsistent=sum(v!=0 for v in orientation.values())
    return dict(file=path.name,sha256=hashlib.sha256(data).hexdigest(),facets=facets,
        unique_vertices=len(vertices),boundary_edges=boundaries,nonmanifold_edges=nonmanifold,
        inconsistent_edge_orientations=inconsistent,degenerate_facets=degenerate,
        nonfinite_facets=nonfinite,signed_volume_mm3=signed_volume,
        passed=facets>0 and not any((boundaries,nonmanifold,inconsistent,degenerate,nonfinite)) and signed_volume>0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    args=parser.parse_args()
    records=[]
    for path in sorted(args.folder.rglob('*.stl')):
        try:r=check(path)
        except Exception as exc:r=dict(file=path.name,passed=False,error=str(exc))
        records.append(r);print(r['file'],r['passed'])
    result=dict(status='PASS' if records and all(r['passed'] for r in records) else 'REVIEW',
        checks='Exact binary-STL edge incidence and orientation, degeneracy, finite coordinates and positive volume; no geometric repair.',
        physical_printability_established=False,files=records)
    (args.folder/'mesh-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
