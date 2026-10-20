ObjC.import('Vision'); ObjC.import('AppKit'); ObjC.import('Foundation');
function run(argv){
  var out=[];
  for (var k=0;k<argv.length;k++){
    var path=argv[k];
    var url=$.NSURL.fileURLWithPath(path);
    var req=$.VNRecognizeTextRequest.alloc.init;
    req.recognitionLevel=0; // accurate
    req.recognitionLanguages=$(['zh-Hans','en-US']);
    req.usesLanguageCorrection=true;
    var h=$.VNImageRequestHandler.alloc.initWithURLOptions(url,$({}));
    var err=Ref();
    h.performRequestsError($([req]),err);
    out.push('##FILE '+path);
    var res=req.results; var n=res.count;
    for (var i=0;i<n;i++){
      var o=res.objectAtIndex(i);
      var c=o.topCandidates(1).objectAtIndex(0);
      var b=o.boundingBox;
      out.push([Math.round(b.origin.x*1000),Math.round((1-b.origin.y-b.size.height)*1000),Math.round((b.origin.x+b.size.width)*1000),Math.round((1-b.origin.y)*1000)].join(' ')+'\t'+c.string.js);
    }
  }
  return out.join('\n');
}
