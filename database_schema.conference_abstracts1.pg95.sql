--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.1
-- Dumped by pg_dump version 9.5.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track execution statistics of all SQL statements executed';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: abstracts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE abstracts (
    id integer NOT NULL,
    title character varying(1000),
    selected_topics character varying(10000),
    abstract_text character varying(20000),
    submission_date timestamp without time zone,
    modification_date timestamp without time zone,
    review_status character varying(128) DEFAULT 'UNSUBMITTED'::character varying,
    fk_submitter integer,
    abstract_type character varying(20),
    abstract_text_edited character varying(20000),
    abstract_attachment boolean,
    presenter_confirmed boolean
);


ALTER TABLE abstracts OWNER TO postgres;

--
-- Name: abstracts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE abstracts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE abstracts_id_seq OWNER TO postgres;

--
-- Name: abstracts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE abstracts_id_seq OWNED BY abstracts.id;


--
-- Name: abstracts_presenting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE abstracts_presenting_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE abstracts_presenting_id_seq OWNER TO postgres;

--
-- Name: abstracts_presenting; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE abstracts_presenting (
    id integer DEFAULT nextval('abstracts_presenting_id_seq'::regclass) NOT NULL,
    fk_abstracts integer NOT NULL,
    fk_authorship integer NOT NULL,
    ip_address character varying(128) DEFAULT now(),
    created timestamp without time zone
);


ALTER TABLE abstracts_presenting OWNER TO postgres;

--
-- Name: abstracts_prize_participation_id; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE abstracts_prize_participation_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE abstracts_prize_participation_id OWNER TO postgres;

--
-- Name: abstracts_prize_participation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE abstracts_prize_participation (
    id integer DEFAULT nextval('abstracts_prize_participation_id'::regclass) NOT NULL,
    fk_abstracts integer,
    participating character varying(1),
    ip_address character varying,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE abstracts_prize_participation OWNER TO postgres;

--
-- Name: abstracts_score_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE abstracts_score_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE abstracts_score_id_seq OWNER TO postgres;

--
-- Name: abstracts_score; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE abstracts_score (
    id integer DEFAULT nextval('abstracts_score_id_seq'::regclass) NOT NULL,
    fk_abstracts integer,
    fk_reviewer integer,
    score integer,
    score_date timestamp without time zone DEFAULT now(),
    suggested_topic integer,
    notes character varying(20000),
    editor_category character varying(100),
    editor_supercategory character varying(100),
    editor_recommended_order integer,
    editor_score integer
);


ALTER TABLE abstracts_score OWNER TO postgres;

--
-- Name: agenda_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE agenda_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE agenda_id_seq OWNER TO postgres;

--
-- Name: agenda; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE agenda (
    id integer DEFAULT nextval('agenda_id_seq'::regclass) NOT NULL,
    session_id character varying(128),
    session_name character varying(128),
    room_name character varying(128),
    date_time character varying(128) NOT NULL,
    session_order integer,
    fk_abstracts integer,
    chair character varying(128) DEFAULT 'TBD'::character varying
);


ALTER TABLE agenda OWNER TO postgres;

--
-- Name: authorship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE authorship (
    id integer NOT NULL,
    fk_abstract integer,
    fname character varying(128),
    mname character varying(128),
    lname character varying(128),
    corresponding boolean,
    presenting boolean,
    author_rank integer,
    institution character varying(128),
    country character varying(128),
    email character varying(256),
    department character varying(128),
    address character varying(256)
);


ALTER TABLE authorship OWNER TO postgres;

--
-- Name: authorlist; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW authorlist AS
 SELECT authorship.fk_abstract,
    array_to_string(array_agg((((authorship.fname)::text || ' '::text) || (authorship.lname)::text) ORDER BY authorship.id), ', '::text) AS all_authors
   FROM authorship
  GROUP BY authorship.fk_abstract;


ALTER TABLE authorlist OWNER TO postgres;

--
-- Name: authorship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE authorship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE authorship_id_seq OWNER TO postgres;

--
-- Name: authorship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE authorship_id_seq OWNED BY authorship.id;


--
-- Name: chairs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE chairs (
    id integer NOT NULL,
    fk_cusers integer,
    topics character varying(2048),
    categories character varying(2048),
    fullname character varying(128),
    email character varying(128),
    accesskey uuid DEFAULT uuid_generate_v1() NOT NULL
);


ALTER TABLE chairs OWNER TO postgres;

--
-- Name: chairs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE chairs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE chairs_id_seq OWNER TO postgres;

--
-- Name: chairs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE chairs_id_seq OWNED BY chairs.id;


--
-- Name: clean_abstracts; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW clean_abstracts AS
 SELECT abstracts.id,
    abstracts.title,
    abstracts.selected_topics,
    abstracts.submission_date,
    abstracts.modification_date,
    abstracts.review_status,
    abstracts.fk_submitter,
    abstracts.abstract_type,
    replace(replace((abstracts.abstract_text_edited)::text, chr(10), '\n'::text), chr(13), '\n'::text) AS abstract_text_edited
   FROM abstracts;


ALTER TABLE clean_abstracts OWNER TO postgres;

--
-- Name: copyeditors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE copyeditors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE copyeditors_id_seq OWNER TO postgres;

--
-- Name: copyeditors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE copyeditors (
    id integer DEFAULT nextval('copyeditors_id_seq'::regclass) NOT NULL,
    fk_cusers integer,
    topics character varying(2048),
    categories character varying(2048),
    fullname character varying(128),
    email character varying(128),
    accesskey uuid DEFAULT uuid_generate_v1() NOT NULL
);


ALTER TABLE copyeditors OWNER TO postgres;

--
-- Name: cusers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE cusers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE cusers_id_seq OWNER TO postgres;

--
-- Name: cusers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE cusers (
    id integer DEFAULT nextval('cusers_id_seq'::regclass) NOT NULL,
    first_name character varying(128),
    middle_initial character varying(128),
    last_name character varying(128),
    institution character varying(256),
    email character varying(256),
    notes character varying(512),
    created timestamp without time zone DEFAULT now(),
    password character varying(100),
    country character varying(10),
    address1 character varying(256),
    address2 character varying(256),
    city character varying(128),
    province_state character varying(128),
    postalcode character varying(128),
    salutation character varying(10),
    department character varying(128)
);


ALTER TABLE cusers OWNER TO postgres;

--
-- Name: editor_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE editor_assignments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE editor_assignments_id_seq OWNER TO postgres;

--
-- Name: editor_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE editor_assignments (
    id integer DEFAULT nextval('editor_assignments_id_seq'::regclass) NOT NULL,
    fk_abstracts integer,
    fk_copyeditor integer,
    assigned_date date,
    responsibility_rank integer
);


ALTER TABLE editor_assignments OWNER TO postgres;

--
-- Name: posters; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE posters (
    id integer DEFAULT nextval('abstracts_presenting_id_seq'::regclass),
    fk_abstracts integer NOT NULL
);


ALTER TABLE posters OWNER TO postgres;

--
-- Name: review_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE review_assignments (
    id integer NOT NULL,
    fk_abstracts integer,
    fk_reviewer integer,
    assigned_date date DEFAULT now(),
    responsibility_rank integer
);


ALTER TABLE review_assignments OWNER TO postgres;

--
-- Name: review_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE review_assignments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE review_assignments_id_seq OWNER TO postgres;

--
-- Name: review_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE review_assignments_id_seq OWNED BY review_assignments.id;


--
-- Name: stats_and_dates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE stats_and_dates (
    id integer NOT NULL,
    recorded timestamp without time zone DEFAULT now(),
    registered_participants integer,
    abstracts_received integer,
    conference_date date,
    abstracts_deadline date,
    seats_available integer
);


ALTER TABLE stats_and_dates OWNER TO postgres;

--
-- Name: stats_and_dates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE stats_and_dates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE stats_and_dates_id_seq OWNER TO postgres;

--
-- Name: stats_and_dates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE stats_and_dates_id_seq OWNED BY stats_and_dates.id;


--
-- Name: test; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE test (
    val character varying(10)
);


ALTER TABLE test OWNER TO postgres;

--
-- Name: topics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE topics (
    id integer NOT NULL,
    label character varying(128),
    category character varying(128)
);


ALTER TABLE topics OWNER TO postgres;

--
-- Name: topics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE topics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE topics_id_seq OWNER TO postgres;

--
-- Name: topics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE topics_id_seq OWNED BY topics.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts ALTER COLUMN id SET DEFAULT nextval('abstracts_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY authorship ALTER COLUMN id SET DEFAULT nextval('authorship_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY chairs ALTER COLUMN id SET DEFAULT nextval('chairs_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY review_assignments ALTER COLUMN id SET DEFAULT nextval('review_assignments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY stats_and_dates ALTER COLUMN id SET DEFAULT nextval('stats_and_dates_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY topics ALTER COLUMN id SET DEFAULT nextval('topics_id_seq'::regclass);


--
-- Name: abstract_presenting_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts_presenting
    ADD CONSTRAINT abstract_presenting_id UNIQUE (fk_abstracts);


--
-- Name: abstracts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts
    ADD CONSTRAINT abstracts_pkey PRIMARY KEY (id);


--
-- Name: abstracts_presenting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts_presenting
    ADD CONSTRAINT abstracts_presenting_pkey PRIMARY KEY (id);


--
-- Name: abstracts_prize_participation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts_prize_participation
    ADD CONSTRAINT abstracts_prize_participation_pkey PRIMARY KEY (id);


--
-- Name: abstracts_score_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts_score
    ADD CONSTRAINT abstracts_score_pkey PRIMARY KEY (id);


--
-- Name: authorship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY authorship
    ADD CONSTRAINT authorship_pkey PRIMARY KEY (id);


--
-- Name: chairs_copy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY copyeditors
    ADD CONSTRAINT chairs_copy_pkey PRIMARY KEY (id);


--
-- Name: chairs_copy_pkey1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY agenda
    ADD CONSTRAINT chairs_copy_pkey1 PRIMARY KEY (id);


--
-- Name: chairs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY chairs
    ADD CONSTRAINT chairs_pkey PRIMARY KEY (id);


--
-- Name: cusers_id_idx; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cusers
    ADD CONSTRAINT cusers_id_idx PRIMARY KEY (id);


--
-- Name: review_assignments_copy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY editor_assignments
    ADD CONSTRAINT review_assignments_copy_pkey PRIMARY KEY (id);


--
-- Name: review_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY review_assignments
    ADD CONSTRAINT review_assignments_pkey PRIMARY KEY (id);


--
-- Name: stats_and_dates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY stats_and_dates
    ADD CONSTRAINT stats_and_dates_pkey PRIMARY KEY (id);


--
-- Name: topics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (id);


--
-- Name: abstracts_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX abstracts_id_key ON abstracts USING btree (id);


--
-- Name: chairs_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX chairs_id_key ON chairs USING btree (id);


--
-- Name: copyeditors_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX copyeditors_id_key ON copyeditors USING btree (id);


--
-- Name: cusers_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX cusers_id_key ON cusers USING btree (id);


--
-- Name: abstract_score_fk_abstracts; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts_score
    ADD CONSTRAINT abstract_score_fk_abstracts FOREIGN KEY (fk_abstracts) REFERENCES abstracts(id);


--
-- Name: abstract_score_fk_reviewer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts_score
    ADD CONSTRAINT abstract_score_fk_reviewer FOREIGN KEY (fk_reviewer) REFERENCES chairs(id);


--
-- Name: abstracts_fk_submitter; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY abstracts
    ADD CONSTRAINT abstracts_fk_submitter FOREIGN KEY (fk_submitter) REFERENCES cusers(id);


--
-- Name: authorship_fk_abstract_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY authorship
    ADD CONSTRAINT authorship_fk_abstract_fkey FOREIGN KEY (fk_abstract) REFERENCES abstracts(id);


--
-- Name: chairs_fk_cusers_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY chairs
    ADD CONSTRAINT chairs_fk_cusers_fkey FOREIGN KEY (fk_cusers) REFERENCES cusers(id);


--
-- Name: chairs_fk_cusers_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY copyeditors
    ADD CONSTRAINT chairs_fk_cusers_fkey FOREIGN KEY (fk_cusers) REFERENCES cusers(id);


--
-- Name: editor_assignments_fk_abstracts_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY editor_assignments
    ADD CONSTRAINT editor_assignments_fk_abstracts_fkey FOREIGN KEY (fk_abstracts) REFERENCES abstracts(id);


--
-- Name: editor_assignments_fk_reviewer_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY editor_assignments
    ADD CONSTRAINT editor_assignments_fk_reviewer_fkey FOREIGN KEY (fk_copyeditor) REFERENCES copyeditors(id);


--
-- Name: review_assignments_fk_abstracts_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY review_assignments
    ADD CONSTRAINT review_assignments_fk_abstracts_fkey FOREIGN KEY (fk_abstracts) REFERENCES abstracts(id);


--
-- Name: review_assignments_fk_reviewer_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY review_assignments
    ADD CONSTRAINT review_assignments_fk_reviewer_fkey FOREIGN KEY (fk_reviewer) REFERENCES chairs(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: abstracts; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE abstracts FROM PUBLIC;
REVOKE ALL ON TABLE abstracts FROM postgres;
GRANT ALL ON TABLE abstracts TO postgres;
GRANT SELECT ON TABLE abstracts TO datamanager;


--
-- Name: abstracts_presenting; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE abstracts_presenting FROM PUBLIC;
REVOKE ALL ON TABLE abstracts_presenting FROM postgres;
GRANT ALL ON TABLE abstracts_presenting TO postgres;
GRANT SELECT ON TABLE abstracts_presenting TO datamanager;


--
-- Name: abstracts_score; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE abstracts_score FROM PUBLIC;
REVOKE ALL ON TABLE abstracts_score FROM postgres;
GRANT ALL ON TABLE abstracts_score TO postgres;
GRANT SELECT ON TABLE abstracts_score TO datamanager;


--
-- Name: agenda; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE agenda FROM PUBLIC;
REVOKE ALL ON TABLE agenda FROM postgres;
GRANT ALL ON TABLE agenda TO postgres;
GRANT SELECT,INSERT,UPDATE ON TABLE agenda TO datamanager;


--
-- Name: authorship; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE authorship FROM PUBLIC;
REVOKE ALL ON TABLE authorship FROM postgres;
GRANT ALL ON TABLE authorship TO postgres;
GRANT SELECT ON TABLE authorship TO datamanager;


--
-- Name: authorlist; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE authorlist FROM PUBLIC;
REVOKE ALL ON TABLE authorlist FROM postgres;
GRANT ALL ON TABLE authorlist TO postgres;
GRANT SELECT ON TABLE authorlist TO datamanager;


--
-- Name: chairs; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE chairs FROM PUBLIC;
REVOKE ALL ON TABLE chairs FROM postgres;
GRANT ALL ON TABLE chairs TO postgres;
GRANT SELECT ON TABLE chairs TO datamanager;


--
-- Name: clean_abstracts; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE clean_abstracts FROM PUBLIC;
REVOKE ALL ON TABLE clean_abstracts FROM postgres;
GRANT ALL ON TABLE clean_abstracts TO postgres;
GRANT SELECT ON TABLE clean_abstracts TO datamanager;


--
-- Name: copyeditors; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE copyeditors FROM PUBLIC;
REVOKE ALL ON TABLE copyeditors FROM postgres;
GRANT ALL ON TABLE copyeditors TO postgres;
GRANT SELECT ON TABLE copyeditors TO datamanager;


--
-- Name: cusers; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE cusers FROM PUBLIC;
REVOKE ALL ON TABLE cusers FROM postgres;
GRANT ALL ON TABLE cusers TO postgres;
GRANT SELECT ON TABLE cusers TO datamanager;


--
-- Name: editor_assignments; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE editor_assignments FROM PUBLIC;
REVOKE ALL ON TABLE editor_assignments FROM postgres;
GRANT ALL ON TABLE editor_assignments TO postgres;
GRANT SELECT ON TABLE editor_assignments TO datamanager;


--
-- Name: posters; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE posters FROM PUBLIC;
REVOKE ALL ON TABLE posters FROM postgres;
GRANT ALL ON TABLE posters TO postgres;
GRANT SELECT ON TABLE posters TO datamanager;


--
-- Name: review_assignments; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE review_assignments FROM PUBLIC;
REVOKE ALL ON TABLE review_assignments FROM postgres;
GRANT ALL ON TABLE review_assignments TO postgres;
GRANT SELECT ON TABLE review_assignments TO datamanager;


--
-- Name: stats_and_dates; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE stats_and_dates FROM PUBLIC;
REVOKE ALL ON TABLE stats_and_dates FROM postgres;
GRANT ALL ON TABLE stats_and_dates TO postgres;
GRANT SELECT ON TABLE stats_and_dates TO datamanager;


--
-- Name: test; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE test FROM PUBLIC;
REVOKE ALL ON TABLE test FROM postgres;
GRANT ALL ON TABLE test TO postgres;
GRANT SELECT ON TABLE test TO datamanager;


--
-- Name: topics; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE topics FROM PUBLIC;
REVOKE ALL ON TABLE topics FROM postgres;
GRANT ALL ON TABLE topics TO postgres;
GRANT SELECT ON TABLE topics TO datamanager;


--
-- Name: topics_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE topics_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE topics_id_seq FROM postgres;
GRANT ALL ON SEQUENCE topics_id_seq TO postgres;
GRANT ALL ON SEQUENCE topics_id_seq TO datamanager;


--
-- PostgreSQL database dump complete
--

