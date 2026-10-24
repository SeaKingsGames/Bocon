// Piezas compartidas del servidor de Bocón (funciones de Vercel).
// Los archivos que empiezan con "_" no son direcciones públicas: solo los usan las demás.
const env=k=>(process.env[k]||'').trim();
const num=(k,d)=>{const v=Number(env(k));return Number.isFinite(v)&&v>0?v:d;};
// precios y opciones: se cambian en Vercel (Settings → Environment Variables) sin tocar código
function precios(){
  return {mensual:num('PRO_PRECIO_MENSUAL',79),anual:num('PRO_PRECIO_ANUAL',690),fundador:num('PRO_FUNDADOR_PRECIO',0),cupo:num('PRO_FUNDADOR_CUPO',0),prueba:num('PRO_PRUEBA_DIAS',0)};
}
const configurado=()=>!!(env('SUPABASE_URL')&&env('SUPABASE_ANON_KEY')&&env('SUPABASE_SERVICE_ROLE_KEY'));
const base=()=>env('SUPABASE_URL').replace(/\/+$/,'');
// quién hace la petición (con la sesión de Supabase que manda la app)
async function usuario(req){
  const h=String(req.headers.authorization||''),tok=h.startsWith('Bearer ')?h.slice(7):'';if(!tok) return null;
  try{const r=await fetch(base()+'/auth/v1/user',{headers:{apikey:env('SUPABASE_ANON_KEY'),Authorization:'Bearer '+tok}});if(!r.ok) return null;const u=await r.json();return u&&u.id?u:null;}catch(_){return null;}
}
// base de datos con la llave secreta (solo aquí en el servidor, nunca en la app)
async function db(path,opts){
  opts=opts||{};const k=env('SUPABASE_SERVICE_ROLE_KEY');
  // las llaves nuevas de Supabase (sb_secret_…) van solo en "apikey"; las de antes (eyJ…) también en Authorization
  const h={apikey:k,'Content-Type':'application/json'};if(k.startsWith('eyJ')) h.Authorization='Bearer '+k;
  const r=await fetch(base()+'/rest/v1/'+path,Object.assign({},opts,{headers:Object.assign(h,opts.headers||{})}));
  let j=null;try{j=await r.json();}catch(_){}return {ok:r.ok,status:r.status,j};
}
async function mp(path,opts){
  opts=opts||{};
  const r=await fetch('https://api.mercadopago.com'+path,Object.assign({},opts,{headers:Object.assign({Authorization:'Bearer '+env('MP_ACCESS_TOKEN'),'Content-Type':'application/json'},opts.headers||{})}));
  let j={};try{j=await r.json();}catch(_){}return {ok:r.ok,status:r.status,j};
}
async function leerSub(uid){const r=await db('suscripciones?select=*&user_id=eq.'+encodeURIComponent(uid));return r.ok&&Array.isArray(r.j)?r.j[0]||null:null;}
async function guardarSub(uid,campos){
  return db('suscripciones?on_conflict=user_id',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify(Object.assign({user_id:uid,actualizado:new Date().toISOString()},campos))});
}
async function contarFundadores(){const r=await db('suscripciones?select=user_id&plan=eq.fundador&estado=eq.authorized');return r.ok&&Array.isArray(r.j)?r.j.length:0;}
// lo que nos importa de una suscripción de Mercado Pago
function desdeMP(pre){
  const o={mp_id:String(pre.id),estado:pre.status||null,correo_mp:pre.payer_email||null,proximo_cobro:pre.next_payment_date||null};
  if(pre.status==='authorized'){const n=pre.next_payment_date?new Date(pre.next_payment_date):null;if(n&&!isNaN(n)) o.pagado_hasta=n.toISOString();o.uso_prueba=true;}
  return o;
}
// Pro de regalo para ti y tus amigos: correos separados por coma en PRO_GRATIS
const cortesia=email=>!!email&&env('PRO_GRATIS').toLowerCase().split(/[,\s]+/).filter(Boolean).includes(String(email).toLowerCase());
// Pro si la suscripción está activa, o si ya canceló pero todavía le queda tiempo pagado (un día de gracia)
function esPro(row,email){
  if(cortesia(email)) return true;if(!row) return false;if(row.estado==='authorized') return true;
  const h=row.pagado_hasta?new Date(row.pagado_hasta).getTime():0;return h+864e5>Date.now();
}
function resumen(row,email){
  return {pro:esPro(row,email),cortesia:cortesia(email),plan:row&&row.plan||null,estado:row&&row.estado||null,pagado_hasta:row&&row.pagado_hasta||null,proximo_cobro:row&&row.proximo_cobro||null,correo_mp:row&&row.correo_mp||null};
}
const origen=req=>env('APP_URL').replace(/\/+$/,'')||('https://'+(req.headers['x-forwarded-host']||req.headers.host));
function cuerpo(req){if(req.body&&typeof req.body==='object') return req.body;try{return JSON.parse(req.body||'{}');}catch(_){return {};}}
const correoOK=s=>/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(s||''));
module.exports={env,precios,configurado,usuario,db,mp,leerSub,guardarSub,contarFundadores,desdeMP,cortesia,esPro,resumen,origen,cuerpo,correoOK};
