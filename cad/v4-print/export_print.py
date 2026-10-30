"""Export oriented A1 mini prototype parts and calibration fixtures in FreeCAD."""
from pathlib import Path
import json
import FreeCAD as App
import Part
import MeshPart
import bracelet_v4_print as b

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'print/v4-a1-mini'
V=App.Vector


def main(model=None):
    document=App.openDocument(str(model or ROOT/'build/v4-print/RibosomeV4Print.FCStd'))
    plates=[]; items={}
    def export(name,shape,material,rotation=None,notes=''):
        s=shape.copy(); s.Placement=App.Placement()
        if rotation: s.rotate(V(),V(*rotation[0]),rotation[1])
        box=s.BoundBox
        s.translate(V(-box.XMin,-box.YMin,-box.ZMin))
        if not s.isValid(): s.fix(.000001,.000001,.0001)
        if not s.isValid() or len(s.Solids)!=1: raise ValueError('Invalid export '+name)
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.18,Relative=False)
        path=OUT/'stl'/(name+'.stl'); path.parent.mkdir(parents=True,exist_ok=True)
        mesh.write(str(path))
        box=s.BoundBox
        record=dict(name=name,file='stl/'+path.name,material=material,
                    bounds_mm=[box.XLength,box.YLength,box.ZLength],volume_mm3=s.Volume,
                    facets=mesh.CountFacets,orientation=notes)
        items[name]=record
        print('Exported '+name,flush=True)
        return record
    def part(name,obj,material,rotation,notes):
        return export(name,document.getObject(obj).Shape,material,rotation,notes)
    def plate(name,material,parts): plates.append(dict(name=name,material=material,parts=parts))
    up=((1,0,0),90); down=((1,0,0),-90)
    plate('10-PETG-cuff-front','PETG',[part('CuffFrame','CuffFrame','PETG',down,'Mating seam down; remove accessible tree supports and clean channel.')])
    plate('11-PETG-cuff-rear','PETG',[part('CuffRear','CuffRear','PETG',up,'Mating seam down; remove supports and clean channel.')])
    plate('12-PETG-RNA','PETG',[part('Rna','Rna','PETG',down,'Concealed gear face down; bases point upwards; single colour.')])
    mechanics=[part('InputDrive','InputDrive','PLA',up,'Pinion face down; keyed shaft upright.'),
               part('SwivelCam','SwivelCam','PLA',up,'Flat rear face down; open cam groove upwards.'),
               part('FollowerSlider','FollowerSlider','PLA',down,'Slider broad face parallel to plate; accessible supports below transverse pin.'),
               part('LeverPost','LeverPost','PLA',None,'Arm flat on plate; post upwards; clean side-loading nut pocket.'),
               part('UpperLobe','UpperLobe','PLA',None,'Open cavity down; removable tree supports; clean swivel cavity.'),
               part('SwivelWasher','SwivelWasher','PLA',None,'Flat retainer cap down.')]
    wheel=document.BeadWheel.Shape.copy(); wheel.Placement=App.Placement()
    front=wheel.common(Part.makeBox(60,34.4,60,V(-30,-30,-30))).removeSplitter()
    rear=wheel.common(Part.makeBox(60,30,60,V(-30,4.4,-30))).removeSplitter()
    mechanics += [export('FeedWheelFront',front,'PLA',up,'Outer fork face down; split hub up.'),
                  export('FeedWheelRear',rear,'PLA',down,'Outer fork face down; split hub up.')]
    plate('13-PLA-mechanism','PLA',mechanics)
    leaves=[export('Leaf-'+str(t).replace('.','p'),b.printed_leaf(t),'PETG',up,'Leaf broad face flat; select force after bench test.') for t in (.6,.8,1.0)]
    # Simple fit gauge: holes along print Z, matching the printed shaft/stop/nut fits.
    gauge=Part.makeBox(56,18,3)
    for i,d in enumerate((1.05,1.1,1.2,2.2,2.3,2.4)):
        gauge=gauge.cut(Part.makeCylinder(d/2,5,V(5+i*8,5,-1)))
    for i,af in enumerate((4.2,4.4,4.6)):
        gauge=gauge.cut(b.hex_prism(af,5,V(9+i*17,13,-1)))
    fits=export('FitGauge',gauge,'PETG',None,'Hole row left-to-right: 1.05,1.10,1.20,2.20,2.30,2.40; hex row 4.2,4.4,4.6 AF.')
    # Short feeder fixture reuses the actual curved entry and tangent exit.
    body=Part.makeBox(38,10.4,24,V(-18,-.8,b.STORE_R-6))
    void=b.union([b.storage_tube(b.CHANNEL_R),b.output_tube(b.CHANNEL_R,30),
                  b.cylinder(9.65,4.5,V(0,2.15,b.SHAFT_Z)),
                  b.cylinder(2.65,12,V(0,-1,b.SHAFT_Z)),
                  b.cylinder(1.15,15,V(0,-2,b.SHAFT_Z))])
    fixture=body.cut(void)
    for x,z in [(-14,b.STORE_R+14),(16,b.STORE_R-2)]:
        fixture=fixture.cut(b.cylinder(1.1,14,V(x,-2,z)))
    front=fixture.common(Part.makeBox(80,44.4,100,V(-40,-40,0))).removeSplitter()
    rear=fixture.common(Part.makeBox(80,40,100,V(-40,4.4,0))).removeSplitter()
    coupon=[export('FeederTestFront',front,'PETG',down,'Mating seam down; actual curved entry and feeder pocket.'),
            export('FeederTestRear',rear,'PETG',up,'Mating seam down; clamp with two M2 x 14 screws and nuts (test fixture only).')]
    plate('01-PETG-fits-and-feeder-test','PETG',leaves+[fits]+coupon)
    jig=Part.makeBox(160,16,3)
    # Open top seats register 26 bead centres, not the crimp centres.
    for i in range(26):
        jig=jig.cut(Part.makeCylinder(2.35,2,V(5+6*i,8,1)))
    jig=jig.cut(Part.makeBox(158,.6,1.5,V(1,7.7,1.5)))
    plate('14-PLA-chain-pitch-jig','PLA',[export('ChainPitchJig',jig,'PLA',None,'26 centres at 6 mm pitch. Work one bead/stop pair first; jig does not set pull strength.')])
    calibration=[]
    for diameter in (.4,.5,.6,.8):
        for kind in range(3):
            calibration.append(export('TestBead-'+str(diameter).replace('.','p')+'-'+b.BEAD_FAMILY[kind],b.bead_shape(kind,diameter),'TPU',((0,1,0),-90),'Flat sole down; central bore vertical. Row order follows manifest.'))
    for diameter in (4.1,4.25,4.35):
        calibration.append(export('TestAxlePlug-'+str(diameter).replace('.','p'),b.axle_plug(diameter),'TPU',down,'Wide flange down; compare retention before selecting.'))
    plate('00-TPU-bore-tests','TPU',calibration)
    production=[]
    counts={kind:sum(document.getObject(f'Bead{i:02}').BeadVariant==kind for i in range(b.BEADS)) for kind in range(3)}
    for kind,count in counts.items():
        bead=export('Bead-'+b.BEAD_FAMILY[kind]+'-0p6',b.bead_shape(kind),'TPU',((0,1,0),-90),'Flat sole down; 0.6 mm candidate central bore, 2 mm recessed stop pockets.')
        for i in range(count+1): production.append(dict(bead,name=bead['name']+f'-{i+1:02}'))
    production.append(export('AxlePlug-4p35',b.axle_plug(),'TPU',down,'Wide flange down. 4.35 mm candidate retention plug.'))
    plate('15-TPU-production-beads','TPU',production)
    manifest=dict(version='V4 Print A1 mini prototype',printer='Bambu Lab A1 mini',nozzle_mm=.4,
                  build_volume_mm=[180,180,180],physical_print_tested=False,
                  central_bore_candidate_mm=.6,copper_wire_candidate_mm=.25,
                  bead_variant_assembly_counts={b.BEAD_FAMILY[k]:v for k,v in counts.items()},
                  spare_beads=3,parts=list(items.values()),plates=plates)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('PRINT_EXPORT_COMPLETE',flush=True)


if __name__=='__main__': main()
