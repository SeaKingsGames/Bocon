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
