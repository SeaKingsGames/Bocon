// Cancela la suscripción (ya no se cobra; el tiempo ya pagado se respeta).
const L=require('./_lib');
module.exports=async(req,res)=>{
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST') return res.status(405).json({error:'Usa POST'});
  if(!L.configurado()||!L.env('MP_ACCESS_TOKEN')) return res.status(503).json({error:'Los pagos todavía no están configurados'});
  const u=await L.usuario(req);if(!u) return res.status(401).json({error:'Primero entra a tu cuenta'});
  const row=await L.leerSub(u.id);if(!row||!row.mp_id) return res.status(404).json({error:'No tienes una suscripción'});
  const r=await L.mp('/preapproval/'+encodeURIComponent(row.mp_id),{method:'PUT',body:JSON.stringify({status:'cancelled'})});
  if(!r.ok) return res.status(502).json({error:'Mercado Pago no pudo cancelarla; intenta otra vez'});
  const c=L.desdeMP(Object.assign({id:row.mp_id},r.j,{status:(r.j&&r.j.status)||'cancelled'}));
  await L.guardarSub(u.id,c);
  res.status(200).json(L.resumen(Object.assign({},row,c),u.email));
};
