// Crea la suscripción en Mercado Pago y regresa el enlace para pagar.
const L=require('./_lib');
module.exports=async(req,res)=>{
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST') return res.status(405).json({error:'Usa POST'});
  if(!L.configurado()||!L.env('MP_ACCESS_TOKEN')) return res.status(503).json({error:'Los pagos todavía no están configurados'});
  const u=await L.usuario(req);if(!u) return res.status(401).json({error:'Primero entra a tu cuenta'});
  const b=L.cuerpo(req),P=L.precios(),plan=['mensual','anual','fundador'].includes(b.plan)?b.plan:'mensual';
  const row=await L.leerSub(u.id);
  if(row&&row.estado==='authorized') return res.status(409).json({error:'Ya tienes Bocón Pro'});
  if(plan==='fundador'){
    if(!P.fundador||!P.cupo) return res.status(409).json({error:'No hay precio fundador'});
    if(P.cupo-await L.contarFundadores()<=0) return res.status(409).json({error:'Ya se acabaron los lugares de fundador'});
  }
  const correo=String(b.correo||u.email||'').trim();if(!L.correoOK(correo)) return res.status(400).json({error:'Revisa el correo de Mercado Pago'});
  const monto=plan==='anual'?P.anual:plan==='fundador'?P.fundador:P.mensual;
  const auto={frequency:plan==='anual'?12:1,frequency_type:'months',transaction_amount:monto,currency_id:'MXN'};
  // la prueba gratis es solo la primera vez
  if(P.prueba>0&&!(row&&row.uso_prueba)) auto.free_trial={frequency:P.prueba,frequency_type:'days'};
  const r=await L.mp('/preapproval',{method:'POST',body:JSON.stringify({reason:plan==='anual'?'Bocón Pro · anual':'Bocón Pro · mensual',external_reference:u.id,payer_email:correo,auto_recurring:auto,back_url:L.origen(req)+'/?pro=volver',status:'pending'})});
  if(!r.ok||!r.j||!r.j.init_point) return res.status(502).json({error:'Mercado Pago no aceptó la suscripción'+(r.j&&r.j.message?': '+r.j.message:'')});
  await L.guardarSub(u.id,Object.assign(L.desdeMP(r.j),{plan,monto}));
  res.status(200).json({url:r.j.init_point});
};
