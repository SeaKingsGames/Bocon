// Trazo dentro de Bocón: una IA de texto escribe el dibujo como código SVG, siempre con el mismo estilo.
// Es el mismo estilo que la página de Trazo, para que los dibujos combinen.
const ESTILO=`You draw cartoon stickers as SVG code.
Reply with ONE complete SVG document and nothing else: no markdown fences, no comments, no explanation.

Canvas
- Start with <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"> and no width/height attributes.
- Transparent background: never draw a background rectangle, floor or scenery unless the request is a place or a scene.
- Center the subject. It fills about 80% of the canvas, with a margin of about 30 units.

Style (always the same)
- 2D cartoon, friendly and expressive, like a sticker for a kids' animated show. Clean and simple, never busy.
- One bold dark outline around the silhouette and around each main part: stroke="#1b1a22", stroke-width 9, stroke-linejoin="round", stroke-linecap="round".
- Never double outlines. Do not put an outlined shape just inside or just outside another outlined shape, and do not draw rims, rings or borders as two lines. A rim (a peel, a crust, a frame) is one filled shape; the part inside it goes on top with NO stroke.
- Inner details (shading, highlights, cheeks, spots, patterns) have NO stroke. Eyes, mouth and small lines use stroke-width 5.
- Flat, saturated fills. At most one darker shade per part (same hue, no stroke) and one small white highlight (no stroke). No gradients, filters, blur, shadows or textures.
- Few shapes, usually 10 to 40 elements. Simple, instantly recognizable shapes. Prefer <path> with smooth curves; also circle, ellipse, rect, polygon, line, polyline and g.
- Anything with a face gets big simple eyes with a white shine dot and a small mouth.
- Draw from back to front so the outlines overlap correctly.

Limits
- Use only these elements: svg, g, path, circle, ellipse, rect, line, polyline, polygon. No text unless the user asks for words. No image, script, style, foreignObject, links, CSS or animation.
- Keep it under about 60 elements and 12 KB.
- The drawing must be suitable for all ages. If the request is not, draw a cute question mark sticker instead.`;

// solo figuras: nada que pueda ejecutar código o traer cosas de fuera
const PERMITIDOS=new Set(['svg','g','path','circle','ellipse','rect','line','polyline','polygon','title','desc','defs','lineargradient','radialgradient','stop','clippath','use']);
function limpiar(texto){
  const m=String(texto||'').match(/<svg[\s\S]*<\/svg>/i);if(!m) return null;
  let s=m[0].replace(/<!--[\s\S]*?-->/g,'').replace(/<!\[CDATA\[[\s\S]*?\]\]>/g,'');
  s=s.replace(/<(script|style|foreignObject|iframe|object|embed|image|a|animate\w*|set|audio|video|text)\b[\s\S]*?(<\/\1\s*>|\/>)/gi,'');
  s=s.replace(/<\/?([a-zA-Z][\w:-]*)\b[^>]*>/g,(tag,nombre)=>PERMITIDOS.has(nombre.toLowerCase())?tag:'');
  s=s.replace(/\s(on\w+|style)\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi,'');
  s=s.replace(/\s(xlink:)?href\s*=\s*("(?!#)[^"]*"|'(?!#)[^']*')/gi,'');
  s=s.replace(/url\(\s*['"]?(?!#)[^)]*\)/gi,'none');
  if(!/viewBox=/i.test(s)) s=s.replace(/<svg\b/i,'<svg viewBox="0 0 512 512"');
  if(!/xmlns=/i.test(s)) s=s.replace(/<svg\b/i,'<svg xmlns="http://www.w3.org/2000/svg"');
  s=s.replace(/<svg\b[^>]*>/i,t=>t.replace(/\s(width|height)\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi,''));
  if(!/<(path|circle|ellipse|rect|polygon|polyline|line)\b/i.test(s)) return null;
  return s.length>120000?null:s;
}

// lo que se le pide a la IA: un dibujo nuevo, otra versión o un cambio al dibujo actual
function pedido(b){
  const que=String(b.que||'').trim().slice(0,200),cambio=String(b.cambio||'').trim().slice(0,200);
  if(!que) return {error:'Escribe qué quieres dibujar.'};
  if(cambio){
    const actual=limpiar(b.svg);if(!actual) return {error:'No encontré el dibujo que quieres cambiar.'};
    return {que,temp:.5,texto:`Here is the current drawing of "${que}":\n${actual.slice(0,60000)}\n\nChange it like this: ${cambio}\nKeep everything else and the same style. Reply with the full new SVG.`};
  }
  if(b.otra) return {que,temp:1.1,texto:`Draw: ${que}\nMake a different version from the usual one (new pose, angle or design), variation #${Math.floor(Math.random()*1000)}.`};
  return {que,temp:.8,texto:'Draw: '+que};
}

// Gemini (nivel gratis). Prueba los modelos en orden; el tope del nivel gratis es por proyecto de Google.
async function gemini(key,modelos,texto,temp){
  let ultimo='sin-respuesta';
  for(const modelo of modelos){
    let r;
    try{
      r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(modelo)}:generateContent`,{
        method:'POST',headers:{'Content-Type':'application/json','x-goog-api-key':key},
        body:JSON.stringify({systemInstruction:{parts:[{text:ESTILO}]},contents:[{role:'user',parts:[{text:texto}]}],generationConfig:{temperature:temp,maxOutputTokens:16000}})});
    }catch(_){ultimo='red';continue;}
    if(r.status===429){ultimo='agotado';continue;}
    if(!r.ok){ultimo='error-'+r.status;continue;}
    const j=await r.json().catch(()=>null),c=j&&j.candidates&&j.candidates[0];
    if(!c){ultimo=j&&j.promptFeedback&&j.promptFeedback.blockReason?'bloqueado':'vacio';continue;}
    return {texto:((c.content&&c.content.parts)||[]).filter(p=>!p.thought).map(p=>p.text||'').join(''),modelo};
  }
  return {error:ultimo};
}

module.exports={ESTILO,limpiar,pedido,gemini};
