create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique,
  avatar_url text,
  bio text
);

create table if not exists public.articles (
  id uuid primary key default gen_random_uuid(),
  author_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  slug text not null unique,
  content_mdx text not null default '',
  tags text[] not null default '{}',
  status text not null default 'draft',
  created_at timestamptz not null default now()
);

create table if not exists public.assets (
  id uuid primary key default gen_random_uuid(),
  article_id uuid not null references public.articles(id) on delete cascade,
  file_url text not null,
  file_type text not null
);

alter table public.profiles enable row level security;
alter table public.articles enable row level security;
alter table public.assets enable row level security;

create policy "profiles self manage"
on public.profiles for all
using (auth.uid() = id)
with check (auth.uid() = id);

create policy "articles read published"
on public.articles for select
using (status = 'published' or auth.uid() = author_id);

create policy "articles self manage"
on public.articles for all
using (auth.uid() = author_id)
with check (auth.uid() = author_id);

create policy "assets linked read"
on public.assets for select
using (
  exists (
    select 1 from public.articles a
    where a.id = article_id and (a.status = 'published' or a.author_id = auth.uid())
  )
);

create policy "assets self manage"
on public.assets for all
using (
  exists (select 1 from public.articles a where a.id = article_id and a.author_id = auth.uid())
)
with check (
  exists (select 1 from public.articles a where a.id = article_id and a.author_id = auth.uid())
);
