// «Dibujar con IA» (Trazo) para Bocón Pro. Cada cuenta Pro tiene un tope de dibujos al mes (DIBUJOS_POR_MES, 30 si no se pone).
// GET: cuántos lleva este mes. POST {que, cambio?, svg?, otra?}: hace el dibujo y regresa el SVG.
// Si la IA falla, el dibujo no se cuenta.
const L=require('./_lib'),T=require('./_trazo');
const tope=()=>{const v=Number(L.env('DIBUJOS_POR_MES'));return Number.isFinite(v)&&v>0?Math.floor(v):30;};
// el mes en hora de México, para que se renueve el día 1 a medianoche de aquí
const mesActual=()=>new Date().toLocaleString('sv-SE',{timeZone:'America/Mexico_City'}).slice(0,7);
async function usados(uid,mes){
  const r=await L.db('bocon_dibujos?select=usados&user_id=eq.'+encodeURIComponent(uid)+'&mes=eq.'+mes);
  return r.ok&&Array.isArray(r.j)&&r.j[0]?r.j[0].usados:0;
}
const rpc=(fn,args)=>L.db('rpc/'+fn,{method:'POST',body:JSON.stringify(args)});
const MENSAJES={
  agotado:'La IA está muy ocupada o ya se usaron los dibujos de hoy. Intenta en un rato.',
  bloqueado:'Ese dibujo no se puede hacer. Prueba con otra cosa.',
};

module.exports=async(req,res)=>{
  res.setHeader('Cache-Control','no-store');
  if(!L.configurado()) return res.status(404).json({error:'Dibujar con IA necesita las cuentas de Bocón Pro'});
  const key=L.env('GEMINI_API_KEY');if(!key) return res.status(503).json({error:'Falta la llave de la IA en Vercel (GEMINI_API_KEY)'});
  const u=await L.usuario(req);if(!u) return res.status(401).json({error:'Primero entra a tu cuenta'});
  const pro=L.esPro(await L.leerSub(u.id),u.email),mes=mesActual(),max=tope();
  if(req.method==='GET') return res.status(200).json({pro,usados:await usados(u.id,mes),tope:max});
  if(req.method!=='POST') return res.status(405).json({error:'Usa POST'});
  if(!pro) return res.status(403).json({error:'Dibujar con IA es de Bocón Pro'});

  const p=T.pedido(L.cuerpo(req));if(p.error) return res.status(400).json({error:p.error});
  // se aparta el dibujo antes de llamar a la IA (así no se pasa del tope aunque pida varios a la vez)
  const r=await rpc('bocon_dibujo_usar',{p_user:u.id,p_mes:mes,p_tope:max});
  if(!r.ok) return res.status(500).json({error:'No pude revisar tus dibujos del mes. ¿Ya corriste el SQL nuevo en Supabase?'});
  const n=Number(r.j);
  if(!(n>0)) return res.status(429).json({error:`Ya usaste tus ${max} dibujos con IA de este mes. Se renuevan el día 1.`,usados:max,tope:max});
  const devolver=()=>rpc('bocon_dibujo_devolver',{p_user:u.id,p_mes:mes}).catch(()=>null);

  const modelos=(L.env('GEMINI_MODELOS')||'gemini-flash-latest,gemini-flash-lite-latest').split(',').map(x=>x.trim()).filter(Boolean);
  const g=await T.gemini(key,modelos,p.texto,p.temp);
  if(g.error){await devolver();return res.status(g.error==='agotado'?429:502).json({error:MENSAJES[g.error]||'La IA no respondió. Intenta otra vez.',usados:n-1,tope:max});}
  const svg=T.limpiar(g.texto);
  if(!svg){await devolver();return res.status(502).json({error:'La IA no regresó un dibujo. Intenta otra vez.',usados:n-1,tope:max});}
  res.status(200).json({svg,usados:n,tope:max});
};
