// ¿Este usuario es Pro? Pregunta a Mercado Pago cómo va su suscripción y lo anota.
const L=require('./_lib');
module.exports=async(req,res)=>{
  res.setHeader('Cache-Control','no-store');
  if(!L.configurado()) return res.status(404).json({error:'Sin configurar'});
  const u=await L.usuario(req);if(!u) return res.status(401).json({error:'Primero entra a tu cuenta'});
  let row=await L.leerSub(u.id);
  if(row&&row.mp_id&&row.estado!=='cancelled'&&L.env('MP_ACCESS_TOKEN')){
    const r=await L.mp('/preapproval/'+encodeURIComponent(row.mp_id));
    if(r.ok&&r.j&&r.j.id){const c=L.desdeMP(r.j);await L.guardarSub(u.id,c);row=Object.assign({},row,c);}
  }
  res.status(200).json(L.resumen(row,u.email));
};
