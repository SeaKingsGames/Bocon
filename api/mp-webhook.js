// Avisos de Mercado Pago (se suscribió, pagó, canceló…).
// No confiamos en lo que dice el aviso: con su número le preguntamos directo a Mercado Pago cómo está la suscripción.
const L=require('./_lib');
module.exports=async(req,res)=>{
  try{
    if(L.configurado()&&L.env('MP_ACCESS_TOKEN')){
      const q=req.query||{},b=L.cuerpo(req),tipo=String(q.type||q.topic||b.type||b.topic||''),id=String((b.data&&b.data.id)||q['data.id']||q.id||'');
      let pre=null;
      if(id&&/preapproval/.test(tipo)&&!/plan/.test(tipo)){const r=await L.mp('/preapproval/'+encodeURIComponent(id));if(r.ok) pre=r.j;}
      else if(id&&/authorized_payment/.test(tipo)){
        const r=await L.mp('/authorized_payments/'+encodeURIComponent(id));
        if(r.ok&&r.j&&r.j.preapproval_id){const r2=await L.mp('/preapproval/'+encodeURIComponent(r.j.preapproval_id));if(r2.ok) pre=r2.j;}
      }
      const uid=pre&&String(pre.external_reference||'');
      if(pre&&pre.id&&/^[0-9a-f-]{36}$/i.test(uid)){
        // solo si es su suscripción actual (un aviso viejo no debe pisar una nueva)
        const row=await L.leerSub(uid);if(!row||!row.mp_id||row.mp_id===String(pre.id)) await L.guardarSub(uid,L.desdeMP(pre));
      }
    }
  }catch(_){}
  res.status(200).json({ok:true});
};
