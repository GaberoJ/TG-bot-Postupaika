--
-- PostgreSQL database dump
--

\restrict lKNnqHABVkfyIiY3PuedfeX3xutP4WOWCZX8PN47QZIRf4nSzq6nnDBCXcpWSMh

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: directions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.directions (
    id integer NOT NULL,
    num_dir text,
    name_dir text,
    link_po text,
    vuz_id integer
);


ALTER TABLE public.directions OWNER TO postgres;

--
-- Name: directions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.directions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.directions_id_seq OWNER TO postgres;

--
-- Name: directions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.directions_id_seq OWNED BY public.directions.id;


--
-- Name: entrance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entrance (
    id integer NOT NULL,
    program_id integer,
    variants_of_passing integer,
    average_passing_grade_from integer,
    count_places integer,
    cost_of_education_for_year integer,
    link_po text
);


ALTER TABLE public.entrance OWNER TO postgres;

--
-- Name: entrance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.entrance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.entrance_id_seq OWNER TO postgres;

--
-- Name: entrance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.entrance_id_seq OWNED BY public.entrance.id;


--
-- Name: exams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exams (
    id integer NOT NULL,
    entrance_id integer,
    subject integer,
    priority integer,
    points integer
);


ALTER TABLE public.exams OWNER TO postgres;

--
-- Name: exams_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exams_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exams_id_seq OWNER TO postgres;

--
-- Name: exams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exams_id_seq OWNED BY public.exams.id;


--
-- Name: programs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.programs (
    id integer NOT NULL,
    direction_id integer,
    name text,
    education_lvl text,
    education_form text,
    has_budget boolean,
    has_contract boolean,
    count_budget integer,
    count_contract integer,
    education_cost_from integer,
    link_po text
);


ALTER TABLE public.programs OWNER TO postgres;

--
-- Name: programs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.programs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.programs_id_seq OWNER TO postgres;

--
-- Name: programs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.programs_id_seq OWNED BY public.programs.id;


--
-- Name: subjects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subjects (
    id integer NOT NULL,
    name text
);


ALTER TABLE public.subjects OWNER TO postgres;

--
-- Name: subjects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subjects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subjects_id_seq OWNER TO postgres;

--
-- Name: subjects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subjects_id_seq OWNED BY public.subjects.id;


--
-- Name: variants_of_entrance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.variants_of_entrance (
    id integer NOT NULL,
    name text
);


ALTER TABLE public.variants_of_entrance OWNER TO postgres;

--
-- Name: variants_of_entrance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.variants_of_entrance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.variants_of_entrance_id_seq OWNER TO postgres;

--
-- Name: variants_of_entrance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.variants_of_entrance_id_seq OWNED BY public.variants_of_entrance.id;


--
-- Name: vuzi; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vuzi (
    id integer NOT NULL,
    name text,
    city text,
    link_po text
);


ALTER TABLE public.vuzi OWNER TO postgres;

--
-- Name: vuzi_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vuzi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vuzi_id_seq OWNER TO postgres;

--
-- Name: vuzi_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vuzi_id_seq OWNED BY public.vuzi.id;


--
-- Name: directions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.directions ALTER COLUMN id SET DEFAULT nextval('public.directions_id_seq'::regclass);


--
-- Name: entrance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entrance ALTER COLUMN id SET DEFAULT nextval('public.entrance_id_seq'::regclass);


--
-- Name: exams id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams ALTER COLUMN id SET DEFAULT nextval('public.exams_id_seq'::regclass);


--
-- Name: programs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs ALTER COLUMN id SET DEFAULT nextval('public.programs_id_seq'::regclass);


--
-- Name: subjects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects ALTER COLUMN id SET DEFAULT nextval('public.subjects_id_seq'::regclass);


--
-- Name: variants_of_entrance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variants_of_entrance ALTER COLUMN id SET DEFAULT nextval('public.variants_of_entrance_id_seq'::regclass);


--
-- Name: vuzi id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vuzi ALTER COLUMN id SET DEFAULT nextval('public.vuzi_id_seq'::regclass);


--
-- Data for Name: directions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.directions (id, num_dir, name_dir, link_po, vuz_id) FROM stdin;
1	09.03.02	Информационные системы и технологии	https://spb.postupi.online/vuz/universitet-itmo/specialnost/09.03.02/	1
\.


--
-- Data for Name: entrance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entrance (id, program_id, variants_of_passing, average_passing_grade_from, count_places, cost_of_education_for_year, link_po) FROM stdin;
1	1	2	103	151	\N	https://spb.postupi.online/vuz/fakultet-informacionnyh-tehnologiy-i-programmirovaniya-universitet-itmo/variant-programmi/60631/#free
2	1	1	62	500	459000	https://spb.postupi.online/vuz/fakultet-informacionnyh-tehnologiy-i-programmirovaniya-universitet-itmo/variant-programmi/60631/#pay
\.


--
-- Data for Name: exams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams (id, entrance_id, subject, priority, points) FROM stdin;
1	1	1	2	60
2	1	2	3	60
3	1	3	1	60
4	2	1	2	60
5	2	2	3	60
6	2	3	1	60
\.


--
-- Data for Name: programs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.programs (id, direction_id, name, education_lvl, education_form, has_budget, has_contract, count_budget, count_contract, education_cost_from, link_po) FROM stdin;
1	1	Разработка программного обеспечения / Software Engineering	Бакалавриат	Очно	t	t	151	500	459000	https://spb.postupi.online/vuz/universitet-itmo/programma/13129/
\.


--
-- Data for Name: subjects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subjects (id, name) FROM stdin;
1	Русский язык
2	Математтика
3	Информатика
\.


--
-- Data for Name: variants_of_entrance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.variants_of_entrance (id, name) FROM stdin;
1	Платно, очный вариант, 4 года обучения
2	Бюджет, очный вариант, 4 года обучения
\.


--
-- Data for Name: vuzi; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vuzi (id, name, city, link_po) FROM stdin;
1	Национальный исследовательский университет ИТМО	Санкт-Петербург	https://spb.postupi.online/vuz/universitet-itmo/
\.


--
-- Name: directions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.directions_id_seq', 1, true);


--
-- Name: entrance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.entrance_id_seq', 2, true);


--
-- Name: exams_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_id_seq', 6, true);


--
-- Name: programs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.programs_id_seq', 1, true);


--
-- Name: subjects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subjects_id_seq', 3, true);


--
-- Name: variants_of_entrance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.variants_of_entrance_id_seq', 2, true);


--
-- Name: vuzi_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vuzi_id_seq', 1, true);


--
-- Name: directions directions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.directions
    ADD CONSTRAINT directions_pkey PRIMARY KEY (id);


--
-- Name: entrance entrance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entrance
    ADD CONSTRAINT entrance_pkey PRIMARY KEY (id);


--
-- Name: exams exams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_pkey PRIMARY KEY (id);


--
-- Name: programs programs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_pkey PRIMARY KEY (id);


--
-- Name: subjects subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (id);


--
-- Name: variants_of_entrance variants_of_entrance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variants_of_entrance
    ADD CONSTRAINT variants_of_entrance_pkey PRIMARY KEY (id);


--
-- Name: vuzi vuzi_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vuzi
    ADD CONSTRAINT vuzi_name_key UNIQUE (name);


--
-- Name: vuzi vuzi_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vuzi
    ADD CONSTRAINT vuzi_pkey PRIMARY KEY (id);


--
-- Name: directions directions_vuz_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.directions
    ADD CONSTRAINT directions_vuz_id_fkey FOREIGN KEY (vuz_id) REFERENCES public.vuzi(id) ON DELETE CASCADE;


--
-- Name: entrance entrance_program_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entrance
    ADD CONSTRAINT entrance_program_id_fkey FOREIGN KEY (program_id) REFERENCES public.programs(id) ON DELETE CASCADE;


--
-- Name: entrance entrance_variants_of_passing_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entrance
    ADD CONSTRAINT entrance_variants_of_passing_fkey FOREIGN KEY (variants_of_passing) REFERENCES public.variants_of_entrance(id) ON DELETE CASCADE;


--
-- Name: exams exams_entrance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_entrance_id_fkey FOREIGN KEY (entrance_id) REFERENCES public.entrance(id);


--
-- Name: exams exams_subject_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_subject_fkey FOREIGN KEY (subject) REFERENCES public.subjects(id);


--
-- Name: programs programs_direction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_direction_id_fkey FOREIGN KEY (direction_id) REFERENCES public.directions(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict lKNnqHABVkfyIiY3PuedfeX3xutP4WOWCZX8PN47QZIRf4nSzq6nnDBCXcpWSMh

