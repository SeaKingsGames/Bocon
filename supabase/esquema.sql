-- Bocón Pro: una fila por usuario con su suscripción de Mercado Pago.
-- Pégalo en Supabase → SQL Editor → New query → Run.
-- Puede ir en un proyecto que ya uses para otra app: la tabla se llama bocon_suscripciones para no chocar con las tuyas,
-- y las cuentas (Authentication) se comparten: con la misma cuenta se entra a tus dos apps.
create table if not exists public.bocon_suscripciones (
  user_id       uuid primary key references auth.users(id) on delete cascade,
  plan          text,            -- mensual | anual | fundador
  monto         numeric,
  mp_id         text,            -- número de la suscripción en Mercado Pago
  estado        text,            -- pending | authorized | paused | cancelled
  correo_mp     text,
  proximo_cobro timestamptz,
  pagado_hasta  timestamptz,
  uso_prueba    boolean default false,
  actualizado   timestamptz default now()
);
alter table public.bocon_suscripciones enable row level security;
-- cada quien puede ver la suya; nadie escribe desde la app (solo el servidor, con la llave secreta)
drop policy if exists "ver la mia" on public.bocon_suscripciones;
create policy "ver la mia" on public.bocon_suscripciones for select using (auth.uid() = user_id);

-- ===== Dibujar con IA (Trazo): cuántos dibujos lleva cada cuenta Pro en el mes =====
-- Si ya habías corrido lo de arriba, basta con correr desde aquí.
create table if not exists public.bocon_dibujos (
  user_id uuid not null references auth.users(id) on delete cascade,
  mes     text not null,           -- '2026-11' (hora de México)
  usados  int  not null default 0,
  primary key (user_id, mes)
);
alter table public.bocon_dibujos enable row level security;
-- sin reglas: nadie la lee ni escribe desde la app, solo el servidor con la llave secreta

-- aparta un dibujo si todavía no llega al tope; regresa cuántos lleva o -1 si ya no le quedan
create or replace function public.bocon_dibujo_usar(p_user uuid, p_mes text, p_tope int)
returns int language plpgsql security definer set search_path = public as $$
declare n int;
begin
  insert into bocon_dibujos(user_id, mes, usados) values (p_user, p_mes, 1)
  on conflict (user_id, mes) do update set usados = bocon_dibujos.usados + 1
    where bocon_dibujos.usados < p_tope
  returning usados into n;
  return coalesce(n, -1);
end $$;

-- si la IA falla, el dibujo se regresa
create or replace function public.bocon_dibujo_devolver(p_user uuid, p_mes text)
returns void language sql security definer set search_path = public as $$
  update bocon_dibujos set usados = greatest(0, usados - 1) where user_id = p_user and mes = p_mes;
$$;

revoke all on function public.bocon_dibujo_usar(uuid, text, int) from public, anon, authenticated;
revoke all on function public.bocon_dibujo_devolver(uuid, text) from public, anon, authenticated;
grant execute on function public.bocon_dibujo_usar(uuid, text, int) to service_role;
grant execute on function public.bocon_dibujo_devolver(uuid, text) to service_role;
