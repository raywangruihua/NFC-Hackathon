-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.event_theme_map (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  event_id uuid,
  theme_id uuid,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT event_theme_map_pkey PRIMARY KEY (id),
  CONSTRAINT event_theme_map_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id),
  CONSTRAINT event_theme_map_theme_id_fkey FOREIGN KEY (theme_id) REFERENCES public.themes(theme_id)
);
CREATE TABLE public.events (
  event_id uuid NOT NULL DEFAULT gen_random_uuid(),
  event_type text,
  source text,
  published_at timestamp with time zone NOT NULL,
  region text,
  asset_classes ARRAY,
  entities jsonb,
  content text,
  importance_score double precision CHECK (importance_score >= 0::double precision AND importance_score <= 1::double precision),
  topic text,
  sentiment text,
  raw_payload_ref text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT events_pkey PRIMARY KEY (event_id)
);
CREATE TABLE public.memory (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  content_type text CHECK (content_type = ANY (ARRAY['article_chunk'::text, 'summary'::text, 'recommendation_rationale'::text, 'timeline_note'::text])),
  content text NOT NULL,
  embedding USER-DEFINED,
  metadata jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT memory_pkey PRIMARY KEY (id)
);
CREATE TABLE public.portfolio_exposure (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  asset_class text,
  region text,
  sector text,
  ticker text,
  exposure_pct double precision CHECK (exposure_pct >= 0::double precision AND exposure_pct <= 100::double precision),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT portfolio_exposure_pkey PRIMARY KEY (id),
  CONSTRAINT portfolio_exposure_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.recommendations (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  theme_id uuid,
  action text,
  confidence_score double precision CHECK (confidence_score >= 0::double precision AND confidence_score <= 1::double precision),
  explanation_ref uuid,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT recommendations_pkey PRIMARY KEY (id),
  CONSTRAINT recommendations_theme_id_fkey FOREIGN KEY (theme_id) REFERENCES public.themes(theme_id),
  CONSTRAINT recommendations_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.risk_alerts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  theme_id uuid,
  severity text CHECK (severity = ANY (ARRAY['low'::text, 'medium'::text, 'high'::text, 'critical'::text])),
  trigger_reason text,
  acknowledged boolean DEFAULT false,
  acknowledged_at timestamp with time zone,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT risk_alerts_pkey PRIMARY KEY (id),
  CONSTRAINT risk_alerts_theme_id_fkey FOREIGN KEY (theme_id) REFERENCES public.themes(theme_id),
  CONSTRAINT risk_alerts_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.themes (
  theme_id uuid NOT NULL DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text,
  status text DEFAULT 'active'::text CHECK (status = ANY (ARRAY['active'::text, 'cooling'::text, 'inactive'::text])),
  heat_score double precision DEFAULT 0,
  first_seen_at timestamp with time zone DEFAULT now(),
  last_seen_at timestamp with time zone DEFAULT now(),
  region text,
  asset_classes ARRAY,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT themes_pkey PRIMARY KEY (theme_id)
);
