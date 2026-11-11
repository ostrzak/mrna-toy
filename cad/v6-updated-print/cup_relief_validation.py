"""Audit the material-only cup correction against the complete prior sweep.

The full validator remains the normal reproducible check. This follow-up is
limited to a 0.3 mm trim of the fixed outer cup wall. It proves unchanged
geometry/expressions elsewhere, subset removal, retained roots, and repeats
the affected clearance sweep and stock-spring audit. It never waives overlap.
"""
from pathlib import Path
import copy
import hashlib
import json
import FreeCAD as App
import bracelet_v6_updated_print as b
import stock_springs as stock
import validation_v6_updated_print as validation


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def shape_digest(shape):
    q=shape.copy();q.Placement=App.Placement()
    return hashlib.sha256(q.exportBrepToString().encode('utf-8')).hexdigest()


def same_brep_parameters(a,c):
    """Compare complete topology and curve/surface data after save roundoff.

    OCCT reserialization changes some last decimal places. Preserve every
    nonnumeric token and token count; bound every numeric parameter change.
    Cleaning removes cached tessellation, without changing CAD geometry.
    """
    texts=[]
    for shape in (a,c):
        q=shape.cleaned();q.Placement=App.Placement()
        texts.append(q.exportBrepToString().split())
    if len(texts[0])!=len(texts[1]):return False,None
    maximum=0.
    for x,y in zip(*texts):
        if x==y:continue
        try:maximum=max(maximum,abs(float(x)-float(y)))
        except ValueError:return False,None
    return maximum<=1e-10,maximum


def run(model,previous_model,previous_report,report_path):
    model,previous_model,previous_report=map(Path,(model,previous_model,previous_report))
    base=json.loads(previous_report.read_text(encoding='utf-8'))
    assert base['model_sha256']==digest(previous_model)
    assert not base['invalid_objects'] and all(base['logical_checks'].values())
    assert set(base['collision_failures_mm3'])=={'upper shell/ReturnSpringHousing'}
    for name,value in base['source_sha256'].items():
        if name!='stock_springs.py':assert digest(b.HERE/name)==value,name
    old=App.openDocument(str(previous_model.resolve()))
    new=App.openDocument(str(model.resolve()))
    tests={};unchanged=[];differences=[];roundoff={}
    tests['same native object names and types']={o.Name:o.TypeId for o in old.Objects}=={o.Name:o.TypeId for o in new.Objects}
    for o in old.Objects:
        n=new.getObject(o.Name)
        if n is None:continue
        if list(o.ExpressionEngine)!=list(n.ExpressionEngine):differences.append(o.Name+' expressions')
        if 'Placement' in o.PropertiesList and max(abs(a-c) for a,c in zip(o.Placement.toMatrix().A,n.Placement.toMatrix().A))>1e-10:
            differences.append(o.Name+' placement')
        if 'Shape' in o.PropertiesList and o.Name!='ReturnSpringHousing':
            same=shape_digest(o.Shape)==shape_digest(n.Shape)
            if not same:
                same,delta=same_brep_parameters(o.Shape,n.Shape)
                roundoff[o.Name]=delta
            if not same:differences.append(o.Name+' local shape')
            else:unchanged.append(o.Name)
    tests['all other local shapes placements and native expressions unchanged']=not differences
    for name in old.Motion.PropertiesList:
        if name in ('ExpressionEngine','Proxy','_Body') or name.startswith('_'):continue
        a,c=old.Motion.getPropertyByName(name),new.Motion.getPropertyByName(name)
        if hasattr(a,'Value'):a,c=a.Value,c.Value
        tests['motion property '+name+' unchanged']=a==c
    a=b.world(old.ReturnSpringHousing);c=b.world(new.ReturnSpringHousing)
    mask=stock.return_cup_relief();removed=a.cut(c)
    tests['only material removed from cup']=c.cut(a).Volume<1e-5 and removed.Volume>.01
    tests['removal confined to outer wall top']=removed.cut(mask).Volume<1e-5
    tests['new cup valid and one solid']=c.isValid() and len(c.Solids)==1
    c.check(True)
    guard=b.world(new.GearGuard)
    root_old=a.common(guard);root_new=c.common(guard)
    tests['cover root contact unchanged']=abs(root_old.Volume-root_new.Volume)<1e-5 and root_new.Volume>.001
    fused=c.fuse(guard)
    tests['cup and cover still one connected solid']=fused.isValid() and len(fused.Solids)==1
    new.Motion.BeadSteps=0;new.Motion.CapReturning=False
    strokes=sorted(set([j/40 for j in range(41)]+[j/12 for j in range(13)]+
        [(b.ENTRY_DEG+x)/b.CAP_ANGLE for x in (-.2,0,.01,.2)]+
        [(2.7+x)/b.CAP_ANGLE for x in (-.05,0,.05)]))
    rows=[]
    for f in strokes:
        new.Motion.CapStroke=f;new.recompute()
        volume=validation.overlap(b.world(new.UpperLobe),c)
        rows.append(dict(stroke=f,overlap_mm3=volume))
    maximum=max(r['overlap_mm3'] for r in rows)
    tests['full affected upper to cup sweep clear']=maximum<1e-5
    springs=stock.audit(new,validation.overlap)
    tests['stock spring contacts and hosts still pass']=springs['passed']
    print('CUP_FOLLOWUP',tests,'DIFFERENCES',differences,flush=True)
    result=copy.deepcopy(base)
    result['full_sweep_evidence']=base
    result['model_sha256']=digest(model)
    result['parts']['ReturnSpringHousing'].update(valid=c.isValid(),solids=len(c.Solids),volume_mm3=round(c.Volume,6))
    result['maximum_unintended_overlap_mm3']['upper shell/ReturnSpringHousing']=maximum
    result['collision_failures_mm3']={k:v for k,v in result['collision_failures_mm3'].items() if k!='upper shell/ReturnSpringHousing'}
    if maximum>=1e-5:result['collision_failures_mm3']['upper shell/ReturnSpringHousing']=maximum
    result['logical_checks']['cup_material_removal_followup']=all(tests.values())
    result['spring_audit']=springs
    result['incremental_geometry_validation']=dict(
        method='Complete prior sweep plus proved material-only fixed cup trim and affected rechecks',
        previous_model_sha256=digest(previous_model),previous_report_sha256=digest(previous_report),
        unchanged_local_shape_count=len(unchanged),differences=differences,checks=tests,
        BRep_reserialization_max_numeric_differences=roundoff,BRep_parameter_tolerance=1e-10,
        removed_volume_mm3=removed.Volume,upper_cup_samples=rows,
        reasoning='All other shapes, placements, Motion values and native expressions are identical. The new fixed cup is a subset of the old cup. Removing only its outer wall top cannot introduce any new collision. The unchanged cover contact and connected root are checked separately; the affected shell/cup sweep and spring audit are repeated. This does not qualify physical operation.')
    result['source_sha256']={name:digest(b.HERE/name) for name in base['source_sha256']}
    result['source_sha256'][Path(__file__).name]=digest(__file__)
    result['status']='FOCUSED_PASS' if all(tests.values()) and not result['collision_failures_mm3'] else 'REVIEW'
    Path(report_path).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('CUP_FOLLOWUP_COMPLETE',result['status'],flush=True)
    return result
