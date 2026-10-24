// La app pregunta aquí si hay cuentas y cuánto cuesta Pro. Sin variables configuradas responde 404
// y la app funciona como siempre (todo abierto, sin cuentas).
const L=require('./_lib');
module.exports=async(req,res)=>{
  res.setHeader('Cache-Control','no-store');
  if(!L.configurado()) return res.status(404).json({});
  const P=L.precios();let fundador=null;
  if(P.fundador&&P.cupo){try{fundador={precio:P.fundador,quedan:Math.max(0,P.cupo-await L.contarFundadores())};}catch(_){}}
  res.status(200).json({supabaseUrl:L.env('SUPABASE_URL'),supabaseKey:L.env('SUPABASE_ANON_KEY'),google:L.env('LOGIN_GOOGLE')==='1',pagos:!!L.env('MP_ACCESS_TOKEN'),mensual:P.mensual,anual:P.anual,prueba:P.prueba,fundador});
};
