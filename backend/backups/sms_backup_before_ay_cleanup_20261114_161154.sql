--
-- PostgreSQL database dump
--

\restrict JtfRwSkqdmZ5KGgT3qwdqdOgVXgo39Of1FW8lm21c0C88C1pc94wvTHwKNsk790

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: attendance_submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance_submissions (
    id integer NOT NULL,
    academic_year character varying(50) NOT NULL,
    class_id integer NOT NULL,
    subject_id integer NOT NULL,
    date date NOT NULL,
    period character varying(50),
    teacher_id integer,
    submitted_by_id integer,
    status character varying(20) DEFAULT 'SUBMITTED'::character varying NOT NULL,
    total_students integer DEFAULT 0 NOT NULL,
    present_count integer DEFAULT 0 NOT NULL,
    late_count integer DEFAULT 0 NOT NULL,
    absent_count integer DEFAULT 0 NOT NULL,
    submission_time timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.attendance_submissions OWNER TO postgres;

--
-- Name: attendance_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendance_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_submissions_id_seq OWNER TO postgres;

--
-- Name: attendance_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendance_submissions_id_seq OWNED BY public.attendance_submissions.id;


--
-- Name: attendances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendances (
    id integer NOT NULL,
    student_id integer NOT NULL,
    class_id integer NOT NULL,
    subject_id integer NOT NULL,
    teacher_id integer,
    academic_year character varying(50) NOT NULL,
    date date NOT NULL,
    period character varying(50),
    status character varying(20) DEFAULT 'PRESENT'::character varying NOT NULL,
    remarks character varying(255),
    recorded_by_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.attendances OWNER TO postgres;

--
-- Name: attendances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendances_id_seq OWNER TO postgres;

--
-- Name: attendances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendances_id_seq OWNED BY public.attendances.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    status character varying(20) NOT NULL,
    ip_address character varying(50),
    user_agent character varying(500),
    details json,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: class_promotion_batches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.class_promotion_batches (
    id integer NOT NULL,
    batch_code character varying(50) NOT NULL,
    source_academic_year character varying(50) NOT NULL,
    target_academic_year character varying(50) NOT NULL,
    promotion_type character varying(30) DEFAULT 'BULK_PROMOTION'::character varying NOT NULL,
    status character varying(30) DEFAULT 'COMPLETED'::character varying NOT NULL,
    total_promoted integer DEFAULT 0 NOT NULL,
    total_graduated integer DEFAULT 0 NOT NULL,
    total_skipped integer DEFAULT 0 NOT NULL,
    reason text,
    created_by_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.class_promotion_batches OWNER TO postgres;

--
-- Name: class_promotion_batches_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.class_promotion_batches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_promotion_batches_id_seq OWNER TO postgres;

--
-- Name: class_promotion_batches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.class_promotion_batches_id_seq OWNED BY public.class_promotion_batches.id;


--
-- Name: class_promotion_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.class_promotion_records (
    id integer NOT NULL,
    batch_id integer NOT NULL,
    student_id integer NOT NULL,
    from_class_id integer,
    to_class_id integer,
    from_enrollment_id integer,
    to_enrollment_id integer,
    source_academic_year character varying(50) NOT NULL,
    target_academic_year character varying(50) NOT NULL,
    action character varying(30) DEFAULT 'PROMOTED'::character varying NOT NULL,
    status character varying(30) DEFAULT 'COMPLETED'::character varying NOT NULL,
    reason character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.class_promotion_records OWNER TO postgres;

--
-- Name: class_promotion_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.class_promotion_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_promotion_records_id_seq OWNER TO postgres;

--
-- Name: class_promotion_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.class_promotion_records_id_seq OWNED BY public.class_promotion_records.id;


--
-- Name: classes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classes (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(50) NOT NULL,
    section character varying(50),
    academic_year character varying(50) NOT NULL,
    capacity integer DEFAULT 40 NOT NULL,
    description text,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    division character varying(20) DEFAULT 'PRIMARY'::character varying,
    level character varying(50)
);


ALTER TABLE public.classes OWNER TO postgres;

--
-- Name: classes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classes_id_seq OWNER TO postgres;

--
-- Name: classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.classes_id_seq OWNED BY public.classes.id;


--
-- Name: exam_deadline_extensions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exam_deadline_extensions (
    id integer NOT NULL,
    exam_id integer NOT NULL,
    previous_deadline timestamp without time zone,
    new_deadline timestamp without time zone NOT NULL,
    reason text NOT NULL,
    extended_by_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.exam_deadline_extensions OWNER TO postgres;

--
-- Name: exam_deadline_extensions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exam_deadline_extensions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exam_deadline_extensions_id_seq OWNER TO postgres;

--
-- Name: exam_deadline_extensions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exam_deadline_extensions_id_seq OWNED BY public.exam_deadline_extensions.id;


--
-- Name: exam_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exam_results (
    id integer NOT NULL,
    exam_id integer NOT NULL,
    student_id integer NOT NULL,
    subject_id integer NOT NULL,
    marks_obtained numeric(5,2),
    grade character varying(20),
    remarks character varying(255),
    recorded_by_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    class_id integer,
    submission_id integer,
    release_batch_id integer,
    attendance_status character varying(20) DEFAULT 'PRESENT'::character varying NOT NULL,
    status character varying(20) DEFAULT 'DRAFT'::character varying NOT NULL,
    paper_file_path character varying(500),
    paper_original_name character varying(255),
    paper_mime_type character varying(100),
    paper_file_size integer,
    paper_uploaded_at timestamp with time zone,
    absence_reason text,
    complaint text
);


ALTER TABLE public.exam_results OWNER TO postgres;

--
-- Name: exam_results_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exam_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exam_results_id_seq OWNER TO postgres;

--
-- Name: exam_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exam_results_id_seq OWNED BY public.exam_results.id;


--
-- Name: exams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exams (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    exam_type character varying(50) NOT NULL,
    academic_year character varying(50) NOT NULL,
    class_id integer NOT NULL,
    subject_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date,
    max_marks numeric(5,2) DEFAULT 100.00 NOT NULL,
    pass_marks numeric(5,2) DEFAULT 50.00 NOT NULL,
    status character varying(20) DEFAULT 'SCHEDULED'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    teacher_id integer,
    instructions text,
    start_time character varying(20),
    end_time character varying(20),
    result_submission_deadline timestamp without time zone,
    created_by_id integer,
    reopened_at timestamp without time zone,
    reopened_by_id integer,
    reopen_reason text,
    published_at timestamp with time zone,
    published_by_id integer
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
-- Name: fee_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fee_payments (
    id integer NOT NULL,
    student_fee_id integer NOT NULL,
    student_id integer NOT NULL,
    receipt_number character varying(50) NOT NULL,
    amount_paid numeric(10,2) NOT NULL,
    payment_date date NOT NULL,
    payment_method character varying(50) NOT NULL,
    reference_number character varying(100),
    recorded_by_id integer,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    status character varying(20) DEFAULT 'VERIFIED'::character varying NOT NULL
);


ALTER TABLE public.fee_payments OWNER TO postgres;

--
-- Name: fee_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fee_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fee_payments_id_seq OWNER TO postgres;

--
-- Name: fee_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fee_payments_id_seq OWNED BY public.fee_payments.id;


--
-- Name: fee_structures; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fee_structures (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    academic_year character varying(50) NOT NULL,
    class_id integer,
    amount numeric(10,2) NOT NULL,
    due_date date NOT NULL,
    description text,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    frequency character varying(50) DEFAULT 'Term'::character varying NOT NULL,
    education_level character varying(20),
    created_by_id integer
);


ALTER TABLE public.fee_structures OWNER TO postgres;

--
-- Name: fee_structures_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fee_structures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fee_structures_id_seq OWNER TO postgres;

--
-- Name: fee_structures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fee_structures_id_seq OWNED BY public.fee_structures.id;


--
-- Name: form_master_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.form_master_assignments (
    id integer NOT NULL,
    teacher_id integer NOT NULL,
    class_id integer NOT NULL,
    academic_year character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    notes text,
    appointed_by_id integer,
    appointed_at timestamp with time zone DEFAULT now() NOT NULL,
    revoked_by_id integer,
    revoked_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.form_master_assignments OWNER TO postgres;

--
-- Name: form_master_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.form_master_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.form_master_assignments_id_seq OWNER TO postgres;

--
-- Name: form_master_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.form_master_assignments_id_seq OWNED BY public.form_master_assignments.id;


--
-- Name: inquiries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inquiries (
    id integer NOT NULL,
    full_name character varying(150) NOT NULL,
    school_name character varying(200) NOT NULL,
    email character varying(150) NOT NULL,
    phone character varying(50) NOT NULL,
    plan character varying(120),
    message text NOT NULL,
    status character varying(30) NOT NULL,
    priority character varying(20) NOT NULL,
    admin_notes text,
    contacted_by character varying(100),
    preferred_channel character varying(50),
    source character varying(50) NOT NULL,
    converted_institution_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.inquiries OWNER TO postgres;

--
-- Name: inquiries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inquiries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inquiries_id_seq OWNER TO postgres;

--
-- Name: inquiries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inquiries_id_seq OWNED BY public.inquiries.id;


--
-- Name: institution_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institution_payments (
    id integer NOT NULL,
    institution_id integer NOT NULL,
    subscription_id integer,
    reference character varying(100) NOT NULL,
    amount numeric(10,2) NOT NULL,
    currency character varying(10) NOT NULL,
    payment_method character varying(50) NOT NULL,
    payment_date timestamp without time zone NOT NULL,
    status character varying(50) NOT NULL,
    invoice_number character varying(100),
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.institution_payments OWNER TO postgres;

--
-- Name: institution_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.institution_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institution_payments_id_seq OWNER TO postgres;

--
-- Name: institution_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.institution_payments_id_seq OWNED BY public.institution_payments.id;


--
-- Name: institutions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institutions (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(50) NOT NULL,
    logo_url character varying(500),
    contact_person character varying(200),
    email character varying(255),
    phone character varying(50),
    region character varying(100),
    city character varying(100),
    address text,
    status character varying(50) NOT NULL,
    database_name character varying(100),
    provisioning_status character varying(50) NOT NULL,
    provisioning_error text,
    admin_email character varying(255),
    admin_username character varying(100),
    subscription_plan character varying(100) NOT NULL,
    subscription_status character varying(50) NOT NULL,
    subscription_start_date date,
    subscription_expiry_date date,
    admin_user_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.institutions OWNER TO postgres;

--
-- Name: institutions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.institutions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institutions_id_seq OWNER TO postgres;

--
-- Name: institutions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.institutions_id_seq OWNED BY public.institutions.id;


--
-- Name: notification_deliveries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_deliveries (
    id integer NOT NULL,
    notification_id integer NOT NULL,
    channel character varying(50) NOT NULL,
    recipient character varying(255) NOT NULL,
    provider_name character varying(100),
    provider_message_id character varying(255),
    status character varying(50) DEFAULT 'PENDING'::character varying NOT NULL,
    error_code character varying(100),
    error_message text,
    attempt_number integer DEFAULT 1 NOT NULL,
    sent_at timestamp with time zone,
    delivered_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.notification_deliveries OWNER TO postgres;

--
-- Name: notification_deliveries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_deliveries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_deliveries_id_seq OWNER TO postgres;

--
-- Name: notification_deliveries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_deliveries_id_seq OWNED BY public.notification_deliveries.id;


--
-- Name: notification_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_templates (
    id integer NOT NULL,
    code character varying(100) NOT NULL,
    name character varying(200) NOT NULL,
    title_template character varying(255) NOT NULL,
    body_template text NOT NULL,
    category character varying(50) DEFAULT 'GENERAL'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_system boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.notification_templates OWNER TO postgres;

--
-- Name: notification_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_templates_id_seq OWNER TO postgres;

--
-- Name: notification_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_templates_id_seq OWNED BY public.notification_templates.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    notification_type character varying(50) NOT NULL,
    title character varying(255) NOT NULL,
    message text NOT NULL,
    channel character varying(50) DEFAULT 'SMS'::character varying NOT NULL,
    status character varying(50) DEFAULT 'PENDING'::character varying NOT NULL,
    failure_reason character varying(255),
    student_id integer,
    guardian_name character varying(200),
    guardian_phone character varying(50),
    guardian_email character varying(255),
    guardian_relationship character varying(50),
    class_id integer,
    academic_year character varying(50),
    related_attendance_id integer,
    related_exam_id integer,
    related_result_id integer,
    related_release_batch_id integer,
    idempotency_key character varying(255),
    created_by_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    sent_at timestamp with time zone,
    delivered_at timestamp with time zone,
    read_at timestamp with time zone,
    attempt_count integer DEFAULT 0 NOT NULL,
    extra_data json
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: result_release_batches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.result_release_batches (
    id integer NOT NULL,
    batch_code character varying(50) NOT NULL,
    exam_name character varying(100) NOT NULL,
    academic_year character varying(50) NOT NULL,
    class_id integer NOT NULL,
    release_type character varying(20) DEFAULT 'FULL'::character varying NOT NULL,
    status character varying(20) DEFAULT 'RELEASED'::character varying NOT NULL,
    released_by_id integer,
    released_at timestamp with time zone DEFAULT now() NOT NULL,
    results_count integer DEFAULT 0 NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.result_release_batches OWNER TO postgres;

--
-- Name: result_release_batches_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.result_release_batches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.result_release_batches_id_seq OWNER TO postgres;

--
-- Name: result_release_batches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.result_release_batches_id_seq OWNED BY public.result_release_batches.id;


--
-- Name: result_submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.result_submissions (
    id integer NOT NULL,
    exam_id integer NOT NULL,
    class_id integer NOT NULL,
    subject_id integer NOT NULL,
    teacher_id integer NOT NULL,
    academic_year character varying(50) NOT NULL,
    exam_name character varying(100) NOT NULL,
    status character varying(30) DEFAULT 'DRAFT'::character varying NOT NULL,
    expected_students integer DEFAULT 0 NOT NULL,
    completed_students integer DEFAULT 0 NOT NULL,
    pending_students integer DEFAULT 0 NOT NULL,
    submitted_at timestamp with time zone,
    submitted_by_id integer,
    reviewed_at timestamp with time zone,
    reviewed_by_id integer,
    approved_at timestamp with time zone,
    approved_by_id integer,
    returned_at timestamp with time zone,
    return_reason text,
    submission_deadline date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    revisions json,
    exam_type character varying(50)
);


ALTER TABLE public.result_submissions OWNER TO postgres;

--
-- Name: result_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.result_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.result_submissions_id_seq OWNER TO postgres;

--
-- Name: result_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.result_submissions_id_seq OWNED BY public.result_submissions.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    is_system boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    refresh_token text NOT NULL,
    ip_address character varying(50),
    user_agent character varying(500),
    is_revoked boolean NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sessions_id_seq OWNER TO postgres;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sessions_id_seq OWNED BY public.sessions.id;


--
-- Name: student_enrollments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_enrollments (
    id integer NOT NULL,
    student_id integer NOT NULL,
    class_id integer NOT NULL,
    academic_year character varying(50) NOT NULL,
    roll_number character varying(50),
    start_date date,
    end_date date,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.student_enrollments OWNER TO postgres;

--
-- Name: student_enrollments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_enrollments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_enrollments_id_seq OWNER TO postgres;

--
-- Name: student_enrollments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_enrollments_id_seq OWNED BY public.student_enrollments.id;


--
-- Name: student_fees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_fees (
    id integer NOT NULL,
    student_id integer NOT NULL,
    fee_structure_id integer,
    amount_due numeric(10,2) NOT NULL,
    discount_amount numeric(10,2) DEFAULT 0.00 NOT NULL,
    due_date date NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    invoice_number character varying(50) NOT NULL,
    academic_year character varying(50) NOT NULL,
    class_id integer,
    fee_type character varying(100)
);


ALTER TABLE public.student_fees OWNER TO postgres;

--
-- Name: student_fees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_fees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_fees_id_seq OWNER TO postgres;

--
-- Name: student_fees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_fees_id_seq OWNED BY public.student_fees.id;


--
-- Name: student_import_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_import_logs (
    id integer NOT NULL,
    admin_user_id integer,
    file_name character varying(255) NOT NULL,
    class_id integer,
    academic_year character varying(50) NOT NULL,
    total_rows integer NOT NULL,
    imported_count integer NOT NULL,
    already_enrolled_count integer NOT NULL,
    skipped_count integer NOT NULL,
    failed_count integer NOT NULL,
    details text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.student_import_logs OWNER TO postgres;

--
-- Name: student_import_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_import_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_import_logs_id_seq OWNER TO postgres;

--
-- Name: student_import_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_import_logs_id_seq OWNED BY public.student_import_logs.id;


--
-- Name: student_result_views; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_result_views (
    id integer NOT NULL,
    student_id integer NOT NULL,
    exam_name character varying(100) NOT NULL,
    class_id integer NOT NULL,
    academic_year character varying(50) NOT NULL,
    release_batch_id integer,
    first_viewed_at timestamp with time zone DEFAULT now() NOT NULL,
    last_viewed_at timestamp with time zone DEFAULT now() NOT NULL,
    view_count integer DEFAULT 1 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.student_result_views OWNER TO postgres;

--
-- Name: student_result_views_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_result_views_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_result_views_id_seq OWNER TO postgres;

--
-- Name: student_result_views_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_result_views_id_seq OWNED BY public.student_result_views.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    id integer NOT NULL,
    user_id integer,
    admission_number character varying(50) NOT NULL,
    first_name character varying(100) NOT NULL,
    middle_name character varying(100),
    last_name character varying(100) NOT NULL,
    gender character varying(20) NOT NULL,
    date_of_birth date,
    phone character varying(50),
    address text,
    guardian_name character varying(200),
    guardian_phone character varying(50),
    guardian_email character varying(255),
    guardian_relationship character varying(50),
    admission_date date,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    photo_path character varying(500),
    photo_filename character varying(255),
    photo_mime_type character varying(100),
    photo_size integer,
    photo_uploaded_at timestamp with time zone,
    photo_updated_at timestamp with time zone
);


ALTER TABLE public.students OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_id_seq OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: subjects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subjects (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(50) NOT NULL,
    department character varying(100),
    description text,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    division character varying(20) DEFAULT 'ALL'::character varying,
    applicable_levels character varying(255)
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
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    institution_id integer NOT NULL,
    plan_name character varying(100) NOT NULL,
    billing_cycle character varying(50) NOT NULL,
    price numeric(10,2) NOT NULL,
    setup_fee numeric(10,2) NOT NULL,
    status character varying(50) NOT NULL,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    auto_renew boolean NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.subscriptions OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_settings (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    value text NOT NULL,
    description character varying(255),
    is_public boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.system_settings OWNER TO postgres;

--
-- Name: system_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_settings_id_seq OWNER TO postgres;

--
-- Name: system_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_settings_id_seq OWNED BY public.system_settings.id;


--
-- Name: teacher_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_assignments (
    id integer NOT NULL,
    teacher_id integer NOT NULL,
    class_id integer NOT NULL,
    subject_id integer NOT NULL,
    academic_year character varying(50) NOT NULL,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.teacher_assignments OWNER TO postgres;

--
-- Name: teacher_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teacher_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teacher_assignments_id_seq OWNER TO postgres;

--
-- Name: teacher_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teacher_assignments_id_seq OWNED BY public.teacher_assignments.id;


--
-- Name: teacher_attendances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_attendances (
    id integer NOT NULL,
    teacher_id integer NOT NULL,
    date date NOT NULL,
    academic_year character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    reason character varying(255),
    recorded_by_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.teacher_attendances OWNER TO postgres;

--
-- Name: teacher_attendances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teacher_attendances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teacher_attendances_id_seq OWNER TO postgres;

--
-- Name: teacher_attendances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teacher_attendances_id_seq OWNED BY public.teacher_attendances.id;


--
-- Name: teacher_availabilities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_availabilities (
    id integer NOT NULL,
    teacher_id integer NOT NULL,
    academic_year character varying(50) NOT NULL,
    day_of_week character varying(20) NOT NULL,
    start_time time without time zone,
    end_time time without time zone,
    is_available boolean DEFAULT true NOT NULL,
    max_periods_per_day integer DEFAULT 5,
    max_periods_per_week integer DEFAULT 25,
    notes character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.teacher_availabilities OWNER TO postgres;

--
-- Name: teacher_availabilities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teacher_availabilities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teacher_availabilities_id_seq OWNER TO postgres;

--
-- Name: teacher_availabilities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teacher_availabilities_id_seq OWNED BY public.teacher_availabilities.id;


--
-- Name: teachers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teachers (
    id integer NOT NULL,
    user_id integer,
    teacher_number character varying(50) NOT NULL,
    first_name character varying(100) NOT NULL,
    middle_name character varying(100),
    last_name character varying(100) NOT NULL,
    gender character varying(20) NOT NULL,
    date_of_birth date,
    phone character varying(50),
    email character varying(255) NOT NULL,
    address text,
    qualification character varying(200),
    hire_date date,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.teachers OWNER TO postgres;

--
-- Name: teachers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teachers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teachers_id_seq OWNER TO postgres;

--
-- Name: teachers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teachers_id_seq OWNED BY public.teachers.id;


--
-- Name: timetable_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.timetable_settings (
    id integer NOT NULL,
    academic_year character varying(50) NOT NULL,
    division character varying(20) DEFAULT 'ALL'::character varying NOT NULL,
    school_days character varying(255) DEFAULT 'Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday'::character varying NOT NULL,
    start_time time without time zone DEFAULT '07:30:00'::time without time zone NOT NULL,
    end_time time without time zone DEFAULT '13:30:00'::time without time zone NOT NULL,
    period_duration_minutes integer DEFAULT 45 NOT NULL,
    break_duration_minutes integer DEFAULT 20 NOT NULL,
    break_after_period integer DEFAULT 3 NOT NULL,
    lunch_duration_minutes integer DEFAULT 30 NOT NULL,
    lunch_after_period integer DEFAULT 5 NOT NULL,
    periods_per_day integer DEFAULT 6 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.timetable_settings OWNER TO postgres;

--
-- Name: timetable_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.timetable_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.timetable_settings_id_seq OWNER TO postgres;

--
-- Name: timetable_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.timetable_settings_id_seq OWNED BY public.timetable_settings.id;


--
-- Name: timetables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.timetables (
    id integer NOT NULL,
    class_id integer NOT NULL,
    subject_id integer NOT NULL,
    teacher_id integer,
    academic_year character varying(50) NOT NULL,
    day_of_week character varying(20) NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    room character varying(50),
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    period_number integer,
    is_break boolean DEFAULT false NOT NULL,
    published_at timestamp with time zone,
    published_by_id integer
);


ALTER TABLE public.timetables OWNER TO postgres;

--
-- Name: timetables_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.timetables_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.timetables_id_seq OWNER TO postgres;

--
-- Name: timetables_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.timetables_id_seq OWNED BY public.timetables.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    assigned_at timestamp with time zone NOT NULL,
    assigned_by integer
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_roles_id_seq OWNER TO postgres;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(200) NOT NULL,
    phone_number character varying(50),
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: attendance_submissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_submissions ALTER COLUMN id SET DEFAULT nextval('public.attendance_submissions_id_seq'::regclass);


--
-- Name: attendances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances ALTER COLUMN id SET DEFAULT nextval('public.attendances_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: class_promotion_batches id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_batches ALTER COLUMN id SET DEFAULT nextval('public.class_promotion_batches_id_seq'::regclass);


--
-- Name: class_promotion_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_records ALTER COLUMN id SET DEFAULT nextval('public.class_promotion_records_id_seq'::regclass);


--
-- Name: classes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes ALTER COLUMN id SET DEFAULT nextval('public.classes_id_seq'::regclass);


--
-- Name: exam_deadline_extensions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_deadline_extensions ALTER COLUMN id SET DEFAULT nextval('public.exam_deadline_extensions_id_seq'::regclass);


--
-- Name: exam_results id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results ALTER COLUMN id SET DEFAULT nextval('public.exam_results_id_seq'::regclass);


--
-- Name: exams id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams ALTER COLUMN id SET DEFAULT nextval('public.exams_id_seq'::regclass);


--
-- Name: fee_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_payments ALTER COLUMN id SET DEFAULT nextval('public.fee_payments_id_seq'::regclass);


--
-- Name: fee_structures id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_structures ALTER COLUMN id SET DEFAULT nextval('public.fee_structures_id_seq'::regclass);


--
-- Name: form_master_assignments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_master_assignments ALTER COLUMN id SET DEFAULT nextval('public.form_master_assignments_id_seq'::regclass);


--
-- Name: inquiries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inquiries ALTER COLUMN id SET DEFAULT nextval('public.inquiries_id_seq'::regclass);


--
-- Name: institution_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institution_payments ALTER COLUMN id SET DEFAULT nextval('public.institution_payments_id_seq'::regclass);


--
-- Name: institutions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions ALTER COLUMN id SET DEFAULT nextval('public.institutions_id_seq'::regclass);


--
-- Name: notification_deliveries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_deliveries ALTER COLUMN id SET DEFAULT nextval('public.notification_deliveries_id_seq'::regclass);


--
-- Name: notification_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_templates ALTER COLUMN id SET DEFAULT nextval('public.notification_templates_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: result_release_batches id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_release_batches ALTER COLUMN id SET DEFAULT nextval('public.result_release_batches_id_seq'::regclass);


--
-- Name: result_submissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions ALTER COLUMN id SET DEFAULT nextval('public.result_submissions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions ALTER COLUMN id SET DEFAULT nextval('public.sessions_id_seq'::regclass);


--
-- Name: student_enrollments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_enrollments ALTER COLUMN id SET DEFAULT nextval('public.student_enrollments_id_seq'::regclass);


--
-- Name: student_fees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees ALTER COLUMN id SET DEFAULT nextval('public.student_fees_id_seq'::regclass);


--
-- Name: student_import_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_import_logs ALTER COLUMN id SET DEFAULT nextval('public.student_import_logs_id_seq'::regclass);


--
-- Name: student_result_views id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_result_views ALTER COLUMN id SET DEFAULT nextval('public.student_result_views_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: subjects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects ALTER COLUMN id SET DEFAULT nextval('public.subjects_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: system_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings ALTER COLUMN id SET DEFAULT nextval('public.system_settings_id_seq'::regclass);


--
-- Name: teacher_assignments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_assignments ALTER COLUMN id SET DEFAULT nextval('public.teacher_assignments_id_seq'::regclass);


--
-- Name: teacher_attendances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_attendances ALTER COLUMN id SET DEFAULT nextval('public.teacher_attendances_id_seq'::regclass);


--
-- Name: teacher_availabilities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_availabilities ALTER COLUMN id SET DEFAULT nextval('public.teacher_availabilities_id_seq'::regclass);


--
-- Name: teachers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers ALTER COLUMN id SET DEFAULT nextval('public.teachers_id_seq'::regclass);


--
-- Name: timetable_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetable_settings ALTER COLUMN id SET DEFAULT nextval('public.timetable_settings_id_seq'::regclass);


--
-- Name: timetables id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetables ALTER COLUMN id SET DEFAULT nextval('public.timetables_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
017_prevent_dup_attendance
\.


--
-- Data for Name: attendance_submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance_submissions (id, academic_year, class_id, subject_id, date, period, teacher_id, submitted_by_id, status, total_students, present_count, late_count, absent_count, submission_time, created_at, updated_at) FROM stdin;
2	2026/2027	84	1	2026-09-15	08:00 - 09:00	\N	\N	SUBMITTED	1	1	0	0	2026-10-27 08:32:42.500821+03	2026-10-27 08:32:42.500821+03	2026-10-27 08:32:42.50083+03
3	2025/2026	1	1	2026-06-10	1	1	\N	SUBMITTED	2	0	0	2	2026-09-21 01:43:19.904027+03	2026-09-21 01:43:19.904027+03	2026-11-12 10:13:51.885744+03
4	2026-2027	1	26	2026-09-21	\N	6	377	SUBMITTED	21	21	0	0	2026-09-21 03:58:30.365864+03	2026-09-21 03:58:30.365864+03	2026-09-21 03:58:30.365996+03
5	2026/2027	1	1	2026-09-20	1	1	\N	SUBMITTED	1	0	0	1	2026-09-21 01:43:18.999854+03	2026-09-21 01:43:18.999854+03	2026-09-21 01:43:18.999858+03
7	2026/2027	87	38	2026-11-12	1	14	\N	SUBMITTED	1	0	0	1	2026-11-13 08:48:05.484239+03	2026-11-13 08:48:05.484239+03	2026-11-13 08:48:05.484242+03
8	2026/2027	87	38	2026-11-11	1	14	\N	SUBMITTED	1	0	0	1	2026-11-13 08:48:05.484244+03	2026-11-13 08:48:05.484244+03	2026-11-13 08:48:05.484244+03
9	2026/2027	87	38	2026-11-09	1	14	\N	SUBMITTED	1	1	0	0	2026-11-13 08:48:05.484246+03	2026-11-13 08:48:05.484246+03	2026-11-13 08:48:05.484247+03
10	2025-2026	1	1	2026-10-23	\N	1	304	SUBMITTED	21	20	0	1	2026-10-23 23:31:20.749959+03	2026-10-23 23:31:20.749959+03	2026-10-23 23:31:20.749985+03
11	2026/2027	87	38	2026-11-10	1	14	\N	SUBMITTED	1	0	0	1	2026-11-13 08:48:05.484245+03	2026-11-13 08:48:05.484245+03	2026-11-13 08:48:05.484246+03
13	2026/2027	1	1	2026-09-21	1	1	\N	SUBMITTED	1	0	0	1	2026-09-21 01:43:19.071956+03	2026-09-21 01:43:19.071956+03	2026-09-21 01:43:19.071961+03
14	2026/2027	13	1	2026-09-15	08:00 - 09:00	\N	\N	SUBMITTED	1	1	0	0	2026-09-21 01:43:08.647135+03	2026-09-21 01:43:08.647135+03	2026-09-21 01:43:08.647139+03
15	2026/2027	78	1	2026-09-15	08:00 - 09:00	\N	\N	SUBMITTED	1	1	0	0	2026-10-27 08:25:59.382682+03	2026-10-27 08:25:59.382682+03	2026-10-27 08:25:59.38269+03
45	2026/2027	94	13	2026-11-13	\N	30	424	SUBMITTED	1	1	0	0	2026-11-13 16:09:38.105969+03	2026-11-13 16:09:38.115197+03	2026-11-13 16:09:38.115201+03
46	2026/2027	94	5	2026-11-13	\N	30	424	SUBMITTED	1	0	0	1	2026-11-13 16:09:38.196737+03	2026-11-13 16:09:38.198207+03	2026-11-13 16:09:38.198211+03
47	2026/2027	94	13	2026-11-12	\N	30	424	SUBMITTED	1	0	1	0	2026-11-13 16:09:38.269538+03	2026-11-13 16:09:38.270677+03	2026-11-13 16:09:38.270679+03
48	2026/2027	94	13	2026-11-03	\N	30	424	SUBMITTED	1	1	0	0	2026-11-13 16:09:38.648948+03	2026-11-13 16:09:38.648662+03	2026-11-13 16:09:38.648668+03
50	2025/2026	1	13	2026-11-13	\N	23	417	SUBMITTED	1	1	0	0	2026-11-13 16:09:38.732417+03	2026-11-13 16:09:38.734103+03	2026-11-13 16:09:38.734105+03
51	2025/2026	1	4	2026-11-13	\N	24	418	SUBMITTED	1	0	0	1	2026-11-13 16:09:38.7564+03	2026-11-13 16:09:38.758053+03	2026-11-13 16:09:38.758055+03
53	2025-2026	1	1	2026-11-13	\N	1	304	SUBMITTED	1	1	0	0	2026-11-13 16:09:40.538236+03	2026-11-13 16:09:40.539269+03	2026-11-13 16:09:40.539271+03
54	2026/2027	91	13	2026-11-11	Morning Session	25	419	SUBMITTED	1	1	0	0	2026-11-13 16:09:40.735777+03	2026-11-13 16:09:40.737239+03	2026-11-13 16:09:40.737241+03
\.


--
-- Data for Name: attendances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendances (id, student_id, class_id, subject_id, teacher_id, academic_year, date, period, status, remarks, recorded_by_id, created_at, updated_at) FROM stdin;
1	90	13	1	\N	2026/2027	2026-09-15	08:00 - 09:00	PRESENT	\N	\N	2026-09-21 01:43:08.647135+03	2026-09-21 01:43:08.647139+03
2	1	1	1	1	2026/2027	2026-09-20	1	ABSENT	\N	\N	2026-09-21 01:43:18.999854+03	2026-09-21 01:43:18.999858+03
3	1	1	1	1	2026/2027	2026-09-21	1	ABSENT	\N	\N	2026-09-21 01:43:19.071956+03	2026-09-21 01:43:19.071961+03
4	1	1	1	1	2025/2026	2026-06-10	1	ABSENT	\N	\N	2026-09-21 01:43:19.904027+03	2026-09-21 01:43:19.904033+03
5	3	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365864+03	2026-09-21 03:58:30.365875+03
6	15	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365879+03	2026-09-21 03:58:30.365883+03
7	5	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365886+03	2026-09-21 03:58:30.365889+03
8	2	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365893+03	2026-09-21 03:58:30.365896+03
9	14	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365899+03	2026-09-21 03:58:30.365902+03
10	18	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365905+03	2026-09-21 03:58:30.365908+03
11	10	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.36591+03	2026-09-21 03:58:30.365912+03
12	11	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365917+03	2026-09-21 03:58:30.365934+03
13	4	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365936+03	2026-09-21 03:58:30.365938+03
14	9	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365941+03	2026-09-21 03:58:30.365943+03
15	17	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365945+03	2026-09-21 03:58:30.365947+03
16	100	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365949+03	2026-09-21 03:58:30.365951+03
17	16	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365954+03	2026-09-21 03:58:30.365956+03
18	6	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365959+03	2026-09-21 03:58:30.365961+03
19	1	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365964+03	2026-09-21 03:58:30.365966+03
20	13	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365969+03	2026-09-21 03:58:30.365972+03
21	12	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365974+03	2026-09-21 03:58:30.365976+03
22	20	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365979+03	2026-09-21 03:58:30.365981+03
23	8	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365985+03	2026-09-21 03:58:30.365987+03
24	19	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.36599+03	2026-09-21 03:58:30.365992+03
25	7	1	26	6	2026-2027	2026-09-21	\N	PRESENT	\N	377	2026-09-21 03:58:30.365994+03	2026-09-21 03:58:30.365996+03
26	3	1	1	1	2025-2026	2026-10-23	\N	ABSENT	Sick with flu	304	2026-10-23 23:31:20.749959+03	2026-10-23 23:31:20.749962+03
27	15	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749964+03	2026-10-23 23:31:20.749964+03
28	5	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749965+03	2026-10-23 23:31:20.749966+03
29	2	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749966+03	2026-10-23 23:31:20.749967+03
30	14	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749967+03	2026-10-23 23:31:20.749968+03
31	18	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749968+03	2026-10-23 23:31:20.749969+03
32	10	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749969+03	2026-10-23 23:31:20.74997+03
33	11	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749971+03	2026-10-23 23:31:20.749972+03
34	4	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749972+03	2026-10-23 23:31:20.749973+03
35	9	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749973+03	2026-10-23 23:31:20.749974+03
36	17	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749974+03	2026-10-23 23:31:20.749975+03
37	100	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749975+03	2026-10-23 23:31:20.749976+03
38	16	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749976+03	2026-10-23 23:31:20.749977+03
39	6	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749977+03	2026-10-23 23:31:20.749978+03
40	1	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749978+03	2026-10-23 23:31:20.749979+03
41	13	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749979+03	2026-10-23 23:31:20.74998+03
42	12	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749981+03	2026-10-23 23:31:20.749981+03
43	20	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749982+03	2026-10-23 23:31:20.749982+03
44	8	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749983+03	2026-10-23 23:31:20.749983+03
45	19	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749984+03	2026-10-23 23:31:20.749984+03
46	7	1	1	1	2025-2026	2026-10-23	\N	PRESENT	\N	304	2026-10-23 23:31:20.749985+03	2026-10-23 23:31:20.749985+03
47	150	78	1	\N	2026/2027	2026-09-15	08:00 - 09:00	PRESENT	\N	\N	2026-10-27 08:25:59.382682+03	2026-10-27 08:25:59.38269+03
48	168	84	1	\N	2026/2027	2026-09-15	08:00 - 09:00	PRESENT	\N	\N	2026-10-27 08:32:42.500821+03	2026-10-27 08:32:42.50083+03
146	230	94	13	30	2026/2027	2026-11-13	\N	PRESENT	Prompt and attentive	424	2026-11-13 16:09:38.10735+03	2026-11-13 16:09:38.107353+03
147	230	94	5	30	2026/2027	2026-11-13	\N	ABSENT	Excused sick	424	2026-11-13 16:09:38.197191+03	2026-11-13 16:09:38.197194+03
51	156	1	1	1	2025/2026	2026-06-10	1	ABSENT	\N	\N	2026-11-12 10:13:51.88574+03	2026-11-12 10:13:51.885744+03
52	218	87	38	14	2026/2027	2026-11-12	1	ABSENT	\N	\N	2026-11-13 08:48:05.484239+03	2026-11-13 08:48:05.484242+03
53	218	87	38	14	2026/2027	2026-11-11	1	ABSENT	\N	\N	2026-11-13 08:48:05.484244+03	2026-11-13 08:48:05.484244+03
54	218	87	38	14	2026/2027	2026-11-10	1	ABSENT	\N	\N	2026-11-13 08:48:05.484245+03	2026-11-13 08:48:05.484246+03
55	218	87	38	14	2026/2027	2026-11-09	1	PRESENT	\N	\N	2026-11-13 08:48:05.484246+03	2026-11-13 08:48:05.484247+03
148	230	94	13	30	2026/2027	2026-11-12	\N	LATE	Late bus	424	2026-11-13 16:09:38.269962+03	2026-11-13 16:09:38.269965+03
149	1	1	13	23	2025/2026	2026-11-13	\N	PRESENT	Attended Arabic session	417	2026-11-13 16:09:38.732941+03	2026-11-13 16:09:38.732944+03
172	1	1	1	1	2025-2026	2026-11-13	\N	PRESENT	Automated verification	304	2026-11-13 16:09:40.538694+03	2026-11-13 16:09:40.538697+03
150	1	1	4	24	2025/2026	2026-11-13	\N	ABSENT	Missed Math session	418	2026-11-13 16:09:38.756863+03	2026-11-13 16:09:38.756866+03
173	229	91	13	25	2026/2027	2026-11-11	Morning Session	PRESENT	On time for Arabic	419	2026-11-13 16:09:40.736311+03	2026-11-13 16:09:40.736313+03
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, user_id, action, status, ip_address, user_agent, details, created_at) FROM stdin;
1	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-09-20 05:33:32.853298+03
2	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-20 05:33:59.946406+03
3	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 1, "name": "Grade 1 - A", "code": "G1-A-2025", "division": "PRIMARY", "level": "Grade 1", "section": "A"}	2026-09-20 05:35:21.795516+03
4	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"Students_20.xlsx\\", \\"class_id\\": 1, \\"class_name\\": \\"Grade 1 - A\\", \\"academic_year\\": \\"2025/2026\\", \\"imported_count\\": 20, \\"skipped_count\\": 0}"	2026-09-20 05:36:35.95275+03
5	1	TEACHER_CREATED	SUCCESS	\N	\N	{"teacher_id": 1, "teacher_number": "TCH-4305", "has_portal": true}	2026-09-20 05:38:12.60644+03
6	1	SUBJECT_CREATED	SUCCESS	\N	\N	{"subject_id": 1, "name": "math", "code": "MAT-101", "division": "ALL"}	2026-09-20 05:38:39.749948+03
7	1	SUBJECT_TEACHER_ASSIGNED	SUCCESS	\N	\N	{"subject_id": 1, "teacher_id": 1, "class_id": 1}	2026-09-20 05:39:17.66182+03
8	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-20 05:40:41.508311+03
9	304	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-09-20 05:41:20.643929+03
10	304	TEACHER_CREATED_EXAM	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "class_id": 1, "subject_id": 1, "teacher_id": 1, "academic_year": "2025/2026"}	2026-09-20 05:43:09.240326+03
11	304	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-20 05:45:22.582927+03
12	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"identifier_used": "rahma20"}	2026-09-20 05:45:46.105324+03
13	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"identifier_used": "rahma20"}	2026-09-20 05:46:04.295775+03
14	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-20 05:47:00.051235+03
15	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 2, "name": "Form 4 - B", "code": "F4-B-2025", "division": "SECONDARY", "level": "Form 4", "section": "B"}	2026-09-20 05:47:42.166684+03
632	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"identifier_used": "khadrastu180"}	2026-11-13 12:30:04.590422+03
17	305	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 2, "class_id": 3, "subject_id": 2, "completed": 2, "expected": 2}	2026-09-21 01:42:58.619487+03
663	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:52:24.941747+03
664	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 13:52:25.016711+03
20	305	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 2, "class_id": 3, "subject_id": 2, "completed": 2, "expected": 2}	2026-09-21 01:42:58.938453+03
706	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:04:03.220566+03
707	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 5, "subject_name": "English", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 16:04:03.325398+03
23	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 3, "class_id": 5, "subject_id": 4, "completed": 30, "expected": 30}	2026-09-21 01:42:59.839096+03
708	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-12", "present_count": 0, "late_count": 1, "absent_count": 0}	2026-11-13 16:04:03.430096+03
25	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 4, "class_id": 5, "subject_id": 5, "completed": 30, "expected": 30}	2026-09-21 01:43:00.06401+03
709	424	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:04:03.88797+03
27	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 5, "class_id": 5, "subject_id": 6, "completed": 30, "expected": 30}	2026-09-21 01:43:00.279419+03
748	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-13 16:28:00.925762+03
749	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-13 16:28:47.240931+03
30	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 7, "class_id": 5, "subject_id": 8, "completed": 30, "expected": 30}	2026-09-21 01:43:00.722104+03
750	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-13 16:28:56.583859+03
32	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 8, "class_id": 5, "subject_id": 9, "completed": 30, "expected": 30}	2026-09-21 01:43:01.164695+03
757	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 57, "class_id": 30, "subject_id": 24, "day": "Tuesday", "time": "07:30:00-08:15:00"}	2026-11-13 16:36:08.613424+03
34	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 9, "class_id": 5, "subject_id": 10, "completed": 30, "expected": 30}	2026-09-21 01:43:01.388655+03
778	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 160, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-11-13 18:21:20.80492+03
36	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 10, "class_id": 5, "subject_id": 11, "completed": 30, "expected": 30}	2026-09-21 01:43:01.590418+03
780	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 18:21:21.104768+03
38	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 11, "class_id": 5, "subject_id": 12, "completed": 30, "expected": 30}	2026-09-21 01:43:01.793979+03
40	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 12, "class_id": 5, "subject_id": 13, "completed": 30, "expected": 30}	2026-09-21 01:43:01.998064+03
42	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 13, "class_id": 5, "subject_id": 14, "completed": 30, "expected": 30}	2026-09-21 01:43:02.203153+03
44	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 14, "class_id": 5, "subject_id": 15, "completed": 30, "expected": 30}	2026-09-21 01:43:02.589574+03
47	308	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 6, "class_id": 5, "subject_id": 7, "completed": 30, "expected": 30}	2026-09-21 01:43:03.491546+03
633	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"identifier_used": "teacher_2291"}	2026-11-13 12:38:04.772569+03
52	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:06.635544+03
53	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 7, "name": "Grade 7 - DELTA STREAM", "code": "CLS-590859", "division": "PRIMARY", "level": "Grade 7", "section": "DELTA STREAM"}	2026-09-21 01:43:06.748704+03
57	365	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["STUDENT"]}	2026-09-21 01:43:09.161084+03
58	1	STUDENT_CLASS_CHANGED	SUCCESS	\N	\N	{"student_id": 90, "admission_number": "ADM-PROM-5-1-5369", "old_class": "Form 5", "new_class": "Form 6", "academic_year": "2027/2028", "reason": "Annual Academic Progression"}	2026-09-21 01:43:09.266729+03
69	367	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 3, "target_type": "CLASS", "created_count": 23, "skipped_count": 0, "total_billed": 460.0}	2026-09-21 01:43:15.558557+03
70	367	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 4, "target_type": "SINGLE_STUDENT", "created_count": 1, "skipped_count": 0, "total_billed": 30.0}	2026-09-21 01:43:15.616169+03
74	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 3, "receipt_number": "RCT-2026-000003", "student_id": 1, "student_fee_id": 28, "amount": 35.0, "method": "EDAHAB", "reference": "ED-7788"}	2026-09-21 01:43:15.929877+03
76	367	FEE_PAYMENT_CANCELLED	SUCCESS	\N	\N	{"payment_id": 4, "receipt_number": "RCT-2026-000004", "reason": "Mistaken Entry"}	2026-09-21 01:43:16.112625+03
77	367	FEE_NOTIFICATIONS_SENT	SUCCESS	\N	\N	{"target_type": "ALL_OUTSTANDING", "sent_count": 20, "missing_phone_count": 0, "already_notified_count": 0}	2026-09-21 01:43:16.528921+03
79	367	FEE_STRUCTURE_DELETED	SUCCESS	\N	\N	{"structure_id": 10, "name": "Fee To Delete"}	2026-09-21 01:43:16.662364+03
80	1	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 11, "target_type": "SINGLE_STUDENT", "created_count": 1, "skipped_count": 0, "total_billed": 20.0}	2026-09-21 01:43:17.406095+03
83	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "std_farhan"}	2026-09-21 01:43:19.315387+03
84	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:19.658749+03
634	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-13 12:46:28.361638+03
86	373	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 17, "class_id": 3, "subject_id": 4, "completed": 2, "expected": 2}	2026-09-21 01:43:21.138934+03
665	419	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 91, "class_name": "Class 1 DynFilter", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-11", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:53:05.231758+03
666	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:53:07.127172+03
667	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 13:53:07.187051+03
90	373	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 17, "class_id": 3, "subject_id": 4, "completed": 2, "expected": 2}	2026-09-21 01:43:21.359985+03
710	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:04:13.058462+03
711	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 5, "subject_name": "English", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 16:04:13.169301+03
94	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 20, "name": "Grade 7 - F1C1", "code": "G7-717934", "division": "PRIMARY", "level": "Grade 7", "section": "F1C1"}	2026-09-21 01:43:21.96679+03
95	1	CLASS_UPDATED	SUCCESS	\N	\N	{"class_id": 20, "name": "Grade 7 - F1C1", "division": "PRIMARY"}	2026-09-21 01:43:21.992795+03
98	1	SUBJECT_CREATED	SUCCESS	\N	\N	{"subject_id": 28, "name": "General Science SCI-1CECA6", "code": "SCI-1CECA6", "division": "ALL"}	2026-09-21 01:43:22.362278+03
100	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 21, "name": "Grade 7 - E638D7", "code": "CONF-E638D7", "division": "PRIMARY", "level": "Grade 7", "section": "E638D7"}	2026-09-21 01:43:22.710421+03
101	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 1, "class_id": 21, "subject_id": 13, "day": "Friday", "time": "06:00:00-07:00:00"}	2026-09-21 01:43:22.859947+03
102	1	CLASS_DEACTIVATED	SUCCESS	\N	\N	{"class_id": 21, "name": "Grade 7 - E638D7"}	2026-09-21 01:43:22.888383+03
103	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:23.212569+03
104	366	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": []}	2026-09-21 01:43:23.598398+03
109	1	STUDENT_STATUS_CHANGED	SUCCESS	\N	\N	{"student_id": 100, "admission_number": "ADM-633578", "old_status": "INACTIVE", "new_status": "ACTIVE", "reason": "Re-activated"}	2026-09-21 01:43:25.617981+03
712	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-12", "present_count": 0, "late_count": 1, "absent_count": 0}	2026-11-13 16:04:13.276058+03
713	424	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:04:13.681148+03
714	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:04:13.879378+03
717	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "late_count": 0, "absent_count": 1}	2026-11-13 16:04:15.507891+03
718	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 16:04:15.942868+03
719	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:04:16.598938+03
753	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-13 16:34:12.297221+03
783	410	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["SUPER_ADMIN"]}	2026-11-13 18:34:48.11534+03
785	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-14 11:45:37.130674+03
50	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "nonexistent_user"}	2026-09-21 01:43:04.821534+03
51	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:05.306006+03
54	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 8, "name": "Grade 7 - A", "code": "CLS-590859-362", "division": "PRIMARY", "level": "Grade 7", "section": "A"}	2026-09-21 01:43:06.765752+03
55	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:07.151244+03
56	364	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-09-21 01:43:08.000636+03
59	1	BULK_CLASS_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0034", "source_year": "2026/2027", "target_year": "2027/2028", "total_promoted": 14, "total_graduated": 3}	2026-09-21 01:43:09.471322+03
60	1	PROMOTION_BATCH_ROLLED_BACK	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0034", "batch_id": 86, "restored_count": 17}	2026-09-21 01:43:09.89903+03
61	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 15, "name": "Grade 7 - C", "code": "G7-C-2026", "division": "PRIMARY", "level": "Grade 7", "section": "C"}	2026-09-21 01:43:09.951443+03
62	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 16, "name": "Form 1 - B", "code": "F1-B-2026", "division": "SECONDARY", "level": "Form 1", "section": "B"}	2026-09-21 01:43:09.970529+03
63	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 17, "name": "Grade 7 - A", "code": "G7-A-2026", "division": "PRIMARY", "level": "Grade 7", "section": "A"}	2026-09-21 01:43:10.005658+03
64	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 18, "name": "Grade 4 - E", "code": "G4-E-2026", "division": "PRIMARY", "level": "Grade 4", "section": "E"}	2026-09-21 01:43:10.032903+03
65	1	STUDENT_ENROLLED_IN_CLASS	SUCCESS	\N	\N	{"class_id": 3, "student_id": 1, "academic_year": "2026-2027"}	2026-09-21 01:43:10.275963+03
66	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:14.870348+03
67	367	FEE_STRUCTURE_CREATED	SUCCESS	\N	\N	{"structure_id": 1, "name": "Term 1 Tuition 2026/2027", "amount": 25.0, "frequency": "Monthly", "academic_year": "2026/2027", "education_level": null}	2026-09-21 01:43:15.232392+03
68	367	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 2, "target_type": "SINGLE_STUDENT", "created_count": 1, "skipped_count": 0, "total_billed": 15.0}	2026-09-21 01:43:15.331012+03
71	367	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 4, "target_type": "SINGLE_STUDENT", "created_count": 0, "skipped_count": 1, "total_billed": 0}	2026-09-21 01:43:15.64879+03
72	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 1, "receipt_number": "RCT-2026-000001", "student_id": 1, "student_fee_id": 26, "amount": 20.0, "method": "EVC_PLUS", "reference": "EVC-TXN-101"}	2026-09-21 01:43:15.707161+03
73	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 2, "receipt_number": "RCT-2026-000002", "student_id": 1, "student_fee_id": 26, "amount": 30.0, "method": "CASH", "reference": "CASH-REC-102"}	2026-09-21 01:43:15.815083+03
75	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 4, "receipt_number": "RCT-2026-000004", "student_id": 1, "student_fee_id": 30, "amount": 60.0, "method": "CASH", "reference": null}	2026-09-21 01:43:16.067437+03
78	367	FEE_STRUCTURE_CREATED	SUCCESS	\N	\N	{"structure_id": 10, "name": "Fee To Delete", "amount": 50.0, "frequency": "Monthly", "academic_year": "2026/2027", "education_level": null}	2026-09-21 01:43:16.634358+03
81	1	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 5, "receipt_number": "RCT-2026-000005", "student_id": 78, "student_fee_id": 31, "amount": 8.0, "method": "EVC_PLUS", "reference": "TX-PARTIAL-001"}	2026-09-21 01:43:17.448413+03
82	1	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 6, "receipt_number": "RCT-2026-000006", "student_id": 78, "student_fee_id": 31, "amount": 12.0, "method": "CASH", "reference": "TX-FULL-002"}	2026-09-21 01:43:17.499479+03
93	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:21.95336+03
96	1	CLASS_DEACTIVATED	SUCCESS	\N	\N	{"class_id": 20, "name": "Grade 7 - F1C1"}	2026-09-21 01:43:22.014551+03
97	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:22.341376+03
99	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:22.693168+03
105	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-09-21 01:43:23.63194+03
106	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-09-21 01:43:24.984543+03
107	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 100, "admission_number": "ADM-633578", "class_id": 1}	2026-09-21 01:43:25.548604+03
108	1	STUDENT_STATUS_CHANGED	SUCCESS	\N	\N	{"student_id": 100, "admission_number": "ADM-633578", "old_status": "ACTIVE", "new_status": "INACTIVE", "reason": "Temporary transfer"}	2026-09-21 01:43:25.599836+03
110	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-09-21 01:53:35.116787+03
111	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-09-21 01:53:42.495245+03
112	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": []}	2026-09-21 01:53:42.858337+03
113	\N	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "std_farhan"}	2026-09-21 01:53:42.879849+03
114	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-21 02:02:06.721989+03
115	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-09-21 02:06:52.969166+03
116	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-09-21 02:06:59.127935+03
117	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-09-21 02:07:05.23824+03
118	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-21 03:05:54.655364+03
119	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 03:26:11.508968+03
120	308	LOGIN_SUCCESS	SUCCESS	\N	\N	{"roles": ["TEACHER"]}	2026-09-21 03:31:52.299379+03
121	308	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Python-urllib/3.14	{"roles": ["TEACHER"]}	2026-09-21 03:32:33.141415+03
122	308	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-09-21 03:33:07.664165+03
123	308	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 03:33:52.084784+03
124	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-21 03:34:01.102563+03
125	1	TEACHER_CREATED	SUCCESS	\N	\N	{"teacher_id": 6, "teacher_number": "TCH-5022", "has_portal": true}	2026-09-21 03:35:43.668768+03
126	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 03:36:05.392116+03
127	377	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-09-21 03:36:16.871199+03
128	377	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 03:43:08.751934+03
129	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-21 03:43:18.61564+03
131	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 03:44:05.689479+03
130	1	TEACHER_ASSIGNED_TO_CLASS	SUCCESS	\N	\N	{"class_id": 1, "teacher_id": 6, "subject_id": 26}	2026-09-21 03:43:44.591469+03
132	377	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-09-21 03:44:20.384094+03
635	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"students_8DFEC2.xlsx\\", \\"class_id\\": 29, \\"class_name\\": \\"Grade 1 - A\\", \\"academic_year\\": \\"2026/2027\\", \\"imported_count\\": 10, \\"skipped_count\\": 0}"	2026-11-13 12:46:28.619664+03
668	419	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 91, "class_name": "Class 1 DynFilter", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-11", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:54:02.105903+03
669	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:54:03.277929+03
670	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 13:54:03.348034+03
715	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 16:04:13.905813+03
716	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:04:15.098049+03
720	419	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 91, "class_name": "Class 1 DynFilter", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-11", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:04:16.844941+03
759	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 16:37:23.024399+03
760	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 12}	2026-11-13 16:37:23.7049+03
761	1	TIMETABLE_PUBLISHED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "published_count": 12}	2026-11-13 16:37:23.749751+03
762	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 16:37:24.141256+03
763	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 75, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-11-13 16:37:24.467883+03
765	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 75, "class_id": 1, "day": "Saturday"}	2026-11-13 16:37:24.620901+03
767	1	TIMETABLE_SLOT_MOVED	SUCCESS	\N	\N	{"slot_id": 76, "class_id": 1, "new_day": "Monday", "new_time": "08:00:00-08:45:00"}	2026-11-13 16:37:25.054418+03
768	1	TIMETABLE_SLOTS_SWAPPED	SUCCESS	\N	\N	{"slot_id_1": 76, "slot_id_2": 77, "class_id": 1}	2026-11-13 16:37:25.128254+03
784	410	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-13 18:39:08.289938+03
786	1	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 21, "target_type": "SINGLE_STUDENT", "created_count": 1, "skipped_count": 0, "total_billed": 35.0}	2026-11-14 11:46:30.953451+03
133	377	TEACHER_CREATED_EXAM	SUCCESS	\N	\N	{"exam_id": 20, "exam_name": "Final Computer G9 Examination (Grade 1 - A)", "class_id": 1, "subject_id": 26, "teacher_id": 6, "academic_year": "2026/2027"}	2026-09-21 03:45:01.369033+03
636	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "absent_count": 0}	2026-11-13 12:47:24.624861+03
671	419	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 91, "class_name": "Class 1 DynFilter", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-11", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:54:30.929906+03
672	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:54:32.084435+03
673	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 13:54:32.159246+03
674	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:54:34.886396+03
675	1	SAVE_TEACHER_ATTENDANCE	SUCCESS	\N	\N	{"date": "2026-11-13", "academic_year": "2026/2027", "total_teachers_marked": 22, "present_count": 6, "absent_count": 6, "late_count": 5, "on_leave_count": 5}	2026-11-13 13:54:35.429281+03
721	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:09:38.117084+03
722	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 5, "subject_name": "English", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 16:09:38.199018+03
723	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-12", "present_count": 0, "late_count": 1, "absent_count": 0}	2026-11-13 16:09:38.271219+03
724	424	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:09:38.574232+03
725	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:09:38.734779+03
728	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "late_count": 0, "absent_count": 1}	2026-11-13 16:09:39.84186+03
729	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 16:09:40.115901+03
730	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:09:40.539869+03
764	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 75, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-11-13 16:37:24.601181+03
766	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 16:37:24.942806+03
134	377	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["TEACHER"]}	2026-09-21 03:49:57.901374+03
135	377	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["TEACHER"]}	2026-09-21 03:50:53.922667+03
637	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 12:47:35.963924+03
137	377	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 20, "exam_name": "Final Computer G9 Examination (Grade 1 - A)", "student_id": 8, "filename": "pexels-bhuppigraphy-757919.jpg", "file_size": 457310}	2026-09-21 03:52:59.172448+03
138	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-09-21 03:57:17.558668+03
139	377	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 26, "subject_name": "Computer G9", "date": "2026-09-21", "present_count": 21, "absent_count": 0}	2026-09-21 03:58:30.37908+03
140	377	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 03:58:55.638909+03
141	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-21 03:59:04.472418+03
142	1	STUDENT_PORTAL_ACCOUNT_CREATED	SUCCESS	\N	\N	{"student_id": 95, "username": "student63prom635369"}	2026-09-21 04:00:10.930913+03
143	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 04:00:35.68993+03
144	378	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["STUDENT"]}	2026-09-21 04:00:46.43978+03
145	378	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 04:01:04.198426+03
146	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-21 04:01:13.196461+03
147	1	STUDENT_PORTAL_ACCOUNT_CREATED	SUCCESS	\N	\N	{"student_id": 18, "username": "deqa18"}	2026-09-21 04:02:30.909617+03
148	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 04:02:35.377711+03
149	379	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["STUDENT"]}	2026-09-21 04:02:44.219047+03
150	379	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 04:04:20.185912+03
151	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-21 04:04:27.683843+03
152	374	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["STUDENT"]}	2026-09-21 04:09:56.97108+03
153	374	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["STUDENT"]}	2026-09-21 04:10:04.848405+03
154	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-21 04:12:38.825118+03
155	379	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	{"roles": ["STUDENT"]}	2026-09-21 04:12:59.269546+03
156	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-26 08:52:24.831683+03
157	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-26 08:59:01.388138+03
158	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-26 09:01:06.954212+03
159	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-26 09:05:23.05707+03
160	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-09-26 09:05:38.151487+03
161	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-26 09:06:01.415866+03
162	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"identifier_used": "abdirahman"}	2026-09-26 09:06:06.782302+03
163	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"identifier_used": "abdirahman"}	2026-09-26 09:06:09.133036+03
164	379	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": ["STUDENT"]}	2026-09-26 09:06:19.78635+03
165	379	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-26 09:06:31.344571+03
166	379	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": ["STUDENT"]}	2026-09-26 09:06:52.797401+03
167	379	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-26 09:07:28.883609+03
168	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": []}	2026-09-26 09:07:38.276632+03
169	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": []}	2026-09-26 09:07:43.465603+03
170	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": []}	2026-09-26 09:07:49.852804+03
171	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": []}	2026-09-26 09:07:51.058708+03
172	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": []}	2026-09-26 09:07:54.596885+03
173	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0	{"roles": []}	2026-09-26 09:11:14.5131+03
174	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0	{"roles": []}	2026-09-26 09:11:18.994262+03
175	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0	{"roles": []}	2026-09-26 09:11:24.183716+03
176	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0	{"roles": []}	2026-09-26 09:12:45.798905+03
177	366	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": []}	2026-09-26 09:12:45.861222+03
178	\N	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "TCH-1001"}	2026-09-26 09:12:45.876604+03
179	305	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["TEACHER"]}	2026-09-26 09:12:46.242823+03
180	305	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["TEACHER"]}	2026-09-26 09:12:46.596501+03
181	304	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["TEACHER"]}	2026-09-26 09:12:46.916991+03
182	304	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["TEACHER"]}	2026-09-26 09:12:47.22741+03
183	308	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["TEACHER"]}	2026-09-26 09:12:47.533801+03
184	366	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-26 09:17:07.517857+03
185	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"identifier_used": "teacher.abdi"}	2026-09-26 09:17:21.673932+03
186	305	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-09-26 09:17:28.054409+03
187	305	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-26 09:17:35.296653+03
188	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"identifier_used": "teacher_9324"}	2026-09-26 09:18:07.114017+03
189	305	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-09-26 09:18:14.308613+03
190	305	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-09-26 09:18:19.800144+03
191	305	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-09-26 09:18:32.072226+03
192	305	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 15, "exam_name": "Final Examination 2026", "student_id": 53, "filename": "pexels-anntarazevich-5598288.jpg", "file_size": 286969}	2026-09-26 09:21:50.884542+03
638	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "absent_count": 1}	2026-11-13 12:47:36.870135+03
194	370	EXAM_CREATED	SUCCESS	\N	\N	{"exam_id": 21, "name": "TEST_Monthly_Exam_October", "exam_type": "MONTHLY", "class_id": 1, "deadline": "2026-11-21 11:43:16.826589"}	2026-10-22 11:43:16.9027+03
195	304	TEACHER_CREATED_EXAM	SUCCESS	\N	\N	{"exam_id": 22, "exam_name": "TEST_Teacher_Quiz1", "class_id": 1, "subject_id": 1, "teacher_id": 1, "academic_year": "2025-2026"}	2026-10-22 11:43:17.076353+03
196	370	EXAM_DEADLINE_EXTENDED	SUCCESS	\N	\N	{"exam_id": 21, "exam_name": "TEST_Monthly_Exam_October", "previous_deadline": "2026-10-20T08:43:17.154378+00:00", "new_deadline": "2026-11-05T08:43:17.194912+00:00", "reason": "School term extended by 2 weeks due to national holidays"}	2026-10-22 11:43:17.221463+03
197	370	EXAM_CREATED	SUCCESS	\N	\N	{"exam_id": 23, "name": "TEST_Monthly_Exam_October", "exam_type": "MONTHLY", "class_id": 1, "deadline": "2026-11-21 11:43:40.982992"}	2026-10-22 11:43:41.022736+03
198	304	TEACHER_CREATED_EXAM	SUCCESS	\N	\N	{"exam_id": 24, "exam_name": "TEST_Teacher_Quiz1", "class_id": 1, "subject_id": 1, "teacher_id": 1, "academic_year": "2025-2026"}	2026-10-22 11:43:41.123058+03
199	370	EXAM_DEADLINE_EXTENDED	SUCCESS	\N	\N	{"exam_id": 23, "exam_name": "TEST_Monthly_Exam_October", "previous_deadline": "2026-10-20T08:43:41.178007+00:00", "new_deadline": "2026-11-05T08:43:41.209208+00:00", "reason": "School term extended by 2 weeks due to national holidays"}	2026-10-22 11:43:41.23109+03
200	370	EXAM_CREATED	SUCCESS	\N	\N	{"exam_id": 25, "name": "TEST_Monthly_Exam_October", "exam_type": "MONTHLY", "class_id": 1, "deadline": "2026-11-21 11:44:07.448145"}	2026-10-22 11:44:07.476671+03
201	304	TEACHER_CREATED_EXAM	SUCCESS	\N	\N	{"exam_id": 26, "exam_name": "TEST_Teacher_Quiz1", "class_id": 1, "subject_id": 1, "teacher_id": 1, "academic_year": "2025-2026"}	2026-10-22 11:44:07.565522+03
202	370	EXAM_DEADLINE_EXTENDED	SUCCESS	\N	\N	{"exam_id": 25, "exam_name": "TEST_Monthly_Exam_October", "previous_deadline": "2026-10-20T08:44:07.610829+00:00", "new_deadline": "2026-11-05T08:44:07.635243+00:00", "reason": "School term extended by 2 weeks due to national holidays"}	2026-10-22 11:44:07.654573+03
203	370	EXAM_SUBMISSIONS_REOPENED	SUCCESS	\N	\N	{"exam_id": 25, "exam_name": "TEST_Monthly_Exam_October", "reopened_at": "2026-10-22T08:44:07.691170+00:00", "new_deadline": "2026-10-29T08:44:07.688517+00:00", "reason": "Authorized reopening for mark verification"}	2026-10-22 11:44:07.697075+03
204	1	LOGIN_SUCCESS	SUCCESS	\N	\N	{"roles": ["ADMIN"]}	2026-10-22 17:28:09.497463+03
205	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "nonexistent_user"}	2026-10-22 17:29:41.636576+03
206	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-22 17:29:41.941448+03
207	367	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 12, "target_type": "SINGLE_STUDENT", "created_count": 1, "skipped_count": 0, "total_billed": 15.0}	2026-10-22 17:29:52.055294+03
208	367	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 13, "target_type": "CLASS", "created_count": 24, "skipped_count": 0, "total_billed": 480.0}	2026-10-22 17:29:52.255419+03
209	367	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 14, "target_type": "SINGLE_STUDENT", "created_count": 1, "skipped_count": 0, "total_billed": 30.0}	2026-10-22 17:29:52.33568+03
210	367	FEE_INVOICES_ASSIGNED	SUCCESS	\N	\N	{"fee_structure_id": 14, "target_type": "SINGLE_STUDENT", "created_count": 0, "skipped_count": 1, "total_billed": 0}	2026-10-22 17:29:52.359242+03
211	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 7, "receipt_number": "RCT-2026-000005", "student_id": 3, "student_fee_id": 58, "amount": 20.0, "method": "EVC_PLUS", "reference": "EVC-TXN-101"}	2026-10-22 17:29:52.404446+03
212	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 8, "receipt_number": "RCT-2026-000008", "student_id": 3, "student_fee_id": 58, "amount": 30.0, "method": "CASH", "reference": "CASH-REC-102"}	2026-10-22 17:29:52.477414+03
213	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 9, "receipt_number": "RCT-2026-000009", "student_id": 3, "student_fee_id": 60, "amount": 35.0, "method": "EDAHAB", "reference": "ED-7788"}	2026-10-22 17:29:52.566907+03
214	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 10, "receipt_number": "RCT-2026-000010", "student_id": 3, "student_fee_id": 62, "amount": 60.0, "method": "CASH", "reference": null}	2026-10-22 17:29:52.741532+03
215	367	FEE_PAYMENT_CANCELLED	SUCCESS	\N	\N	{"payment_id": 10, "receipt_number": "RCT-2026-000010", "reason": "Mistaken Entry"}	2026-10-22 17:29:52.789631+03
216	367	FEE_NOTIFICATIONS_SENT	SUCCESS	\N	\N	{"target_type": "ALL_OUTSTANDING", "sent_count": 21, "missing_phone_count": 0, "already_notified_count": 0}	2026-10-22 17:29:53.170084+03
217	367	FEE_STRUCTURE_CREATED	SUCCESS	\N	\N	{"structure_id": 20, "name": "Fee To Delete", "amount": 50.0, "frequency": "Monthly", "academic_year": "2026/2027", "education_level": null}	2026-10-22 17:29:53.263127+03
218	367	FEE_STRUCTURE_DELETED	SUCCESS	\N	\N	{"structure_id": 20, "name": "Fee To Delete"}	2026-10-22 17:29:53.28176+03
219	367	FEE_PAYMENT_RECORDED	SUCCESS	\N	\N	{"payment_id": 11, "receipt_number": "RCT-2026-000011", "student_id": 3, "student_fee_id": 63, "amount": 35.0, "method": "EDAHAB", "reference": "ED-7788"}	2026-10-22 17:31:11.860403+03
220	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-10-22 17:34:08.996901+03
221	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"students_974A8C.xlsx\\", \\"class_id\\": 18, \\"class_name\\": \\"Grade 4 - E\\", \\"academic_year\\": \\"2026/2027\\", \\"imported_count\\": 10, \\"skipped_count\\": 0}"	2026-10-22 17:34:09.350004+03
222	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-10-22 17:34:19.329153+03
223	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-10-22 17:35:07.646798+03
224	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 22, "name": "Grade 8 - 74", "code": "G8-E2E-749B3D", "division": "PRIMARY", "level": "Grade 8", "section": "74"}	2026-10-22 17:35:07.707263+03
225	1	SUBJECT_CREATED	SUCCESS	\N	\N	{"subject_id": 29, "name": "Somali Literature 749B3D", "code": "SOM-749B3D", "division": "ALL"}	2026-10-22 17:35:07.729882+03
226	1	TEACHER_CREATED	SUCCESS	\N	\N	{"teacher_id": 7, "teacher_number": "TCH-749B3D", "has_portal": true}	2026-10-22 17:35:08.085574+03
227	1	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 7, "class_id": 22, "subject_id": 29}	2026-10-22 17:35:08.130029+03
228	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 114, "admission_number": "ADM-749B3D", "class_id": 22}	2026-10-22 17:35:08.402289+03
229	380	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["TEACHER"]}	2026-10-22 17:35:08.66832+03
230	381	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["STUDENT"]}	2026-10-22 17:35:09.113931+03
231	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-10-22 17:36:26.234033+03
232	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-10-22 17:44:28.594808+03
233	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-10-22 17:47:04.169867+03
234	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-10-22 18:07:15.225449+03
235	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-10-22 18:09:44.809748+03
236	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-10-22 18:14:16.410464+03
237	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-10-22 18:22:02.758522+03
238	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"identifier_used": "admin3"}	2026-10-22 18:22:05.890575+03
239	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"identifier_used": "admin3"}	2026-10-22 18:22:13.828839+03
240	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"identifier_used": "admin3"}	2026-10-22 18:22:31.089684+03
241	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Python-urllib/3.14	{"roles": ["ADMIN"]}	2026-10-22 18:23:54.639119+03
242	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Python-urllib/3.14	{"roles": ["ADMIN"]}	2026-10-22 18:24:02.537072+03
243	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-10-22 18:24:44.663216+03
244	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-10-22 18:24:59.758345+03
245	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"identifier_used": "garasle"}	2026-10-22 18:25:29.835556+03
246	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-10-22 18:26:09.39945+03
247	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-10-22 18:26:32.840701+03
248	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"identifier_used": "garasle"}	2026-10-22 18:26:44.926415+03
249	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-10-22 18:27:15.509081+03
250	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-10-22 18:27:39.586178+03
251	377	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"identifier_used": "alimire8x14@gmail.com"}	2026-10-22 18:27:49.789602+03
252	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"identifier_used": "garasle"}	2026-10-22 18:28:03.874594+03
253	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-22 18:47:12.937582+03
254	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "admin_updated"}	2026-10-22 18:47:29.008524+03
255	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-22 18:47:42.403869+03
256	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-22 18:51:47.941445+03
257	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-22 18:51:48.887467+03
258	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-10-22 22:29:55.702668+03
259	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-10-22 22:30:01.115383+03
260	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Python-urllib/3.14	{"roles": ["ADMIN"]}	2026-10-22 23:43:39.912799+03
261	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Python-urllib/3.14	{"roles": ["ADMIN"]}	2026-10-22 23:43:45.401398+03
639	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 12:47:37.290781+03
640	1	SAVE_TEACHER_ATTENDANCE	SUCCESS	\N	\N	{"date": "2026-11-13", "academic_year": "2026/2027", "total_teachers_marked": 16, "present_count": 4, "absent_count": 4, "late_count": 4, "on_leave_count": 4}	2026-11-13 12:47:37.432273+03
264	373	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 17, "class_id": 3, "subject_id": 4, "completed": 8, "expected": 8}	2026-10-23 00:38:40.408199+03
676	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 1, "class_id": 1, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 13:54:36.877342+03
677	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 2, "academic_year": "2028-2029"}	2026-11-13 13:54:36.929304+03
678	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 2, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 13:54:36.959239+03
268	373	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 17, "class_id": 3, "subject_id": 4, "completed": 8, "expected": 8}	2026-10-23 00:38:41.074395+03
679	\N	TEACHER_ASSIGNMENT_UPDATED	SUCCESS	\N	\N	{"assignment_id": 67, "teacher_id": 1, "class_id": 1, "subject_id": 1}	2026-11-13 13:54:37.047507+03
680	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 1, "academic_year": "2029-2030"}	2026-11-13 13:54:37.100216+03
681	\N	TEACHER_ASSIGNMENT_REMOVED	SUCCESS	\N	\N	{"assignment_id": 70}	2026-11-13 13:54:37.117583+03
272	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 00:46:41.788584+03
726	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 16:09:38.758858+03
727	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:09:39.576548+03
275	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 00:46:43.225378+03
641	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 12:59:06.052586+03
642	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 12:59:08.264065+03
279	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 00:47:09.119803+03
644	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 12:59:10.169974+03
682	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 15:51:17.689976+03
282	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 00:49:07.665979+03
683	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 15:51:17.731387+03
731	419	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 91, "class_name": "Class 1 DynFilter", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-11", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:09:40.737824+03
285	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 00:49:08.427166+03
290	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 00:50:13.045527+03
293	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 00:50:13.665369+03
297	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-23 00:50:40.814829+03
298	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 00:50:41.429873+03
299	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 00:50:42.125494+03
300	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 00:50:42.242042+03
301	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 00:50:42.351952+03
302	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 00:50:42.474264+03
303	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 00:50:42.586148+03
304	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 00:50:42.699511+03
306	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:01:54.198394+03
309	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:01:55.814067+03
314	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:04:27.23508+03
317	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:04:28.946484+03
322	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:05:10.526674+03
325	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:05:12.201323+03
643	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "late_count": 0, "absent_count": 1}	2026-11-13 12:59:09.256214+03
684	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 15:51:34.580577+03
330	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:06:11.904262+03
686	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 15:51:35.730108+03
687	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 15:51:36.190135+03
333	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:06:13.593383+03
732	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 16:20:15.041338+03
733	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 38, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-11-13 16:20:15.440701+03
735	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 38, "class_id": 1, "day": "Saturday"}	2026-11-13 16:20:15.701554+03
769	\N	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2026/2027", "periods_generated": 23}	2026-11-13 18:10:59.84421+03
338	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:20:02.031737+03
341	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 02:20:03.706471+03
345	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Python-urllib/3.14	{"roles": ["ADMIN"]}	2026-10-23 21:59:52.028766+03
347	373	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 17, "class_id": 3, "subject_id": 4, "completed": 10, "expected": 10}	2026-10-23 22:36:15.395573+03
351	373	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 17, "class_id": 3, "subject_id": 4, "completed": 10, "expected": 10}	2026-10-23 22:36:16.682387+03
354	\N	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "garasle"}	2026-10-23 22:43:08.286773+03
355	\N	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "garasle"}	2026-10-23 22:43:08.722208+03
356	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-23 23:30:59.062142+03
357	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 2, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-10-23 23:30:59.475647+03
358	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 2, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-10-23 23:30:59.577851+03
359	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 2, "class_id": 1, "day": "Saturday"}	2026-10-23 23:30:59.601791+03
360	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-23 23:31:17.38812+03
361	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 26, "name": "Grade 7 - 12D7", "code": "G7-FF058C", "division": "PRIMARY", "level": "Grade 7", "section": "12D7"}	2026-10-23 23:31:17.463261+03
362	1	CLASS_UPDATED	SUCCESS	\N	\N	{"class_id": 26, "name": "Grade 7 - 12D7", "division": "PRIMARY"}	2026-10-23 23:31:17.514735+03
363	1	CLASS_DEACTIVATED	SUCCESS	\N	\N	{"class_id": 26, "name": "Grade 7 - 12D7"}	2026-10-23 23:31:17.554453+03
364	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-23 23:31:17.825566+03
365	1	SUBJECT_CREATED	SUCCESS	\N	\N	{"subject_id": 36, "name": "General Science SCI-B0E14A", "code": "SCI-B0E14A", "division": "ALL"}	2026-10-23 23:31:17.86782+03
366	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-23 23:31:18.137918+03
367	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 27, "name": "Grade 7 - C7AB2C", "code": "CONF-C7AB2C", "division": "PRIMARY", "level": "Grade 7", "section": "C7AB2C"}	2026-10-23 23:31:18.149038+03
368	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 3, "class_id": 27, "subject_id": 13, "day": "Friday", "time": "06:00:00-07:00:00"}	2026-10-23 23:31:18.409272+03
369	1	CLASS_DEACTIVATED	SUCCESS	\N	\N	{"class_id": 27, "name": "Grade 7 - C7AB2C"}	2026-10-23 23:31:18.431227+03
370	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-23 23:31:18.720464+03
371	366	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-10-23 23:31:19.169833+03
372	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 23:31:19.63943+03
373	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-10-23 23:31:20.250778+03
374	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-10-23", "present_count": 20, "absent_count": 1}	2026-10-23 23:31:20.755762+03
375	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-10-23 23:31:21.16829+03
376	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-23 23:31:21.581595+03
377	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 23:31:21.61461+03
378	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 23:31:21.64675+03
379	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 23:31:21.677977+03
380	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 23:31:21.709906+03
381	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 23:31:21.741727+03
383	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 23:31:21.807613+03
645	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:02:13.650633+03
646	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 13:02:13.736752+03
685	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "late_count": 0, "absent_count": 1}	2026-11-13 15:51:35.405709+03
688	419	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 91, "class_name": "Class 1 DynFilter", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-11", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 15:51:36.370379+03
734	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 38, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-11-13 16:20:15.679025+03
770	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2026/2027", "periods_generated": 23}	2026-11-13 18:18:50.972311+03
382	\N	LOGIN_FAILED	FAILURE	testclient	testclient	{"identifier_used": "student.mustaf"}	2026-10-23 23:31:21.773851+03
647	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:02:37.012123+03
385	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 23:31:33.533588+03
648	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 13:02:37.063179+03
649	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:02:39.632774+03
388	392	TEACHER_SAVE_DRAFT	SUCCESS	\N	\N	{"exam_id": 27, "class_id": 25, "subject_id": 34, "completed": 3, "expected": 3}	2026-10-23 23:31:34.148811+03
650	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 13:02:42.086378+03
689	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:00:28.38263+03
392	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-23 23:31:46.26235+03
393	1	CLASS_CREATED	SUCCESS	\N	\N	{"class_id": 28, "name": "Grade 7 - 89045F", "code": "CONF-89045F", "division": "PRIMARY", "level": "Grade 7", "section": "89045F"}	2026-10-23 23:31:46.343742+03
394	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 4, "class_id": 28, "subject_id": 13, "day": "Friday", "time": "06:00:00-07:00:00"}	2026-10-23 23:31:46.619848+03
395	1	CLASS_DEACTIVATED	SUCCESS	\N	\N	{"class_id": 28, "name": "Grade 7 - 89045F"}	2026-10-23 23:31:46.642314+03
396	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:00:04.357487+03
397	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 5, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-10-24 00:00:04.709225+03
398	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 5, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-10-24 00:00:04.804694+03
399	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 5, "class_id": 1, "day": "Saturday"}	2026-10-24 00:00:04.818401+03
400	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:00:37.996238+03
401	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:02:09.128707+03
402	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:05:24.389322+03
403	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:06:41.549674+03
404	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 3}	2026-10-24 00:06:41.926429+03
405	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:07:05.959991+03
406	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 3}	2026-10-24 00:07:06.42725+03
407	1	TIMETABLE_PUBLISHED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "published_count": 3}	2026-10-24 00:07:06.464632+03
408	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:07:17.368018+03
409	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 12, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-10-24 00:07:17.717025+03
410	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 12, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-10-24 00:07:17.821944+03
411	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 12, "class_id": 1, "day": "Saturday"}	2026-10-24 00:07:17.835441+03
412	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:07:18.069525+03
413	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 3}	2026-10-24 00:07:18.213599+03
414	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:08:19.209841+03
415	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 16, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-10-24 00:08:19.54579+03
416	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 16, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-10-24 00:08:19.66007+03
417	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 16, "class_id": 1, "day": "Saturday"}	2026-10-24 00:08:19.694425+03
418	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:08:19.926878+03
419	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 3}	2026-10-24 00:08:20.071216+03
420	1	TIMETABLE_PUBLISHED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "published_count": 3}	2026-10-24 00:08:20.101506+03
421	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:33:11.596595+03
422	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 20, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-10-24 00:33:12.799109+03
423	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 20, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-10-24 00:33:13.144962+03
424	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 20, "class_id": 1, "day": "Saturday"}	2026-10-24 00:33:13.197836+03
425	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-24 00:33:14.072732+03
426	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 3}	2026-10-24 00:33:14.488156+03
427	1	TIMETABLE_PUBLISHED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "published_count": 3}	2026-10-24 00:33:14.584096+03
428	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-25 00:22:52.339236+03
429	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 3}	2026-10-25 00:22:52.845261+03
430	1	TIMETABLE_PUBLISHED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "published_count": 3}	2026-10-25 00:22:52.901547+03
431	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-25 00:23:05.204505+03
432	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 27, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-10-25 00:23:05.744917+03
433	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 27, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-10-25 00:23:05.909696+03
434	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 27, "class_id": 1, "day": "Saturday"}	2026-10-25 00:23:05.929465+03
435	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-25 00:38:17.501448+03
436	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 3}	2026-10-25 00:38:18.039101+03
437	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-25 00:39:39.998721+03
438	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 3}	2026-10-25 00:39:41.228949+03
439	1	TIMETABLE_PUBLISHED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "published_count": 6}	2026-10-25 00:39:41.329808+03
440	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-25 00:39:58.136099+03
441	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 34, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-10-25 00:39:59.227356+03
442	1	TIMETABLE_SLOT_UPDATED	SUCCESS	\N	\N	{"slot_id": 34, "day": "Saturday", "time": "14:00:00-15:00:00"}	2026-10-25 00:39:59.566598+03
443	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 34, "class_id": 1, "day": "Saturday"}	2026-10-25 00:39:59.606453+03
444	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-25 00:40:56.147419+03
445	1	TIMETABLE_SLOT_MOVED	SUCCESS	\N	\N	{"slot_id": 35, "class_id": 1, "new_day": "Monday", "new_time": "08:00:00-08:45:00"}	2026-10-25 00:40:57.235007+03
446	1	TIMETABLE_SLOTS_SWAPPED	SUCCESS	\N	\N	{"slot_id_1": 35, "slot_id_2": 36, "class_id": 1}	2026-10-25 00:40:57.418008+03
447	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.9711	{"roles": ["ADMIN"]}	2026-10-27 06:57:43.233789+03
448	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-27 08:25:57.215996+03
449	364	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-10-27 08:25:58.20816+03
450	399	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["STUDENT"]}	2026-10-27 08:26:00.352689+03
451	1	STUDENT_CLASS_CHANGED	SUCCESS	\N	\N	{"student_id": 150, "admission_number": "ADM-PROM-5-1-3300", "old_class": "Form 5", "new_class": "Form 6", "academic_year": "2027/2028", "reason": "Annual Academic Progression"}	2026-10-27 08:26:00.722224+03
452	1	BULK_CLASS_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0036", "source_year": "2026/2027", "target_year": "2027/2028", "total_promoted": 14, "total_graduated": 3}	2026-10-27 08:26:01.28515+03
453	1	PROMOTION_BATCH_ROLLED_BACK	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0036", "batch_id": 91, "restored_count": 17}	2026-10-27 08:26:03.307592+03
454	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-27 08:26:59.376955+03
455	1	CLASS_LEVEL_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0037", "from_class": "Grade 4 - A", "to_class": "Grade 5 - A", "promoted": 4}	2026-10-27 08:27:00.410972+03
456	1	INDIVIDUAL_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0038", "student_id": 128, "action": "PROMOTE", "target_class": "Grade 5 - B"}	2026-10-27 08:27:00.643637+03
457	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-27 08:29:20.114266+03
458	1	CLASS_LEVEL_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0039", "from_class": "Grade 4 - A", "to_class": "Grade 5 - A", "promoted": 0}	2026-10-27 08:29:21.081577+03
459	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-27 08:30:49.509012+03
460	1	CLASS_LEVEL_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0038", "from_class": "Grade 4 - A", "to_class": "Grade 5 - A", "promoted": 4}	2026-10-27 08:30:50.785858+03
461	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-27 08:31:41.033745+03
462	1	CLASS_LEVEL_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0038", "from_class": "Grade 4 - A", "to_class": "Grade 5 - A", "promoted": 4}	2026-10-27 08:31:42.434633+03
463	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-27 08:32:21.712184+03
464	1	CLASS_LEVEL_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0038", "from_class": "Grade 4 - A", "to_class": "Grade 5 - A", "promoted": 4}	2026-10-27 08:32:23.10349+03
465	1	INDIVIDUAL_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0040", "student_id": 128, "action": "PROMOTE", "target_class": "Grade 5 - B"}	2026-10-27 08:32:23.302224+03
466	1	PROMOTION_BATCH_ROLLED_BACK	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0040", "batch_id": 102, "restored_count": 1}	2026-10-27 08:32:24.906888+03
467	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-10-27 08:32:40.345474+03
468	364	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-10-27 08:32:41.34771+03
469	400	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["STUDENT"]}	2026-10-27 08:32:43.397248+03
470	1	STUDENT_CLASS_CHANGED	SUCCESS	\N	\N	{"student_id": 168, "admission_number": "ADM-PROM-5-1-6582", "old_class": "Form 5", "new_class": "Form 6", "academic_year": "2027/2028", "reason": "Annual Academic Progression"}	2026-10-27 08:32:43.681654+03
471	1	BULK_CLASS_PROMOTION_EXECUTED	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0042", "source_year": "2026/2027", "target_year": "2027/2028", "total_promoted": 14, "total_graduated": 3}	2026-10-27 08:32:44.322441+03
472	1	PROMOTION_BATCH_ROLLED_BACK	SUCCESS	\N	\N	{"batch_code": "PROM-2027-0042", "batch_id": 104, "restored_count": 17}	2026-10-27 08:32:46.647125+03
473	401	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 174, "admission_number": "ADM-TEST-PHOTO-4ED88D", "class_id": null}	2026-11-11 08:58:33.869857+03
474	401	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 174, "admission_number": "ADM-TEST-PHOTO-4ED88D", "photo_filename": "profile.jpg", "photo_size": 825, "photo_mime_type": "image/jpeg"}	2026-11-11 08:58:34.036408+03
475	401	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 174, "admission_number": "ADM-TEST-PHOTO-4ED88D", "photo_filename": "updated_photo.png", "photo_size": 287, "photo_mime_type": "image/png"}	2026-11-11 08:58:34.122198+03
476	401	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 174, "admission_number": "ADM-TEST-PHOTO-4ED88D", "photo_filename": "photo.webp", "photo_size": 106, "photo_mime_type": "image/webp"}	2026-11-11 08:58:34.312323+03
477	401	STUDENT_PHOTO_REMOVED	SUCCESS	\N	\N	{"student_id": 174, "admission_number": "ADM-TEST-PHOTO-4ED88D"}	2026-11-11 08:58:34.328104+03
478	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"students_import_54AB0.xlsx\\", \\"class_id\\": 32, \\"class_name\\": \\"Grade 2 - B\\", \\"academic_year\\": \\"2026/2027\\", \\"imported_count\\": 10, \\"skipped_count\\": 0}"	2026-11-11 08:58:58.43862+03
479	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"dup_test.xlsx\\", \\"class_id\\": 32, \\"class_name\\": \\"Grade 2 - B\\", \\"academic_year\\": \\"2026/2027\\", \\"imported_count\\": 10, \\"skipped_count\\": 0}"	2026-11-11 08:58:58.794156+03
480	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"dup_test.xlsx\\", \\"class_id\\": 32, \\"class_name\\": \\"Grade 2 - B\\", \\"academic_year\\": \\"2026/2027\\", \\"imported_count\\": 0, \\"skipped_count\\": 10}"	2026-11-11 08:58:58.858291+03
481	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"form1_students.xlsx\\", \\"class_id\\": 16, \\"class_name\\": \\"Form 1 - B\\", \\"academic_year\\": \\"2026/2027\\", \\"imported_count\\": 2, \\"skipped_count\\": 0}"	2026-11-11 08:58:59.058982+03
482	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"admin_route_test.xlsx\\", \\"class_id\\": 32, \\"class_name\\": \\"Grade 2 - B\\", \\"academic_year\\": \\"2026/2027\\", \\"imported_count\\": 2, \\"skipped_count\\": 0}"	2026-11-11 08:58:59.240446+03
483	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:13:21.871233+03
484	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 199, "admission_number": "ADM-P1-87945F", "class_id": null}	2026-11-11 09:13:21.907026+03
485	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:14:06.267092+03
486	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 200, "admission_number": "ADM-P1-43EC8C", "class_id": null}	2026-11-11 09:14:06.314954+03
487	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 200, "admission_number": "ADM-P1-43EC8C", "photo_filename": "mustafe_avatar.jpg", "photo_size": 885, "photo_mime_type": "image/jpeg"}	2026-11-11 09:14:06.385001+03
488	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 201, "admission_number": "ADM-P2-E55629", "class_id": null}	2026-11-11 09:14:06.399278+03
489	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"students.xlsx\\", \\"class_id\\": 50, \\"class_name\\": \\"Grade 1 - A\\", \\"academic_year\\": \\"2027/2028\\", \\"imported_count\\": 1, \\"skipped_count\\": 0}"	2026-11-11 09:14:06.845789+03
491	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 200, "admission_number": "ADM-P1-43EC8C", "photo_filename": "mustafe_new.webp", "photo_size": 114, "photo_mime_type": "image/webp"}	2026-11-11 09:14:07.002893+03
492	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:14:07.336815+03
651	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "late_count": 0, "absent_count": 1}	2026-11-13 13:02:43.16255+03
690	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 16:00:28.9978+03
736	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 16:20:24.863459+03
737	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 12}	2026-11-13 16:20:25.281839+03
738	1	TIMETABLE_PUBLISHED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "published_count": 12}	2026-11-13 16:20:25.318527+03
739	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 16:20:25.590882+03
771	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-13 18:20:24.757536+03
490	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 202, "admission_number": "ADM-IMP-4BD181", "photo_filename": "guled_photo.png", "photo_size": 344, "photo_mime_type": "image/png"}	2026-11-11 09:14:06.896848+03
493	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:15:53.950683+03
494	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 203, "admission_number": "ADM-P1-3AF07B", "class_id": null}	2026-11-11 09:15:54.083992+03
495	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 203, "admission_number": "ADM-P1-3AF07B", "photo_filename": "mustafe_avatar.jpg", "photo_size": 885, "photo_mime_type": "image/jpeg"}	2026-11-11 09:15:54.151533+03
496	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 204, "admission_number": "ADM-P2-9CD02F", "class_id": null}	2026-11-11 09:15:54.1629+03
497	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:16:04.554239+03
498	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:16:14.738085+03
499	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:18:40.358985+03
500	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 205, "admission_number": "ADM-P1-3DE770", "class_id": null}	2026-11-11 09:18:40.411895+03
501	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 205, "admission_number": "ADM-P1-3DE770", "photo_filename": "mustafe_avatar.jpg", "photo_size": 885, "photo_mime_type": "image/jpeg"}	2026-11-11 09:18:40.47092+03
502	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 206, "admission_number": "ADM-P2-60E577", "class_id": null}	2026-11-11 09:18:40.48125+03
503	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:19:18.899051+03
504	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 207, "admission_number": "ADM-P1-260B99", "class_id": null}	2026-11-11 09:19:18.919521+03
505	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 207, "admission_number": "ADM-P1-260B99", "photo_filename": "mustafe_avatar.jpg", "photo_size": 885, "photo_mime_type": "image/jpeg"}	2026-11-11 09:19:18.954824+03
506	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 208, "admission_number": "ADM-P2-03B8F2", "class_id": null}	2026-11-11 09:19:18.966827+03
507	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:19:43.334568+03
508	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 209, "admission_number": "ADM-P1-DF97D9", "class_id": null}	2026-11-11 09:19:43.34717+03
509	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 209, "admission_number": "ADM-P1-DF97D9", "photo_filename": "mustafe_avatar.jpg", "photo_size": 885, "photo_mime_type": "image/jpeg"}	2026-11-11 09:19:43.38177+03
510	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 210, "admission_number": "ADM-P2-6CCF03", "class_id": null}	2026-11-11 09:19:43.392313+03
511	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:20:20.343157+03
512	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 211, "admission_number": "ADM-P1-665539", "class_id": null}	2026-11-11 09:20:20.354601+03
513	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 211, "admission_number": "ADM-P1-665539", "photo_filename": "mustafe_avatar.jpg", "photo_size": 885, "photo_mime_type": "image/jpeg"}	2026-11-11 09:20:20.386584+03
514	1	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 212, "admission_number": "ADM-P2-CA4E71", "class_id": null}	2026-11-11 09:20:20.395636+03
515	1	STUDENT_BULK_IMPORT	SUCCESS	\N	\N	"{\\"file_name\\": \\"students.xlsx\\", \\"class_id\\": 50, \\"class_name\\": \\"Grade 1 - A\\", \\"academic_year\\": \\"2027/2028\\", \\"imported_count\\": 1, \\"skipped_count\\": 0}"	2026-11-11 09:20:20.755678+03
516	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 213, "admission_number": "ADM-IMP-15804B", "photo_filename": "guled_photo.png", "photo_size": 344, "photo_mime_type": "image/png"}	2026-11-11 09:20:20.790182+03
517	1	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 211, "admission_number": "ADM-P1-665539", "photo_filename": "mustafe_new.webp", "photo_size": 114, "photo_mime_type": "image/webp"}	2026-11-11 09:20:20.883071+03
518	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-11 09:20:21.116883+03
519	401	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 214, "admission_number": "ADM-TEST-PHOTO-90C2DA", "class_id": null}	2026-11-11 09:20:46.568173+03
520	401	STUDENT_REGISTERED	SUCCESS	\N	\N	{"student_id": 215, "admission_number": "ADM-TEST-PHOTO-EAA099", "class_id": null}	2026-11-11 09:21:12.715662+03
521	401	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 215, "admission_number": "ADM-TEST-PHOTO-EAA099", "photo_filename": "profile.jpg", "photo_size": 825, "photo_mime_type": "image/jpeg"}	2026-11-11 09:21:12.808938+03
522	401	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 215, "admission_number": "ADM-TEST-PHOTO-EAA099", "photo_filename": "updated_photo.png", "photo_size": 287, "photo_mime_type": "image/png"}	2026-11-11 09:21:12.885284+03
523	401	STUDENT_PHOTO_UPLOADED	SUCCESS	\N	\N	{"student_id": 215, "admission_number": "ADM-TEST-PHOTO-EAA099", "photo_filename": "photo.webp", "photo_size": 106, "photo_mime_type": "image/webp"}	2026-11-11 09:21:12.974012+03
524	401	STUDENT_PHOTO_REMOVED	SUCCESS	\N	\N	{"student_id": 215, "admission_number": "ADM-TEST-PHOTO-EAA099"}	2026-11-11 09:21:12.993418+03
525	401	EXAM_CREATED	SUCCESS	\N	\N	{"exam_id": 31, "name": "Grade 5 Mid-Term Science Exam 2026", "exam_type": "MID_TERM", "class_id": 37, "deadline": "None"}	2026-11-11 09:59:31.155804+03
526	401	EXAM_DELETED	SUCCESS	\N	\N	{"exam_id": 31, "name": "Grade 5 Mid-Term Science Exam 2026"}	2026-11-11 10:02:08.38942+03
527	401	EXAM_CREATED	SUCCESS	\N	\N	{"exam_id": 32, "name": "Grade 5 Mid-Term Science Exam 2026", "exam_type": "MID_TERM", "class_id": 37, "deadline": "None"}	2026-11-11 10:02:08.454795+03
528	401	EXAM_PUBLISHED	SUCCESS	\N	\N	{"exam_id": 32, "name": "Grade 5 Mid-Term Science Exam 2026", "academic_year": "2026/2027", "class_id": 37, "class_name": "Grade 5 - A", "subject_id": 37}	2026-11-11 10:02:08.630289+03
529	401	EXAM_UNPUBLISHED	SUCCESS	\N	\N	{"exam_id": 32, "name": "Grade 5 Mid-Term Science Exam 2026", "academic_year": "2026/2027", "class_id": 37, "class_name": "Grade 5 - A", "subject_id": 37}	2026-11-11 10:02:08.765874+03
530	401	EXAM_PUBLISHED	SUCCESS	\N	\N	{"exam_id": 32, "name": "Grade 5 Mid-Term Science Exam 2026", "academic_year": "2026/2027", "class_id": 37, "class_name": "Grade 5 - A", "subject_id": 37}	2026-11-11 10:02:08.805965+03
531	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"identifier_used": "muna400"}	2026-11-11 12:51:08.308555+03
532	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"identifier_used": "muna400"}	2026-11-11 12:51:12.335753+03
533	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-11 16:06:15.409701+03
534	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-11 16:52:10.930684+03
535	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-11 16:53:15.010264+03
536	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-11 16:54:48.240277+03
537	\N	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "garasle"}	2026-11-12 08:56:15.357325+03
538	\N	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "garasle"}	2026-11-12 08:56:16.129735+03
652	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 13:02:44.110264+03
653	1	SAVE_TEACHER_ATTENDANCE	SUCCESS	\N	\N	{"date": "2026-11-13", "academic_year": "2026/2027", "total_teachers_marked": 18, "present_count": 5, "absent_count": 5, "late_count": 4, "on_leave_count": 4}	2026-11-13 13:02:44.493128+03
691	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:01:51.591121+03
692	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 16:01:51.612208+03
693	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:01:52.714865+03
697	419	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 91, "class_name": "Class 1 DynFilter", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-11", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:01:54.049929+03
740	1	TIMETABLE_SLOT_MOVED	SUCCESS	\N	\N	{"slot_id": 51, "class_id": 1, "new_day": "Monday", "new_time": "08:00:00-08:45:00"}	2026-11-13 16:20:25.786364+03
741	1	TIMETABLE_SLOTS_SWAPPED	SUCCESS	\N	\N	{"slot_id_1": 51, "slot_id_2": 52, "class_id": 1}	2026-11-13 16:20:25.868873+03
772	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2026/2027", "periods_generated": 23}	2026-11-13 18:20:25.072669+03
539	\N	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "garasle"}	2026-11-12 08:56:16.799882+03
540	1	LOGIN_FAILED	FAILURE	127.0.0.1	Python-urllib/3.14	{"identifier_used": "admin"}	2026-11-12 09:23:10.632378+03
541	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Python-urllib/3.14	{"identifier_used": "garasle"}	2026-11-12 09:23:11.087252+03
542	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Python-urllib/3.14	{"identifier_used": "garasle"}	2026-11-12 09:23:11.509889+03
543	309	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["STUDENT"]}	2026-11-12 10:02:05.047515+03
544	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-12 10:02:05.315996+03
545	309	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["STUDENT"]}	2026-11-12 10:04:27.788425+03
546	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-12 10:04:28.043509+03
547	309	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["STUDENT"]}	2026-11-12 10:13:51.265682+03
548	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-12 10:13:51.570786+03
549	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-12 11:04:26.225078+03
550	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-12 11:33:54.601229+03
551	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-12 11:36:24.0488+03
552	1	LOGIN_SUCCESS	SUCCESS	\N	\N	{"roles": ["ADMIN"]}	2026-11-12 12:27:52.995577+03
553	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.9711	{"roles": ["ADMIN"]}	2026-11-12 12:28:45.179199+03
554	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-12 12:43:31.332002+03
555	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-12 12:47:24.163324+03
556	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-12 18:28:47.722043+03
557	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-12 18:41:12.737509+03
558	377	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-11-12 18:53:06.074872+03
559	377	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-12 19:10:23.186769+03
560	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-12 19:10:35.956062+03
561	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-12 19:10:49.511097+03
562	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Python-urllib/3.14	{"roles": ["ADMIN"]}	2026-11-13 08:08:00.873785+03
563	377	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["TEACHER"]}	2026-11-13 08:08:40.232445+03
564	1	SUBJECT_ASSIGNED_TO_CLASS	SUCCESS	\N	\N	{"subject_id": 7, "class_id": 31, "academic_year": "2026/2027"}	2026-11-13 08:46:45.14622+03
565	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "absent_count": 0}	2026-11-13 09:58:02.823421+03
566	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "absent_count": 0}	2026-11-13 09:58:58.89662+03
567	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 09:59:27.249922+03
568	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "absent_count": 1}	2026-11-13 09:59:30.067577+03
569	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 09:59:31.058211+03
570	1	SAVE_TEACHER_ATTENDANCE	SUCCESS	\N	\N	{"date": "2026-11-13", "academic_year": "2026/2027", "total_teachers_marked": 11, "present_count": 3, "absent_count": 3, "late_count": 3, "on_leave_count": 2}	2026-11-13 10:17:15.34291+03
571	1	SAVE_TEACHER_ATTENDANCE	SUCCESS	\N	\N	{"date": "2026-11-13", "academic_year": "2026/2027", "total_teachers_marked": 11, "present_count": 3, "absent_count": 3, "late_count": 3, "on_leave_count": 2}	2026-11-13 10:17:55.497293+03
572	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "absent_count": 0}	2026-11-13 10:18:24.640961+03
573	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 10:18:26.772059+03
574	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "absent_count": 1}	2026-11-13 10:18:27.802827+03
575	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 10:18:28.717586+03
576	1	SAVE_TEACHER_ATTENDANCE	SUCCESS	\N	\N	{"date": "2026-11-13", "academic_year": "2026/2027", "total_teachers_marked": 11, "present_count": 3, "absent_count": 3, "late_count": 3, "on_leave_count": 2}	2026-11-13 10:33:48.552741+03
577	1	SAVE_TEACHER_ATTENDANCE	SUCCESS	\N	\N	{"date": "2026-11-13", "academic_year": "2026/2027", "total_teachers_marked": 4, "present_count": 1, "absent_count": 1, "late_count": 1, "on_leave_count": 1}	2026-11-13 10:34:55.752015+03
578	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-13 10:43:33.474526+03
579	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-13 10:43:44.8645+03
580	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-13 10:43:59.744119+03
581	1	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-13 10:44:05.44788+03
582	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"identifier_used": "admin@somroyal.com"}	2026-11-13 10:44:13.140443+03
583	\N	LOGIN_FAILED	FAILURE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"identifier_used": "superadmin@somroyal.com"}	2026-11-13 10:44:20.798752+03
584	410	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["SUPER_ADMIN"]}	2026-11-13 10:49:40.486396+03
585	410	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	{"roles": ["SUPER_ADMIN"]}	2026-11-13 10:52:38.588385+03
586	410	LOGOUT	SUCCESS	\N	\N	{"message": "Logged out successfully"}	2026-11-13 10:56:58.792608+03
587	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 1, "class_id": 1, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:09:14.78803+03
588	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 2, "academic_year": "2028-2029"}	2026-11-13 12:09:14.808913+03
589	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 2, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:09:14.819039+03
590	\N	TEACHER_ASSIGNMENT_UPDATED	SUCCESS	\N	\N	{"assignment_id": 38, "teacher_id": 1, "class_id": 1, "subject_id": 1}	2026-11-13 12:09:14.847984+03
591	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 1, "academic_year": "2029-2030"}	2026-11-13 12:09:14.868823+03
592	\N	TEACHER_ASSIGNMENT_REMOVED	SUCCESS	\N	\N	{"assignment_id": 41}	2026-11-13 12:09:14.875311+03
593	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 1, "class_id": 1, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:09:31.474192+03
594	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 2, "academic_year": "2028-2029"}	2026-11-13 12:09:31.496892+03
595	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 2, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:09:31.506621+03
596	\N	TEACHER_ASSIGNMENT_UPDATED	SUCCESS	\N	\N	{"assignment_id": 42, "teacher_id": 1, "class_id": 1, "subject_id": 1}	2026-11-13 12:09:31.531241+03
597	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 1, "academic_year": "2029-2030"}	2026-11-13 12:09:31.549182+03
598	\N	TEACHER_ASSIGNMENT_REMOVED	SUCCESS	\N	\N	{"assignment_id": 45}	2026-11-13 12:09:31.554418+03
599	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 12:15:20.238788+03
600	1	TEACHER_CREATED	SUCCESS	\N	\N	{"teacher_id": 17, "teacher_number": "TCH-959610", "has_portal": true}	2026-11-13 12:15:20.761028+03
601	1	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 17, "class_id": 29, "subject_id": 13, "academic_year": "2025-2026"}	2026-11-13 12:15:20.898008+03
602	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 1, "class_id": 1, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:15:21.333099+03
603	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 2, "academic_year": "2028-2029"}	2026-11-13 12:15:21.347094+03
604	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 2, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:15:21.354239+03
605	\N	TEACHER_ASSIGNMENT_UPDATED	SUCCESS	\N	\N	{"assignment_id": 47, "teacher_id": 1, "class_id": 1, "subject_id": 1}	2026-11-13 12:15:21.376589+03
606	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 1, "academic_year": "2029-2030"}	2026-11-13 12:15:21.390849+03
607	\N	TEACHER_ASSIGNMENT_REMOVED	SUCCESS	\N	\N	{"assignment_id": 50}	2026-11-13 12:15:21.394765+03
608	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 12:15:36.510918+03
609	1	TEACHER_CREATED	SUCCESS	\N	\N	{"teacher_id": 18, "teacher_number": "TCH-239150", "has_portal": true}	2026-11-13 12:15:37.116523+03
610	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 12:16:00.087798+03
611	1	TEACHER_CREATED	SUCCESS	\N	\N	{"teacher_id": 19, "teacher_number": "TCH-206739", "has_portal": true}	2026-11-13 12:16:00.698089+03
612	1	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 19, "class_id": 29, "subject_id": 13, "academic_year": "2028-2029"}	2026-11-13 12:16:00.755242+03
613	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 12:16:31.290213+03
614	1	TEACHER_CREATED	SUCCESS	\N	\N	{"teacher_id": 20, "teacher_number": "TCH-899666", "has_portal": true}	2026-11-13 12:16:31.960324+03
615	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 1, "class_id": 1, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:16:32.35875+03
616	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 2, "academic_year": "2028-2029"}	2026-11-13 12:16:32.373585+03
617	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 2, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:16:32.381139+03
618	\N	TEACHER_ASSIGNMENT_UPDATED	SUCCESS	\N	\N	{"assignment_id": 52, "teacher_id": 1, "class_id": 1, "subject_id": 1}	2026-11-13 12:16:32.400663+03
619	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 1, "academic_year": "2029-2030"}	2026-11-13 12:16:32.414911+03
620	\N	TEACHER_ASSIGNMENT_REMOVED	SUCCESS	\N	\N	{"assignment_id": 55}	2026-11-13 12:16:32.41933+03
621	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 12:16:54.569649+03
622	1	TEACHER_CREATED	SUCCESS	\N	\N	{"teacher_id": 21, "teacher_number": "TCH-398544", "has_portal": true}	2026-11-13 12:16:55.33131+03
623	1	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 21, "class_id": 29, "subject_id": 13, "academic_year": "2054-2055"}	2026-11-13 12:16:55.386335+03
624	1	TEACHER_STATUS_CHANGED	SUCCESS	\N	\N	{"teacher_id": 21, "new_status": "INACTIVE", "reason": "Sabbatical leave"}	2026-11-13 12:16:55.440147+03
625	1	TEACHER_STATUS_CHANGED	SUCCESS	\N	\N	{"teacher_id": 21, "new_status": "ACTIVE", "reason": "Resumed duties"}	2026-11-13 12:16:55.461373+03
654	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:16:53.107985+03
655	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 13:16:53.143606+03
656	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:16:54.066174+03
657	304	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 13:16:54.788679+03
659	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 13:16:55.501967+03
660	1	SAVE_TEACHER_ATTENDANCE	SUCCESS	\N	\N	{"date": "2026-11-13", "academic_year": "2026/2027", "total_teachers_marked": 18, "present_count": 5, "absent_count": 5, "late_count": 4, "on_leave_count": 4}	2026-11-13 13:16:55.672415+03
694	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "late_count": 0, "absent_count": 1}	2026-11-13 16:01:53.05858+03
695	304	UPLOAD_EXAM_PAPER	SUCCESS	\N	\N	{"exam_id": 1, "exam_name": "Final math Examination (Grade 1 - A)", "student_id": 3, "filename": "student_exam_sheet.pdf", "file_size": 48}	2026-11-13 16:01:53.366687+03
696	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:01:53.820475+03
742	\N	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "admin@somroyal.edu.so"}	2026-11-13 16:24:33.899673+03
745	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 54, "class_id": 50, "subject_id": 13, "day": "Sunday", "time": "08:00:00-08:45:00"}	2026-11-13 16:24:57.044544+03
751	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 55, "class_id": 50, "subject_id": 13, "day": "Saturday", "time": "08:00:00-09:00:00"}	2026-11-13 16:29:02.010979+03
773	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 18:21:08.925615+03
774	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "periods_generated": 12}	2026-11-13 18:21:09.42044+03
658	304	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 1, "subject_name": "math", "date": "2026-11-13", "present_count": 20, "late_count": 0, "absent_count": 1}	2026-11-13 13:16:55.18567+03
698	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:03:27.329163+03
699	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 5, "subject_name": "English", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 16:03:27.448843+03
700	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-12", "present_count": 0, "late_count": 1, "absent_count": 0}	2026-11-13 16:03:27.532486+03
701	424	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:03:27.879661+03
743	1	LOGIN_FAILED	FAILURE	127.0.0.1	python-requests/2.34.2	{"identifier_used": "admin@hawlwadaagschool.edu.so"}	2026-11-13 16:24:34.748618+03
744	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-13 16:24:56.833669+03
755	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-13 16:35:26.580223+03
758	1	TIMETABLE_AUTO_GENERATED	SUCCESS	\N	\N	{"class_id": 29, "academic_year": "2026/2027", "periods_generated": 5}	2026-11-13 16:36:13.793439+03
775	1	TIMETABLE_PUBLISHED	SUCCESS	\N	\N	{"class_id": 1, "academic_year": "2025-2026", "published_count": 12}	2026-11-13 18:21:09.467335+03
661	417	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 13:51:24.715927+03
662	418	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 1, "class_name": "Grade 1 - A", "subject_id": 4, "subject_name": "Mathematics", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 13:51:24.804856+03
702	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-13", "present_count": 1, "late_count": 0, "absent_count": 0}	2026-11-13 16:03:44.186868+03
703	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 5, "subject_name": "English", "date": "2026-11-13", "present_count": 0, "late_count": 0, "absent_count": 1}	2026-11-13 16:03:44.299482+03
704	424	SAVE_ATTENDANCE	SUCCESS	\N	\N	{"class_id": 94, "class_name": "Class 1 LockTest", "subject_id": 13, "subject_name": "Arabic", "date": "2026-11-12", "present_count": 0, "late_count": 1, "absent_count": 0}	2026-11-13 16:03:44.395592+03
705	424	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["TEACHER"]}	2026-11-13 16:03:44.945668+03
746	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	python-requests/2.34.2	{"roles": ["ADMIN"]}	2026-11-13 16:26:00.912568+03
747	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-13 16:27:35.071449+03
752	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-13 16:29:23.795797+03
754	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 56, "class_id": 29, "subject_id": 13, "day": "Monday", "time": "11:15:00-12:00:00"}	2026-11-13 16:34:17.585664+03
756	1	LOGIN_SUCCESS	SUCCESS	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	{"roles": ["ADMIN"]}	2026-11-13 16:36:03.292352+03
776	1	LOGIN_SUCCESS	SUCCESS	testclient	testclient	{"roles": ["ADMIN"]}	2026-11-13 18:21:20.135307+03
777	1	TIMETABLE_SLOT_CREATED	SUCCESS	\N	\N	{"slot_id": 160, "class_id": 1, "subject_id": 13, "day": "Saturday", "time": "13:00:00-14:00:00"}	2026-11-13 18:21:20.563122+03
779	1	TIMETABLE_SLOT_DELETED	SUCCESS	\N	\N	{"slot_id": 160, "class_id": 1, "day": "Saturday"}	2026-11-13 18:21:20.828219+03
781	1	TIMETABLE_SLOT_MOVED	SUCCESS	\N	\N	{"slot_id": 161, "class_id": 1, "new_day": "Monday", "new_time": "08:00:00-08:45:00"}	2026-11-13 18:21:21.223331+03
782	1	TIMETABLE_SLOTS_SWAPPED	SUCCESS	\N	\N	{"slot_id_1": 161, "slot_id_2": 162, "class_id": 1}	2026-11-13 18:21:21.290286+03
626	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 1, "class_id": 1, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:17:36.089428+03
627	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 2, "academic_year": "2028-2029"}	2026-11-13 12:17:36.107678+03
628	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 2, "subject_id": 1, "academic_year": "2028-2029"}	2026-11-13 12:17:36.116223+03
629	\N	TEACHER_ASSIGNMENT_UPDATED	SUCCESS	\N	\N	{"assignment_id": 57, "teacher_id": 1, "class_id": 1, "subject_id": 1}	2026-11-13 12:17:36.139372+03
630	\N	TEACHER_ASSIGNMENT_CREATED	SUCCESS	\N	\N	{"teacher_id": 2, "class_id": 1, "subject_id": 1, "academic_year": "2029-2030"}	2026-11-13 12:17:36.157201+03
631	\N	TEACHER_ASSIGNMENT_REMOVED	SUCCESS	\N	\N	{"assignment_id": 60}	2026-11-13 12:17:36.162045+03
\.


--
-- Data for Name: class_promotion_batches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.class_promotion_batches (id, batch_code, source_academic_year, target_academic_year, promotion_type, status, total_promoted, total_graduated, total_skipped, reason, created_by_id, created_at) FROM stdin;
1	PROM-2027-0001	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-17 14:06:15.856304+03
2	PROM-2027-0002	2026/2027	2027/2028	BULK_PROMOTION	COMPLETED	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-17 14:06:16.229562+03
65	PROM-2027-0027	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-19 08:46:48.793109+03
4	PROM-2027-0003	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-17 14:06:56.276201+03
29	PROM-2027-0013	2026/2027	2027/2028	INDIVIDUAL_CHANGE	ROLLED_BACK	1	0	0	Annual Academic Progression	1	2026-09-17 15:01:22.385742+03
76	PROM-2027-0030	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-19 12:07:17.57207+03
5	PROM-2027-0004	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-17 14:06:56.679745+03
9	PROM-2027-0005	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-17 14:16:04.961751+03
34	PROM-2027-0015	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-17 15:45:59.805725+03
66	PROM-2027-0028	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-19 08:46:48.929407+03
70	PROM-2026-0002	2026/2027	2026/2027	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Mid-term level reassignment to Grade 8-A	1	2026-09-19 10:41:51.438735+03
71	PROM-2026-0003	2026/2027	2026/2027	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Mid-term level reassignment to Grade 8-A	1	2026-09-19 10:42:23.081302+03
10	PROM-2027-0006	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-17 14:16:05.412626+03
14	PROM-2027-0007	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-17 14:16:25.926368+03
72	PROM-2026-0004	2026/2027	2026/2027	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Mid-term level reassignment to Grade 8-A	1	2026-09-19 10:42:35.731354+03
73	PROM-2026-0005	2026/2027	2026/2027	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Mid-term level reassignment to Grade 8-A	1	2026-09-19 10:42:46.659662+03
74	PROM-2026-0006	2026/2027	2026/2027	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Mid-term level reassignment to Grade 8-A	1	2026-09-19 10:43:40.879776+03
75	PROM-2027-0029	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-19 12:07:17.491319+03
15	PROM-2027-0008	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-17 14:16:26.364092+03
19	PROM-2027-0009	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-17 14:16:47.800725+03
85	PROM-2027-0033	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-21 01:43:09.232972+03
55	PROM-2027-0023	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-18 21:27:06.598365+03
20	PROM-2027-0010	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-17 14:16:48.307835+03
24	PROM-2027-0011	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-17 14:45:26.998395+03
80	PROM-2027-0031	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-20 03:56:07.884739+03
86	PROM-2027-0034	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-21 01:43:09.397427+03
25	PROM-2027-0012	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-17 14:45:27.197917+03
81	PROM-2027-0032	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-20 03:56:08.251604+03
30	PROM-2027-0014	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-17 15:01:22.582129+03
90	PROM-2027-0035	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-10-27 08:26:00.697049+03
35	PROM-2027-0016	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-17 15:46:00.070175+03
39	PROM-2027-0017	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-18 01:29:38.51677+03
91	PROM-2027-0036	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-10-27 08:26:01.177121+03
40	PROM-2027-0018	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-18 01:29:38.793479+03
44	PROM-2026-0001	2025-2026	2026/2027	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Individual Class Change	1	2026-09-18 01:48:09.482489+03
45	PROM-2027-0019	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-18 20:27:51.154843+03
97	PROM-2027-0039	2026/2027	2027/2028	CLASS_LEVEL	COMPLETED	0	0	0	Test Single Class Promotion Grade 4A	1	2026-10-27 08:29:21.052854+03
46	PROM-2027-0020	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-18 20:27:51.426013+03
50	PROM-2027-0021	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-18 21:11:17.4262+03
101	PROM-2027-0038	2026/2027	2027/2028	CLASS_LEVEL	COMPLETED	4	0	0	Test Single Class Promotion Grade 4A	1	2026-10-27 08:32:23.021967+03
102	PROM-2027-0040	2026/2027	2027/2028	INDIVIDUAL_PROMOTION	ROLLED_BACK	1	0	0	Individual student promotion test	1	2026-10-27 08:32:23.296383+03
103	PROM-2027-0041	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-10-27 08:32:43.672483+03
51	PROM-2027-0022	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-18 21:11:17.676368+03
56	PROM-2027-0024	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-18 21:27:06.897846+03
60	PROM-2027-0025	2026/2027	2027/2028	INDIVIDUAL_CHANGE	COMPLETED	1	0	0	Annual Academic Progression	1	2026-09-18 23:00:15.382801+03
61	PROM-2027-0026	2026/2027	2027/2028	BULK_PROMOTION	COMPLETED	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-09-18 23:00:15.559107+03
104	PROM-2027-0042	2026/2027	2027/2028	BULK_PROMOTION	ROLLED_BACK	14	3	0	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	1	2026-10-27 08:32:44.201264+03
\.


--
-- Data for Name: class_promotion_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.class_promotion_records (id, batch_id, student_id, from_class_id, to_class_id, from_enrollment_id, to_enrollment_id, source_academic_year, target_academic_year, action, status, reason, created_at) FROM stdin;
1	85	90	13	14	90	96	2026/2027	2027/2028	PROMOTED	COMPLETED	Annual Academic Progression	2026-09-21 01:43:09.269118+03
19	90	150	78	79	174	180	2026/2027	2027/2028	PROMOTED	COMPLETED	Annual Academic Progression	2026-10-27 08:26:00.725167+03
16	86	93	14	\N	93	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.477095+03
17	86	94	14	\N	94	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.477096+03
18	86	95	14	\N	95	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.477096+03
2	86	78	9	10	78	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.415652+03
3	86	79	9	10	79	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.420912+03
4	86	80	9	10	80	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.426532+03
5	86	81	10	11	81	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.430154+03
6	86	82	10	11	82	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.433474+03
7	86	83	10	11	83	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.437832+03
8	86	84	11	12	84	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.441868+03
9	86	85	11	12	85	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.446118+03
10	86	86	11	12	86	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.45067+03
11	86	87	12	13	87	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.45377+03
12	86	88	12	13	88	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.456879+03
13	86	89	12	13	89	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.462163+03
14	86	91	13	14	91	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.465356+03
15	86	92	13	14	92	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-09-21 01:43:09.477091+03
34	91	153	79	\N	177	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.295563+03
35	91	154	79	\N	178	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.295566+03
36	91	155	79	\N	179	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.295567+03
20	91	138	74	75	162	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.19094+03
21	91	139	74	75	163	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.196149+03
22	91	140	74	75	164	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.204631+03
23	91	141	75	76	165	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.211197+03
24	91	142	75	76	166	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.217619+03
25	91	143	75	76	167	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.232464+03
26	91	144	76	77	168	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.237985+03
27	91	145	76	77	169	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.244053+03
28	91	146	76	77	170	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.251232+03
29	91	147	77	78	171	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.256856+03
30	91	148	77	78	172	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.263887+03
31	91	149	77	78	173	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.271946+03
32	91	151	78	79	175	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.279199+03
33	91	152	78	79	176	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:26:01.295539+03
54	102	128	36	59	152	\N	2026/2027	2027/2028	PROMOTE	ROLLED_BACK	Individual student promotion test	2026-10-27 08:32:23.303513+03
55	103	168	84	85	225	231	2026/2027	2027/2028	PROMOTED	COMPLETED	Annual Academic Progression	2026-10-27 08:32:43.684676+03
50	101	121	35	58	145	208	2026/2027	2027/2028	PROMOTE	COMPLETED	Test Single Class Promotion Grade 4A	2026-10-27 08:32:23.075295+03
51	101	122	35	58	146	209	2026/2027	2027/2028	PROMOTE	COMPLETED	Test Single Class Promotion Grade 4A	2026-10-27 08:32:23.089955+03
52	101	123	35	58	147	210	2026/2027	2027/2028	PROMOTE	COMPLETED	Test Single Class Promotion Grade 4A	2026-10-27 08:32:23.100067+03
53	101	124	35	58	148	211	2026/2027	2027/2028	PROMOTE	COMPLETED	Test Single Class Promotion Grade 4A	2026-10-27 08:32:23.109317+03
70	104	171	85	\N	228	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.331419+03
71	104	172	85	\N	229	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.331421+03
72	104	173	85	\N	230	\N	2026/2027	2027/2028	GRADUATED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.331422+03
56	104	156	80	81	213	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.219407+03
57	104	157	80	81	214	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.228161+03
58	104	158	80	81	215	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.237001+03
59	104	159	81	82	216	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.245561+03
60	104	160	81	82	217	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.25122+03
61	104	161	81	82	218	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.261659+03
62	104	162	82	83	219	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.266946+03
63	104	163	82	83	220	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.274071+03
64	104	164	82	83	221	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.283374+03
65	104	165	83	84	222	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.290013+03
66	104	166	83	84	223	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.298478+03
67	104	167	83	84	224	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.307696+03
68	104	169	84	85	226	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.315709+03
69	104	170	84	85	227	\N	2026/2027	2027/2028	PROMOTED	ROLLED_BACK	Annual Hawlwadaag School Promotion 2026/2027 -> 2027/2028	2026-10-27 08:32:44.331412+03
\.


--
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classes (id, name, code, section, academic_year, capacity, description, status, created_at, updated_at, division, level) FROM stdin;
1	Grade 1 - A	G1-A-2025	A	2025-2026	40	\N	ACTIVE	2026-09-20 05:35:21.785103+03	2026-09-20 05:35:21.785113+03	PRIMARY	Grade 1
2	Form 4 - B	F4-B-2025	B	2025-2026	40	\N	ACTIVE	2026-09-20 05:47:42.154111+03	2026-09-20 05:47:42.154117+03	SECONDARY	Form 4
7	Grade 7 - DELTA STREAM	CLS-590859	DELTA STREAM	2025-2026	35	Secondary school Grade 10 Delta stream	ACTIVE	2026-09-21 01:43:06.745623+03	2026-09-21 01:43:06.745627+03	PRIMARY	Grade 7
8	Grade 7 - A	CLS-590859-362	A	2025-2026	30	\N	ACTIVE	2026-09-21 01:43:06.763102+03	2026-09-21 01:43:06.763106+03	PRIMARY	Grade 7
15	Grade 7 - C	G7-C-2026	C	2026/2027	45	Grade 7 Stream C	ACTIVE	2026-09-21 01:43:09.948298+03	2026-09-21 01:43:09.948304+03	PRIMARY	Grade 7
16	Form 1 - B	F1-B-2026	B	2026/2027	40	Form 1 Stream B	ACTIVE	2026-09-21 01:43:09.968139+03	2026-09-21 01:43:09.968143+03	SECONDARY	Form 1
17	Grade 7 - A	G7-A-2026	A	2026/2027	40	\N	ACTIVE	2026-09-21 01:43:10.003309+03	2026-09-21 01:43:10.003312+03	PRIMARY	Grade 7
18	Grade 4 - E	G4-E-2026	E	2026/2027	35	\N	ACTIVE	2026-09-21 01:43:10.029944+03	2026-09-21 01:43:10.029949+03	PRIMARY	Grade 4
20	Grade 7 - F1C1	G7-717934	F1C1	2026/2027	35	Test grade section	INACTIVE	2026-09-21 01:43:21.964528+03	2026-09-21 01:43:22.011979+03	PRIMARY	Grade 7
21	Grade 7 - E638D7	CONF-E638D7	E638D7	2026/2027	30	\N	INACTIVE	2026-09-21 01:43:22.707896+03	2026-09-21 01:43:22.886085+03	PRIMARY	Grade 7
22	Grade 8 - 74	G8-E2E-749B3D	74	2025-2026	45	\N	ACTIVE	2026-10-22 17:35:07.701055+03	2026-10-22 17:35:07.701059+03	PRIMARY	Grade 8
26	Grade 7 - 12D7	G7-FF058C	12D7	2026/2027	35	Test grade section	INACTIVE	2026-10-23 23:31:17.45498+03	2026-10-23 23:31:17.552239+03	PRIMARY	Grade 7
27	Grade 7 - C7AB2C	CONF-C7AB2C	C7AB2C	2026/2027	30	\N	INACTIVE	2026-10-23 23:31:18.14668+03	2026-10-23 23:31:18.428775+03	PRIMARY	Grade 7
28	Grade 7 - 89045F	CONF-89045F	89045F	2026/2027	30	\N	INACTIVE	2026-10-23 23:31:46.336861+03	2026-10-23 23:31:46.640123+03	PRIMARY	Grade 7
3	Grade 7-Test	G7-TST	\N	2026-2027	40	\N	ACTIVE	2026-09-21 01:42:57.990023+03	2026-10-27 08:14:22.918462+03	PRIMARY	Grade 7
4	Grade 8-Test	G8-TST	\N	2026-2027	40	\N	ACTIVE	2026-09-21 01:42:57.995034+03	2026-10-27 08:14:22.918476+03	PRIMARY	Grade 8
5	Grade 7-12Subj	G7-12S	\N	2026-2027	40	\N	ACTIVE	2026-09-21 01:42:59.30028+03	2026-10-27 08:14:22.918481+03	PRIMARY	Grade 7
6	Grade 9-Test-CF	G9-TCF	\N	2026-2027	40	\N	ACTIVE	2026-09-21 01:43:04.360121+03	2026-10-27 08:14:22.918484+03	PRIMARY	Grade 9
9	Form 1	F1-PROM-5369	Stream A	2026/2027	40	\N	ACTIVE	2026-09-21 01:43:08.011184+03	2026-10-27 08:14:22.925356+03	SECONDARY	Form 1
10	Form 2	F2-PROM-5369	Stream A	2026/2027	40	\N	ACTIVE	2026-09-21 01:43:08.015308+03	2026-10-27 08:14:22.925365+03	SECONDARY	Form 2
11	Form 3	F3-PROM-5369	Stream A	2026/2027	40	\N	ACTIVE	2026-09-21 01:43:08.018532+03	2026-10-27 08:14:22.925369+03	SECONDARY	Form 3
12	Form 4	F4-PROM-5369	Stream A	2026/2027	40	\N	ACTIVE	2026-09-21 01:43:08.02096+03	2026-10-27 08:14:22.925372+03	SECONDARY	Form 4
13	Form 5	F5-PROM-5369	Stream A	2026/2027	40	\N	ACTIVE	2026-09-21 01:43:08.024013+03	2026-10-27 08:14:22.925375+03	SECONDARY	Form 5
14	Form 6	F6-PROM-5369	Stream A	2026/2027	40	\N	ACTIVE	2026-09-21 01:43:08.026544+03	2026-10-27 08:14:22.925378+03	SECONDARY	Form 6
19	Grade 8	G8-A	\N	2025-2026	40	\N	ACTIVE	2026-09-21 01:43:21.521377+03	2026-10-27 08:14:22.929877+03	PRIMARY	Grade 8
25	Form 3-Alpha WF	F3-ALPHA-WF	A	2026/2027	40	\N	ACTIVE	2026-10-23 00:42:41.385969+03	2026-10-27 08:14:22.929884+03	SECONDARY	Form 3
29	Grade 1 - A	G1-A-2026-2027	A	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136458+03	2026-10-27 08:14:23.136466+03	PRIMARY	Grade 1
30	Grade 1 - B	G1-B-2026-2027	B	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136471+03	2026-10-27 08:14:23.136473+03	PRIMARY	Grade 1
31	Grade 2 - A	G2-A-2026-2027	A	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136475+03	2026-10-27 08:14:23.136476+03	PRIMARY	Grade 2
32	Grade 2 - B	G2-B-2026-2027	B	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136478+03	2026-10-27 08:14:23.13648+03	PRIMARY	Grade 2
33	Grade 3 - A	G3-A-2026-2027	A	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136482+03	2026-10-27 08:14:23.136483+03	PRIMARY	Grade 3
34	Grade 3 - B	G3-B-2026-2027	B	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136485+03	2026-10-27 08:14:23.136487+03	PRIMARY	Grade 3
35	Grade 4 - A	G4-A-2026-2027	A	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136488+03	2026-10-27 08:14:23.13649+03	PRIMARY	Grade 4
36	Grade 4 - B	G4-B-2026-2027	B	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136492+03	2026-10-27 08:14:23.136493+03	PRIMARY	Grade 4
37	Grade 5 - A	G5-A-2026-2027	A	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136495+03	2026-10-27 08:14:23.136497+03	PRIMARY	Grade 5
38	Grade 5 - B	G5-B-2026-2027	B	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136499+03	2026-10-27 08:14:23.1365+03	PRIMARY	Grade 5
39	Grade 6 - A	G6-A-2026-2027	A	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136502+03	2026-10-27 08:14:23.136503+03	PRIMARY	Grade 6
40	Grade 6 - B	G6-B-2026-2027	B	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136505+03	2026-10-27 08:14:23.136507+03	PRIMARY	Grade 6
41	Grade 7 - B	G7-B-2026-2027	B	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136509+03	2026-10-27 08:14:23.13651+03	PRIMARY	Grade 7
42	Grade 8 - A	G8-A-2026-2027	A	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136512+03	2026-10-27 08:14:23.136513+03	PRIMARY	Grade 8
43	Grade 8 - B	G8-B-2026-2027	B	2026/2027	45	\N	ACTIVE	2026-10-27 08:14:23.136516+03	2026-10-27 08:14:23.136517+03	PRIMARY	Grade 8
44	Form 1 - A	F1-A-2026-2027	A	2026/2027	40	\N	ACTIVE	2026-10-27 08:14:23.136519+03	2026-10-27 08:14:23.136521+03	SECONDARY	Form 1
45	Form 2 - A	F2-A-2026-2027	A	2026/2027	40	\N	ACTIVE	2026-10-27 08:14:23.136523+03	2026-10-27 08:14:23.136524+03	SECONDARY	Form 2
46	Form 2 - B	F2-B-2026-2027	B	2026/2027	40	\N	ACTIVE	2026-10-27 08:14:23.136526+03	2026-10-27 08:14:23.136528+03	SECONDARY	Form 2
47	Form 3 - B	F3-B-2026-2027	B	2026/2027	40	\N	ACTIVE	2026-10-27 08:14:23.136529+03	2026-10-27 08:14:23.136531+03	SECONDARY	Form 3
48	Form 4 - A	F4-A-2026-2027	A	2026/2027	40	\N	ACTIVE	2026-10-27 08:14:23.136533+03	2026-10-27 08:14:23.136534+03	SECONDARY	Form 4
49	Form 4 - B	F4-B-2026-2027	B	2026/2027	40	\N	ACTIVE	2026-10-27 08:14:23.136536+03	2026-10-27 08:14:23.136537+03	SECONDARY	Form 4
50	Grade 1 - A	G1-A-2027-2028	A	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136539+03	2026-10-27 08:14:23.136541+03	PRIMARY	Grade 1
51	Grade 1 - B	G1-B-2027-2028	B	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136542+03	2026-10-27 08:14:23.136544+03	PRIMARY	Grade 1
52	Grade 2 - A	G2-A-2027-2028	A	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136546+03	2026-10-27 08:14:23.136547+03	PRIMARY	Grade 2
53	Grade 2 - B	G2-B-2027-2028	B	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136549+03	2026-10-27 08:14:23.13655+03	PRIMARY	Grade 2
54	Grade 3 - A	G3-A-2027-2028	A	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136553+03	2026-10-27 08:14:23.136554+03	PRIMARY	Grade 3
55	Grade 3 - B	G3-B-2027-2028	B	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136556+03	2026-10-27 08:14:23.136558+03	PRIMARY	Grade 3
56	Grade 4 - A	G4-A-2027-2028	A	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.13656+03	2026-10-27 08:14:23.136561+03	PRIMARY	Grade 4
57	Grade 4 - B	G4-B-2027-2028	B	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136563+03	2026-10-27 08:14:23.136564+03	PRIMARY	Grade 4
58	Grade 5 - A	G5-A-2027-2028	A	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136566+03	2026-10-27 08:14:23.136567+03	PRIMARY	Grade 5
59	Grade 5 - B	G5-B-2027-2028	B	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136569+03	2026-10-27 08:14:23.13657+03	PRIMARY	Grade 5
60	Grade 6 - A	G6-A-2027-2028	A	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136571+03	2026-10-27 08:14:23.136573+03	PRIMARY	Grade 6
61	Grade 6 - B	G6-B-2027-2028	B	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136575+03	2026-10-27 08:14:23.136579+03	PRIMARY	Grade 6
62	Grade 7 - A	G7-A-2027-2028	A	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.13658+03	2026-10-27 08:14:23.136582+03	PRIMARY	Grade 7
63	Grade 7 - B	G7-B-2027-2028	B	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136583+03	2026-10-27 08:14:23.136584+03	PRIMARY	Grade 7
64	Grade 8 - A	G8-A-2027-2028	A	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136586+03	2026-10-27 08:14:23.136587+03	PRIMARY	Grade 8
65	Grade 8 - B	G8-B-2027-2028	B	2027/2028	45	\N	ACTIVE	2026-10-27 08:14:23.136589+03	2026-10-27 08:14:23.13659+03	PRIMARY	Grade 8
66	Form 1 - A	F1-A-2027-2028	A	2027/2028	40	\N	ACTIVE	2026-10-27 08:14:23.136592+03	2026-10-27 08:14:23.136593+03	SECONDARY	Form 1
67	Form 1 - B	F1-B-2027-2028	B	2027/2028	40	\N	ACTIVE	2026-10-27 08:14:23.136595+03	2026-10-27 08:14:23.136596+03	SECONDARY	Form 1
68	Form 2 - A	F2-A-2027-2028	A	2027/2028	40	\N	ACTIVE	2026-10-27 08:14:23.136598+03	2026-10-27 08:14:23.136599+03	SECONDARY	Form 2
69	Form 2 - B	F2-B-2027-2028	B	2027/2028	40	\N	ACTIVE	2026-10-27 08:14:23.136601+03	2026-10-27 08:14:23.136602+03	SECONDARY	Form 2
70	Form 3 - A	F3-A-2027-2028	A	2027/2028	40	\N	ACTIVE	2026-10-27 08:14:23.136604+03	2026-10-27 08:14:23.136605+03	SECONDARY	Form 3
71	Form 3 - B	F3-B-2027-2028	B	2027/2028	40	\N	ACTIVE	2026-10-27 08:14:23.136607+03	2026-10-27 08:14:23.136608+03	SECONDARY	Form 3
72	Form 4 - A	F4-A-2027-2028	A	2027/2028	40	\N	ACTIVE	2026-10-27 08:14:23.136609+03	2026-10-27 08:14:23.136611+03	SECONDARY	Form 4
73	Form 4 - B	F4-B-2027-2028	B	2027/2028	40	\N	ACTIVE	2026-10-27 08:14:23.136612+03	2026-10-27 08:14:23.136614+03	SECONDARY	Form 4
74	Form 1	F1-PROM-3300	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:25:58.228178+03	2026-10-27 08:25:58.228184+03	PRIMARY	\N
75	Form 2	F2-PROM-3300	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:25:58.252107+03	2026-10-27 08:25:58.252115+03	PRIMARY	\N
76	Form 3	F3-PROM-3300	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:25:58.258193+03	2026-10-27 08:25:58.2582+03	PRIMARY	\N
77	Form 4	F4-PROM-3300	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:25:58.264327+03	2026-10-27 08:25:58.264334+03	PRIMARY	\N
78	Form 5	F5-PROM-3300	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:25:58.269368+03	2026-10-27 08:25:58.269374+03	PRIMARY	\N
79	Form 6	F6-PROM-3300	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:25:58.274547+03	2026-10-27 08:25:58.274553+03	PRIMARY	\N
80	Form 1	F1-PROM-6582	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:32:41.365689+03	2026-10-27 08:32:41.365698+03	PRIMARY	\N
81	Form 2	F2-PROM-6582	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:32:41.383203+03	2026-10-27 08:32:41.383212+03	PRIMARY	\N
82	Form 3	F3-PROM-6582	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:32:41.389192+03	2026-10-27 08:32:41.389203+03	PRIMARY	\N
83	Form 4	F4-PROM-6582	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:32:41.395069+03	2026-10-27 08:32:41.395077+03	PRIMARY	\N
84	Form 5	F5-PROM-6582	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:32:41.400322+03	2026-10-27 08:32:41.400331+03	PRIMARY	\N
85	Form 6	F6-PROM-6582	Stream A	2026/2027	40	\N	ACTIVE	2026-10-27 08:32:41.406687+03	2026-10-27 08:32:41.406696+03	PRIMARY	\N
87	Form Master Class A	FMA-2026	FM1	2026/2027	40	\N	ACTIVE	2026-11-13 08:48:05.316716+03	2026-11-13 08:48:05.31672+03	PRIMARY	Grade 7
88	Form Master Class B	FMB-2026	FM2	2026/2027	40	\N	ACTIVE	2026-11-13 08:48:05.322183+03	2026-11-13 08:48:05.322188+03	PRIMARY	Grade 7
89	Form Master Class C	FMC-2026	FM3	2026/2027	40	\N	ACTIVE	2026-11-13 08:48:05.324941+03	2026-11-13 08:48:05.324944+03	SECONDARY	Form 1
90	Form Master Class D	FMD-2026	FM4	2026/2027	40	\N	ACTIVE	2026-11-13 08:48:05.327404+03	2026-11-13 08:48:05.327406+03	SECONDARY	Form 2
91	Class 1 DynFilter	C1-DYN	\N	2026/2027	40	\N	ACTIVE	2026-11-13 13:51:15.186618+03	2026-11-13 13:51:15.186633+03	PRIMARY	\N
92	Class 2 DynFilter	C2-DYN	\N	2026/2027	40	\N	ACTIVE	2026-11-13 13:51:15.212141+03	2026-11-13 13:51:15.212156+03	PRIMARY	\N
93	Class Past DynFilter	CP-DYN	\N	2025/2026	40	\N	ACTIVE	2026-11-13 13:51:15.21916+03	2026-11-13 13:51:15.219173+03	PRIMARY	\N
94	Class 1 LockTest	C1-LOCK	\N	2026/2027	40	\N	ACTIVE	2026-11-13 16:03:25.601131+03	2026-11-13 16:03:25.601135+03	PRIMARY	\N
\.


--
-- Data for Name: exam_deadline_extensions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exam_deadline_extensions (id, exam_id, previous_deadline, new_deadline, reason, extended_by_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: exam_results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exam_results (id, exam_id, student_id, subject_id, marks_obtained, grade, remarks, recorded_by_id, created_at, updated_at, class_id, submission_id, release_batch_id, attendance_status, status, paper_file_path, paper_original_name, paper_mime_type, paper_file_size, paper_uploaded_at, absence_reason, complaint) FROM stdin;
366	20	3	26	76.00	B	Very good progress	377	2026-09-21 03:52:34.835253+03	2026-09-21 03:52:34.835263+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
367	20	15	26	\N	\N		377	2026-09-21 03:52:34.835266+03	2026-09-21 03:52:34.835268+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
368	20	5	26	\N	\N		377	2026-09-21 03:52:34.83527+03	2026-09-21 03:52:34.835272+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
369	20	2	26	\N	\N		377	2026-09-21 03:52:34.835275+03	2026-09-21 03:52:34.835277+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
370	20	14	26	\N	\N		377	2026-09-21 03:52:34.835279+03	2026-09-21 03:52:34.83528+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
371	20	18	26	\N	\N		377	2026-09-21 03:52:34.835282+03	2026-09-21 03:52:34.835284+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
372	20	10	26	\N	\N		377	2026-09-21 03:52:34.835286+03	2026-09-21 03:52:34.835287+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
373	20	11	26	\N	\N		377	2026-09-21 03:52:34.835289+03	2026-09-21 03:52:34.83529+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
374	20	4	26	\N	\N		377	2026-09-21 03:52:34.835292+03	2026-09-21 03:52:34.835294+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
375	20	9	26	\N	\N		377	2026-09-21 03:52:34.835295+03	2026-09-21 03:52:34.835297+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
1	2	21	2	85.00	A	Excellent mastery	305	2026-09-21 01:42:58.528279+03	2026-09-21 01:42:59.003097+03	3	2	1	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
2	2	22	2	65.00	C	Passed after re-evaluation	305	2026-09-21 01:42:58.528289+03	2026-09-21 01:42:59.0031+03	3	2	1	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
376	20	17	26	\N	\N		377	2026-09-21 03:52:34.835298+03	2026-09-21 03:52:34.8353+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
377	20	100	26	\N	\N		377	2026-09-21 03:52:34.835302+03	2026-09-21 03:52:34.835304+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
378	20	16	26	\N	\N		377	2026-09-21 03:52:34.835305+03	2026-09-21 03:52:34.835307+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
379	20	6	26	\N	\N		377	2026-09-21 03:52:34.835309+03	2026-09-21 03:52:34.83531+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
380	20	1	26	\N	\N		377	2026-09-21 03:52:34.835312+03	2026-09-21 03:52:34.835313+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
381	20	13	26	\N	\N		377	2026-09-21 03:52:34.835315+03	2026-09-21 03:52:34.835316+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
382	20	12	26	\N	\N		377	2026-09-21 03:52:34.835318+03	2026-09-21 03:52:34.83532+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
383	20	20	26	\N	\N		377	2026-09-21 03:52:34.835321+03	2026-09-21 03:52:34.835323+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
385	20	19	26	\N	\N		377	2026-09-21 03:52:34.835328+03	2026-09-21 03:52:34.83533+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
386	20	7	26	\N	\N		377	2026-09-21 03:52:34.835331+03	2026-09-21 03:52:34.835333+03	1	16	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
384	20	8	26	\N	\N		377	2026-09-21 03:52:34.835324+03	2026-09-21 03:52:59.177457+03	1	16	\N	PRESENT	DRAFT	result_20_8_1b057a09a768.jpg	pexels-bhuppigraphy-757919.jpg	image/jpeg	457310	2026-09-21 03:52:59.170169+03	\N	\N
387	15	53	16	75.00	B	Very good progress	305	2026-09-26 09:21:50.885978+03	2026-09-26 09:22:00.541783+03	6	17	\N	PRESENT	DRAFT	result_15_53_6f70d647c0ae.jpg	pexels-anntarazevich-5598288.jpg	image/jpeg	286969	2026-09-26 09:21:50.88408+03	\N	\N
388	15	54	16	\N	\N		305	2026-09-26 09:22:00.543907+03	2026-09-26 09:22:00.543909+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
389	15	55	16	\N	\N		305	2026-09-26 09:22:00.543909+03	2026-09-26 09:22:00.54391+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
390	15	56	16	\N	\N		305	2026-09-26 09:22:00.54391+03	2026-09-26 09:22:00.543911+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
391	15	57	16	\N	\N		305	2026-09-26 09:22:00.543911+03	2026-09-26 09:22:00.543911+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
392	15	58	16	\N	\N		305	2026-09-26 09:22:00.543912+03	2026-09-26 09:22:00.543912+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
393	15	59	16	\N	\N		305	2026-09-26 09:22:00.543913+03	2026-09-26 09:22:00.543913+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
394	15	60	16	\N	\N		305	2026-09-26 09:22:00.543914+03	2026-09-26 09:22:00.543914+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
395	15	61	16	\N	\N		305	2026-09-26 09:22:00.543915+03	2026-09-26 09:22:00.543915+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
396	15	62	16	\N	\N		305	2026-09-26 09:22:00.543915+03	2026-09-26 09:22:00.543916+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
397	15	63	16	\N	\N		305	2026-09-26 09:22:00.543916+03	2026-09-26 09:22:00.543917+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
398	15	64	16	\N	\N		305	2026-09-26 09:22:00.543917+03	2026-09-26 09:22:00.543917+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
399	15	65	16	\N	\N		305	2026-09-26 09:22:00.543918+03	2026-09-26 09:22:00.543918+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
400	15	66	16	\N	\N		305	2026-09-26 09:22:00.543919+03	2026-09-26 09:22:00.543919+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
3	3	23	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831621+03	2026-09-21 01:43:03.688181+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
4	3	24	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831627+03	2026-09-21 01:43:03.688183+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
5	3	25	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831633+03	2026-09-21 01:43:03.688184+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
6	3	26	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831634+03	2026-09-21 01:43:03.688184+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
7	3	27	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831636+03	2026-09-21 01:43:03.688185+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
8	3	28	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831638+03	2026-09-21 01:43:03.688185+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
9	3	29	4	80.00	A	Good effort	308	2026-09-21 01:42:59.83164+03	2026-09-21 01:43:03.688186+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
10	3	30	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831642+03	2026-09-21 01:43:03.688186+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
11	3	31	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831644+03	2026-09-21 01:43:03.688187+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
12	3	32	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831646+03	2026-09-21 01:43:03.688188+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
13	3	33	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831648+03	2026-09-21 01:43:03.688188+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
14	3	34	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831649+03	2026-09-21 01:43:03.688189+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
15	3	35	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831651+03	2026-09-21 01:43:03.688189+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
16	3	36	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831653+03	2026-09-21 01:43:03.68819+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
17	3	37	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831655+03	2026-09-21 01:43:03.688191+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
18	3	38	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831657+03	2026-09-21 01:43:03.688191+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
19	3	39	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831658+03	2026-09-21 01:43:03.688192+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
20	3	40	4	65.00	C	Good effort	308	2026-09-21 01:42:59.83166+03	2026-09-21 01:43:03.688192+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
21	3	41	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831662+03	2026-09-21 01:43:03.688193+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
22	3	42	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831663+03	2026-09-21 01:43:03.688193+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
23	3	43	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831665+03	2026-09-21 01:43:03.688194+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
24	3	44	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831667+03	2026-09-21 01:43:03.688195+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
25	3	45	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831669+03	2026-09-21 01:43:03.688195+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
26	3	46	4	65.00	C	Good effort	308	2026-09-21 01:42:59.83167+03	2026-09-21 01:43:03.688196+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
27	3	47	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831672+03	2026-09-21 01:43:03.688196+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
28	3	48	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831674+03	2026-09-21 01:43:03.688197+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
29	3	49	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831676+03	2026-09-21 01:43:03.688197+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
33	4	23	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053523+03	2026-09-21 01:43:03.70115+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
34	4	24	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053527+03	2026-09-21 01:43:03.701154+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
401	15	67	16	\N	\N		305	2026-09-26 09:22:00.54392+03	2026-09-26 09:22:00.54392+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
402	15	68	16	\N	\N		305	2026-09-26 09:22:00.54392+03	2026-09-26 09:22:00.543921+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
403	15	69	16	\N	\N		305	2026-09-26 09:22:00.543921+03	2026-09-26 09:22:00.543922+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
404	15	70	16	\N	\N		305	2026-09-26 09:22:00.543922+03	2026-09-26 09:22:00.543923+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
405	15	71	16	\N	\N		305	2026-09-26 09:22:00.543923+03	2026-09-26 09:22:00.543924+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
406	15	72	16	\N	\N		305	2026-09-26 09:22:00.543924+03	2026-09-26 09:22:00.543924+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
407	15	73	16	\N	\N		305	2026-09-26 09:22:00.543925+03	2026-09-26 09:22:00.543925+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
408	15	74	16	\N	\N		305	2026-09-26 09:22:00.543926+03	2026-09-26 09:22:00.543926+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
409	15	75	16	\N	\N		305	2026-09-26 09:22:00.543927+03	2026-09-26 09:22:00.543927+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
410	15	76	16	\N	\N		305	2026-09-26 09:22:00.543928+03	2026-09-26 09:22:00.543928+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
411	15	77	16	\N	\N		305	2026-09-26 09:22:00.543929+03	2026-09-26 09:22:00.543929+03	6	17	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
38	4	28	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053532+03	2026-09-21 01:43:03.701156+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
39	4	29	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053533+03	2026-09-21 01:43:03.701157+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
40	4	30	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053535+03	2026-09-21 01:43:03.701158+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
41	4	31	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053536+03	2026-09-21 01:43:03.701158+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
42	4	32	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053537+03	2026-09-21 01:43:03.701159+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
43	4	33	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053538+03	2026-09-21 01:43:03.70116+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
44	4	34	5	65.00	C	Good effort	308	2026-09-21 01:43:00.05354+03	2026-09-21 01:43:03.70116+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
45	4	35	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053541+03	2026-09-21 01:43:03.701161+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
46	4	36	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053542+03	2026-09-21 01:43:03.701162+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
47	4	37	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053543+03	2026-09-21 01:43:03.701163+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
48	4	38	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053545+03	2026-09-21 01:43:03.701163+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
49	4	39	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053546+03	2026-09-21 01:43:03.701164+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
50	4	40	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053547+03	2026-09-21 01:43:03.701164+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
51	4	41	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053548+03	2026-09-21 01:43:03.701165+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
52	4	42	5	65.00	C	Good effort	308	2026-09-21 01:43:00.05355+03	2026-09-21 01:43:03.701166+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
53	4	43	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053551+03	2026-09-21 01:43:03.701166+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
54	4	44	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053552+03	2026-09-21 01:43:03.701167+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
55	4	45	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053553+03	2026-09-21 01:43:03.701167+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
56	4	46	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053554+03	2026-09-21 01:43:03.701168+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
57	4	47	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053556+03	2026-09-21 01:43:03.701169+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
58	4	48	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053557+03	2026-09-21 01:43:03.70117+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
475	33	218	38	42.00	F	\N	\N	2026-11-13 08:48:05.443398+03	2026-11-13 08:48:05.443401+03	87	\N	\N	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
459	17	7	4	92.00	A+	Excellent comprehension.	373	2026-10-23 22:36:14.923318+03	2026-10-23 22:36:16.848967+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
460	17	8	4	\N	\N	Medical absence.	373	2026-10-23 22:36:14.92334+03	2026-10-23 22:36:16.848976+03	3	44	\N	ABSENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
461	17	21	4	75.00	B	Good progress.	373	2026-10-23 22:36:14.923348+03	2026-10-23 22:36:16.848978+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
462	17	22	4	75.00	B	Good progress.	373	2026-10-23 22:36:14.923356+03	2026-10-23 22:36:16.848981+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
463	17	2	4	75.00	B	Good progress.	373	2026-10-23 22:36:14.923364+03	2026-10-23 22:36:16.848983+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
464	17	3	4	75.00	B	Good progress.	373	2026-10-23 22:36:14.923372+03	2026-10-23 22:36:16.848985+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
465	17	4	4	75.00	B	Good progress.	373	2026-10-23 22:36:14.923379+03	2026-10-23 22:36:16.848987+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
466	17	6	4	75.00	B	Good progress.	373	2026-10-23 22:36:14.923387+03	2026-10-23 22:36:16.848989+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
467	17	1	4	75.00	B	Good progress.	373	2026-10-23 22:36:14.923395+03	2026-10-23 22:36:16.848991+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
468	17	5	4	75.00	B	Good progress.	373	2026-10-23 22:36:14.923403+03	2026-10-23 22:36:16.848993+03	3	44	\N	PRESENT	APPROVED	\N	\N	\N	\N	\N	\N	\N
473	29	150	1	94.50	A	\N	\N	2026-10-27 08:25:59.483123+03	2026-10-27 08:25:59.483133+03	\N	\N	\N	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
85	5	45	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270904+03	2026-09-21 01:43:03.701186+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
86	5	46	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270906+03	2026-09-21 01:43:03.701187+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
87	5	47	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270907+03	2026-09-21 01:43:03.701187+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
88	5	48	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270908+03	2026-09-21 01:43:03.701188+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
89	5	49	6	80.00	A	Good effort	308	2026-09-21 01:43:00.27091+03	2026-09-21 01:43:03.701188+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
90	5	50	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270911+03	2026-09-21 01:43:03.701189+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
91	5	51	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270912+03	2026-09-21 01:43:03.70119+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
92	5	52	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270913+03	2026-09-21 01:43:03.70119+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
93	6	23	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480733+03	2026-09-21 01:43:03.701191+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
94	6	24	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480737+03	2026-09-21 01:43:03.701192+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
95	6	25	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480739+03	2026-09-21 01:43:03.701192+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
96	6	26	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.48074+03	2026-09-21 01:43:03.701193+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
97	6	27	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480742+03	2026-09-21 01:43:03.701194+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
98	6	28	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480743+03	2026-09-21 01:43:03.701194+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
99	6	29	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480745+03	2026-09-21 01:43:03.701195+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
81	5	41	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270899+03	2026-09-21 01:43:03.701184+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
82	5	42	6	65.00	C	Good effort	308	2026-09-21 01:43:00.2709+03	2026-09-21 01:43:03.701184+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
83	5	43	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270902+03	2026-09-21 01:43:03.701185+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
84	5	44	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270903+03	2026-09-21 01:43:03.701185+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
100	6	30	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480746+03	2026-09-21 01:43:03.701196+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
101	6	31	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480748+03	2026-09-21 01:43:03.701196+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
102	6	32	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480749+03	2026-09-21 01:43:03.701197+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
103	6	33	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480751+03	2026-09-21 01:43:03.701198+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
104	6	34	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480752+03	2026-09-21 01:43:03.701198+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
363	16	90	1	94.50	A	\N	\N	2026-09-21 01:43:08.681605+03	2026-09-21 01:43:08.681609+03	\N	\N	\N	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
469	1	3	1	\N	\N	\N	304	2026-10-23 23:31:21.169877+03	2026-11-13 16:09:40.167841+03	1	\N	\N	PRESENT	DRAFT	\N	\N	\N	\N	\N	\N	\N
474	30	168	1	94.50	A	\N	\N	2026-10-27 08:32:42.567959+03	2026-10-27 08:32:42.56797+03	\N	\N	\N	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
132	7	34	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702292+03	2026-09-21 01:43:03.701218+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
133	7	35	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702293+03	2026-09-21 01:43:03.701219+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
134	7	36	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702294+03	2026-09-21 01:43:03.701219+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
135	7	37	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702296+03	2026-09-21 01:43:03.70122+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
136	7	38	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702297+03	2026-09-21 01:43:03.70122+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
137	7	39	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702298+03	2026-09-21 01:43:03.701221+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
138	7	40	8	65.00	C	Good effort	308	2026-09-21 01:43:00.7023+03	2026-09-21 01:43:03.701221+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
139	7	41	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702301+03	2026-09-21 01:43:03.701222+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
140	7	42	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702302+03	2026-09-21 01:43:03.701222+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
141	7	43	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702303+03	2026-09-21 01:43:03.701224+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
142	7	44	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702305+03	2026-09-21 01:43:03.701224+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
143	7	45	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702306+03	2026-09-21 01:43:03.701225+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
144	7	46	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702307+03	2026-09-21 01:43:03.701225+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
145	7	47	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702309+03	2026-09-21 01:43:03.701226+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
146	7	48	8	65.00	C	Good effort	308	2026-09-21 01:43:00.70231+03	2026-09-21 01:43:03.701226+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
147	7	49	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702311+03	2026-09-21 01:43:03.701227+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
148	7	50	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702312+03	2026-09-21 01:43:03.701227+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
149	7	51	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702314+03	2026-09-21 01:43:03.701228+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
150	7	52	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702315+03	2026-09-21 01:43:03.701229+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
151	8	23	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154321+03	2026-09-21 01:43:03.701229+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
152	8	24	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154327+03	2026-09-21 01:43:03.70123+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
153	8	25	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154329+03	2026-09-21 01:43:03.70123+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
154	8	26	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154331+03	2026-09-21 01:43:03.701231+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
155	8	27	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154334+03	2026-09-21 01:43:03.701231+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
156	8	28	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154336+03	2026-09-21 01:43:03.701232+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
157	8	29	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154338+03	2026-09-21 01:43:03.701232+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
158	8	30	9	65.00	C	Good effort	308	2026-09-21 01:43:01.15434+03	2026-09-21 01:43:03.701233+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
470	27	115	34	91.00	A+	Re-verified paper mark.	392	2026-10-23 23:31:33.45563+03	2026-10-23 23:31:34.304685+03	25	45	12	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
471	27	116	34	\N	\N	Medical certificate verified	392	2026-10-23 23:31:33.455634+03	2026-10-23 23:31:34.304688+03	25	45	12	ABSENT	RELEASED	\N	\N	\N	\N	\N	Severe malaria, admitted at Banadir Hospital	\N
472	27	117	34	94.00	A+	Outstanding test score	392	2026-10-23 23:31:33.455635+03	2026-10-23 23:31:34.304688+03	25	45	12	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	Question 4 on Euclidean geometry had blurry printing
169	8	41	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154361+03	2026-09-21 01:43:03.701239+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
170	8	42	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154363+03	2026-09-21 01:43:03.70124+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
171	8	43	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154365+03	2026-09-21 01:43:03.70124+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
172	8	44	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154367+03	2026-09-21 01:43:03.701241+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
173	8	45	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154369+03	2026-09-21 01:43:03.701242+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
174	8	46	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154372+03	2026-09-21 01:43:03.701242+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
175	8	47	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154374+03	2026-09-21 01:43:03.701243+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
176	8	48	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154376+03	2026-09-21 01:43:03.701244+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
177	8	49	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154378+03	2026-09-21 01:43:03.701245+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
178	8	50	9	65.00	C	Good effort	308	2026-09-21 01:43:01.15438+03	2026-09-21 01:43:03.701245+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
179	8	51	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154382+03	2026-09-21 01:43:03.701246+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
180	8	52	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154384+03	2026-09-21 01:43:03.701247+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
181	9	23	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379556+03	2026-09-21 01:43:03.701247+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
182	9	24	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379562+03	2026-09-21 01:43:03.701248+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
183	9	25	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379563+03	2026-09-21 01:43:03.701249+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
184	9	26	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379565+03	2026-09-21 01:43:03.701249+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
185	9	27	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379567+03	2026-09-21 01:43:03.70125+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
186	9	28	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379569+03	2026-09-21 01:43:03.701251+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
187	9	29	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379571+03	2026-09-21 01:43:03.701251+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
188	9	30	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379572+03	2026-09-21 01:43:03.701252+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
189	9	31	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379574+03	2026-09-21 01:43:03.701253+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
190	9	32	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379576+03	2026-09-21 01:43:03.701253+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
191	9	33	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379578+03	2026-09-21 01:43:03.701254+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
192	9	34	10	65.00	C	Good effort	308	2026-09-21 01:43:01.37958+03	2026-09-21 01:43:03.701254+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
193	9	35	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379581+03	2026-09-21 01:43:03.701256+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
194	9	36	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379583+03	2026-09-21 01:43:03.701256+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
195	9	37	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379585+03	2026-09-21 01:43:03.701257+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
206	9	48	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379603+03	2026-09-21 01:43:03.701263+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
207	9	49	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379605+03	2026-09-21 01:43:03.701263+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
208	9	50	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379607+03	2026-09-21 01:43:03.701264+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
209	9	51	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379608+03	2026-09-21 01:43:03.701265+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
210	9	52	10	65.00	C	Good effort	308	2026-09-21 01:43:01.37961+03	2026-09-21 01:43:03.701265+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
211	10	23	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584452+03	2026-09-21 01:43:03.701266+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
212	10	24	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584456+03	2026-09-21 01:43:03.701266+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
213	10	25	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584458+03	2026-09-21 01:43:03.701267+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
214	10	26	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584459+03	2026-09-21 01:43:03.701267+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
215	10	27	11	80.00	A	Good effort	308	2026-09-21 01:43:01.58446+03	2026-09-21 01:43:03.701268+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
216	10	28	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584461+03	2026-09-21 01:43:03.701268+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
217	10	29	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584463+03	2026-09-21 01:43:03.701269+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
218	10	30	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584464+03	2026-09-21 01:43:03.70127+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
219	10	31	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584465+03	2026-09-21 01:43:03.70127+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
220	10	32	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584466+03	2026-09-21 01:43:03.701271+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
221	10	33	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584467+03	2026-09-21 01:43:03.701271+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
222	10	34	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584469+03	2026-09-21 01:43:03.701272+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
223	10	35	11	80.00	A	Good effort	308	2026-09-21 01:43:01.58447+03	2026-09-21 01:43:03.701272+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
224	10	36	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584471+03	2026-09-21 01:43:03.701273+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
225	10	37	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584472+03	2026-09-21 01:43:03.701274+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
226	10	38	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584474+03	2026-09-21 01:43:03.701274+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
227	10	39	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584475+03	2026-09-21 01:43:03.701275+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
228	10	40	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584476+03	2026-09-21 01:43:03.701276+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
229	10	41	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584477+03	2026-09-21 01:43:03.701276+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
230	10	42	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584479+03	2026-09-21 01:43:03.701277+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
231	10	43	11	80.00	A	Good effort	308	2026-09-21 01:43:01.58448+03	2026-09-21 01:43:03.701277+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
244	11	26	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786458+03	2026-09-21 01:43:03.701285+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
245	11	27	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786459+03	2026-09-21 01:43:03.701285+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
246	11	28	12	65.00	C	Good effort	308	2026-09-21 01:43:01.78646+03	2026-09-21 01:43:03.701286+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
247	11	29	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786462+03	2026-09-21 01:43:03.701286+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
248	11	30	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786463+03	2026-09-21 01:43:03.701287+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
249	11	31	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786464+03	2026-09-21 01:43:03.701287+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
250	11	32	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786466+03	2026-09-21 01:43:03.701288+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
251	11	33	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786467+03	2026-09-21 01:43:03.701289+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
252	11	34	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786468+03	2026-09-21 01:43:03.701289+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
253	11	35	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786469+03	2026-09-21 01:43:03.70129+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
254	11	36	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786471+03	2026-09-21 01:43:03.70129+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
255	11	37	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786472+03	2026-09-21 01:43:03.701291+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
256	11	38	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786474+03	2026-09-21 01:43:03.701291+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
257	11	39	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786475+03	2026-09-21 01:43:03.701292+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
258	11	40	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786476+03	2026-09-21 01:43:03.701292+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
259	11	41	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786477+03	2026-09-21 01:43:03.701293+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
260	11	42	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786479+03	2026-09-21 01:43:03.701293+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
261	11	43	12	80.00	A	Good effort	308	2026-09-21 01:43:01.78648+03	2026-09-21 01:43:03.701294+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
262	11	44	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786481+03	2026-09-21 01:43:03.701295+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
263	11	45	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786482+03	2026-09-21 01:43:03.701295+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
264	11	46	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786484+03	2026-09-21 01:43:03.701296+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
265	11	47	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786485+03	2026-09-21 01:43:03.701296+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
266	11	48	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786486+03	2026-09-21 01:43:03.701297+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
285	12	37	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990163+03	2026-09-21 01:43:03.701307+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
286	12	38	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990164+03	2026-09-21 01:43:03.701308+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
287	12	39	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990165+03	2026-09-21 01:43:03.701308+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
288	12	40	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990166+03	2026-09-21 01:43:03.701309+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
289	12	41	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990167+03	2026-09-21 01:43:03.701309+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
290	12	42	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990168+03	2026-09-21 01:43:03.70131+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
291	12	43	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990169+03	2026-09-21 01:43:03.701311+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
292	12	44	13	65.00	C	Good effort	308	2026-09-21 01:43:01.99017+03	2026-09-21 01:43:03.701311+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
293	12	45	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990171+03	2026-09-21 01:43:03.701312+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
294	12	46	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990173+03	2026-09-21 01:43:03.701312+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
295	12	47	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990174+03	2026-09-21 01:43:03.701313+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
296	12	48	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990175+03	2026-09-21 01:43:03.701313+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
297	12	49	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990176+03	2026-09-21 01:43:03.701314+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
298	12	50	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990177+03	2026-09-21 01:43:03.701314+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
299	12	51	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990178+03	2026-09-21 01:43:03.701315+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
300	12	52	13	65.00	C	Good effort	308	2026-09-21 01:43:01.99018+03	2026-09-21 01:43:03.701316+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
301	13	23	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194605+03	2026-09-21 01:43:03.701317+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
302	13	24	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194611+03	2026-09-21 01:43:03.701317+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
303	13	25	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194613+03	2026-09-21 01:43:03.701318+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
304	13	26	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194614+03	2026-09-21 01:43:03.701319+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
305	13	27	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194615+03	2026-09-21 01:43:03.701319+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
306	13	28	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194617+03	2026-09-21 01:43:03.70132+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
307	13	29	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194618+03	2026-09-21 01:43:03.70132+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
308	13	30	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194619+03	2026-09-21 01:43:03.701321+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
309	13	31	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194621+03	2026-09-21 01:43:03.701321+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
310	13	32	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194623+03	2026-09-21 01:43:03.701322+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
311	13	33	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194624+03	2026-09-21 01:43:03.701323+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
322	13	44	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194639+03	2026-09-21 01:43:03.701329+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
323	13	45	14	80.00	A	Good effort	308	2026-09-21 01:43:02.19464+03	2026-09-21 01:43:03.70133+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
324	13	46	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194641+03	2026-09-21 01:43:03.70133+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
325	13	47	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194643+03	2026-09-21 01:43:03.701331+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
326	13	48	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194644+03	2026-09-21 01:43:03.701331+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
327	13	49	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194645+03	2026-09-21 01:43:03.701332+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
328	13	50	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194647+03	2026-09-21 01:43:03.701332+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
329	13	51	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194648+03	2026-09-21 01:43:03.701333+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
330	13	52	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194649+03	2026-09-21 01:43:03.701333+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
331	14	23	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573888+03	2026-09-21 01:43:03.701334+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
332	14	24	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573894+03	2026-09-21 01:43:03.701334+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
333	14	25	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573896+03	2026-09-21 01:43:03.701335+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
334	14	26	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573898+03	2026-09-21 01:43:03.701336+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
335	14	27	15	80.00	A	Good effort	308	2026-09-21 01:43:02.5739+03	2026-09-21 01:43:03.701336+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
336	14	28	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573901+03	2026-09-21 01:43:03.701337+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
337	14	29	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573903+03	2026-09-21 01:43:03.701337+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
338	14	30	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573905+03	2026-09-21 01:43:03.701338+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
339	14	31	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573907+03	2026-09-21 01:43:03.701338+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
340	14	32	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573908+03	2026-09-21 01:43:03.701339+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
341	14	33	15	80.00	A	Good effort	308	2026-09-21 01:43:02.57391+03	2026-09-21 01:43:03.701339+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
342	14	34	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573912+03	2026-09-21 01:43:03.70134+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
343	14	35	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573913+03	2026-09-21 01:43:03.70134+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
344	14	36	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573915+03	2026-09-21 01:43:03.701341+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
345	14	37	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573916+03	2026-09-21 01:43:03.701342+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
346	14	38	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573918+03	2026-09-21 01:43:03.701342+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
347	14	39	15	80.00	A	Good effort	308	2026-09-21 01:43:02.57392+03	2026-09-21 01:43:03.701343+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
348	14	40	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573922+03	2026-09-21 01:43:03.701343+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
30	3	50	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831677+03	2026-09-21 01:43:03.688198+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
31	3	51	4	80.00	A	Good effort	308	2026-09-21 01:42:59.831679+03	2026-09-21 01:43:03.688198+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
32	3	52	4	65.00	C	Good effort	308	2026-09-21 01:42:59.831681+03	2026-09-21 01:43:03.688199+03	5	3	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
35	4	25	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053528+03	2026-09-21 01:43:03.701154+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
36	4	26	5	65.00	C	Good effort	308	2026-09-21 01:43:00.05353+03	2026-09-21 01:43:03.701155+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
37	4	27	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053531+03	2026-09-21 01:43:03.701156+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
59	4	49	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053558+03	2026-09-21 01:43:03.70117+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
60	4	50	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053559+03	2026-09-21 01:43:03.701171+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
61	4	51	5	80.00	A	Good effort	308	2026-09-21 01:43:00.053561+03	2026-09-21 01:43:03.701172+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
62	4	52	5	65.00	C	Good effort	308	2026-09-21 01:43:00.053562+03	2026-09-21 01:43:03.701172+03	5	4	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
63	5	23	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270874+03	2026-09-21 01:43:03.701173+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
64	5	24	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270878+03	2026-09-21 01:43:03.701174+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
65	5	25	6	80.00	A	Good effort	308	2026-09-21 01:43:00.27088+03	2026-09-21 01:43:03.701174+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
66	5	26	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270881+03	2026-09-21 01:43:03.701175+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
67	5	27	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270882+03	2026-09-21 01:43:03.701175+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
68	5	28	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270884+03	2026-09-21 01:43:03.701176+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
69	5	29	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270885+03	2026-09-21 01:43:03.701177+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
70	5	30	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270886+03	2026-09-21 01:43:03.701177+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
71	5	31	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270887+03	2026-09-21 01:43:03.701178+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
72	5	32	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270889+03	2026-09-21 01:43:03.701178+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
73	5	33	6	80.00	A	Good effort	308	2026-09-21 01:43:00.27089+03	2026-09-21 01:43:03.701179+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
74	5	34	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270891+03	2026-09-21 01:43:03.701179+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
75	5	35	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270892+03	2026-09-21 01:43:03.70118+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
76	5	36	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270893+03	2026-09-21 01:43:03.701181+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
77	5	37	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270894+03	2026-09-21 01:43:03.701181+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
78	5	38	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270896+03	2026-09-21 01:43:03.701182+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
79	5	39	6	80.00	A	Good effort	308	2026-09-21 01:43:00.270897+03	2026-09-21 01:43:03.701182+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
80	5	40	6	65.00	C	Good effort	308	2026-09-21 01:43:00.270898+03	2026-09-21 01:43:03.701183+03	5	5	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
105	6	35	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480754+03	2026-09-21 01:43:03.701199+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
108	6	38	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480758+03	2026-09-21 01:43:03.701201+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
109	6	39	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.48076+03	2026-09-21 01:43:03.701202+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
110	6	40	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480762+03	2026-09-21 01:43:03.701202+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
111	6	41	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480763+03	2026-09-21 01:43:03.701203+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
112	6	42	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480764+03	2026-09-21 01:43:03.701203+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
113	6	43	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480766+03	2026-09-21 01:43:03.701204+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
114	6	44	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480767+03	2026-09-21 01:43:03.701204+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
115	6	45	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480769+03	2026-09-21 01:43:03.701205+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
116	6	46	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.48077+03	2026-09-21 01:43:03.701206+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
117	6	47	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480771+03	2026-09-21 01:43:03.701206+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
118	6	48	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480773+03	2026-09-21 01:43:03.701207+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
119	6	49	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480774+03	2026-09-21 01:43:03.701207+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
120	6	50	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480776+03	2026-09-21 01:43:03.701208+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
359	14	51	15	80.00	A	Good effort	308	2026-09-21 01:43:02.57394+03	2026-09-21 01:43:03.701349+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
106	6	36	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480755+03	2026-09-21 01:43:03.7012+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
107	6	37	7	75.00	B	Physics completed	308	2026-09-21 01:43:00.480757+03	2026-09-21 01:43:03.7012+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
121	7	23	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702273+03	2026-09-21 01:43:03.701208+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
122	7	24	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702278+03	2026-09-21 01:43:03.701209+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
123	7	25	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702279+03	2026-09-21 01:43:03.701213+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
124	7	26	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702281+03	2026-09-21 01:43:03.701214+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
125	7	27	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702282+03	2026-09-21 01:43:03.701214+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
126	7	28	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702283+03	2026-09-21 01:43:03.701215+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
127	7	29	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702285+03	2026-09-21 01:43:03.701215+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
128	7	30	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702286+03	2026-09-21 01:43:03.701216+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
129	7	31	8	80.00	A	Good effort	308	2026-09-21 01:43:00.702288+03	2026-09-21 01:43:03.701216+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
130	7	32	8	65.00	C	Good effort	308	2026-09-21 01:43:00.702289+03	2026-09-21 01:43:03.701217+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
131	7	33	8	80.00	A	Good effort	308	2026-09-21 01:43:00.70229+03	2026-09-21 01:43:03.701218+03	5	7	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
159	8	31	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154342+03	2026-09-21 01:43:03.701233+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
160	8	32	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154344+03	2026-09-21 01:43:03.701234+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
161	8	33	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154346+03	2026-09-21 01:43:03.701235+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
162	8	34	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154348+03	2026-09-21 01:43:03.701235+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
163	8	35	9	80.00	A	Good effort	308	2026-09-21 01:43:01.15435+03	2026-09-21 01:43:03.701236+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
164	8	36	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154352+03	2026-09-21 01:43:03.701236+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
165	8	37	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154354+03	2026-09-21 01:43:03.701237+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
166	8	38	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154356+03	2026-09-21 01:43:03.701237+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
167	8	39	9	80.00	A	Good effort	308	2026-09-21 01:43:01.154358+03	2026-09-21 01:43:03.701238+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
168	8	40	9	65.00	C	Good effort	308	2026-09-21 01:43:01.154359+03	2026-09-21 01:43:03.701238+03	5	8	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
196	9	38	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379586+03	2026-09-21 01:43:03.701257+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
197	9	39	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379588+03	2026-09-21 01:43:03.701258+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
198	9	40	10	65.00	C	Good effort	308	2026-09-21 01:43:01.37959+03	2026-09-21 01:43:03.701258+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
199	9	41	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379591+03	2026-09-21 01:43:03.701259+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
200	9	42	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379593+03	2026-09-21 01:43:03.701259+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
201	9	43	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379594+03	2026-09-21 01:43:03.70126+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
202	9	44	10	65.00	C	Good effort	308	2026-09-21 01:43:01.379596+03	2026-09-21 01:43:03.701261+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
203	9	45	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379598+03	2026-09-21 01:43:03.701261+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
204	9	46	10	65.00	C	Good effort	308	2026-09-21 01:43:01.3796+03	2026-09-21 01:43:03.701262+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
205	9	47	10	80.00	A	Good effort	308	2026-09-21 01:43:01.379602+03	2026-09-21 01:43:03.701262+03	5	9	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
232	10	44	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584481+03	2026-09-21 01:43:03.701278+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
233	10	45	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584483+03	2026-09-21 01:43:03.701278+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
234	10	46	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584485+03	2026-09-21 01:43:03.701279+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
235	10	47	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584486+03	2026-09-21 01:43:03.70128+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
236	10	48	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584487+03	2026-09-21 01:43:03.70128+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
237	10	49	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584488+03	2026-09-21 01:43:03.701281+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
238	10	50	11	65.00	C	Good effort	308	2026-09-21 01:43:01.58449+03	2026-09-21 01:43:03.701281+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
239	10	51	11	80.00	A	Good effort	308	2026-09-21 01:43:01.584491+03	2026-09-21 01:43:03.701282+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
240	10	52	11	65.00	C	Good effort	308	2026-09-21 01:43:01.584492+03	2026-09-21 01:43:03.701282+03	5	10	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
241	11	23	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786451+03	2026-09-21 01:43:03.701283+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
242	11	24	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786455+03	2026-09-21 01:43:03.701284+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
243	11	25	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786456+03	2026-09-21 01:43:03.701284+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
267	11	49	12	80.00	A	Good effort	308	2026-09-21 01:43:01.786488+03	2026-09-21 01:43:03.701297+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
268	11	50	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786489+03	2026-09-21 01:43:03.701298+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
269	11	51	12	80.00	A	Good effort	308	2026-09-21 01:43:01.78649+03	2026-09-21 01:43:03.701298+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
270	11	52	12	65.00	C	Good effort	308	2026-09-21 01:43:01.786492+03	2026-09-21 01:43:03.701299+03	5	11	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
271	12	23	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990143+03	2026-09-21 01:43:03.7013+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
272	12	24	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990147+03	2026-09-21 01:43:03.7013+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
273	12	25	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990149+03	2026-09-21 01:43:03.701301+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
274	12	26	13	65.00	C	Good effort	308	2026-09-21 01:43:01.99015+03	2026-09-21 01:43:03.701301+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
275	12	27	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990151+03	2026-09-21 01:43:03.701302+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
276	12	28	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990152+03	2026-09-21 01:43:03.701302+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
277	12	29	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990153+03	2026-09-21 01:43:03.701303+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
278	12	30	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990155+03	2026-09-21 01:43:03.701303+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
279	12	31	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990156+03	2026-09-21 01:43:03.701304+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
280	12	32	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990157+03	2026-09-21 01:43:03.701305+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
281	12	33	13	80.00	A	Good effort	308	2026-09-21 01:43:01.990158+03	2026-09-21 01:43:03.701305+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
282	12	34	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990159+03	2026-09-21 01:43:03.701306+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
283	12	35	13	80.00	A	Good effort	308	2026-09-21 01:43:01.99016+03	2026-09-21 01:43:03.701306+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
284	12	36	13	65.00	C	Good effort	308	2026-09-21 01:43:01.990162+03	2026-09-21 01:43:03.701307+03	5	12	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
312	13	34	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194626+03	2026-09-21 01:43:03.701324+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
313	13	35	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194627+03	2026-09-21 01:43:03.701324+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
314	13	36	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194628+03	2026-09-21 01:43:03.701325+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
315	13	37	14	80.00	A	Good effort	308	2026-09-21 01:43:02.19463+03	2026-09-21 01:43:03.701325+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
316	13	38	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194631+03	2026-09-21 01:43:03.701326+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
317	13	39	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194632+03	2026-09-21 01:43:03.701326+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
318	13	40	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194634+03	2026-09-21 01:43:03.701327+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
319	13	41	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194635+03	2026-09-21 01:43:03.701327+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
320	13	42	14	65.00	C	Good effort	308	2026-09-21 01:43:02.194636+03	2026-09-21 01:43:03.701328+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
321	13	43	14	80.00	A	Good effort	308	2026-09-21 01:43:02.194638+03	2026-09-21 01:43:03.701329+03	5	13	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
349	14	41	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573923+03	2026-09-21 01:43:03.701344+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
350	14	42	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573925+03	2026-09-21 01:43:03.701344+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
351	14	43	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573926+03	2026-09-21 01:43:03.701345+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
352	14	44	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573928+03	2026-09-21 01:43:03.701345+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
353	14	45	15	80.00	A	Good effort	308	2026-09-21 01:43:02.57393+03	2026-09-21 01:43:03.701346+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
354	14	46	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573932+03	2026-09-21 01:43:03.701346+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
355	14	47	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573934+03	2026-09-21 01:43:03.701347+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
356	14	48	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573936+03	2026-09-21 01:43:03.701348+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
357	14	49	15	80.00	A	Good effort	308	2026-09-21 01:43:02.573937+03	2026-09-21 01:43:03.701348+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
358	14	50	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573939+03	2026-09-21 01:43:03.701349+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
360	14	52	15	65.00	C	Good effort	308	2026-09-21 01:43:02.573942+03	2026-09-21 01:43:03.70135+03	5	14	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
361	6	51	7	75.00	B	Physics completed	308	2026-09-21 01:43:03.482702+03	2026-09-21 01:43:03.70135+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
362	6	52	7	75.00	B	Physics completed	308	2026-09-21 01:43:03.482707+03	2026-09-21 01:43:03.701351+03	5	6	3	PRESENT	RELEASED	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: exams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams (id, name, exam_type, academic_year, class_id, subject_id, start_date, end_date, max_marks, pass_marks, status, created_at, updated_at, teacher_id, instructions, start_time, end_time, result_submission_deadline, created_by_id, reopened_at, reopened_by_id, reopen_reason, published_at, published_by_id) FROM stdin;
1	Final math Examination (Grade 1 - A)	FINAL	2025/2026	1	1	2026-09-20	\N	100.00	50.00	SCHEDULED	2026-09-20 05:43:09.21116+03	2026-09-20 05:43:09.211168+03	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2	Admin Redesign Mid-Term 2026	MID_TERM	2026-2027	3	2	2026-03-10	2026-03-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:58.09343+03	2026-09-21 01:42:59.001175+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	4	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.586712+03	2026-09-21 01:43:02.841792+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	5	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.593593+03	2026-09-21 01:43:03.678368+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	6	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.599376+03	2026-09-21 01:43:03.678373+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	7	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.604733+03	2026-09-21 01:43:03.678373+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	8	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.612873+03	2026-09-21 01:43:03.678374+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	9	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.619234+03	2026-09-21 01:43:03.678374+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	10	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.625373+03	2026-09-21 01:43:03.678375+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
10	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	11	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.6317+03	2026-09-21 01:43:03.678376+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
11	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	12	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.637202+03	2026-09-21 01:43:03.678376+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
12	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	13	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.643934+03	2026-09-21 01:43:03.678377+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
13	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	14	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.649944+03	2026-09-21 01:43:03.678378+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
14	Mid-Term Examination 2026/2027	Mid-Term	2026-2027	5	15	2026-04-01	2026-04-15	100.00	50.00	PUBLISHED	2026-09-21 01:42:59.656335+03	2026-09-21 01:43:03.678378+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
15	Final Examination 2026	FINAL	2026-2027	6	16	2026-12-01	\N	100.00	50.00	SCHEDULED	2026-09-21 01:43:04.588316+03	2026-09-21 01:43:04.588318+03	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
16	Term 1 Midterm Exam 2026	MIDTERM	2026/2027	13	1	2026-09-10	\N	100.00	50.00	COMPLETED	2026-09-21 01:43:08.670514+03	2026-09-21 01:43:08.670519+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
17	E2E Isolation Exam 2026	Final	2026/2027	3	4	2026-10-15	\N	100.00	50.00	SCHEDULED	2026-09-21 01:43:21.037823+03	2026-09-21 01:43:21.037827+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
18	Unit Testing Examination 2026	Mid-Term	2025-2026	19	4	2026-11-01	\N	100.00	50.00	SCHEDULED	2026-09-21 01:43:21.532446+03	2026-09-21 01:43:21.53245+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
19	Unit Testing Examination 2026	Mid-Term	2025-2026	19	5	2026-11-02	\N	100.00	50.00	SCHEDULED	2026-09-21 01:43:21.532451+03	2026-09-21 01:43:21.532452+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
20	Final Computer G9 Examination (Grade 1 - A)	FINAL	2026/2027	1	26	2026-09-21	\N	100.00	50.00	SCHEDULED	2026-09-21 03:45:01.332222+03	2026-09-21 03:45:01.332231+03	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
28	Midterm Examination 2026 WF	MID_TERM	2026/2027	25	35	2026-11-02	\N	100.00	50.00	SCHEDULED	2026-10-23 00:42:41.634657+03	2026-10-23 00:42:41.634667+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
27	Midterm Examination 2026 WF	MID_TERM	2026/2027	25	34	2026-11-01	\N	100.00	50.00	PUBLISHED	2026-10-23 00:42:41.618402+03	2026-10-23 00:46:43.419409+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
29	Term 1 Midterm Exam 2026	MIDTERM	2026/2027	78	1	2026-09-10	\N	100.00	50.00	COMPLETED	2026-10-27 08:25:59.424362+03	2026-10-27 08:25:59.42437+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
30	Term 1 Midterm Exam 2026	MIDTERM	2026/2027	84	1	2026-09-10	\N	100.00	50.00	COMPLETED	2026-10-27 08:32:42.511041+03	2026-10-27 08:32:42.51105+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
32	Grade 5 Mid-Term Science Exam 2026	MID_TERM	2026/2027	37	37	2026-11-25	2026-11-25	100.00	50.00	PUBLISHED	2026-11-11 10:02:08.450747+03	2026-11-11 10:02:08.802209+03	\N	Scientific calculators and HB pencils permitted. No mobile phones.	08:30 AM	11:30 AM	\N	401	\N	\N	\N	2026-11-11 10:02:08.801665+03	401
33	Mid-Term Math 2026	Mid-Term	2026/2027	87	38	2026-11-13	\N	100.00	50.00	PUBLISHED	2026-11-13 08:48:05.407609+03	2026-11-13 08:48:05.407613+03	14	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: fee_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fee_payments (id, student_fee_id, student_id, receipt_number, amount_paid, payment_date, payment_method, reference_number, recorded_by_id, notes, created_at, updated_at, status) FROM stdin;
1	26	1	RCT-2026-000001	20.00	2026-09-21	EVC_PLUS	EVC-TXN-101	367	First installment via EVC Plus	2026-09-21 01:43:15.689548+03	2026-09-21 01:43:15.689555+03	VERIFIED
2	26	1	RCT-2026-000002	30.00	2026-09-21	CASH	CASH-REC-102	367	Final settlement	2026-09-21 01:43:15.803384+03	2026-09-21 01:43:15.803389+03	VERIFIED
3	28	1	RCT-2026-000003	35.00	2026-09-21	EDAHAB	ED-7788	367	\N	2026-09-21 01:43:15.919811+03	2026-09-21 01:43:15.919817+03	VERIFIED
4	30	1	RCT-2026-000004	60.00	2026-09-21	CASH	\N	367	[VOIDED: Mistaken Entry]	2026-09-21 01:43:16.060254+03	2026-09-21 01:43:16.099121+03	CANCELLED
7	58	3	RCT-2026-000005	20.00	2026-10-22	EVC_PLUS	EVC-TXN-101	367	First installment via EVC Plus	2026-10-22 17:29:52.391574+03	2026-10-22 17:29:52.391578+03	VERIFIED
8	58	3	RCT-2026-000008	30.00	2026-10-22	CASH	CASH-REC-102	367	Final settlement	2026-10-22 17:29:52.467972+03	2026-10-22 17:29:52.467976+03	VERIFIED
9	60	3	RCT-2026-000009	35.00	2026-10-22	EDAHAB	ED-7788	367	\N	2026-10-22 17:29:52.561541+03	2026-10-22 17:29:52.561544+03	VERIFIED
10	62	3	RCT-2026-000010	60.00	2026-10-22	CASH	\N	367	[VOIDED: Mistaken Entry]	2026-10-22 17:29:52.730122+03	2026-10-22 17:29:52.777361+03	CANCELLED
11	63	3	RCT-2026-000011	35.00	2026-10-22	EDAHAB	ED-7788	367	\N	2026-10-22 17:31:11.838105+03	2026-10-22 17:31:11.838111+03	VERIFIED
\.


--
-- Data for Name: fee_structures; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fee_structures (id, name, academic_year, class_id, amount, due_date, description, status, created_at, updated_at, frequency, education_level, created_by_id) FROM stdin;
1	Term 1 Tuition 2026/2027	2026/2027	\N	25.00	2026-10-21	Monthly tuition fee for primary and secondary sections	ACTIVE	2026-09-21 01:43:15.217157+03	2026-09-21 01:43:15.217162+03	Monthly	\N	367
2	Exam Fee Special 260210	2026/2027	\N	15.00	2026-10-06	\N	ACTIVE	2026-09-21 01:43:15.260874+03	2026-09-21 01:43:15.260878+03	Term	\N	\N
3	Class Fee 357665	2026/2027	1	20.00	2026-10-11	\N	ACTIVE	2026-09-21 01:43:15.358598+03	2026-09-21 01:43:15.358602+03	Monthly	\N	\N
4	Dup Test Fee 587445	2026/2027	\N	30.00	2026-10-01	\N	ACTIVE	2026-09-21 01:43:15.588108+03	2026-09-21 01:43:15.588114+03	Annual	\N	\N
5	Tuition Step Payment 659461	2026/2027	\N	50.00	2026-10-01	\N	ACTIVE	2026-09-21 01:43:15.660182+03	2026-09-21 01:43:15.660187+03	Monthly	\N	\N
6	Overpay Test 848185	2026/2027	\N	40.00	2026-10-01	\N	ACTIVE	2026-09-21 01:43:15.848587+03	2026-09-21 01:43:15.84859+03	Monthly	\N	\N
7	Receipt Test Fee 895111	2026/2027	\N	35.00	2026-09-26	\N	ACTIVE	2026-09-21 01:43:15.895524+03	2026-09-21 01:43:15.895528+03	Term	\N	\N
8	Past Due Fee 985263	2026/2027	\N	45.00	2026-09-16	\N	ACTIVE	2026-09-21 01:43:15.985935+03	2026-09-21 01:43:15.985946+03	Monthly	\N	\N
9	Void Test Fee 34397	2026/2027	\N	60.00	2026-10-01	\N	ACTIVE	2026-09-21 01:43:16.034811+03	2026-09-21 01:43:16.034814+03	Monthly	\N	\N
11	Unit Test Fee	2026/2027	\N	20.00	2026-09-21	\N	ACTIVE	2026-09-21 01:43:17.376655+03	2026-09-21 01:43:17.376658+03	Monthly	PRIMARY	1
12	Exam Fee Special 964252	2026/2027	\N	15.00	2026-11-06	\N	ACTIVE	2026-10-22 17:29:51.965926+03	2026-10-22 17:29:51.965929+03	Term	\N	\N
13	Class Fee 116329	2026/2027	1	20.00	2026-11-11	\N	ACTIVE	2026-10-22 17:29:52.116753+03	2026-10-22 17:29:52.116755+03	Monthly	\N	\N
14	Dup Test Fee 314520	2026/2027	\N	30.00	2026-11-01	\N	ACTIVE	2026-10-22 17:29:52.314826+03	2026-10-22 17:29:52.314828+03	Annual	\N	\N
15	Tuition Step Payment 366778	2026/2027	\N	50.00	2026-11-01	\N	ACTIVE	2026-10-22 17:29:52.367123+03	2026-10-22 17:29:52.367126+03	Monthly	\N	\N
16	Overpay Test 501326	2026/2027	\N	40.00	2026-11-01	\N	ACTIVE	2026-10-22 17:29:52.501661+03	2026-10-22 17:29:52.501664+03	Monthly	\N	\N
17	Receipt Test Fee 539642	2026/2027	\N	35.00	2026-10-27	\N	ACTIVE	2026-10-22 17:29:52.540341+03	2026-10-22 17:29:52.540346+03	Term	\N	\N
18	Past Due Fee 619287	2026/2027	\N	45.00	2026-10-17	\N	ACTIVE	2026-10-22 17:29:52.619839+03	2026-10-22 17:29:52.619842+03	Monthly	\N	\N
19	Void Test Fee 693222	2026/2027	\N	60.00	2026-11-01	\N	ACTIVE	2026-10-22 17:29:52.693861+03	2026-10-22 17:29:52.693866+03	Monthly	\N	\N
21	Receipt Test Fee 535369	2026/2027	\N	35.00	2026-10-27	\N	ACTIVE	2026-10-22 17:31:11.536894+03	2026-10-22 17:31:11.536897+03	Term	\N	\N
\.


--
-- Data for Name: form_master_assignments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.form_master_assignments (id, teacher_id, class_id, academic_year, status, notes, appointed_by_id, appointed_at, revoked_by_id, revoked_at, created_at, updated_at) FROM stdin;
9	16	88	2026/2027	ACTIVE	Supervising 2 classes	406	2026-11-13 08:59:31.09945+03	\N	\N	2026-11-13 08:59:31.099829+03	2026-11-13 08:59:31.099832+03
10	16	89	2026/2027	ACTIVE	Supervising 2 classes	406	2026-11-13 08:59:31.106784+03	\N	\N	2026-11-13 08:59:31.107078+03	2026-11-13 08:59:31.10708+03
8	15	87	2026/2027	REVOKED	Appointed Form Master for Grade 7A [Revocation: Replaced by Ordinary Teacher. Handover to Teacher 1]	406	2026-11-13 08:59:31.070362+03	406	2026-11-13 08:59:31.46602+03	2026-11-13 08:59:31.071842+03	2026-11-13 08:59:31.467606+03
11	14	87	2026/2027	REVOKED	Replaced SingleClass Master. Handover to Teacher 1 [Revocation: Revoking appointment]	406	2026-11-13 08:59:31.47243+03	406	2026-11-13 08:59:31.518947+03	2026-11-13 08:59:31.472762+03	2026-11-13 08:59:31.519415+03
\.


--
-- Data for Name: inquiries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inquiries (id, full_name, school_name, email, phone, plan, message, status, priority, admin_notes, contacted_by, preferred_channel, source, converted_institution_id, created_at, updated_at) FROM stdin;
1	Dr. Cabdullahi Maxamed Warsame	Mogadishu Elite International Academy	cabdullahi@eliteacademy.edu.so	+252 61 888 9999	Dugsi / School — Professional (Full Suite & SMS)	Waxaan dooneynaa inaan diiwaangelino dugsigeena oo leh 650 arday iyo 35 macallin. Waxaan u baahannahay demo iyo heshiiska liisanka.	IN_REVIEW	HIGH	Wada-hadal hordhac ah ayaa lala yeeshay Dr. Cabdullahi. Wuxuu codsaday demo Khamiista.	Super Admin Team	WhatsApp	PUBLIC_LANDING_PAGE	\N	2026-10-22 17:47:03.173434+03	2026-10-22 17:47:04.390187+03
2	Dr. Cabdullahi Maxamed Warsame	Mogadishu Elite International Academy	cabdullahi@eliteacademy.edu.so	+252 61 888 9999	Dugsi / School — Professional (Full Suite & SMS)	Waxaan dooneynaa inaan diiwaangelino dugsigeena oo leh 650 arday iyo 35 macallin. Waxaan u baahannahay demo iyo heshiiska liisanka.	IN_REVIEW	HIGH	Wada-hadal hordhac ah ayaa lala yeeshay Dr. Cabdullahi. Wuxuu codsaday demo Khamiista.	Super Admin Team	WhatsApp	PUBLIC_LANDING_PAGE	\N	2026-10-22 18:07:14.18504+03	2026-10-22 18:07:15.36162+03
3	hoodo axmed bile	al khaadiriye	skycast45@gmail.com	+252619677779	Machad - Professional Institute	aadd ayan u raba	READ	NORMAL	\N	\N	WhatsApp	PUBLIC_LANDING_PAGE	\N	2026-10-22 18:09:16.603138+03	2026-10-22 18:09:26.288562+03
4	abdiraxmaan dirir	al jaahiliya	dirir@gmail.com	+252619677779	Machad - Professional Institute	wll ila so xariira	READ	NORMAL	\N	\N	WhatsApp	PUBLIC_LANDING_PAGE	\N	2026-10-22 18:14:03.857488+03	2026-10-22 18:14:21.559574+03
5	abdirashid axmed	school	mahad7@gmail.com	0009988	School - General Inquiry	ndffnsm	READ	NORMAL	\N	\N	WhatsApp	PUBLIC_LANDING_PAGE	\N	2026-11-13 18:34:00.868901+03	2026-11-13 18:34:58.912979+03
\.


--
-- Data for Name: institution_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institution_payments (id, institution_id, subscription_id, reference, amount, currency, payment_method, payment_date, status, invoice_number, notes, created_at) FROM stdin;
8	8	8	PAY-SOM-SCH-0002-202610220918	420.00	USD	EVC Plus	2026-10-22 09:18:11	Completed	INV-SOM-SCH-0002-001	Initial onboarding and licensing fee.	2026-10-22 09:18:11
9	9	9	PAY-SOM-SCH-0003-202611121133	420.00	USD	EVC Plus	2026-11-12 11:33:25.17901	Completed	INV-SOM-SCH-0003-001	Initial onboarding and licensing fee.	2026-11-12 11:33:25.17901
10	16	10	PAY-SOM-SCH-0006-202611121247	420.00	USD	EVC Plus	2026-11-12 12:47:15.627021	Completed	INV-SOM-SCH-0006-001	Initial onboarding and licensing fee.	2026-11-12 12:47:15.627021
11	17	11	PAY-SOM-SCH-0007-202611131056	320.00	USD	EVC Plus	2026-11-13 10:56:46.451992	Completed	INV-SOM-SCH-0007-001	Initial onboarding and licensing fee.	2026-11-13 10:56:46.451992
12	18	12	PAY-SOM-SCH-0008-202611131838	420.00	USD	EVC Plus	2026-11-13 18:38:19.490147	Completed	INV-SOM-SCH-0008-001	Initial onboarding and licensing fee.	2026-11-13 18:38:19.490147
\.


--
-- Data for Name: institutions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institutions (id, code, name, type, logo_url, contact_person, email, phone, region, city, address, status, database_name, provisioning_status, provisioning_error, admin_email, admin_username, subscription_plan, subscription_status, subscription_start_date, subscription_expiry_date, admin_user_id, created_at, updated_at) FROM stdin;
13	SOM-ACD-0001	Al-Huda Academy	Academy	/uploads/institution_logos/logo_alhuda.png	\N	\N	\N	\N	Mogadishu	KM4, Airport Road	ACTIVE	sms_al_huda_academy	PROVISIONED	\N	admin@alhuda.edu.so	admin_alhuda	Professional School	ACTIVE	\N	\N	1	2026-11-12 12:08:48.302211	2026-11-12 12:08:48.498505
14	SOM-SCH-0004	Waberi Secondary School	Secondary School	/uploads/institution_logos/logo_waberi.png	\N	\N	\N	\N	Mogadishu	21 October Road, Waberi	ACTIVE	sms_waberi_secondary_school	PROVISIONED	\N	admin@waberi.edu.so	admin_waberi	Professional School	ACTIVE	\N	\N	1	2026-11-12 12:08:53.202176	2026-11-12 12:08:53.367014
15	SOM-SCH-0005	Kulan Primary School	Primary School	/uploads/institution_logos/logo_kulan.png	\N	\N	\N	\N	Kismayo	Via Kismayo Main Blvd	ACTIVE	sms_kulan_primary_school	PROVISIONED	\N	admin@kulan.edu.so	admin_kulan	Professional School	ACTIVE	\N	\N	1	2026-11-12 12:08:57.754858	2026-11-12 12:08:57.940903
16	SOM-SCH-0006	hormuud	Primary & Secondary School	/uploads/institution_logos/logo_abaf5124c35e_1794476835.jpg	M-Ali Mire	alimire8x14@gmail.com	+252 61 9838377	Banaadir	Mogadishu	2020 Bentworth Dr	ACTIVE	sms_hormuud	PROVISIONED	\N	alimiy@gmail.com	hormuud	Professional School	ACTIVE	2026-11-12	2027-11-12	1	2026-11-12 12:47:15.627021	2026-11-12 12:47:15.627021
8	SOM-SCH-0002	garasale primary school	University	\N	\N	\N	+252 61 6147360	Galgaduud	cabudwaak	waabari	ACTIVE	somroyal_garasale_primary_school	PROVISIONED	\N	alimire8x14@gmail.com	garasle	Professional School	ACTIVE	2026-10-22	2027-10-22	1	2026-10-22 09:18:05	2026-10-22 18:51:50.291544
9	SOM-SCH-0003	hirdo	Primary & Secondary School	\N	xuseen muuse	su7@somroyal.com	+252 61	Galgaduud	abudwak	waabari	ACTIVE	somroyal_hirdo	PROVISIONED	\N	quule@somroyal.com	hirdo@gmail.com	Professional School	ACTIVE	2026-11-12	2027-11-12	1	2026-11-12 11:33:25.17901	2026-11-12 11:33:25.17901
1	SOM-SCH-0001	Hawlwadaag Secondary School	Secondary School	\N	Principal Ahmed	admin@hawlwadaagschool.edu.so	+252 61 5000001	Banaadir	Mogadishu	Hawlwadaag District, Mogadishu	ACTIVE	sms	PROVISIONED	\N	admin@hawlwadaagschool.edu.so	admin	Professional School	ACTIVE	2026-10-22	2027-10-22	1	2026-10-22 08:51:41	2026-10-22 18:51:48.908092
17	SOM-SCH-0007	al ixsaan	Primary & Secondary School	/uploads/institution_logos/logo_aa9603ae64d1_1794556606.png	mahad cabdirisaq	mahad@gmail.com	+252 61 8987662	Galgaduud	cabudwaq	horseed	ACTIVE	sms_al_ixsaan	PROVISIONED	\N	mahad@gmail.com	ixsaan	Starter Academy	ACTIVE	2026-11-13	2027-11-13	1	2026-11-13 10:56:46.451992	2026-11-13 10:56:46.451992
18	SOM-SCH-0008	savana school	Primary & Secondary School	\N	dirir jama	dirir@gmail.com	+252 61 6765447	Galgaduud	cabudwaq	waabari	ACTIVE	sms_savana_school	PROVISIONED	\N	dirir45@gmail.com	savana123	Professional School	ACTIVE	2026-11-13	2027-11-13	1	2026-11-13 18:38:19.490147	2026-11-13 18:38:19.490147
\.


--
-- Data for Name: notification_deliveries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification_deliveries (id, notification_id, channel, recipient, provider_name, provider_message_id, status, error_code, error_message, attempt_number, sent_at, delivered_at, created_at) FROM stdin;
1	3	SMS	252615551111	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:42:59.074632+03
2	4	SMS	252615552222	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:42:59.092083+03
3	16	SMS	252615550001	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.900879+03
4	17	SMS	252615550002	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.912422+03
5	18	SMS	252615550003	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.92115+03
6	19	SMS	252615550004	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.929848+03
7	20	SMS	252615550005	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.936741+03
8	21	SMS	252615550006	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.943639+03
9	22	SMS	252615550007	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.951303+03
10	23	SMS	252615550008	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.958941+03
11	24	SMS	252615550009	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.966646+03
12	25	SMS	252615550010	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.973248+03
13	26	SMS	252615550011	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.981321+03
14	27	SMS	252615550012	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.987896+03
15	28	SMS	252615550013	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:02.996357+03
16	29	SMS	252615550014	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.003322+03
17	30	SMS	252615550015	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.010064+03
18	31	SMS	252615550016	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.016521+03
19	32	SMS	252615550017	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.023027+03
20	33	SMS	252615550018	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.032354+03
21	34	SMS	252615550019	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.039031+03
22	35	SMS	252615550020	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.04833+03
23	36	SMS	252615550021	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.05539+03
24	37	SMS	252615550022	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.063208+03
25	38	SMS	252615550023	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.068823+03
26	39	SMS	252615550024	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.076258+03
27	40	SMS	252615550025	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.083989+03
28	41	SMS	252615550026	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.091536+03
29	42	SMS	252615550027	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.098006+03
30	43	SMS	252615550028	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.104736+03
31	44	SMS	252615550029	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.112257+03
32	45	SMS	252615550030	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.118552+03
33	47	SMS	252615550001	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.868626+03
34	48	SMS	252615550002	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.874729+03
35	49	SMS	252615550003	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.881056+03
36	50	SMS	252615550004	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.886164+03
37	51	SMS	252615550005	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.891987+03
38	52	SMS	252615550006	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.898008+03
39	53	SMS	252615550007	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.903397+03
40	54	SMS	252615550008	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.910308+03
41	55	SMS	252615550009	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.917359+03
42	56	SMS	252615550010	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.927621+03
43	57	SMS	252615550011	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.934297+03
44	58	SMS	252615550012	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.940414+03
45	59	SMS	252615550013	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.948262+03
46	60	SMS	252615550014	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.954518+03
47	61	SMS	252615550015	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.962199+03
48	62	SMS	252615550016	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.968479+03
49	63	SMS	252615550017	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.974845+03
50	64	SMS	252615550018	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.982263+03
51	65	SMS	252615550019	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.987647+03
52	66	SMS	252615550020	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:03.996266+03
53	67	SMS	252615550021	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.003172+03
54	68	SMS	252615550022	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.011494+03
55	69	SMS	252615550023	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.018942+03
56	70	SMS	252615550024	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.026636+03
57	71	SMS	252615550025	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.033519+03
58	72	SMS	252615550026	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.03948+03
59	73	SMS	252615550027	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.048058+03
60	74	SMS	252615550028	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.055467+03
61	75	SMS	252615550029	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.064507+03
62	76	SMS	252615550030	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:04.07196+03
83	97	SMS	252615999888	Hormuud SMS	HORMUUD-MSG-DLR-88263cbd	DELIVERED	\N	\N	1	2026-09-21 01:43:18.5487+03	2026-09-21 01:43:18.582062+03	2026-09-21 01:43:18.5487+03
87	101	SMS	252611234501	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:20.231402+03
89	105	SMS	252611234501	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:20.978714+03
90	106	SMS	252611234501	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:21.004609+03
63	77	SMS	252611234501	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.393588+03
64	78	SMS	252611234502	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.411319+03
65	79	SMS	252611234503	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.417509+03
66	80	SMS	252611234504	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.424694+03
67	81	SMS	252611234505	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.431824+03
68	82	SMS	252611234506	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.437446+03
69	83	SMS	252611234507	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.444357+03
70	84	SMS	252611234508	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.449838+03
71	85	SMS	252611234509	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.455316+03
72	86	SMS	252611234510	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.461861+03
73	87	SMS	252611234511	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.466729+03
74	88	SMS	252611234512	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.471456+03
75	89	SMS	252611234513	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.478555+03
76	90	SMS	252611234514	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.484324+03
77	91	SMS	252611234515	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.490169+03
78	92	SMS	252611234516	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.497708+03
79	93	SMS	252611234517	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.504146+03
80	94	SMS	252611234518	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.51172+03
81	95	SMS	252611234519	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.518485+03
82	96	SMS	252611234520	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-09-21 01:43:16.354055+03	\N	2026-09-21 01:43:16.524433+03
86	100	SMS	252615888777	Hormuud SMS	HORMUUD-RETRY-SUCCESS	SENT	\N	\N	2	2026-09-21 01:43:19.137636+03	\N	2026-09-21 01:43:19.170937+03
88	102	SMS	252611234501	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-09-21 01:43:20.820228+03
91	116	SMS	252611234501	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.074372+03
92	117	SMS	252611234502	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.094585+03
93	118	SMS	252611234503	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.098714+03
94	119	SMS	252611234504	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.102164+03
95	120	SMS	252611234505	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.105565+03
96	121	SMS	252611234506	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.110818+03
97	122	SMS	252611234507	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.11438+03
98	123	SMS	252611234508	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.11798+03
99	124	SMS	252611234509	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.121039+03
100	125	SMS	252611234510	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.126525+03
101	126	SMS	252611234511	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.130729+03
102	127	SMS	252611234512	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.134304+03
103	128	SMS	252611234513	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.137665+03
104	129	SMS	252611234514	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.142826+03
105	130	SMS	252611234515	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.146547+03
106	131	SMS	252611234516	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.149859+03
107	132	SMS	252611234517	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.152921+03
108	133	SMS	252611234518	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.155957+03
109	134	SMS	252611234519	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.161519+03
110	135	SMS	252611234520	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.164713+03
111	136	SMS	252615554433	Hormuud SMS	HORMUUD-FEE-MSG-01	SENT	\N	\N	1	2026-10-22 17:29:52.99518+03	\N	2026-10-22 17:29:53.167698+03
112	202	SMS	252611234503	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-10-23 23:31:20.818733+03
113	211	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:02:05.940117+03
114	214	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:02:06.134466+03
115	215	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:02:06.149597+03
116	217	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:04:28.772494+03
117	220	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:04:28.866937+03
118	221	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:04:28.88415+03
119	223	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:13:52.355471+03
120	226	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:13:52.575913+03
121	227	SMS	252611234509	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-12 10:13:52.595056+03
122	228	SMS	252611234503	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-13 09:59:30.268948+03
123	229	SMS	252611234501	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-13 13:02:13.905956+03
124	230	SMS	252611234501	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-13 16:01:51.679319+03
125	231	SMS	252611234503	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-13 16:01:53.090418+03
126	236	SMS	252611234501	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-13 16:04:13.932532+03
127	237	SMS	252611234503	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-13 16:04:15.518895+03
128	239	SMS	252611234501	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-13 16:09:38.783668+03
129	240	SMS	252611234503	Hormuud SMS	\N	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	Hormuud SMS is not enabled or credentials are missing in system environment.	1	\N	\N	2026-11-13 16:09:39.853342+03
\.


--
-- Data for Name: notification_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification_templates (id, code, name, title_template, body_template, category, is_active, is_system, created_at, updated_at) FROM stdin;
14	RESULT_RELEASED	Exam Results Release Notice (Somali)	Natiijada Imtixaanka - {{student_name}}	Asc {{guardian_name}}, waxaan ku ogeysiinaynaa in natiijada {{student_name}} ee {{exam_name}} la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — {{school_name}}	EXAMS	t	t	2026-09-17 11:47:03.939833+03	2026-09-17 12:40:56.672598+03
15	FEE_REMINDER	Tuition & Fee Balance Reminder (Somali)	Xasuusin Lacagta Dugsiga - {{student_name}}	Asc {{guardian_name}}, waxaan ku xasuusinaynaa in ardaygaaga {{student_name}} uu leeyahay lacag dugsi oo dhan {{fee_balance}} oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — {{school_name}}	FINANCE	t	t	2026-09-17 11:47:03.939835+03	2026-09-17 12:40:56.672602+03
16	GENERAL_ANNOUNCEMENT	General School Announcement (Somali)	Ogeysiis Muhiim ah - {{school_name}}	Asc {{guardian_name}}, waxaa jira ogeysiis cusub oo ka yimid {{school_name}}. Fadlan gal Student Portal si aad u akhrido faahfaahinta ogeysiiska.	GENERAL	t	t	2026-09-17 11:47:03.939836+03	2026-09-17 12:40:56.672604+03
13	ATTENDANCE_ABSENT	Student Absence Alert (Somali)	Ogeysiis Maqnaansho - {{student_name}}	Asc {{guardian_name}}, waxaan ku ogeysiinaynaa in ardaygaaga {{student_name}} maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}	ATTENDANCE	t	t	2026-09-17 11:47:03.939829+03	2026-11-12 10:13:51.901883+03
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, notification_type, title, message, channel, status, failure_reason, student_id, guardian_name, guardian_phone, guardian_email, guardian_relationship, class_id, academic_year, related_attendance_id, related_exam_id, related_result_id, related_release_batch_id, idempotency_key, created_by_id, created_at, updated_at, sent_at, delivered_at, read_at, attempt_count, extra_data) FROM stdin;
214	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Ibrahim Abdi Warsame	Asc Guardian Abdi Warsame, waxaan ku ogeysiinaynaa in ardaygaaga Ibrahim Abdi Warsame maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:02:06.129644+03	2026-11-12 10:13:52.652174+03	\N	\N	2026-11-12 10:13:52.650895+03	1	\N
215	FEE_REMINDER	Xasuusin Lacagta Dugsiga - Ibrahim Abdi Warsame	Asc Guardian Abdi Warsame, waxaan ku xasuusinaynaa in ardaygaaga Ibrahim Abdi Warsame uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:02:06.144637+03	2026-11-12 10:13:52.652174+03	\N	\N	2026-11-12 10:13:52.650895+03	1	\N
217	GENERAL_ANNOUNCEMENT	Hawlwadaag School Notice	Asc Guardian Abdi Warsame, ardayga Ibrahim Abdi Warsame wuxuu helay ogeysiis.	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:04:28.750096+03	2026-11-12 10:13:52.652174+03	\N	\N	2026-11-12 10:13:52.650895+03	1	\N
218	GENERAL_ANNOUNCEMENT	Missing Contact Notice	Hello parent	SMS	READ	MISSING_CONTACT	156	Parent/Guardian	\N	\N	Guardian	80	2026/2027	\N	\N	\N	\N	\N	1	2026-11-12 10:04:28.791082+03	2026-11-12 10:13:52.652174+03	\N	\N	2026-11-12 10:13:52.650895+03	0	\N
219	CUSTOM	Invalid Phone Test	Hello parent	SMS	READ	INVALID_CONTACT	156	Parent/Guardian	invalid-phone	\N	Guardian	80	2026/2027	\N	\N	\N	\N	\N	1	2026-11-12 10:04:28.805205+03	2026-11-12 10:13:52.652174+03	\N	\N	2026-11-12 10:13:52.650895+03	0	\N
220	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Ibrahim Abdi Warsame	Asc Guardian Abdi Warsame, waxaan ku ogeysiinaynaa in ardaygaaga Ibrahim Abdi Warsame maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:04:28.861504+03	2026-11-12 10:13:52.652174+03	\N	\N	2026-11-12 10:13:52.650895+03	1	\N
3	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Noor	Asc Abdi Noor, waxaan ku ogeysiinaynaa in natiijada Mustaf Noor ee Admin Redesign Mid-Term 2026 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	21	Abdi Noor	+252615551111	abdi@test.so	\N	3	2026-2027	\N	\N	\N	1	result_release:21:batch:1	1	2026-09-21 01:42:59.046279+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
222	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Student1_1 A. Surname6582	Asc Waalidka, waxaan ku ogeysiinaynaa in ardaygaaga Student1_1 A. Surname6582 maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	156	Parent/Guardian	\N	\N	Guardian	1	2025/2026	51	\N	\N	\N	attendance:51:student:156:date:2026-06-10	1	2026-11-12 10:13:52.000866+03	2026-11-12 10:13:52.652174+03	\N	\N	2026-11-12 10:13:52.650895+03	0	\N
223	GENERAL_ANNOUNCEMENT	Hawlwadaag School Notice	Asc Guardian Abdi Warsame, ardayga Ibrahim Abdi Warsame wuxuu helay ogeysiis.	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:13:52.323408+03	2026-11-12 10:14:04.615845+03	\N	\N	\N	1	\N
224	GENERAL_ANNOUNCEMENT	Missing Contact Notice	Hello parent	SMS	READ	MISSING_CONTACT	156	Parent/Guardian	\N	\N	Guardian	80	2026/2027	\N	\N	\N	\N	\N	1	2026-11-12 10:13:52.485177+03	2026-11-12 10:14:04.61585+03	\N	\N	\N	0	\N
225	CUSTOM	Invalid Phone Test	Hello parent	SMS	READ	INVALID_CONTACT	156	Parent/Guardian	invalid-phone	\N	Guardian	80	2026/2027	\N	\N	\N	\N	\N	1	2026-11-12 10:13:52.502217+03	2026-11-12 10:14:04.615851+03	\N	\N	\N	0	\N
226	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Ibrahim Abdi Warsame	Asc Guardian Abdi Warsame, waxaan ku ogeysiinaynaa in ardaygaaga Ibrahim Abdi Warsame maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:13:52.569142+03	2026-11-12 10:14:04.615852+03	\N	\N	\N	1	\N
14	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Computer - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	13	\N	\N	\N	308	2026-09-21 01:43:02.254524+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 13, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Computer", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:02.212632+00:00", "link": "/admin/results"}
15	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Physical Education - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	14	\N	\N	\N	308	2026-09-21 01:43:02.622131+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 14, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Physical Education", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:02.597318+00:00", "link": "/admin/results"}
227	FEE_REMINDER	Xasuusin Lacagta Dugsiga - Ibrahim Abdi Warsame	Asc Guardian Abdi Warsame, waxaan ku xasuusinaynaa in ardaygaaga Ibrahim Abdi Warsame uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:13:52.588882+03	2026-11-12 10:14:04.615852+03	\N	\N	\N	1	\N
228	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Abdiqadir Omar Yusuf	Asc Guardian Omar Yusuf, waxaan ku ogeysiinaynaa in ardaygaaga Abdiqadir Omar Yusuf maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	3	Guardian Omar Yusuf	+252611234503	\N	Parent	1	2025-2026	\N	\N	\N	\N	attendance:57:student:3:date:2026-11-13	304	2026-11-13 09:59:30.167154+03	2026-11-13 09:59:30.272968+03	\N	\N	\N	1	\N
23	RESULT_RELEASED	Natiijada Imtixaanka - Student08 GradeSeven	Asc Guardian 08, waxaan ku ogeysiinaynaa in natiijada Student08 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	30	Guardian 08	+252615550008	guardian8@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:30:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
24	RESULT_RELEASED	Natiijada Imtixaanka - Student09 GradeSeven	Asc Guardian 09, waxaan ku ogeysiinaynaa in natiijada Student09 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	31	Guardian 09	+252615550009	guardian9@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:31:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
25	RESULT_RELEASED	Natiijada Imtixaanka - Student10 GradeSeven	Asc Guardian 10, waxaan ku ogeysiinaynaa in natiijada Student10 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	32	Guardian 10	+252615550010	guardian10@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:32:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
122	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Mohamed Ali, waxaan ku xasuusinaynaa in ardaygaaga Yasin Mohamed Ali uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	7	Guardian Mohamed Ali	+252611234507	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:7:2026-10-22	367	2026-10-22 17:29:53.113643+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
31	RESULT_RELEASED	Natiijada Imtixaanka - Student16 GradeSeven	Asc Guardian 16, waxaan ku ogeysiinaynaa in natiijada Student16 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	38	Guardian 16	+252615550016	guardian16@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:38:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
32	RESULT_RELEASED	Natiijada Imtixaanka - Student17 GradeSeven	Asc Guardian 17, waxaan ku ogeysiinaynaa in natiijada Student17 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	39	Guardian 17	+252615550017	guardian17@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:39:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
123	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Hassan Aden, waxaan ku xasuusinaynaa in ardaygaaga Sahra Hassan Aden uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	8	Guardian Hassan Aden	+252611234508	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:8:2026-10-22	367	2026-10-22 17:29:53.117272+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
39	RESULT_RELEASED	Natiijada Imtixaanka - Student24 GradeSeven	Asc Guardian 24, waxaan ku ogeysiinaynaa in natiijada Student24 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	46	Guardian 24	+252615550024	guardian24@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:46:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
127	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ali Jama, waxaan ku xasuusinaynaa in ardaygaaga Nimco Ali Jama uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	12	Guardian Ali Jama	+252611234512	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:12:2026-10-22	367	2026-10-22 17:29:53.133539+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
229	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Mohamed Ali Mire	Asc Guardian Ahmed Ali, waxaan ku ogeysiinaynaa in ardaygaaga Mohamed Ali Mire maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	1	Guardian Ahmed Ali	+252611234501	\N	Parent	1	2025/2026	\N	\N	\N	\N	attendance:78:student:1:date:2026-11-13	418	2026-11-13 13:02:13.815019+03	2026-11-13 13:02:13.910174+03	\N	\N	\N	1	\N
230	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Mohamed Ali Mire	Asc Guardian Ahmed Ali, waxaan ku ogeysiinaynaa in ardaygaaga Mohamed Ali Mire maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	1	Guardian Ahmed Ali	+252611234501	\N	Parent	1	2025/2026	\N	\N	\N	\N	attendance:85:student:1:date:2026-11-13	418	2026-11-13 16:01:51.641993+03	2026-11-13 16:01:51.681718+03	\N	\N	\N	1	\N
51	RESULT_RELEASED	Natiijada Imtixaanka - Student05 GradeSeven	Asc Guardian 05, waxaan ku ogeysiinaynaa in natiijada Student05 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	27	Guardian 05	+252615550005	guardian5@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:27:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
129	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Hassan Mohamed, waxaan ku xasuusinaynaa in ardaygaaga Asma Hassan Mohamed uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	14	Guardian Hassan Mohamed	+252611234514	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:14:2026-10-22	367	2026-10-22 17:29:53.141532+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
52	RESULT_RELEASED	Natiijada Imtixaanka - Student06 GradeSeven	Asc Guardian 06, waxaan ku ogeysiinaynaa in natiijada Student06 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	28	Guardian 06	+252615550006	guardian6@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:28:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
53	RESULT_RELEASED	Natiijada Imtixaanka - Student07 GradeSeven	Asc Guardian 07, waxaan ku ogeysiinaynaa in natiijada Student07 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	29	Guardian 07	+252615550007	guardian7@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:29:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
130	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Yusuf Ahmed, waxaan ku xasuusinaynaa in ardaygaaga Abdirahman Yusuf Ahmed uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	15	Guardian Yusuf Ahmed	+252611234515	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:15:2026-10-22	367	2026-10-22 17:29:53.145803+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
231	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Abdiqadir Omar Yusuf	Asc Guardian Omar Yusuf, waxaan ku ogeysiinaynaa in ardaygaaga Abdiqadir Omar Yusuf maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	3	Guardian Omar Yusuf	+252611234503	\N	Parent	1	2025-2026	\N	\N	\N	\N	attendance:86:student:3:date:2026-11-13	304	2026-11-13 16:01:53.071878+03	2026-11-13 16:01:53.091079+03	\N	\N	\N	1	\N
133	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Abdi Mohamed, waxaan ku xasuusinaynaa in ardaygaaga Deqa Abdi Mohamed uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	18	Guardian Abdi Mohamed	+252611234518	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:18:2026-10-22	367	2026-10-22 17:29:53.155275+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
59	RESULT_RELEASED	Natiijada Imtixaanka - Student13 GradeSeven	Asc Guardian 13, waxaan ku ogeysiinaynaa in natiijada Student13 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	35	Guardian 13	+252615550013	guardian13@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:35:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
232	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Hassan LockStudent	Asc Waalidka, waxaan ku ogeysiinaynaa in ardaygaaga Hassan LockStudent maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_SENT	MISSING_CONTACT	230	Parent/Guardian	\N	\N	\N	94	2026/2027	\N	\N	\N	\N	attendance:110:student:230:date:2026-11-13	424	2026-11-13 16:03:27.473173+03	2026-11-13 16:03:27.505987+03	\N	\N	\N	0	\N
233	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Hassan LockStudent	Asc Waalidka, waxaan ku ogeysiinaynaa in ardaygaaga Hassan LockStudent maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_SENT	MISSING_CONTACT	230	Parent/Guardian	\N	\N	\N	94	2026/2027	\N	\N	\N	\N	attendance:113:student:230:date:2026-11-13	424	2026-11-13 16:03:44.326813+03	2026-11-13 16:03:44.367371+03	\N	\N	\N	0	\N
234	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Hassan LockStudent	Asc Waalidka, waxaan ku ogeysiinaynaa in ardaygaaga Hassan LockStudent maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_SENT	MISSING_CONTACT	230	Parent/Guardian	\N	\N	\N	94	2026/2027	\N	\N	\N	\N	attendance:116:student:230:date:2026-11-13	424	2026-11-13 16:04:03.355986+03	2026-11-13 16:04:03.3931+03	\N	\N	\N	0	\N
237	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Abdiqadir Omar Yusuf	Asc Guardian Omar Yusuf, waxaan ku ogeysiinaynaa in ardaygaaga Abdiqadir Omar Yusuf maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	3	Guardian Omar Yusuf	+252611234503	\N	Parent	1	2025-2026	\N	\N	\N	\N	attendance:123:student:3:date:2026-11-13	304	2026-11-13 16:04:15.515664+03	2026-11-13 16:04:15.520157+03	\N	\N	\N	1	\N
235	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Hassan LockStudent	Asc Waalidka, waxaan ku ogeysiinaynaa in ardaygaaga Hassan LockStudent maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_SENT	MISSING_CONTACT	230	Parent/Guardian	\N	\N	\N	94	2026/2027	\N	\N	\N	\N	attendance:119:student:230:date:2026-11-13	424	2026-11-13 16:04:13.197755+03	2026-11-13 16:04:13.248347+03	\N	\N	\N	0	\N
236	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Mohamed Ali Mire	Asc Guardian Ahmed Ali, waxaan ku ogeysiinaynaa in ardaygaaga Mohamed Ali Mire maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	1	Guardian Ahmed Ali	+252611234501	\N	Parent	1	2025/2026	\N	\N	\N	\N	attendance:122:student:1:date:2026-11-13	418	2026-11-13 16:04:13.91881+03	2026-11-13 16:04:13.93369+03	\N	\N	\N	1	\N
97	ATTENDANCE_ABSENT	Maqnaansho	Test webhook alert	SMS	READ	\N	\N	\N	252615999888	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:18.5487+03	2026-11-12 10:04:28.930316+03	\N	2026-09-21 01:43:18.582062+03	2026-11-12 10:04:28.929294+03	1	\N
240	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Abdiqadir Omar Yusuf	Asc Guardian Omar Yusuf, waxaan ku ogeysiinaynaa in ardaygaaga Abdiqadir Omar Yusuf maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	NOT_CONFIGURED	PROVIDER_NOT_CONFIGURED	3	Guardian Omar Yusuf	+252611234503	\N	Parent	1	2025-2026	\N	\N	\N	\N	attendance:151:student:3:date:2026-11-13	304	2026-11-13 16:09:39.849609+03	2026-11-13 16:09:39.853837+03	\N	\N	\N	1	\N
238	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Hassan LockStudent	Asc Waalidka, waxaan ku ogeysiinaynaa in ardaygaaga Hassan LockStudent maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	230	Parent/Guardian	\N	\N	\N	94	2026/2027	147	\N	\N	\N	attendance:147:student:230:date:2026-11-13	424	2026-11-13 16:09:38.219749+03	2026-11-14 11:53:07.315883+03	\N	\N	2026-11-14 11:53:07.312102+03	0	\N
189	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	10	result_release:116:batch:10	1	2026-10-23 02:06:14.046781+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
221	FEE_REMINDER	Xasuusin Lacagta Dugsiga - Ibrahim Abdi Warsame	Asc Guardian Abdi Warsame, waxaan ku xasuusinaynaa in ardaygaaga Ibrahim Abdi Warsame uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:04:28.877396+03	2026-11-12 10:13:52.652174+03	\N	\N	2026-11-12 10:13:52.650895+03	1	\N
239	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Mohamed Ali Mire	Asc Guardian Ahmed Ali, waxaan ku ogeysiinaynaa in ardaygaaga Mohamed Ali Mire maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	1	Guardian Ahmed Ali	+252611234501	\N	Parent	1	2025/2026	150	\N	\N	\N	attendance:150:student:1:date:2026-11-13	418	2026-11-13 16:09:38.773386+03	2026-11-14 11:55:27.183974+03	\N	\N	2026-11-14 11:55:27.181951+03	1	\N
1	RESULT_SUBMITTED	New examination results submitted	Teacher Ali Warsame submitted results for Admin Redesign Mid-Term 2026 (Mathematics-Test - Grade 7-Test, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026-2027	\N	2	\N	\N	\N	305	2026-09-21 01:42:58.66848+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 2, "teacher_name": "Ali Warsame", "class_name": "Grade 7-Test", "subject_name": "Mathematics-Test", "exam_name": "Admin Redesign Mid-Term 2026", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:42:58.624134+00:00", "link": "/admin/results"}
140	RESULT_APPROVED	Results Approved by Administration	Results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	1	2026-10-23 00:38:41.168644+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 26, "approved_at": "2026-10-22T21:38:41.143660+00:00"}
205	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 23:31:34.167098+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 45, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-23T20:31:34.153027+00:00", "link": "/admin/results"}
206	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 23:31:34.226096+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 45, "approved_at": "2026-10-23T20:31:34.214508+00:00"}
207	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	12	result_release:115:batch:12	1	2026-10-23 23:31:34.342943+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
2	RESULT_SUBMITTED	New examination results submitted	Teacher Ali Warsame submitted results for Admin Redesign Mid-Term 2026 (Mathematics-Test - Grade 7-Test, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026-2027	\N	2	\N	\N	\N	305	2026-09-21 01:42:58.955578+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 2, "teacher_name": "Ali Warsame", "class_name": "Grade 7-Test", "subject_name": "Mathematics-Test", "exam_name": "Admin Redesign Mid-Term 2026", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:42:58.943342+00:00", "link": "/admin/results"}
4	RESULT_RELEASED	Natiijada Imtixaanka - Amina Ibrahim	Asc Hassan Ibrahim, waxaan ku ogeysiinaynaa in natiijada Amina Ibrahim ee Admin Redesign Mid-Term 2026 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	22	Hassan Ibrahim	+252615552222	hassan@test.so	\N	3	2026-2027	\N	\N	\N	1	result_release:22:batch:1	1	2026-09-21 01:42:59.046279+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
5	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Mathematics - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	3	\N	\N	\N	308	2026-09-21 01:42:59.869764+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 3, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Mathematics", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:42:59.847369+00:00", "link": "/admin/results"}
6	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (English - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	4	\N	\N	\N	308	2026-09-21 01:43:00.096444+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 4, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "English", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:00.068769+00:00", "link": "/admin/results"}
7	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Somali - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	5	\N	\N	\N	308	2026-09-21 01:43:00.307426+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 5, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Somali", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:00.284730+00:00", "link": "/admin/results"}
8	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Chemistry - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	7	\N	\N	\N	308	2026-09-21 01:43:00.915236+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 7, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Chemistry", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:00.730430+00:00", "link": "/admin/results"}
9	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Biology - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	8	\N	\N	\N	308	2026-09-21 01:43:01.212054+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 8, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Biology", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:01.170861+00:00", "link": "/admin/results"}
10	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Geography - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	9	\N	\N	\N	308	2026-09-21 01:43:01.426392+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 9, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Geography", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:01.395387+00:00", "link": "/admin/results"}
11	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (History - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	10	\N	\N	\N	308	2026-09-21 01:43:01.620359+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 10, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "History", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:01.595073+00:00", "link": "/admin/results"}
12	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Islamic Studies - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	11	\N	\N	\N	308	2026-09-21 01:43:01.832788+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 11, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Islamic Studies", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:01.798565+00:00", "link": "/admin/results"}
13	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Arabic - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	12	\N	\N	\N	308	2026-09-21 01:43:02.027987+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 12, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Arabic", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:02.002497+00:00", "link": "/admin/results"}
109	EXAM_DEADLINE	New Examination Scheduled: TEST_Monthly_Exam_October	Official MONTHLY examination has been scheduled with result submission deadline: 2026-11-21 11:43.	IN_APP	READ	\N	\N	\N	\N	\N	\N	1	2025-2026	\N	\N	\N	\N	\N	370	2026-10-22 11:43:16.936443+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"exam_id": 21, "exam_name": "TEST_Monthly_Exam_October", "deadline": "2026-11-21T11:43:16.826589"}
116	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ahmed Ali, waxaan ku xasuusinaynaa in ardaygaaga Mohamed Ali Mire uu leeyahay lacag dugsi oo dhan $230.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	1	Guardian Ahmed Ali	+252611234501	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:1:2026-10-22	367	2026-10-22 17:29:53.061884+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
110	EXAM_DEADLINE	Submission Deadline Extended: TEST_Monthly_Exam_October	The result submission deadline for TEST_Monthly_Exam_October has been extended to 2026-11-05 08:43. Reason: School term extended by 2 weeks due to national holidays.	IN_APP	READ	\N	\N	\N	\N	\N	\N	1	2025-2026	\N	\N	\N	\N	\N	370	2026-10-22 11:43:17.226004+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"exam_id": 21, "exam_name": "TEST_Monthly_Exam_October", "deadline": "2026-11-05T11:43:17.194912"}
16	RESULT_RELEASED	Natiijada Imtixaanka - Student01 GradeSeven	Asc Guardian 01, waxaan ku ogeysiinaynaa in natiijada Student01 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	23	Guardian 01	+252615550001	guardian1@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:23:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
17	RESULT_RELEASED	Natiijada Imtixaanka - Student02 GradeSeven	Asc Guardian 02, waxaan ku ogeysiinaynaa in natiijada Student02 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	24	Guardian 02	+252615550002	guardian2@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:24:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
18	RESULT_RELEASED	Natiijada Imtixaanka - Student03 GradeSeven	Asc Guardian 03, waxaan ku ogeysiinaynaa in natiijada Student03 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	25	Guardian 03	+252615550003	guardian3@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:25:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
111	EXAM_DEADLINE	New Examination Scheduled: TEST_Monthly_Exam_October	Official MONTHLY examination has been scheduled with result submission deadline: 2026-11-21 11:43.	IN_APP	READ	\N	\N	\N	\N	\N	\N	1	2025-2026	\N	\N	\N	\N	\N	370	2026-10-22 11:43:41.08855+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"exam_id": 23, "exam_name": "TEST_Monthly_Exam_October", "deadline": "2026-11-21T11:43:40.982992"}
19	RESULT_RELEASED	Natiijada Imtixaanka - Student04 GradeSeven	Asc Guardian 04, waxaan ku ogeysiinaynaa in natiijada Student04 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	26	Guardian 04	+252615550004	guardian4@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:26:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
112	EXAM_DEADLINE	Submission Deadline Extended: TEST_Monthly_Exam_October	The result submission deadline for TEST_Monthly_Exam_October has been extended to 2026-11-05 08:43. Reason: School term extended by 2 weeks due to national holidays.	IN_APP	READ	\N	\N	\N	\N	\N	\N	1	2025-2026	\N	\N	\N	\N	\N	370	2026-10-22 11:43:41.234718+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"exam_id": 23, "exam_name": "TEST_Monthly_Exam_October", "deadline": "2026-11-05T11:43:41.209208"}
20	RESULT_RELEASED	Natiijada Imtixaanka - Student05 GradeSeven	Asc Guardian 05, waxaan ku ogeysiinaynaa in natiijada Student05 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	27	Guardian 05	+252615550005	guardian5@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:27:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
21	RESULT_RELEASED	Natiijada Imtixaanka - Student06 GradeSeven	Asc Guardian 06, waxaan ku ogeysiinaynaa in natiijada Student06 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	28	Guardian 06	+252615550006	guardian6@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:28:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
117	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Hassan Noor, waxaan ku xasuusinaynaa in ardaygaaga Amina Hassan Noor uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	2	Guardian Hassan Noor	+252611234502	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:2:2026-10-22	367	2026-10-22 17:29:53.093406+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
22	RESULT_RELEASED	Natiijada Imtixaanka - Student07 GradeSeven	Asc Guardian 07, waxaan ku ogeysiinaynaa in natiijada Student07 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	29	Guardian 07	+252615550007	guardian7@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:29:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
118	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Omar Yusuf, waxaan ku xasuusinaynaa in ardaygaaga Abdiqadir Omar Yusuf uu leeyahay lacag dugsi oo dhan $230.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	3	Guardian Omar Yusuf	+252611234503	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:3:2026-10-22	367	2026-10-22 17:29:53.097842+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
113	EXAM_DEADLINE	New Examination Scheduled: TEST_Monthly_Exam_October	Official MONTHLY examination has been scheduled with result submission deadline: 2026-11-21 11:44.	IN_APP	READ	\N	\N	\N	\N	\N	\N	1	2025-2026	\N	\N	\N	\N	\N	370	2026-10-22 11:44:07.532602+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"exam_id": 25, "exam_name": "TEST_Monthly_Exam_October", "deadline": "2026-11-21T11:44:07.448145"}
26	RESULT_RELEASED	Natiijada Imtixaanka - Student11 GradeSeven	Asc Guardian 11, waxaan ku ogeysiinaynaa in natiijada Student11 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	33	Guardian 11	+252615550011	guardian11@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:33:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
114	EXAM_DEADLINE	Submission Deadline Extended: TEST_Monthly_Exam_October	The result submission deadline for TEST_Monthly_Exam_October has been extended to 2026-11-05 08:44. Reason: School term extended by 2 weeks due to national holidays.	IN_APP	READ	\N	\N	\N	\N	\N	\N	1	2025-2026	\N	\N	\N	\N	\N	370	2026-10-22 11:44:07.657822+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"exam_id": 25, "exam_name": "TEST_Monthly_Exam_October", "deadline": "2026-11-05T11:44:07.635243"}
27	RESULT_RELEASED	Natiijada Imtixaanka - Student12 GradeSeven	Asc Guardian 12, waxaan ku ogeysiinaynaa in natiijada Student12 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	34	Guardian 12	+252615550012	guardian12@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:34:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
115	EXAM_DEADLINE	Submissions Reopened: TEST_Monthly_Exam_October	Results submission for TEST_Monthly_Exam_October has been officially reopened by Administration. Reason: Authorized reopening for mark verification.	IN_APP	READ	\N	\N	\N	\N	\N	\N	1	2025-2026	\N	\N	\N	\N	\N	370	2026-10-22 11:44:07.69999+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"exam_id": 25, "exam_name": "TEST_Monthly_Exam_October", "deadline": "2026-10-29T11:44:07.688517"}
28	RESULT_RELEASED	Natiijada Imtixaanka - Student13 GradeSeven	Asc Guardian 13, waxaan ku ogeysiinaynaa in natiijada Student13 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	35	Guardian 13	+252615550013	guardian13@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:35:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
119	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Mohamed Ibrahim, waxaan ku xasuusinaynaa in ardaygaaga Hodan Mohamed Ibrahim uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	4	Guardian Mohamed Ibrahim	+252611234504	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:4:2026-10-22	367	2026-10-22 17:29:53.101421+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
29	RESULT_RELEASED	Natiijada Imtixaanka - Student14 GradeSeven	Asc Guardian 14, waxaan ku ogeysiinaynaa in natiijada Student14 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	36	Guardian 14	+252615550014	guardian14@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:36:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
30	RESULT_RELEASED	Natiijada Imtixaanka - Student15 GradeSeven	Asc Guardian 15, waxaan ku ogeysiinaynaa in natiijada Student15 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	37	Guardian 15	+252615550015	guardian15@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:37:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
120	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ahmed Ismail, waxaan ku xasuusinaynaa in ardaygaaga Abdullahi Ahmed Ismail uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	5	Guardian Ahmed Ismail	+252611234505	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:5:2026-10-22	367	2026-10-22 17:29:53.104881+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
121	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Abdi Farah, waxaan ku xasuusinaynaa in ardaygaaga Maryan Abdi Farah uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	6	Guardian Abdi Farah	+252611234506	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:6:2026-10-22	367	2026-10-22 17:29:53.109818+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
33	RESULT_RELEASED	Natiijada Imtixaanka - Student18 GradeSeven	Asc Guardian 18, waxaan ku ogeysiinaynaa in natiijada Student18 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	40	Guardian 18	+252615550018	guardian18@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:40:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
34	RESULT_RELEASED	Natiijada Imtixaanka - Student19 GradeSeven	Asc Guardian 19, waxaan ku ogeysiinaynaa in natiijada Student19 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	41	Guardian 19	+252615550019	guardian19@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:41:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
124	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Abdi Warsame, waxaan ku xasuusinaynaa in ardaygaaga Ibrahim Abdi Warsame uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	9	Guardian Abdi Warsame	+252611234509	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:9:2026-10-22	367	2026-10-22 17:29:53.120372+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
35	RESULT_RELEASED	Natiijada Imtixaanka - Student20 GradeSeven	Asc Guardian 20, waxaan ku ogeysiinaynaa in natiijada Student20 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	42	Guardian 20	+252615550020	guardian20@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:42:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
36	RESULT_RELEASED	Natiijada Imtixaanka - Student21 GradeSeven	Asc Guardian 21, waxaan ku ogeysiinaynaa in natiijada Student21 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	43	Guardian 21	+252615550021	guardian21@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:43:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
125	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ahmed Osman, waxaan ku xasuusinaynaa in ardaygaaga Fadumo Ahmed Osman uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	10	Guardian Ahmed Osman	+252611234510	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:10:2026-10-22	367	2026-10-22 17:29:53.12497+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
37	RESULT_RELEASED	Natiijada Imtixaanka - Student22 GradeSeven	Asc Guardian 22, waxaan ku ogeysiinaynaa in natiijada Student22 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	44	Guardian 22	+252615550022	guardian22@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:44:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
38	RESULT_RELEASED	Natiijada Imtixaanka - Student23 GradeSeven	Asc Guardian 23, waxaan ku ogeysiinaynaa in natiijada Student23 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	45	Guardian 23	+252615550023	guardian23@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:45:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
126	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Mohamed Hassan, waxaan ku xasuusinaynaa in ardaygaaga Hamza Mohamed Hassan uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	11	Guardian Mohamed Hassan	+252611234511	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:11:2026-10-22	367	2026-10-22 17:29:53.129892+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
40	RESULT_RELEASED	Natiijada Imtixaanka - Student25 GradeSeven	Asc Guardian 25, waxaan ku ogeysiinaynaa in natiijada Student25 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	47	Guardian 25	+252615550025	guardian25@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:47:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
41	RESULT_RELEASED	Natiijada Imtixaanka - Student26 GradeSeven	Asc Guardian 26, waxaan ku ogeysiinaynaa in natiijada Student26 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	48	Guardian 26	+252615550026	guardian26@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:48:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
128	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Abdullahi Omar, waxaan ku xasuusinaynaa in ardaygaaga Mustafa Abdullahi Omar uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	13	Guardian Abdullahi Omar	+252611234513	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:13:2026-10-22	367	2026-10-22 17:29:53.136975+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
42	RESULT_RELEASED	Natiijada Imtixaanka - Student27 GradeSeven	Asc Guardian 27, waxaan ku ogeysiinaynaa in natiijada Student27 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	49	Guardian 27	+252615550027	guardian27@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:49:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
134	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ahmed Farah, waxaan ku xasuusinaynaa in ardaygaaga Suleiman Ahmed Farah uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	19	Guardian Ahmed Farah	+252611234519	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:19:2026-10-22	367	2026-10-22 17:29:53.160743+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
43	RESULT_RELEASED	Natiijada Imtixaanka - Student28 GradeSeven	Asc Guardian 28, waxaan ku ogeysiinaynaa in natiijada Student28 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	50	Guardian 28	+252615550028	guardian28@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:50:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
44	RESULT_RELEASED	Natiijada Imtixaanka - Student29 GradeSeven	Asc Guardian 29, waxaan ku ogeysiinaynaa in natiijada Student29 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	51	Guardian 29	+252615550029	guardian29@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:51:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
45	RESULT_RELEASED	Natiijada Imtixaanka - Student30 GradeSeven	Asc Guardian 30, waxaan ku ogeysiinaynaa in natiijada Student30 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	52	Guardian 30	+252615550030	guardian30@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	2	result_release:52:batch:2	1	2026-09-21 01:43:02.883419+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
46	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Ali submitted results for Mid-Term Examination 2026/2027 (Physics - Grade 7-12Subj, 2026-2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	5	2026-2027	\N	6	\N	\N	\N	308	2026-09-21 01:43:03.521049+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 6, "teacher_name": "Ahmed Ali", "class_name": "Grade 7-12Subj", "subject_name": "Physics", "exam_name": "Mid-Term Examination 2026/2027", "academic_year": "2026-2027", "submitted_at": "2026-09-20T22:43:03.497059+00:00", "link": "/admin/results"}
47	RESULT_RELEASED	Natiijada Imtixaanka - Student01 GradeSeven	Asc Guardian 01, waxaan ku ogeysiinaynaa in natiijada Student01 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	23	Guardian 01	+252615550001	guardian1@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:23:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
48	RESULT_RELEASED	Natiijada Imtixaanka - Student02 GradeSeven	Asc Guardian 02, waxaan ku ogeysiinaynaa in natiijada Student02 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	24	Guardian 02	+252615550002	guardian2@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:24:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
49	RESULT_RELEASED	Natiijada Imtixaanka - Student03 GradeSeven	Asc Guardian 03, waxaan ku ogeysiinaynaa in natiijada Student03 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	25	Guardian 03	+252615550003	guardian3@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:25:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
50	RESULT_RELEASED	Natiijada Imtixaanka - Student04 GradeSeven	Asc Guardian 04, waxaan ku ogeysiinaynaa in natiijada Student04 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	26	Guardian 04	+252615550004	guardian4@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:26:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
54	RESULT_RELEASED	Natiijada Imtixaanka - Student08 GradeSeven	Asc Guardian 08, waxaan ku ogeysiinaynaa in natiijada Student08 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	30	Guardian 08	+252615550008	guardian8@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:30:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
55	RESULT_RELEASED	Natiijada Imtixaanka - Student09 GradeSeven	Asc Guardian 09, waxaan ku ogeysiinaynaa in natiijada Student09 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	31	Guardian 09	+252615550009	guardian9@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:31:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
131	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Mohamed Abdi, waxaan ku xasuusinaynaa in ardaygaaga Khadra Mohamed Abdi uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	16	Guardian Mohamed Abdi	+252611234516	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:16:2026-10-22	367	2026-10-22 17:29:53.149156+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
56	RESULT_RELEASED	Natiijada Imtixaanka - Student10 GradeSeven	Asc Guardian 10, waxaan ku ogeysiinaynaa in natiijada Student10 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	32	Guardian 10	+252615550010	guardian10@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:32:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
57	RESULT_RELEASED	Natiijada Imtixaanka - Student11 GradeSeven	Asc Guardian 11, waxaan ku ogeysiinaynaa in natiijada Student11 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	33	Guardian 11	+252615550011	guardian11@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:33:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
132	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Hassan Ali, waxaan ku xasuusinaynaa in ardaygaaga Ismail Hassan Ali uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	17	Guardian Hassan Ali	+252611234517	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:17:2026-10-22	367	2026-10-22 17:29:53.15227+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
58	RESULT_RELEASED	Natiijada Imtixaanka - Student12 GradeSeven	Asc Guardian 12, waxaan ku ogeysiinaynaa in natiijada Student12 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	34	Guardian 12	+252615550012	guardian12@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:34:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
60	RESULT_RELEASED	Natiijada Imtixaanka - Student14 GradeSeven	Asc Guardian 14, waxaan ku ogeysiinaynaa in natiijada Student14 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	36	Guardian 14	+252615550014	guardian14@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:36:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
61	RESULT_RELEASED	Natiijada Imtixaanka - Student15 GradeSeven	Asc Guardian 15, waxaan ku ogeysiinaynaa in natiijada Student15 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	37	Guardian 15	+252615550015	guardian15@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:37:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
62	RESULT_RELEASED	Natiijada Imtixaanka - Student16 GradeSeven	Asc Guardian 16, waxaan ku ogeysiinaynaa in natiijada Student16 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	38	Guardian 16	+252615550016	guardian16@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:38:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
135	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Yusuf Hassan, waxaan ku xasuusinaynaa in ardaygaaga Rahma Yusuf Hassan uu leeyahay lacag dugsi oo dhan $40.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	20	Guardian Yusuf Hassan	+252611234520	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:20:2026-10-22	367	2026-10-22 17:29:53.164045+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
63	RESULT_RELEASED	Natiijada Imtixaanka - Student17 GradeSeven	Asc Guardian 17, waxaan ku ogeysiinaynaa in natiijada Student17 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	39	Guardian 17	+252615550017	guardian17@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:39:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
64	RESULT_RELEASED	Natiijada Imtixaanka - Student18 GradeSeven	Asc Guardian 18, waxaan ku ogeysiinaynaa in natiijada Student18 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	40	Guardian 18	+252615550018	guardian18@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:40:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
136	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Ali Warsame, waxaan ku xasuusinaynaa in ardaygaaga Khadija Ali Warsame uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	100	Ali Warsame	+252615554433	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:100:2026-10-22	367	2026-10-22 17:29:53.167045+03	2026-11-12 10:04:28.930316+03	2026-10-22 17:29:52.99518+03	\N	2026-11-12 10:04:28.929294+03	1	\N
65	RESULT_RELEASED	Natiijada Imtixaanka - Student19 GradeSeven	Asc Guardian 19, waxaan ku ogeysiinaynaa in natiijada Student19 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	41	Guardian 19	+252615550019	guardian19@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:41:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
163	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:01:54.326299+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 34, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:01:54.212312+00:00", "link": "/admin/results"}
66	RESULT_RELEASED	Natiijada Imtixaanka - Student20 GradeSeven	Asc Guardian 20, waxaan ku ogeysiinaynaa in natiijada Student20 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	42	Guardian 20	+252615550020	guardian20@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:42:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
164	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:01:55.624113+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 34, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-22T23:01:55.550252+00:00"}
137	RESULT_SUBMITTED	Examination Results Submitted	Teacher Ahmed Warsame submitted results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	373	2026-10-23 00:38:40.534576+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 26, "teacher_name": "Ahmed Warsame", "class_name": "Grade 7-Test", "subject_name": "Mathematics", "exam_name": "E2E Isolation Exam 2026", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:38:40.416112+00:00", "link": "/admin/results"}
67	RESULT_RELEASED	Natiijada Imtixaanka - Student21 GradeSeven	Asc Guardian 21, waxaan ku ogeysiinaynaa in natiijada Student21 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	43	Guardian 21	+252615550021	guardian21@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:43:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
138	RESULT_RETURNED	Results Returned for Correction	Results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test) have been returned by Administration for correction: Student STU-001 marks require recalculation.	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	1	2026-10-23 00:38:40.853349+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 26, "exam_id": 17, "reason": "Student STU-001 marks require recalculation.", "returned_at": "2026-10-22T21:38:40.770619+00:00"}
68	RESULT_RELEASED	Natiijada Imtixaanka - Student22 GradeSeven	Asc Guardian 22, waxaan ku ogeysiinaynaa in natiijada Student22 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	44	Guardian 22	+252615550022	guardian22@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:44:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
139	RESULT_SUBMITTED	Examination Results Submitted	Teacher Ahmed Warsame submitted results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	373	2026-10-23 00:38:41.11115+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 26, "teacher_name": "Ahmed Warsame", "class_name": "Grade 7-Test", "subject_name": "Mathematics", "exam_name": "E2E Isolation Exam 2026", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:38:41.081586+00:00", "link": "/admin/results"}
69	RESULT_RELEASED	Natiijada Imtixaanka - Student23 GradeSeven	Asc Guardian 23, waxaan ku ogeysiinaynaa in natiijada Student23 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	45	Guardian 23	+252615550023	guardian23@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:45:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
70	RESULT_RELEASED	Natiijada Imtixaanka - Student24 GradeSeven	Asc Guardian 24, waxaan ku ogeysiinaynaa in natiijada Student24 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	46	Guardian 24	+252615550024	guardian24@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:46:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
165	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:01:55.864036+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 34, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:01:55.826581+00:00", "link": "/admin/results"}
71	RESULT_RELEASED	Natiijada Imtixaanka - Student25 GradeSeven	Asc Guardian 25, waxaan ku ogeysiinaynaa in natiijada Student25 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	47	Guardian 25	+252615550025	guardian25@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:47:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
166	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:01:56.028076+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 34, "approved_at": "2026-10-22T23:01:55.990377+00:00"}
72	RESULT_RELEASED	Natiijada Imtixaanka - Student26 GradeSeven	Asc Guardian 26, waxaan ku ogeysiinaynaa in natiijada Student26 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	48	Guardian 26	+252615550026	guardian26@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:48:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
167	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	7	result_release:115:batch:7	1	2026-10-23 02:01:56.29762+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
73	RESULT_RELEASED	Natiijada Imtixaanka - Student27 GradeSeven	Asc Guardian 27, waxaan ku ogeysiinaynaa in natiijada Student27 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	49	Guardian 27	+252615550027	guardian27@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:49:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
168	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	7	result_release:116:batch:7	1	2026-10-23 02:01:56.29762+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
74	RESULT_RELEASED	Natiijada Imtixaanka - Student28 GradeSeven	Asc Guardian 28, waxaan ku ogeysiinaynaa in natiijada Student28 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	50	Guardian 28	+252615550028	guardian28@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:50:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
169	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	7	result_release:117:batch:7	1	2026-10-23 02:01:56.29762+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
141	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 00:46:41.827915+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 27, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:46:41.793623+00:00", "link": "/admin/results"}
75	RESULT_RELEASED	Natiijada Imtixaanka - Student29 GradeSeven	Asc Guardian 29, waxaan ku ogeysiinaynaa in natiijada Student29 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	51	Guardian 29	+252615550029	guardian29@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:51:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
142	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 00:46:43.152503+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 27, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-22T21:46:43.118662+00:00"}
76	RESULT_RELEASED	Natiijada Imtixaanka - Student30 GradeSeven	Asc Guardian 30, waxaan ku ogeysiinaynaa in natiijada Student30 GradeSeven ee Mid-Term Examination 2026/2027 la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	52	Guardian 30	+252615550030	guardian30@hawlwadaag.edu.so	\N	5	2026-2027	\N	\N	\N	3	result_release:52:batch:3	1	2026-09-21 01:43:03.864237+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
143	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 00:46:43.250981+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 27, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:46:43.230794+00:00", "link": "/admin/results"}
100	CUSTOM	Retry Test	Testing retry mechanism	SMS	READ	\N	\N	\N	252615888777	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:19.131446+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:19.137636+03	\N	2026-11-12 10:04:28.929294+03	2	\N
144	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 00:46:43.348934+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 27, "approved_at": "2026-10-22T21:46:43.337245+00:00"}
101	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Mohamed Ali Mire	Asc Guardian Ahmed Ali, waxaan ku ogeysiinaynaa in ardaygaaga Mohamed Ali Mire maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	1	Guardian Ahmed Ali	+252611234501	\N	Parent	1	2025/2026	4	\N	\N	\N	attendance:4:student:1:date:2026-06-10	1	2026-09-21 01:43:20.228308+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
103	GENERAL_ANNOUNCEMENT	Missing Contact Notice	Hello parent	SMS	READ	MISSING_CONTACT	78	Parent/Guardian	\N	\N	Guardian	9	2026/2027	\N	\N	\N	\N	\N	1	2026-09-21 01:43:20.852257+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
145	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	4	result_release:115:batch:4	1	2026-10-23 00:46:43.464034+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
105	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Mohamed Ali Mire	Asc Guardian Ahmed Ali, waxaan ku ogeysiinaynaa in ardaygaaga Mohamed Ali Mire maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	1	Guardian Ahmed Ali	+252611234501	\N	Parent	3	2026-2027	\N	\N	\N	\N	\N	1	2026-09-21 01:43:20.966273+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
146	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	4	result_release:116:batch:4	1	2026-10-23 00:46:43.464034+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
106	FEE_REMINDER	Xasuusin Lacagta Dugsiga - Mohamed Ali Mire	Asc Guardian Ahmed Ali, waxaan ku xasuusinaynaa in ardaygaaga Mohamed Ali Mire uu leeyahay lacag dugsi oo dhan $210.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	1	Guardian Ahmed Ali	+252611234501	\N	Parent	3	2026-2027	\N	\N	\N	\N	\N	1	2026-09-21 01:43:20.994765+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
107	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Warsame submitted results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	373	2026-09-21 01:43:21.163431+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 15, "teacher_name": "Ahmed Warsame", "class_name": "Grade 7-Test", "subject_name": "Mathematics", "exam_name": "E2E Isolation Exam 2026", "academic_year": "2026/2027", "submitted_at": "2026-09-20T22:43:21.147985+00:00", "link": "/admin/results"}
108	RESULT_SUBMITTED	New examination results submitted	Teacher Ahmed Warsame submitted results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	373	2026-09-21 01:43:21.388243+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 15, "teacher_name": "Ahmed Warsame", "class_name": "Grade 7-Test", "subject_name": "Mathematics", "exam_name": "E2E Isolation Exam 2026", "academic_year": "2026/2027", "submitted_at": "2026-09-20T22:43:21.365867+00:00", "link": "/admin/results"}
147	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	4	result_release:117:batch:4	1	2026-10-23 00:46:43.464034+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
170	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:04:27.368862+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 36, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:04:27.246008+00:00", "link": "/admin/results"}
171	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:04:28.753697+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 36, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-22T23:04:28.695002+00:00"}
148	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 00:47:09.159551+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 29, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:47:09.126722+00:00", "link": "/admin/results"}
77	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ahmed Ali, waxaan ku xasuusinaynaa in ardaygaaga Mohamed Ali Mire uu leeyahay lacag dugsi oo dhan $210.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	1	Guardian Ahmed Ali	+252611234501	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:1:2026-09-21	367	2026-09-21 01:43:16.38132+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
172	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:04:29.005718+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 36, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:04:28.962041+00:00", "link": "/admin/results"}
78	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Hassan Noor, waxaan ku xasuusinaynaa in ardaygaaga Amina Hassan Noor uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	2	Guardian Hassan Noor	+252611234502	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:2:2026-09-21	367	2026-09-21 01:43:16.409418+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
173	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:04:29.155692+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 36, "approved_at": "2026-10-22T23:04:29.134465+00:00"}
79	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Omar Yusuf, waxaan ku xasuusinaynaa in ardaygaaga Abdiqadir Omar Yusuf uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	3	Guardian Omar Yusuf	+252611234503	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:3:2026-09-21	367	2026-09-21 01:43:16.416374+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
159	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 00:50:13.75687+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 32, "approved_at": "2026-10-22T21:50:13.743333+00:00"}
174	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	8	result_release:115:batch:8	1	2026-10-23 02:04:29.42273+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
80	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Mohamed Ibrahim, waxaan ku xasuusinaynaa in ardaygaaga Hodan Mohamed Ibrahim uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	4	Guardian Mohamed Ibrahim	+252611234504	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:4:2026-09-21	367	2026-09-21 01:43:16.422293+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
175	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	8	result_release:116:batch:8	1	2026-10-23 02:04:29.42273+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
81	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ahmed Ismail, waxaan ku xasuusinaynaa in ardaygaaga Abdullahi Ahmed Ismail uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	5	Guardian Ahmed Ismail	+252611234505	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:5:2026-09-21	367	2026-09-21 01:43:16.430723+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
176	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	8	result_release:117:batch:8	1	2026-10-23 02:04:29.42273+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
82	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Abdi Farah, waxaan ku xasuusinaynaa in ardaygaaga Maryan Abdi Farah uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	6	Guardian Abdi Farah	+252611234506	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:6:2026-09-21	367	2026-09-21 01:43:16.436335+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
184	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:06:12.264981+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 40, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:06:11.920582+00:00", "link": "/admin/results"}
83	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Mohamed Ali, waxaan ku xasuusinaynaa in ardaygaaga Yasin Mohamed Ali uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	7	Guardian Mohamed Ali	+252611234507	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:7:2026-09-21	367	2026-09-21 01:43:16.442377+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
185	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:06:13.40352+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 40, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-22T23:06:13.331203+00:00"}
84	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Hassan Aden, waxaan ku xasuusinaynaa in ardaygaaga Sahra Hassan Aden uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	8	Guardian Hassan Aden	+252611234508	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:8:2026-09-21	367	2026-09-21 01:43:16.448767+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
188	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	10	result_release:115:batch:10	1	2026-10-23 02:06:14.046781+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
85	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Abdi Warsame, waxaan ku xasuusinaynaa in ardaygaaga Ibrahim Abdi Warsame uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	9	Guardian Abdi Warsame	+252611234509	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:9:2026-09-21	367	2026-09-21 01:43:16.453591+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
86	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ahmed Osman, waxaan ku xasuusinaynaa in ardaygaaga Fadumo Ahmed Osman uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	10	Guardian Ahmed Osman	+252611234510	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:10:2026-09-21	367	2026-09-21 01:43:16.4607+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
149	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 00:49:07.708519+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 30, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:49:07.669841+00:00", "link": "/admin/results"}
87	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Mohamed Hassan, waxaan ku xasuusinaynaa in ardaygaaga Hamza Mohamed Hassan uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	11	Guardian Mohamed Hassan	+252611234511	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:11:2026-09-21	367	2026-09-21 01:43:16.46553+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
150	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 00:49:08.358127+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 30, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-22T21:49:08.331804+00:00"}
88	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ali Jama, waxaan ku xasuusinaynaa in ardaygaaga Nimco Ali Jama uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	12	Guardian Ali Jama	+252611234512	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:12:2026-09-21	367	2026-09-21 01:43:16.470325+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
151	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 00:49:08.444715+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 30, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:49:08.431121+00:00", "link": "/admin/results"}
89	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Abdullahi Omar, waxaan ku xasuusinaynaa in ardaygaaga Mustafa Abdullahi Omar uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	13	Guardian Abdullahi Omar	+252611234513	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:13:2026-09-21	367	2026-09-21 01:43:16.476972+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
152	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 00:49:08.505966+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 30, "approved_at": "2026-10-22T21:49:08.494999+00:00"}
90	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Hassan Mohamed, waxaan ku xasuusinaynaa in ardaygaaga Asma Hassan Mohamed uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	14	Guardian Hassan Mohamed	+252611234514	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:14:2026-09-21	367	2026-09-21 01:43:16.483212+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
153	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	5	result_release:115:batch:5	1	2026-10-23 00:49:08.611847+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
91	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Yusuf Ahmed, waxaan ku xasuusinaynaa in ardaygaaga Abdirahman Yusuf Ahmed uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	15	Guardian Yusuf Ahmed	+252611234515	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:15:2026-09-21	367	2026-09-21 01:43:16.488701+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
154	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	5	result_release:116:batch:5	1	2026-10-23 00:49:08.611847+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
92	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Mohamed Abdi, waxaan ku xasuusinaynaa in ardaygaaga Khadra Mohamed Abdi uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	16	Guardian Mohamed Abdi	+252611234516	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:16:2026-09-21	367	2026-09-21 01:43:16.495793+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
155	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	5	result_release:117:batch:5	1	2026-10-23 00:49:08.611847+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
93	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Hassan Ali, waxaan ku xasuusinaynaa in ardaygaaga Ismail Hassan Ali uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	17	Guardian Hassan Ali	+252611234517	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:17:2026-09-21	367	2026-09-21 01:43:16.502915+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
177	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:05:10.66458+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 38, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:05:10.537674+00:00", "link": "/admin/results"}
94	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Abdi Mohamed, waxaan ku xasuusinaynaa in ardaygaaga Deqa Abdi Mohamed uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	18	Guardian Abdi Mohamed	+252611234518	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:18:2026-09-21	367	2026-09-21 01:43:16.510402+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
95	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Ahmed Farah, waxaan ku xasuusinaynaa in ardaygaaga Suleiman Ahmed Farah uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	19	Guardian Ahmed Farah	+252611234519	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:19:2026-09-21	367	2026-09-21 01:43:16.517236+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
156	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 00:50:13.092329+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 32, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:50:13.049165+00:00", "link": "/admin/results"}
96	FEE_REMINDER	Xasuusin Lacagta Dugsiga	Asc Guardian Yusuf Hassan, waxaan ku xasuusinaynaa in ardaygaaga Rahma Yusuf Hassan uu leeyahay lacag dugsi oo dhan $20.00 oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — Hawlwadaag School	SMS	READ	\N	20	Guardian Yusuf Hassan	+252611234520	\N	\N	\N	2026/2027	\N	\N	\N	\N	fee_reminder:20:2026-09-21	367	2026-09-21 01:43:16.522463+03	2026-11-12 10:04:28.930316+03	2026-09-21 01:43:16.354055+03	\N	2026-11-12 10:04:28.929294+03	1	\N
157	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 00:50:13.593961+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 32, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-22T21:50:13.557446+00:00"}
158	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 00:50:13.684573+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 32, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T21:50:13.670313+00:00", "link": "/admin/results"}
160	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	6	result_release:115:batch:6	1	2026-10-23 00:50:13.865991+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
161	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	6	result_release:116:batch:6	1	2026-10-23 00:50:13.865991+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
162	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	6	result_release:117:batch:6	1	2026-10-23 00:50:13.865991+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
102	GENERAL_ANNOUNCEMENT	Hawlwadaag School Notice	Asc Guardian Ahmed Ali, ardayga Mohamed Ali Mire wuxuu helay ogeysiis.	SMS	READ	PROVIDER_NOT_CONFIGURED	1	Guardian Ahmed Ali	+252611234501	\N	Parent	3	2026-2027	\N	\N	\N	\N	\N	1	2026-09-21 01:43:20.809232+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
104	CUSTOM	Invalid Phone Test	Hello parent	SMS	READ	INVALID_CONTACT	1	Guardian Ahmed Ali	invalid-phone	\N	Parent	3	2026-2027	\N	\N	\N	\N	\N	1	2026-09-21 01:43:20.875113+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
178	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:05:12.002422+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 38, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-22T23:05:11.923320+00:00"}
179	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:05:12.25154+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 38, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:05:12.212524+00:00", "link": "/admin/results"}
180	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:05:12.421813+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 38, "approved_at": "2026-10-22T23:05:12.388577+00:00"}
181	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	9	result_release:115:batch:9	1	2026-10-23 02:05:12.690081+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
182	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	9	result_release:116:batch:9	1	2026-10-23 02:05:12.690081+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
183	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	9	result_release:117:batch:9	1	2026-10-23 02:05:12.690081+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
186	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:06:13.642883+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 40, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:06:13.606207+00:00", "link": "/admin/results"}
187	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:06:13.803605+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 40, "approved_at": "2026-10-22T23:06:13.775119+00:00"}
190	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	10	result_release:117:batch:10	1	2026-10-23 02:06:14.046781+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
191	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:20:02.159018+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 42, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:20:02.042929+00:00", "link": "/admin/results"}
192	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:20:03.520868+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 42, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-22T23:20:03.451144+00:00"}
193	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 02:20:03.756973+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 42, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-22T23:20:03.718726+00:00", "link": "/admin/results"}
194	RESULT_APPROVED	Results Approved by Administration	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 02:20:03.906276+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 42, "approved_at": "2026-10-22T23:20:03.876844+00:00"}
195	RESULT_RELEASED	Natiijada Imtixaanka - Mustaf Farah	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Mustaf Farah ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	115	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	11	result_release:115:batch:11	1	2026-10-23 02:20:04.168496+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
196	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	11	result_release:116:batch:11	1	2026-10-23 02:20:04.168496+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
197	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	11	result_release:117:batch:11	1	2026-10-23 02:20:04.168496+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
198	RESULT_SUBMITTED	Examination Results Submitted	Teacher Ahmed Warsame submitted results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	373	2026-10-23 22:36:15.584392+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 44, "teacher_name": "Ahmed Warsame", "class_name": "Grade 7-Test", "subject_name": "Mathematics", "exam_name": "E2E Isolation Exam 2026", "academic_year": "2026/2027", "submitted_at": "2026-10-23T19:36:15.410509+00:00", "link": "/admin/results"}
199	RESULT_RETURNED	Results Returned for Correction	Results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test) have been returned by Administration for correction: Student STU-001 marks require recalculation.	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	1	2026-10-23 22:36:16.057716+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 44, "exam_id": 17, "reason": "Student STU-001 marks require recalculation.", "returned_at": "2026-10-23T19:36:15.952715+00:00"}
200	RESULT_SUBMITTED	Examination Results Submitted	Teacher Ahmed Warsame submitted results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	373	2026-10-23 22:36:16.762363+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 44, "teacher_name": "Ahmed Warsame", "class_name": "Grade 7-Test", "subject_name": "Mathematics", "exam_name": "E2E Isolation Exam 2026", "academic_year": "2026/2027", "submitted_at": "2026-10-23T19:36:16.697768+00:00", "link": "/admin/results"}
201	RESULT_APPROVED	Results Approved by Administration	Results for E2E Isolation Exam 2026 (Mathematics - Grade 7-Test) have been approved.	IN_APP	READ	\N	\N	\N	\N	\N	\N	3	2026/2027	\N	17	\N	\N	\N	1	2026-10-23 22:36:16.863691+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 44, "approved_at": "2026-10-23T19:36:16.819931+00:00"}
202	ATTENDANCE_ABSENT	Ogeysiis Maqnaansho - Abdiqadir Omar Yusuf	Asc Guardian Omar Yusuf, waxaan ku ogeysiinaynaa in ardaygaaga Abdiqadir Omar Yusuf maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — Hawlwadaag Primary and Secondary School	SMS	READ	PROVIDER_NOT_CONFIGURED	3	Guardian Omar Yusuf	+252611234503	\N	Parent	1	2025-2026	26	\N	\N	\N	attendance:26:student:3:date:2026-10-23	304	2026-10-23 23:31:20.785655+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
203	RESULT_SUBMITTED	Examination Results Submitted	Teacher Hassan Math submitted results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF, 2026/2027).	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	392	2026-10-23 23:31:33.576337+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 45, "teacher_name": "Hassan Math", "class_name": "Form 3-Alpha WF", "subject_name": "Workflow Mathematics", "exam_name": "Midterm Examination 2026 WF", "academic_year": "2026/2027", "submitted_at": "2026-10-23T20:31:33.537720+00:00", "link": "/admin/results"}
204	RESULT_RETURNED	Results Returned for Correction	Results for Midterm Examination 2026 WF (Workflow Mathematics - Form 3-Alpha WF) have been returned by Administration for correction: Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.	IN_APP	READ	\N	\N	\N	\N	\N	\N	25	2026/2027	\N	27	\N	\N	\N	1	2026-10-23 23:31:34.083744+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	{"submission_id": 45, "exam_id": 27, "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2.", "returned_at": "2026-10-23T20:31:34.063038+00:00"}
208	RESULT_RELEASED	Natiijada Imtixaanka - Amina Dahir	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Amina Dahir ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	116	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	12	result_release:116:batch:12	1	2026-10-23 23:31:34.342943+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
209	RESULT_RELEASED	Natiijada Imtixaanka - Jama Noor	Asc Waalidka, waxaan ku ogeysiinaynaa in natiijada Jama Noor ee Midterm Examination 2026 WF la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — Hawlwadaag Primary and Secondary School	SMS	READ	MISSING_CONTACT	117	Parent/Guardian	\N	\N	\N	25	2026/2027	\N	\N	\N	12	result_release:117:batch:12	1	2026-10-23 23:31:34.342943+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
211	GENERAL_ANNOUNCEMENT	Hawlwadaag School Notice	Asc Guardian Abdi Warsame, ardayga Ibrahim Abdi Warsame wuxuu helay ogeysiis.	SMS	READ	PROVIDER_NOT_CONFIGURED	9	Guardian Abdi Warsame	+252611234509	\N	Parent	1	2025/2026	\N	\N	\N	\N	\N	1	2026-11-12 10:02:05.917327+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	1	\N
212	GENERAL_ANNOUNCEMENT	Missing Contact Notice	Hello parent	SMS	READ	MISSING_CONTACT	156	Parent/Guardian	\N	\N	Guardian	80	2026/2027	\N	\N	\N	\N	\N	1	2026-11-12 10:02:05.969646+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
213	CUSTOM	Invalid Phone Test	Hello parent	SMS	READ	INVALID_CONTACT	156	Parent/Guardian	invalid-phone	\N	Guardian	80	2026/2027	\N	\N	\N	\N	\N	1	2026-11-12 10:02:05.983405+03	2026-11-12 10:04:28.930316+03	\N	\N	2026-11-12 10:04:28.929294+03	0	\N
\.


--
-- Data for Name: result_release_batches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.result_release_batches (id, batch_code, exam_name, academic_year, class_id, release_type, status, released_by_id, released_at, results_count, notes, created_at, updated_at) FROM stdin;
1	RB-2026-0001	Admin Redesign Mid-Term 2026	2026-2027	3	FULL	RELEASED	1	2026-09-21 01:42:58.980246+03	2	\N	2026-09-21 01:42:58.996008+03	2026-09-21 01:42:58.996014+03
2	RB-2026-0002	Mid-Term Examination 2026/2027	2026-2027	5	FULL	RELEASED	1	2026-09-21 01:43:02.83626+03	30	\N	2026-09-21 01:43:02.837708+03	2026-09-21 01:43:02.837711+03
3	RB-2026-0003	Mid-Term Examination 2026/2027	2026-2027	5	FULL	RELEASED	1	2026-09-21 01:43:03.659753+03	360	Full release for Grade 7 all 12 subjects	2026-09-21 01:43:03.660201+03	2026-09-21 01:43:03.660203+03
4	RB-2026/2027-0001	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 00:46:43.407885+03	3	\N	2026-10-23 00:46:43.416019+03	2026-10-23 00:46:43.416022+03
5	RB-2026/2027-0002	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 00:49:08.560143+03	3	\N	2026-10-23 00:49:08.567784+03	2026-10-23 00:49:08.567787+03
6	RB-2026/2027-0003	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 00:50:13.818785+03	3	\N	2026-10-23 00:50:13.828395+03	2026-10-23 00:50:13.828399+03
7	RB-2026/2027-0004	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 02:01:56.160956+03	3	\N	2026-10-23 02:01:56.177622+03	2026-10-23 02:01:56.17763+03
8	RB-2026/2027-0005	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 02:04:29.306489+03	3	\N	2026-10-23 02:04:29.319352+03	2026-10-23 02:04:29.31936+03
9	RB-2026/2027-0006	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 02:05:12.567218+03	3	\N	2026-10-23 02:05:12.579857+03	2026-10-23 02:05:12.579869+03
10	RB-2026/2027-0007	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 02:06:13.940498+03	3	\N	2026-10-23 02:06:13.950521+03	2026-10-23 02:06:13.950529+03
11	RB-2026/2027-0008	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 02:20:04.044174+03	3	\N	2026-10-23 02:20:04.057059+03	2026-10-23 02:20:04.057066+03
12	RB-2026/2027-0009	Midterm Examination 2026 WF	2026/2027	25	FULL	RELEASED	1	2026-10-23 23:31:34.281684+03	3	\N	2026-10-23 23:31:34.299614+03	2026-10-23 23:31:34.299618+03
\.


--
-- Data for Name: result_submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.result_submissions (id, exam_id, class_id, subject_id, teacher_id, academic_year, exam_name, status, expected_students, completed_students, pending_students, submitted_at, submitted_by_id, reviewed_at, reviewed_by_id, approved_at, approved_by_id, returned_at, return_reason, submission_deadline, created_at, updated_at, revisions, exam_type) FROM stdin;
46	28	25	35	13	2026/2027	Midterm Examination 2026 WF	DRAFT	3	0	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-10-23 23:31:33.326058+03	2026-10-23 23:31:33.326062+03	[]	MID_TERM
45	27	25	34	12	2026/2027	Midterm Examination 2026 WF	RELEASED	3	3	0	2026-10-23 23:31:34.153027+03	392	2026-10-23 23:31:34.214508+03	1	2026-10-23 23:31:34.214508+03	1	2026-10-23 23:31:34.063038+03	\N	\N	2026-10-23 23:31:33.258377+03	2026-10-23 23:31:34.303716+03	[{"action": "SUBMITTED", "timestamp": "2026-10-23T20:31:33.537720+00:00", "submitted_by_id": 392, "submitted_by_name": "Hassan Math", "students_count": 3, "notes": null, "previous_return_reason": null}, {"action": "RETURNED_FOR_CORRECTION", "timestamp": "2026-10-23T20:31:34.063038+00:00", "returned_by_id": 1, "returned_by_name": "Hawlwadaag System Admin", "reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2."}, {"action": "RESUBMITTED", "timestamp": "2026-10-23T20:31:34.153027+00:00", "submitted_by_id": 392, "submitted_by_name": "Hassan Math", "students_count": 3, "notes": null, "previous_return_reason": "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2."}, {"action": "APPROVED", "timestamp": "2026-10-23T20:31:34.214508+00:00", "approved_by_id": 1, "approved_by_name": "Hawlwadaag System Admin", "notes": null}, {"action": "PUBLISHED_TO_STUDENTS", "timestamp": "2026-10-23T20:31:34.281684+00:00", "released_by_id": 1, "released_by_name": "Hawlwadaag System Admin", "batch_code": "RB-2026/2027-0009"}]	MID_TERM
44	17	3	4	5	2026/2027	E2E Isolation Exam 2026	APPROVED	10	10	0	2026-10-23 22:36:16.697768+03	373	2026-10-23 22:36:16.819931+03	1	2026-10-23 22:36:16.819931+03	1	2026-10-23 22:36:15.952715+03	\N	\N	2026-10-23 22:36:14.602466+03	2026-10-23 22:36:16.846284+03	[{"action": "SUBMITTED", "timestamp": "2026-10-23T19:36:15.410509+00:00", "submitted_by_id": 373, "submitted_by_name": "Ahmed Warsame", "students_count": 11, "notes": null, "previous_return_reason": null}, {"action": "RETURNED_FOR_CORRECTION", "timestamp": "2026-10-23T19:36:15.952715+00:00", "returned_by_id": 1, "returned_by_name": "Hawlwadaag System Admin", "reason": "Student STU-001 marks require recalculation."}, {"action": "RESUBMITTED", "timestamp": "2026-10-23T19:36:16.697768+00:00", "submitted_by_id": 373, "submitted_by_name": "Ahmed Warsame", "students_count": 11, "notes": null, "previous_return_reason": "Student STU-001 marks require recalculation."}, {"action": "APPROVED", "timestamp": "2026-10-23T19:36:16.819931+00:00", "approved_by_id": 1, "approved_by_name": "Hawlwadaag System Admin", "notes": null}]	Final
1	1	1	1	1	2025/2026	Final math Examination (Grade 1 - A)	DRAFT	20	0	20	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-09-20 05:43:09.219589+03	2026-09-20 05:43:09.219594+03	\N	FINAL
8	8	5	9	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:01.170861+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:00.961284+03	2026-09-21 01:43:03.683689+03	\N	Mid-Term
2	2	3	2	2	2026-2027	Admin Redesign Mid-Term 2026	RELEASED	2	2	0	2026-09-21 01:42:58.943342+03	305	2026-09-21 01:42:58.874617+03	1	2026-09-21 01:42:58.980246+03	1	2026-09-21 01:42:58.874617+03	\N	\N	2026-09-21 01:42:58.47802+03	2026-09-21 01:42:59.002153+03	\N	MID_TERM
9	9	5	10	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:01.395387+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:01.243696+03	2026-09-21 01:43:03.683689+03	\N	Mid-Term
10	10	5	11	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:01.595073+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:01.455422+03	2026-09-21 01:43:03.68369+03	\N	Mid-Term
11	11	5	12	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:01.798565+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:01.652618+03	2026-09-21 01:43:03.68369+03	\N	Mid-Term
12	12	5	13	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:02.002497+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:01.865078+03	2026-09-21 01:43:03.683691+03	\N	Mid-Term
13	13	5	14	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:02.212632+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:02.061085+03	2026-09-21 01:43:03.683691+03	\N	Mid-Term
14	14	5	15	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:02.597318+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:02.296318+03	2026-09-21 01:43:03.683692+03	\N	Mid-Term
3	3	5	4	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:42:59.847369+03	308	\N	\N	2026-09-21 01:43:02.83626+03	1	\N	\N	\N	2026-09-21 01:42:59.695228+03	2026-09-21 01:43:02.842706+03	\N	Mid-Term
4	4	5	5	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:00.068769+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:42:59.900956+03	2026-09-21 01:43:03.683684+03	\N	Mid-Term
5	5	5	6	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:00.28473+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:00.129452+03	2026-09-21 01:43:03.683687+03	\N	Mid-Term
6	6	5	7	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:03.497059+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:00.328936+03	2026-09-21 01:43:03.683687+03	\N	Mid-Term
7	7	5	8	3	2026-2027	Mid-Term Examination 2026/2027	RELEASED	30	30	0	2026-09-21 01:43:00.73043+03	308	\N	\N	\N	\N	\N	\N	\N	2026-09-21 01:43:00.557676+03	2026-09-21 01:43:03.683688+03	\N	Mid-Term
16	20	1	26	6	2026/2027	Final Computer G9 Examination (Grade 1 - A)	PARTIAL	0	1	20	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-09-21 03:45:01.340679+03	2026-09-21 03:52:34.827007+03	\N	FINAL
17	15	6	16	2	2026-2027	Final Examination 2026	PARTIAL	25	1	24	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-09-26 09:22:00.42134+03	2026-09-26 09:22:00.540411+03	\N	FINAL
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description, is_system, created_at, updated_at) FROM stdin;
1	ADMIN	System and school administrator with full management access	t	2026-09-16 09:03:26.746928+03	2026-09-16 09:03:26.746939+03
2	TEACHER	Academic faculty member managing attendance and grades	t	2026-09-16 09:03:26.767456+03	2026-09-16 09:03:26.767466+03
3	STUDENT	Enrolled student accessing timetable and results	t	2026-09-16 09:03:26.775319+03	2026-09-16 09:03:26.775327+03
4	PARENT	Parent or legal guardian monitoring student progress	t	2026-09-16 09:03:26.783148+03	2026-09-16 09:03:26.783159+03
5	STAFF	Administrative and supporting school staff	t	2026-09-16 09:03:26.790685+03	2026-09-16 09:03:26.790695+03
6	SUPER_ADMIN	Somroyal Platform Super Administrator	t	2026-11-13 10:49:26.029692+03	2026-11-13 10:49:26.029697+03
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sessions (id, user_id, refresh_token, ip_address, user_agent, is_revoked, expires_at, created_at, updated_at) FROM stdin;
1	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5ODcxNjEyLCJleHAiOjE3OTA0NzY0MTIsImp0aSI6IjEwODM0NmUxOTQxNTRiMTdhYTBhNmJkZTRmMWE1ZThhIiwidHlwZSI6InJlZnJlc2gifQ.BW5gzv37us5VN1_8e3nyTEIXKDy85zaJGYNxv2TATFs	127.0.0.1	python-requests/2.34.2	f	2026-09-27 05:33:32.838762+03	2026-09-20 05:33:32.839909+03	2026-09-20 05:33:32.839912+03
2	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5ODcxNjM5LCJleHAiOjE3OTA0NzY0MzksImp0aSI6ImI4MTM2NDdkM2NkNTQxMjliM2Y3OTZhODY2YzlkMGEzIiwidHlwZSI6InJlZnJlc2gifQ.nuCLiswJWdcnRElj5HaPrE6ogildea97qETsE7XO6DM	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-27 05:33:59.938635+03	2026-09-20 05:33:59.939809+03	2026-09-20 05:40:41.499776+03
3	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3ODk4NzIwODAsImV4cCI6MTc5MDQ3Njg4MCwianRpIjoiZDU3YjI5YzY0N2FlNDY1ZWI0N2EzODAzNDVhOWMxMDMiLCJ0eXBlIjoicmVmcmVzaCJ9.n6EMB9nZhMXvxQS3UbtogDOGbuRa-fBNCOKvsxuN3Qg	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-27 05:41:20.638481+03	2026-09-20 05:41:20.639294+03	2026-09-20 05:45:22.575727+03
4	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5ODcyNDIwLCJleHAiOjE3OTA0NzcyMjAsImp0aSI6IjgwMzMwMTI5OWI0ZjRiNGNiNzFiNjNhMzExNjk1ZmIyIiwidHlwZSI6InJlZnJlc2gifQ.0rJP9h2iMPDNnymQRf2gwti45sEcY1blEHznpCfUTaU	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	f	2026-09-27 05:47:00.041787+03	2026-09-20 05:47:00.042991+03	2026-09-20 05:47:00.042993+03
5	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MTg1LCJleHAiOjE3OTA1NDg5ODUsImp0aSI6ImFjOTllNGQxMGQxODQwMGU4YzFjMzg0NGMwYTI0OGM4IiwidHlwZSI6InJlZnJlc2gifQ.nrMtoOk2SSYokQlswii7Zmtt-xI_b6caQ9yUfEizLVo	testclient	testclient	f	2026-09-28 01:43:05.286305+03	2026-09-21 01:43:05.287765+03	2026-09-21 01:43:05.287768+03
6	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MTg2LCJleHAiOjE3OTA1NDg5ODYsImp0aSI6IjJiYmI0MTE3YzVmMDQwYjQ5NTFiNDdhNjZkYzcyMjA1IiwidHlwZSI6InJlZnJlc2gifQ.d68LIgPMfoHGF2IYw5Zrp3Ddu6pkspcdju7QdUdukrA	testclient	testclient	f	2026-09-28 01:43:06.631722+03	2026-09-21 01:43:06.632622+03	2026-09-21 01:43:06.632625+03
7	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MTg3LCJleHAiOjE3OTA1NDg5ODcsImp0aSI6ImMwZjE2YmZlNjI2MjQ4MTc4ZjI2N2UwNWQ1ZmE2NWM2IiwidHlwZSI6InJlZnJlc2gifQ.GqK7BGxavmVhuJeywVLT_REJ0cb7RhpqcsgogsAMHvs	testclient	testclient	f	2026-09-28 01:43:07.148025+03	2026-09-21 01:43:07.148714+03	2026-09-21 01:43:07.148717+03
8	364	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjQiLCJpYXQiOjE3ODk5NDQxODcsImV4cCI6MTc5MDU0ODk4NywianRpIjoiZGNmOWUzM2UzMjk0NDE3NWIzOGQwYmJhNTcwOTdiOWEiLCJ0eXBlIjoicmVmcmVzaCJ9.W-Nyerozq8-Xye0pZsb8GlDG2XtTf2ZWRerB24sjvgs	testclient	testclient	f	2026-09-28 01:43:07.995847+03	2026-09-21 01:43:07.996922+03	2026-09-21 01:43:07.996926+03
9	365	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjUiLCJpYXQiOjE3ODk5NDQxODksImV4cCI6MTc5MDU0ODk4OSwianRpIjoiOTk4MDMxOTlmMjQ1NDIzN2JmNTMzMjY4NzNkMjA2N2QiLCJ0eXBlIjoicmVmcmVzaCJ9.NtX0zfQQqMR0FIbLq-ORgqnaXFYBC5xJpyaDK7t-UxA	testclient	testclient	f	2026-09-28 01:43:09.153918+03	2026-09-21 01:43:09.155017+03	2026-09-21 01:43:09.155023+03
10	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MTk0LCJleHAiOjE3OTA1NDg5OTQsImp0aSI6IjA2YTkzNDFjNTFiMzRjNGQ4ODg2MzQ1OWI4ZWVlZmY4IiwidHlwZSI6InJlZnJlc2gifQ.-gRCEaOXRRWYhB2cuhZs2LSbso15SCIO9vGnWhx6p_0	testclient	testclient	f	2026-09-28 01:43:14.866467+03	2026-09-21 01:43:14.867369+03	2026-09-21 01:43:14.867373+03
11	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MTk5LCJleHAiOjE3OTA1NDg5OTksImp0aSI6IjJjZTAyNGMxMDFlNTQwMDU4YzcwZmQxMWJjZGYwZDUxIiwidHlwZSI6InJlZnJlc2gifQ.Ab1N6Be6i6CDolWSbwwLGUjwo-MPbgSJez1l1HzfSVY	testclient	testclient	f	2026-09-28 01:43:19.654731+03	2026-09-21 01:43:19.655382+03	2026-09-21 01:43:19.655385+03
12	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MjAxLCJleHAiOjE3OTA1NDkwMDEsImp0aSI6IjhjODI0NzAyMzJiOTQwNzVhYTA4MGUxZjgxMjI2ZmUxIiwidHlwZSI6InJlZnJlc2gifQ.LY0kh4V1XAyN0JEMadwqobG4LhoaCpdWNBnxZUV9few	testclient	testclient	f	2026-09-28 01:43:21.949779+03	2026-09-21 01:43:21.950427+03	2026-09-21 01:43:21.95043+03
13	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MjAyLCJleHAiOjE3OTA1NDkwMDIsImp0aSI6IjEyYjQ2ZTI3YTM3ODQzYjRiNjA4MGExMzQ2MDE5NTI0IiwidHlwZSI6InJlZnJlc2gifQ.qlxEPI6uo0F_bFTTlrHH1RImoMvaTrRf0Wzyxonv69M	testclient	testclient	f	2026-09-28 01:43:22.336608+03	2026-09-21 01:43:22.337404+03	2026-09-21 01:43:22.337407+03
14	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MjAyLCJleHAiOjE3OTA1NDkwMDIsImp0aSI6ImFkYzhhMzQ4NzVhZDRiN2M5YjAyM2M4ZDgzYzM4OGJkIiwidHlwZSI6InJlZnJlc2gifQ.965-q6F6JwrF5wscxvnEqC9yk_zQM94EikP9a45lMw8	testclient	testclient	f	2026-09-28 01:43:22.688366+03	2026-09-21 01:43:22.689+03	2026-09-21 01:43:22.689003+03
15	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MjAzLCJleHAiOjE3OTA1NDkwMDMsImp0aSI6IjBlYWVmMTg2ZTQ3MTRiYmU4M2VhODJhMzkxMzUxZjA0IiwidHlwZSI6InJlZnJlc2gifQ.eRjTP2T9F3sQf0qQL832bSQ1ce8Et9vdRgUYaRVvSYg	testclient	testclient	f	2026-09-28 01:43:23.208355+03	2026-09-21 01:43:23.209333+03	2026-09-21 01:43:23.209337+03
16	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3ODk5NDQyMDMsImV4cCI6MTc5MDU0OTAwMywianRpIjoiOTc0OTJlY2VhYmY1NDdlYmFkZTI3ZWVhMmEwYjVjZWQiLCJ0eXBlIjoicmVmcmVzaCJ9.aKSig5kGw90vqXoYh8OvRkWbgOvayue9gU6UaXd9U18	testclient	testclient	f	2026-09-28 01:43:23.594958+03	2026-09-21 01:43:23.595836+03	2026-09-21 01:43:23.59584+03
17	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0MjA0LCJleHAiOjE3OTA1NDkwMDQsImp0aSI6IjAyNWQ4OTgxNTBiZTRkZDNiMWM4ZmU1MWJjNmRkNDIxIiwidHlwZSI6InJlZnJlc2gifQ.P-bkXxIQRvRQFvd8KfeKZge2IrUSWYN5z4Oxt2XSv_s	testclient	testclient	f	2026-09-28 01:43:24.978369+03	2026-09-21 01:43:24.979657+03	2026-09-21 01:43:24.979661+03
18	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0ODE1LCJleHAiOjE3OTA1NDk2MTUsImp0aSI6IjQxMGU2OTdiZjhmMzQxYjY5MDhjOTlhNzY0ZDkyMjRkIiwidHlwZSI6InJlZnJlc2gifQ.2slHMvYcjWzOas2HaBu-t3ircfu6CdR4fCVFA-XM1JY	127.0.0.1	python-requests/2.34.2	f	2026-09-28 01:53:35.103097+03	2026-09-21 01:53:35.106177+03	2026-09-21 01:53:35.10618+03
19	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ0ODIyLCJleHAiOjE3OTA1NDk2MjIsImp0aSI6ImE0YjNhN2VkNzU5MzQzMDM5N2IzYmViYTkxOGRiNDg2IiwidHlwZSI6InJlZnJlc2gifQ.gAyoqjTK9Np5WoRkWHgMQxg-bf2w00U-ucqzfBGWxZE	127.0.0.1	python-requests/2.34.2	f	2026-09-28 01:53:42.492822+03	2026-09-21 01:53:42.493443+03	2026-09-21 01:53:42.493446+03
20	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3ODk5NDQ4MjIsImV4cCI6MTc5MDU0OTYyMiwianRpIjoiNWNkN2Q5M2Y2MmU5NGVlYjhhYmNkYjJlZGE5OWRkZjciLCJ0eXBlIjoicmVmcmVzaCJ9.BB2LLOIHMjZWpD7Y_vIPpzDpIpyEfI0fO3rcYrn5rcY	127.0.0.1	python-requests/2.34.2	f	2026-09-28 01:53:42.85585+03	2026-09-21 01:53:42.856356+03	2026-09-21 01:53:42.856358+03
21	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ1MzI2LCJleHAiOjE3OTA1NTAxMjYsImp0aSI6ImYwMTUyN2U5YzEzMTRkY2RhODA4MTAzOWIxMWFiZDk0IiwidHlwZSI6InJlZnJlc2gifQ.19QrUoaPEMfoFlUGXRPj2z2Zubld0mDZMChZew5igyQ	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	f	2026-09-28 02:02:06.719234+03	2026-09-21 02:02:06.71999+03	2026-09-21 02:02:06.719993+03
22	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ1NjEyLCJleHAiOjE3OTA1NTA0MTIsImp0aSI6IjA4ZmZjMjZlODI3NjQ0MDhhODI1M2NmZDFmYTdmYjI2IiwidHlwZSI6InJlZnJlc2gifQ.9GM8LTWiMhhk81kSO6wd8qxWwWkUvkuUwfs9-pDHOwk	127.0.0.1	python-requests/2.34.2	f	2026-09-28 02:06:52.964828+03	2026-09-21 02:06:52.965278+03	2026-09-21 02:06:52.96528+03
23	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ1NjE5LCJleHAiOjE3OTA1NTA0MTksImp0aSI6Ijk2YjRmNzRmYjE0NTQ4NjFiZGM3NzVlYzEyMWY3MDM5IiwidHlwZSI6InJlZnJlc2gifQ.k9k_iU4YTuf0E8xvLUdVt5xSNFBNUZbKJWgE5pw8L4o	127.0.0.1	python-requests/2.34.2	f	2026-09-28 02:06:59.124912+03	2026-09-21 02:06:59.125674+03	2026-09-21 02:06:59.125676+03
24	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ1NjI1LCJleHAiOjE3OTA1NTA0MjUsImp0aSI6ImZiYzg2OGE4NDA5YjRhY2E4ZGRiOTI2MTI0YzAzZGZjIiwidHlwZSI6InJlZnJlc2gifQ.TPefZfwSCTFElLmFw3c2n6sXtpqVWP86YbPJuDG9UWA	127.0.0.1	python-requests/2.34.2	f	2026-09-28 02:07:05.236172+03	2026-09-21 02:07:05.236636+03	2026-09-21 02:07:05.236637+03
25	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTQ5MTU0LCJleHAiOjE3OTA1NTM5NTQsImp0aSI6ImYyZDk3YzVlZjkzOTRkODg4Yzk3MTcwNzc1OTM5ZDgxIiwidHlwZSI6InJlZnJlc2gifQ.13wW2ZXPmMiBMimNbMqFQoDPmu2oqnHaBDAB8YhJ2b0	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 03:05:54.646782+03	2026-09-21 03:05:54.647394+03	2026-09-21 03:26:11.49909+03
26	308	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgiLCJpYXQiOjE3ODk5NTA3MTIsImV4cCI6MTc5MDU1NTUxMiwianRpIjoiZjkyNGFmNzJlZmE5NDljYWFmOGZmOGJiYTAzNTQ5ODUiLCJ0eXBlIjoicmVmcmVzaCJ9.rjJ6LX6mwzcpu2Ps40KTvHFVKCks5zzAaElyZaYOve8	\N	\N	f	2026-09-28 03:31:52.268061+03	2026-09-21 03:31:52.2735+03	2026-09-21 03:31:52.273508+03
27	308	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgiLCJpYXQiOjE3ODk5NTA3NTMsImV4cCI6MTc5MDU1NTU1MywianRpIjoiZGYxY2RjMzQ4YTU0NDIwODk4N2Y1N2IyNjNiZDA3ZGQiLCJ0eXBlIjoicmVmcmVzaCJ9.d5NxT6_o6dofmS8vAlBAcBLQHRK6RpoI1uYV-1WxM00	127.0.0.1	Python-urllib/3.14	f	2026-09-28 03:32:33.130417+03	2026-09-21 03:32:33.132212+03	2026-09-21 03:32:33.132218+03
28	308	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgiLCJpYXQiOjE3ODk5NTA3ODcsImV4cCI6MTc5MDU1NTU4NywianRpIjoiOTY3NWUzMWM0Yjk3NGRiN2I0ZDIzYTY0OWNiZDIwYjkiLCJ0eXBlIjoicmVmcmVzaCJ9.28zt54LwaHlqE0gnvou0OYaa3J4HDrLHtR66UJJIeTM	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 03:33:07.650121+03	2026-09-21 03:33:07.651965+03	2026-09-21 03:33:52.076837+03
29	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTUwODQxLCJleHAiOjE3OTA1NTU2NDEsImp0aSI6IjgxNmZiYjc2MzljOTQ1ZGY4ZTlmYmJjY2JhNmU3MmJhIiwidHlwZSI6InJlZnJlc2gifQ.fIl15n5J_uOqtqv4TisuB8hNT8txYiVZi6WL32r4iuw	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 03:34:01.09482+03	2026-09-21 03:34:01.096462+03	2026-09-21 03:36:05.384679+03
30	377	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzciLCJpYXQiOjE3ODk5NTA5NzYsImV4cCI6MTc5MDU1NTc3NiwianRpIjoiYzYxOTE5YjRlY2NkNDM1YWI0YzU5MTNiNDY0MzQzMTUiLCJ0eXBlIjoicmVmcmVzaCJ9.KHD9T4IO9z_Prmp0JUBr7oNAbszHzqKznNHWQ34lAlU	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 03:36:16.864216+03	2026-09-21 03:36:16.865771+03	2026-09-21 03:43:08.743567+03
31	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTUxMzk4LCJleHAiOjE3OTA1NTYxOTgsImp0aSI6IjYwMjU2ZmQ2MjAxMjRjYjk4MDYwNWQ4OGFlYWY2MWJkIiwidHlwZSI6InJlZnJlc2gifQ.dPBIjmotQE1qu-dDOCAEoHJZ7VJkO4z-45BerFnPiVY	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 03:43:18.607076+03	2026-09-21 03:43:18.60862+03	2026-09-21 03:44:05.681402+03
33	377	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzciLCJpYXQiOjE3ODk5NTE3OTcsImV4cCI6MTc5MDU1NjU5NywianRpIjoiMDFhMzhmMzI0YmE4NDkzOGExYWYwMzEyZDI1YjdlMmEiLCJ0eXBlIjoicmVmcmVzaCJ9.RnEZmzqE16uxcByf2xylj9yzS8sc23-Fw3rgizTIlkI	127.0.0.1	python-requests/2.34.2	f	2026-09-28 03:49:57.896394+03	2026-09-21 03:49:57.897228+03	2026-09-21 03:49:57.89723+03
34	377	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzciLCJpYXQiOjE3ODk5NTE4NTMsImV4cCI6MTc5MDU1NjY1MywianRpIjoiZDU4ODAwOTgwNWU2NDcwZDhhMDIyMDY1NThkZTY0Y2UiLCJ0eXBlIjoicmVmcmVzaCJ9.pkx9RwwZ_CIW8s9oujpZB3gvy1RwgkONb7VKcU6aCLI	127.0.0.1	python-requests/2.34.2	f	2026-09-28 03:50:53.897144+03	2026-09-21 03:50:53.901811+03	2026-09-21 03:50:53.901817+03
35	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTUyMjM3LCJleHAiOjE3OTA1NTcwMzcsImp0aSI6IjViOWQ5ODBiZWIzMDQ3NDFiMTIxYTk4ODQ1OTAzMzA1IiwidHlwZSI6InJlZnJlc2gifQ.z9LJiJS_GISLcTDCa29R_Xsv1d1J4Dt8LWaLCzjny8w	127.0.0.1	python-requests/2.34.2	f	2026-09-28 03:57:17.552897+03	2026-09-21 03:57:17.553867+03	2026-09-21 03:57:17.553869+03
32	377	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzciLCJpYXQiOjE3ODk5NTE0NjAsImV4cCI6MTc5MDU1NjI2MCwianRpIjoiMDZiZGViYzBhYmI0NDU2NmJlYjhlMzE0OTcxODIxYTgiLCJ0eXBlIjoicmVmcmVzaCJ9.dOImVVAooaPpbEUiEfQ0IxTqHJlJdfwM4nB6TTz4Chc	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 03:44:20.377872+03	2026-09-21 03:44:20.379248+03	2026-09-21 03:58:55.629712+03
36	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTUyMzQ0LCJleHAiOjE3OTA1NTcxNDQsImp0aSI6IjhlMzdiNmU4MzkxNzRiNzhiM2U2ZGVhMmUyZGVkZDU4IiwidHlwZSI6InJlZnJlc2gifQ.AQ-m9dePAsh98KqiCNZMMdZfWgo-mWsJyRBCGYMaOSo	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	f	2026-09-28 03:59:04.46009+03	2026-09-21 03:59:04.461675+03	2026-09-21 03:59:04.461682+03
37	378	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzgiLCJpYXQiOjE3ODk5NTI0NDYsImV4cCI6MTc5MDU1NzI0NiwianRpIjoiM2I4Y2UzZWRkYWIwNDkzMTk0ZTM3MGJmZjBiYmZjNGUiLCJ0eXBlIjoicmVmcmVzaCJ9.hd0BzbbFM5HNad2WHvHiMT6sIkEf1_e5wqO7VKBvUUY	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 04:00:46.426497+03	2026-09-21 04:00:46.428101+03	2026-09-21 04:01:04.187421+03
38	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTUyNDczLCJleHAiOjE3OTA1NTcyNzMsImp0aSI6IjE1N2Y4ZTNmZWE3ZTQ1MDc4MDA3NzA1NDVhODhjYzE2IiwidHlwZSI6InJlZnJlc2gifQ.gLBsvvl-oC0ItE07FK8JWvqHCBeRnDxP9F7kj_p6bj0	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 04:01:13.189868+03	2026-09-21 04:01:13.191306+03	2026-09-21 04:02:35.368249+03
39	379	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzkiLCJpYXQiOjE3ODk5NTI1NjQsImV4cCI6MTc5MDU1NzM2NCwianRpIjoiMzczYmMzOTFjMjhjNGRkMTk4MmMxOWZhYTQ0Mzc0MzciLCJ0eXBlIjoicmVmcmVzaCJ9.JuST-5cMp_OEWmY9NaKlDP0yBwd-RQVe2y4SSaKjGsk	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	f	2026-09-28 04:02:44.210856+03	2026-09-21 04:02:44.212263+03	2026-09-21 04:02:44.212269+03
41	374	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzQiLCJpYXQiOjE3ODk5NTI5OTYsImV4cCI6MTc5MDU1Nzc5NiwianRpIjoiMDkxMTZiYmUxN2Q5NDFlMmE0YWZhYzcyMDc5N2E4YTQiLCJ0eXBlIjoicmVmcmVzaCJ9.bmrMJPREOF8HmI5zHDFWXR9PPovH-7Vy5PW94B9Gtp0	127.0.0.1	python-requests/2.34.2	f	2026-09-28 04:09:56.967504+03	2026-09-21 04:09:56.968388+03	2026-09-21 04:09:56.96839+03
42	374	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzQiLCJpYXQiOjE3ODk5NTMwMDQsImV4cCI6MTc5MDU1NzgwNCwianRpIjoiNTVhOGMwZGVjOWE3NGQ4MDlkZTcyMjM1OGYxZTMzMGEiLCJ0eXBlIjoicmVmcmVzaCJ9.lFDCaH7r2I5L3xCaLfjpylJxm7b-UfHjlNwwVIQfH64	127.0.0.1	python-requests/2.34.2	f	2026-09-28 04:10:04.844885+03	2026-09-21 04:10:04.845629+03	2026-09-21 04:10:04.845632+03
40	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg5OTUyNjY3LCJleHAiOjE3OTA1NTc0NjcsImp0aSI6Ijc5MTM4YTBmM2IzZDRlNmE5Yzg0NWFkYmQ0YTcyYjgzIiwidHlwZSI6InJlZnJlc2gifQ.gAjjq0tAnuxX5-d0uEsm-n7B7zVM31diKVnsmB0TYAY	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	t	2026-09-28 04:04:27.674872+03	2026-09-21 04:04:27.676331+03	2026-09-21 04:12:38.816896+03
43	379	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzkiLCJpYXQiOjE3ODk5NTMxNzksImV4cCI6MTc5MDU1Nzk3OSwianRpIjoiMWY0NWNjNjU1MmVkNDUzOTkwY2IxZGEzMmNjOGQwYTUiLCJ0eXBlIjoicmVmcmVzaCJ9.sGBQR9Ge_c46PecVuuE6_6HYRTrx3Pr0DZ1ae0nrb5A	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	f	2026-09-28 04:12:59.262718+03	2026-09-21 04:12:59.264148+03	2026-09-21 04:12:59.264154+03
44	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkwNDAxOTQ0LCJleHAiOjE3OTEwMDY3NDQsImp0aSI6IjMxMTExZGQ2MDBhYzQzZGM5ODM3ZTI2YjcxOWJmOTk5IiwidHlwZSI6InJlZnJlc2gifQ.0A0PiqXXY89QpHSIb1YSkj8i9UVsLJOI9FqxQWz7NgQ	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	t	2026-10-03 08:52:24.80421+03	2026-09-26 08:52:24.806108+03	2026-09-26 08:59:01.379663+03
54	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDMwNzQsImV4cCI6MTc5MTAwNzg3NCwianRpIjoiYzdkZWE3MDRjNTZhNGRlZTg3MDVmZTQ0ZmNjMjlkZWMiLCJ0eXBlIjoicmVmcmVzaCJ9.xweWj8p1ZU0pjIAtK-cqfGLMUH5i_7i5UcTY-CKj5nk	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0	f	2026-10-03 09:11:14.508905+03	2026-09-26 09:11:14.509935+03	2026-09-26 09:11:14.509938+03
45	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkwNDAyNDY2LCJleHAiOjE3OTEwMDcyNjYsImp0aSI6IjQ3M2NmNjkxMDc3NTQzMGNiZGJhMDhjMDQxYzdmOGQ3IiwidHlwZSI6InJlZnJlc2gifQ.DPuafF-riOgPUivqSm5JTiBAmPaZ9pXeBqHlrvOXtoI	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	t	2026-10-03 09:01:06.94242+03	2026-09-26 09:01:06.943661+03	2026-09-26 09:05:23.050465+03
46	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkwNDAyNzM4LCJleHAiOjE3OTEwMDc1MzgsImp0aSI6IjQwOWJiZWUwMzM5ZDQ5ZTVhMTJlMjk5MTgxMDdkMDVmIiwidHlwZSI6InJlZnJlc2gifQ.hggVvIYik7UCJ6VI5GtECYcEVaaUJV60_YTcswGf24U	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	t	2026-10-03 09:05:38.136359+03	2026-09-26 09:05:38.136975+03	2026-09-26 09:06:01.409071+03
47	379	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzkiLCJpYXQiOjE3OTA0MDI3NzksImV4cCI6MTc5MTAwNzU3OSwianRpIjoiZDBhYzc4N2UzZDgzNDZjYTg3Mzc2YWY1NmM4YmEyZjAiLCJ0eXBlIjoicmVmcmVzaCJ9.2vE926hiR_4hemA706W1XdXqbzF26etLNwyarJE9Xvc	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	t	2026-10-03 09:06:19.781289+03	2026-09-26 09:06:19.781977+03	2026-09-26 09:06:31.338461+03
48	379	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzkiLCJpYXQiOjE3OTA0MDI4MTIsImV4cCI6MTc5MTAwNzYxMiwianRpIjoiNmY4MWM1NmRkZTRjNDZjYTk0MjgxNjI0NTQwNDE1NTYiLCJ0eXBlIjoicmVmcmVzaCJ9.XT0Gx-W6Tv5JVhYySqXzcByBe4SAvVMZFQTATpvR6ds	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	t	2026-10-03 09:06:52.794035+03	2026-09-26 09:06:52.794743+03	2026-09-26 09:07:28.876643+03
49	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDI4NTgsImV4cCI6MTc5MTAwNzY1OCwianRpIjoiNGNiMzViNzkyZTQxNDMyZjljMWJmOWQ2NWQ1M2UzZGUiLCJ0eXBlIjoicmVmcmVzaCJ9.JktvbvlXHPygKFAXgwHrydAygiuv1v2OJhH4aeNtUco	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	f	2026-10-03 09:07:38.272284+03	2026-09-26 09:07:38.273345+03	2026-09-26 09:07:38.27335+03
50	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDI4NjMsImV4cCI6MTc5MTAwNzY2MywianRpIjoiZjBkY2RkZjE4MzUxNGMyNjk3OWU1ZjRiNTc4NTJmMGYiLCJ0eXBlIjoicmVmcmVzaCJ9.KYGHGSfBMX8ddgCf4bnFbhUIg9bMd6a4jMQwSTDdiX8	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	f	2026-10-03 09:07:43.462051+03	2026-09-26 09:07:43.463108+03	2026-09-26 09:07:43.46311+03
51	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDI4NjksImV4cCI6MTc5MTAwNzY2OSwianRpIjoiMTlhMTRhMWI1YjIxNDcyZmJhZmVkOWM1N2M3ZTU4ZmMiLCJ0eXBlIjoicmVmcmVzaCJ9.pNYIF0ZCvtsfHeQAelXXFB61pahGGY0OrVReQ9fdRW8	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	f	2026-10-03 09:07:49.849881+03	2026-09-26 09:07:49.850421+03	2026-09-26 09:07:49.850423+03
52	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDI4NzEsImV4cCI6MTc5MTAwNzY3MSwianRpIjoiNjVmMWQ4ZGRjYjBmNDRhMmExYTNhNDQyZjc5ODU2OTQiLCJ0eXBlIjoicmVmcmVzaCJ9.oCjC-cLpvr2Pv73tvhztJ2jCbLZD09DGUcnIxxe1ZGM	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	f	2026-10-03 09:07:51.054968+03	2026-09-26 09:07:51.055637+03	2026-09-26 09:07:51.05564+03
55	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDMwNzgsImV4cCI6MTc5MTAwNzg3OCwianRpIjoiMjY4YmJkNTBkYTgxNDRhZjlhNDRiZTk1ZjhjODkyYjMiLCJ0eXBlIjoicmVmcmVzaCJ9.Dv31PB-N0Eb33soiz1Zv29F3vSIVbG_CDaTJyrlOiLs	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0	f	2026-10-03 09:11:18.989398+03	2026-09-26 09:11:18.990478+03	2026-09-26 09:11:18.990482+03
56	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDMwODQsImV4cCI6MTc5MTAwNzg4NCwianRpIjoiOGUzYmQ0YjQ1ZjExNGEyNDlkNDQ1ZDViOTAzYmI1NzYiLCJ0eXBlIjoicmVmcmVzaCJ9.OoUNsqzVUSmBfgVyjmPXQZSHaYmDILUZHGurw2Sy8ts	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0	f	2026-10-03 09:11:24.180762+03	2026-09-26 09:11:24.181462+03	2026-09-26 09:11:24.181464+03
57	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDMxNjUsImV4cCI6MTc5MTAwNzk2NSwianRpIjoiMjJhNWJlOWZhZjQ4NGYzZThiYTMyN2RhYTllZjJmODIiLCJ0eXBlIjoicmVmcmVzaCJ9.a5MB8g2UI0PuDfP6vGfM7cdkYnDf__Kf8mxZHY56N0M	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0	f	2026-10-03 09:12:45.792606+03	2026-09-26 09:12:45.793788+03	2026-09-26 09:12:45.793795+03
58	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDMxNjUsImV4cCI6MTc5MTAwNzk2NSwianRpIjoiODNkYzRlYjk0MGIzNDExMTg4NDllODZkMTczZTI2NGQiLCJ0eXBlIjoicmVmcmVzaCJ9.DH4Y-_eSP8S3JhH_yWOu5dPl-EBMMaXdk7HSWe1KuOo	127.0.0.1	python-requests/2.34.2	f	2026-10-03 09:12:45.858531+03	2026-09-26 09:12:45.859024+03	2026-09-26 09:12:45.859026+03
59	305	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDUiLCJpYXQiOjE3OTA0MDMxNjYsImV4cCI6MTc5MTAwNzk2NiwianRpIjoiOGUxMGViMTEwYjQwNDQ4OTgzZTUyMmVlZGU1ZDU3NmQiLCJ0eXBlIjoicmVmcmVzaCJ9.e8ME2xnZpN86VMF7LMRk6sC7CTMjzcWQ4lcrjOzmldQ	127.0.0.1	python-requests/2.34.2	f	2026-10-03 09:12:46.238861+03	2026-09-26 09:12:46.239797+03	2026-09-26 09:12:46.239801+03
60	305	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDUiLCJpYXQiOjE3OTA0MDMxNjYsImV4cCI6MTc5MTAwNzk2NiwianRpIjoiZjRjNWU3MWE5YTM2NDgwNDllOTI5OTMzMTA5MjYzMTMiLCJ0eXBlIjoicmVmcmVzaCJ9.Ym2Ny4B9I1RmYPuH4nKnvGSmu1ij5qFVdf4Mij763JM	127.0.0.1	python-requests/2.34.2	f	2026-10-03 09:12:46.593145+03	2026-09-26 09:12:46.594216+03	2026-09-26 09:12:46.594217+03
61	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTA0MDMxNjYsImV4cCI6MTc5MTAwNzk2NiwianRpIjoiOWJhMDYzNjVlMDBjNGVlZjg4ZGY1MmFiMmVmYjBiODYiLCJ0eXBlIjoicmVmcmVzaCJ9.gC4ABZFtsZZ5JWl-Jc8WIfyaMKvoZgDvVPiszwDNxJQ	127.0.0.1	python-requests/2.34.2	f	2026-10-03 09:12:46.914565+03	2026-09-26 09:12:46.91517+03	2026-09-26 09:12:46.915172+03
62	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTA0MDMxNjcsImV4cCI6MTc5MTAwNzk2NywianRpIjoiMzQyZGU2ODhmMzUxNGU5MGIwNTAyZTE5Nzk3MjQ1NzMiLCJ0eXBlIjoicmVmcmVzaCJ9.wzCpsOcSVm8ittNmoUOveQv-ai1bpG42b0oO1vDrSi4	127.0.0.1	python-requests/2.34.2	f	2026-10-03 09:12:47.224441+03	2026-09-26 09:12:47.225211+03	2026-09-26 09:12:47.225213+03
63	308	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgiLCJpYXQiOjE3OTA0MDMxNjcsImV4cCI6MTc5MTAwNzk2NywianRpIjoiNDE1ZTRkNzI4OGRmNDcyODg4Zjc2ZDJjMjgzODZiYjUiLCJ0eXBlIjoicmVmcmVzaCJ9.iSjiQVqcphsz4YaB5rMtqZa-SRdF9ZxlePvsOpop7PQ	127.0.0.1	python-requests/2.34.2	f	2026-10-03 09:12:47.53036+03	2026-09-26 09:12:47.531151+03	2026-09-26 09:12:47.531169+03
53	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTA0MDI4NzQsImV4cCI6MTc5MTAwNzY3NCwianRpIjoiNzM4MzY1NDFmODA1NDA0OWI4ZGViOWRmYzY4OTZlYWUiLCJ0eXBlIjoicmVmcmVzaCJ9.-MB1iQN-VnnMMxw99m0UeCAtxJYbD4NTzESlqgHBI4E	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	t	2026-10-03 09:07:54.594049+03	2026-09-26 09:07:54.59473+03	2026-09-26 09:17:07.507775+03
64	305	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDUiLCJpYXQiOjE3OTA0MDM0NDgsImV4cCI6MTc5MTAwODI0OCwianRpIjoiMTJhMTFiNTFiODcwNDhjOWI0MTgzMzRiYTUyYWE0ZTEiLCJ0eXBlIjoicmVmcmVzaCJ9.4W2yZ5f840a8LuuiDW9xd7RYgszkZ1C45tdfxYvlF3E	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	t	2026-10-03 09:17:28.049794+03	2026-09-26 09:17:28.05095+03	2026-09-26 09:17:35.295369+03
114	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyODc2OTcyLCJleHAiOjE3OTM0ODE3NzIsImp0aSI6ImEyZWQyYjkwMjM1MzQ4ZjdhNDMzODU2MWM0ODkzYWEwIiwidHlwZSI6InJlZnJlc2gifQ.gHPnHV9wDnSkjcQqGqhplGy5LbKSCyFbO8Iq99VXJew	testclient	testclient	f	2026-11-01 00:22:52.29851+03	2026-10-25 00:22:52.300613+03	2026-10-25 00:22:52.300615+03
115	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyODc2OTg1LCJleHAiOjE3OTM0ODE3ODUsImp0aSI6IjJkZjUwNGFiZmRmMTQyMDE4N2ExNDNjN2U2YTQyYTRjIiwidHlwZSI6InJlZnJlc2gifQ.ml8Ckk99Hh3r_XzP3zx35zANUYKXrWo-mwLEWPWSdKY	testclient	testclient	f	2026-11-01 00:23:05.188856+03	2026-10-25 00:23:05.191022+03	2026-10-25 00:23:05.191024+03
65	305	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDUiLCJpYXQiOjE3OTA0MDM0OTQsImV4cCI6MTc5MTAwODI5NCwianRpIjoiZTgxMDg3MTNkZGY3NDRkNWE4NzIwZjczODhiZjk0ZjgiLCJ0eXBlIjoicmVmcmVzaCJ9.OL-0Fbq1J1jOahgyze-KaV9MklLsUG_FnLv0Vx-kij0	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	t	2026-10-03 09:18:14.305335+03	2026-09-26 09:18:14.306053+03	2026-09-26 09:18:19.793923+03
66	305	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDUiLCJpYXQiOjE3OTA0MDM1MTIsImV4cCI6MTc5MTAwODMxMiwianRpIjoiYzc3ZDUwNmM0Mzg4NDUwMzg5N2YxMzE0NzlkZTU3OTIiLCJ0eXBlIjoicmVmcmVzaCJ9.0HBRik9iVjLRwO19DiB2vqAtJu56P1RqhiPe9EMQ_wc	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	f	2026-10-03 09:18:32.067422+03	2026-09-26 09:18:32.068182+03	2026-09-26 09:18:32.068184+03
67	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjc5Mjg5LCJleHAiOjE3OTMyODQwODksImp0aSI6IjYwNTA0MzVkMGFjMTRkOTliZTVjMzg2MzM4ZGEzNmIzIiwidHlwZSI6InJlZnJlc2gifQ.yWBLHRrrcvo4K3MdFrwz3NqzRB7TsbSC5Kvs6dhKBHM	\N	\N	f	2026-10-29 17:28:09.470156+03	2026-10-22 17:28:09.471254+03	2026-10-22 17:28:09.471256+03
68	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjc5MzgxLCJleHAiOjE3OTMyODQxODEsImp0aSI6IjcwMWM5MGJiZGM0YTRhNmZiNDZmNDUzM2U0MTEyYjdkIiwidHlwZSI6InJlZnJlc2gifQ.XXy9NiXePonORbS_3YQS_sFe0tJ0zgE2eD2PqPO_yvQ	testclient	testclient	f	2026-10-29 17:29:41.93164+03	2026-10-22 17:29:41.933134+03	2026-10-22 17:29:41.933137+03
69	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjc5NjQ4LCJleHAiOjE3OTMyODQ0NDgsImp0aSI6IjlhMGU0ODBmOTNlYTQ1NjliZmNkOWQxZmExNWI5MmFmIiwidHlwZSI6InJlZnJlc2gifQ.BB0K5OUf8pCdh5uaV7Xj1MZaTHtm8enS8IGae4gqi6Q	127.0.0.1	python-requests/2.34.2	f	2026-10-29 17:34:08.980012+03	2026-10-22 17:34:08.983755+03	2026-10-22 17:34:08.98376+03
70	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjc5NjU5LCJleHAiOjE3OTMyODQ0NTksImp0aSI6ImQwMjJiMTNjYTNlZjRkZmI5ZjY4ODBmOGFjZWQ3ZTgwIiwidHlwZSI6InJlZnJlc2gifQ.rWSHh5PGYHFnqZdxxx6RPdB-SRA9BGRgtDn0uTLYMAE	127.0.0.1	python-requests/2.34.2	f	2026-10-29 17:34:19.325936+03	2026-10-22 17:34:19.326669+03	2026-10-22 17:34:19.326671+03
71	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjc5NzA3LCJleHAiOjE3OTMyODQ1MDcsImp0aSI6IjY0YTQ0MGI0YWUyNDQ0YTdiZThiNDVmNGZhYjVjMTY4IiwidHlwZSI6InJlZnJlc2gifQ.7EtAmDQvMxp2SxxU0CXioQE_bwP_5qn9nHjM2EdzjvI	127.0.0.1	python-requests/2.34.2	f	2026-10-29 17:35:07.643778+03	2026-10-22 17:35:07.644403+03	2026-10-22 17:35:07.644406+03
72	380	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzODAiLCJpYXQiOjE3OTI2Nzk3MDgsImV4cCI6MTc5MzI4NDUwOCwianRpIjoiMGQyMDk4ZjM1NWIxNDBjN2JhNWMwOGE5MzRmNDhjYTAiLCJ0eXBlIjoicmVmcmVzaCJ9.hcrLXQya48hHSjNTyYtqETpM8YnzhQSt4hdETN8ODwA	127.0.0.1	python-requests/2.34.2	f	2026-10-29 17:35:08.665436+03	2026-10-22 17:35:08.666125+03	2026-10-22 17:35:08.666128+03
73	381	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzODEiLCJpYXQiOjE3OTI2Nzk3MDksImV4cCI6MTc5MzI4NDUwOSwianRpIjoiZjE2NGUwY2JlZWViNDVjNjhkNDFlYjllMWQ4NWQ3NDEiLCJ0eXBlIjoicmVmcmVzaCJ9.agERTKTaw8iLcnjgB3zNVW9UkVVxWBYdXrKeRwvrHrE	127.0.0.1	python-requests/2.34.2	f	2026-10-29 17:35:09.110514+03	2026-10-22 17:35:09.111336+03	2026-10-22 17:35:09.111339+03
74	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjc5Nzg2LCJleHAiOjE3OTMyODQ1ODYsImp0aSI6IjhlMjQ1OWJjN2ZhNzRiMmU4MmVhOGE1YWZlNzNiOWU5IiwidHlwZSI6InJlZnJlc2gifQ.aUlZlFSNhFfI_yuNqt6Mr8vWs8hwAD67BLnr2IY7nOM	127.0.0.1	python-requests/2.34.2	f	2026-10-29 17:36:26.231283+03	2026-10-22 17:36:26.23172+03	2026-10-22 17:36:26.231722+03
76	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgwNDI0LCJleHAiOjE3OTMyODUyMjQsImp0aSI6IjQ5NDIwMzE3MzkzZTQ3ODBhOTE5M2I0MzM4MDhlMzEyIiwidHlwZSI6InJlZnJlc2gifQ.zXm1viGdj-wJHHSvtvQU-Z4diYwdEOvYIIfmcZifFWk	127.0.0.1	python-requests/2.34.2	f	2026-10-29 17:47:04.148316+03	2026-10-22 17:47:04.151934+03	2026-10-22 17:47:04.151941+03
77	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgxNjM1LCJleHAiOjE3OTMyODY0MzUsImp0aSI6IjYwNjRjNmEyZGFhYjQzOTdiNTVjZGNhNDE5MGQwNmQ4IiwidHlwZSI6InJlZnJlc2gifQ.AfNuSKUQleA_u4IUb2uowP9P4GIrl0eZ2XbtfL1Yfdw	127.0.0.1	python-requests/2.34.2	f	2026-10-29 18:07:15.213317+03	2026-10-22 18:07:15.214986+03	2026-10-22 18:07:15.214993+03
75	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgwMjY4LCJleHAiOjE3OTMyODUwNjgsImp0aSI6IjVjNTAyOThjNTNlMTQxZGJiZTczZTVlZTg4OGM0NDgwIiwidHlwZSI6InJlZnJlc2gifQ.9pUrzM0_Xd7R0nHFUbfw7Akn3G-HVLzVkmYsQ9bBRpo	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	t	2026-10-29 17:44:28.587908+03	2026-10-22 17:44:28.589551+03	2026-10-22 18:09:44.804227+03
78	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgyMDU2LCJleHAiOjE3OTMyODY4NTYsImp0aSI6IjVlOWE1YmQyYzYyZTQ0Mjg4NDVjNjQxMGZjMzI0YmJlIiwidHlwZSI6InJlZnJlc2gifQ.fLNduNDA_vI5wPCH5AEfEBYx-aA3YPpGb9lzdwCERwY	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	t	2026-10-29 18:14:16.400348+03	2026-10-22 18:14:16.402452+03	2026-10-22 18:22:02.748751+03
79	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgyNjM0LCJleHAiOjE3OTMyODc0MzQsImp0aSI6IjQ3MjA3NmEyMDdhYzQzNjY5Y2VjZWJmZGY3YTZhOWNlIiwidHlwZSI6InJlZnJlc2gifQ.h_x6Hnj2FdPigADRQv3RymxxHdBdfI8yS1-9SzFPD14	127.0.0.1	Python-urllib/3.14	f	2026-10-29 18:23:54.633255+03	2026-10-22 18:23:54.63452+03	2026-10-22 18:23:54.634526+03
80	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgyNjQyLCJleHAiOjE3OTMyODc0NDIsImp0aSI6ImU4YzU0YjI4MmE5OTQ1NjBiNWNmMTVkMzBlZDA5YjAxIiwidHlwZSI6InJlZnJlc2gifQ.DxBjwfdQFOVS_7cCCimtgn9YjAl6V4lYr-_-AHsOaIE	127.0.0.1	Python-urllib/3.14	f	2026-10-29 18:24:02.532528+03	2026-10-22 18:24:02.533724+03	2026-10-22 18:24:02.533729+03
81	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgyNjg0LCJleHAiOjE3OTMyODc0ODQsImp0aSI6IjQ0ZGYxN2I0ODAwZjQ2NjBiMTczNjBlMTdiZmEyYzcyIiwidHlwZSI6InJlZnJlc2gifQ.0g-IXmaZFNFPRN4QondEzi5ss_-ZACZ1F0xQbAhoYzA	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	t	2026-10-29 18:24:44.655243+03	2026-10-22 18:24:44.65698+03	2026-10-22 18:24:59.75374+03
82	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgyNzY5LCJleHAiOjE3OTMyODc1NjksImp0aSI6Ijg1Yzg5ZWU1Nzk2NTRhODA5ZDUyZWI1YWFlNDhiYWFhIiwidHlwZSI6InJlZnJlc2gifQ.6sGrhnU2B1HpR2NoyF7ZzCVGmlK77pRzw5u-d_zjavk	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	t	2026-10-29 18:26:09.390901+03	2026-10-22 18:26:09.392822+03	2026-10-22 18:26:32.831685+03
83	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjgyODM1LCJleHAiOjE3OTMyODc2MzUsImp0aSI6IjFlOWVmYzVmNzg0MjQyN2M4YWU3Y2ExNzdhOGQ5YmQ2IiwidHlwZSI6InJlZnJlc2gifQ.-mLlDN3UgFgbPKMC2B3sFrlgyv6hcr0CYd8xKmVvsRk	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	t	2026-10-29 18:27:15.500685+03	2026-10-22 18:27:15.502496+03	2026-10-22 18:27:39.577083+03
84	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjg0MDMyLCJleHAiOjE3OTMyODg4MzIsImp0aSI6ImE3YzkyNzJjMzE2ODRlNGY5ODFhODc5OTAwNTViZGFiIiwidHlwZSI6InJlZnJlc2gifQ.jdPxhcoDVQIs_kBuNbMDsyTJ-B9XV3TPYhv8zbXjsIQ	testclient	testclient	f	2026-10-29 18:47:12.909343+03	2026-10-22 18:47:12.915666+03	2026-10-22 18:47:12.915674+03
85	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjg0MDYyLCJleHAiOjE3OTMyODg4NjIsImp0aSI6ImViNmEyYjk4YTUyMTRjYzdiMWJiMWQwYmUwN2ZiZTBiIiwidHlwZSI6InJlZnJlc2gifQ.QhwCPJK7-N8B3EBkkHWJ4yxkF3DIBXb7W7pTQhq05Bc	testclient	testclient	f	2026-10-29 18:47:42.389952+03	2026-10-22 18:47:42.392625+03	2026-10-22 18:47:42.392628+03
86	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjg0MzA3LCJleHAiOjE3OTMyODkxMDcsImp0aSI6IjY3NzNjODg2OTAzOTQyNGFhODkyMjEzODM3YmVmNzVlIiwidHlwZSI6InJlZnJlc2gifQ.T1Uds4svX2w4Zegq-o6VjN2iSG6buVcgno7TENdQ-qA	testclient	testclient	f	2026-10-29 18:51:47.90929+03	2026-10-22 18:51:47.913445+03	2026-10-22 18:51:47.91345+03
87	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjg0MzA4LCJleHAiOjE3OTMyODkxMDgsImp0aSI6IjFlYWUyMWI3ZjA2NTQ3MzU4MjRmMzFiODA5MzFkYTljIiwidHlwZSI6InJlZnJlc2gifQ.VVBKQPySWeF-LC4Jh0QpfmQWNOL_AdZinqHRg3gumFw	testclient	testclient	f	2026-10-29 18:51:48.879185+03	2026-10-22 18:51:48.880794+03	2026-10-22 18:51:48.880801+03
88	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNjk3Mzk1LCJleHAiOjE3OTMzMDIxOTUsImp0aSI6IjU3YjIwNDRlNjQxMTRmYjBiZjVkYjczNWNiNGQ3NDcyIiwidHlwZSI6InJlZnJlc2gifQ.3LcthC7me9xKESuKU5Y_AXgkSloh6mh5mGNSa_1r08Y	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36	t	2026-10-29 22:29:55.68817+03	2026-10-22 22:29:55.690004+03	2026-10-22 22:30:01.113251+03
89	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzAxODE5LCJleHAiOjE3OTMzMDY2MTksImp0aSI6IjMzYWZhMWRkOTc1YjQ4NjRiMzQzM2IwMjYyNDRlOTk1IiwidHlwZSI6InJlZnJlc2gifQ.NoenT-ezx-FCMJlCV4byyQsVwtIUVT0gM8N-DSdIi28	127.0.0.1	Python-urllib/3.14	f	2026-10-29 23:43:39.877865+03	2026-10-22 23:43:39.879701+03	2026-10-22 23:43:39.879703+03
90	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzAxODI1LCJleHAiOjE3OTMzMDY2MjUsImp0aSI6IjI5NzliZjQzYmM1NjRiMzJiY2I2ZjUzMjhmNTlmMDg5IiwidHlwZSI6InJlZnJlc2gifQ.k0LVvMqZ-6165ZMDDKCK_MY66suVwUvRi2c4JmPe_rU	127.0.0.1	Python-urllib/3.14	f	2026-10-29 23:43:45.399407+03	2026-10-22 23:43:45.399782+03	2026-10-22 23:43:45.399784+03
91	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzA1ODQwLCJleHAiOjE3OTMzMTA2NDAsImp0aSI6IjdhOGEwYWNjNzljZTRjYmZiMDNhNGRkODA5ZGIwNTg5IiwidHlwZSI6InJlZnJlc2gifQ.0gul5YKIB2t2zUfXyN8INjP3mNt5RHE1Rldrum9hGaI	testclient	testclient	f	2026-10-30 00:50:40.781327+03	2026-10-23 00:50:40.786958+03	2026-10-23 00:50:40.786967+03
92	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzgxOTkxLCJleHAiOjE3OTMzODY3OTEsImp0aSI6IjcyOWI0OGY2Y2FlYzQwNjM5ODcyZWIyZDE3ZmE5MmI4IiwidHlwZSI6InJlZnJlc2gifQ.z_T1-UVxRN5gAIWzObXnVTTXgyBPa2ulvvWHjpTu17E	127.0.0.1	Python-urllib/3.14	f	2026-10-30 21:59:51.982412+03	2026-10-23 21:59:51.985358+03	2026-10-23 21:59:51.985361+03
93	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg3NDU5LCJleHAiOjE3OTMzOTIyNTksImp0aSI6IjliMGY4YWExNGU2NzQ3ZTZhZWRkMGMxMjRiY2YzOWVkIiwidHlwZSI6InJlZnJlc2gifQ.mIx99hadDd5LXgKkS6iU2lJvcpTvEspEzkhQSiXuK1M	testclient	testclient	f	2026-10-30 23:30:59.040854+03	2026-10-23 23:30:59.042799+03	2026-10-23 23:30:59.042802+03
94	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg3NDc3LCJleHAiOjE3OTMzOTIyNzcsImp0aSI6IjkyZDJjNWVkNDhhMTRlMjZhZmUwOTJkN2VlMzI4MmRlIiwidHlwZSI6InJlZnJlc2gifQ.Fu19SEa2ctLPgHLYNqVUDMT75gnot-cx8Qjgo6C1ul8	testclient	testclient	f	2026-10-30 23:31:17.374226+03	2026-10-23 23:31:17.375925+03	2026-10-23 23:31:17.375927+03
95	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg3NDc3LCJleHAiOjE3OTMzOTIyNzcsImp0aSI6ImE3M2VhYmVhYmRjMTQwY2NiNzI5N2Y1NTQ3ZTc4Mjg2IiwidHlwZSI6InJlZnJlc2gifQ.OEgi58Gw10qW7p7E1CGs8lLNMlma4NQfUl0W4Vtt8qI	testclient	testclient	f	2026-10-30 23:31:17.823365+03	2026-10-23 23:31:17.823777+03	2026-10-23 23:31:17.82378+03
96	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg3NDc4LCJleHAiOjE3OTMzOTIyNzgsImp0aSI6ImIzZjc1ZWQ4NTcyMDQ5NjJiNDNkYjdiMDgyOTYwNTA2IiwidHlwZSI6InJlZnJlc2gifQ.APD3QoiLHK-4Htj6YEpfZXkgLFz1vO938_WcomMc6Dg	testclient	testclient	f	2026-10-30 23:31:18.135593+03	2026-10-23 23:31:18.136007+03	2026-10-23 23:31:18.13601+03
97	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg3NDc4LCJleHAiOjE3OTMzOTIyNzgsImp0aSI6ImE3YTczMDdkNzJkMjRmZmJhNzMyY2RmZTg3ZTkxYjI5IiwidHlwZSI6InJlZnJlc2gifQ.WycagCdakiY-Y8YcXBffZS3Xd-ym1JIfu061Xnw9RA0	testclient	testclient	f	2026-10-30 23:31:18.715374+03	2026-10-23 23:31:18.715846+03	2026-10-23 23:31:18.715848+03
98	366	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjYiLCJpYXQiOjE3OTI3ODc0NzksImV4cCI6MTc5MzM5MjI3OSwianRpIjoiOTVjZDMwZGQyNTNkNGE4NGFhMmM4MzFkYjNkMGQxMWMiLCJ0eXBlIjoicmVmcmVzaCJ9.AIu-sPDw-4UpwXoSwIPVTILxz91dJI23YzlEGG75L20	testclient	testclient	f	2026-10-30 23:31:19.167453+03	2026-10-23 23:31:19.167986+03	2026-10-23 23:31:19.167988+03
99	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTI3ODc0ODAsImV4cCI6MTc5MzM5MjI4MCwianRpIjoiMWI0MGE0MzhlNWI5NDRkNGI4MmUwNmI4MmQxNGY0OTkiLCJ0eXBlIjoicmVmcmVzaCJ9.OUyVhJAeoeZ2vmZ50YlEBD7k26h6RabZ4ulzEMloXnk	testclient	testclient	f	2026-10-30 23:31:20.245656+03	2026-10-23 23:31:20.246354+03	2026-10-23 23:31:20.246356+03
100	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg3NDgxLCJleHAiOjE3OTMzOTIyODEsImp0aSI6IjczNzM0ZjI2YWFjMDQyYmU4NDdmYTI1ZmMxZGYwNDQzIiwidHlwZSI6InJlZnJlc2gifQ.5gR7gL23xKIyPCL3XTmHae_Pa_x1DYEsyBwJukMpLeE	testclient	testclient	f	2026-10-30 23:31:21.576288+03	2026-10-23 23:31:21.576764+03	2026-10-23 23:31:21.576766+03
101	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg3NTA2LCJleHAiOjE3OTMzOTIzMDYsImp0aSI6IjZkYjkwMTFhYzI2MTQ0MjU4NmMzYjI3YzY3ZGJjMzNmIiwidHlwZSI6InJlZnJlc2gifQ.XtLIKdwBgd_hpIIdWDRs_8ZTSkL0saZDNZTd18LJkHU	testclient	testclient	f	2026-10-30 23:31:46.249041+03	2026-10-23 23:31:46.250927+03	2026-10-23 23:31:46.250929+03
102	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5MjA0LCJleHAiOjE3OTMzOTQwMDQsImp0aSI6IjE1NzJmMWUxNTc3NTQwYmJiZWU2MDM2YzU0OGRkZDg4IiwidHlwZSI6InJlZnJlc2gifQ.eME_Y0Q_ap-fXHiceM7LECMSeRRudASf4OWXfZR_zRg	testclient	testclient	f	2026-10-31 00:00:04.346829+03	2026-10-24 00:00:04.348197+03	2026-10-24 00:00:04.348199+03
103	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5MjM3LCJleHAiOjE3OTMzOTQwMzcsImp0aSI6ImNlOTA2NjRhNTY3MTQ5MGJhYmQxNzVlMGYzOTJiMTk0IiwidHlwZSI6InJlZnJlc2gifQ.t57WuUvffNqlc42BD2tKIcyOHrTmmKr4AzUEVjNfTPw	testclient	testclient	f	2026-10-31 00:00:37.983613+03	2026-10-24 00:00:37.985131+03	2026-10-24 00:00:37.985133+03
104	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5MzI5LCJleHAiOjE3OTMzOTQxMjksImp0aSI6Ijc0MzExNzkzZThkMDRhNmJhMDIzMGU1YmQxYTdhNjM5IiwidHlwZSI6InJlZnJlc2gifQ.8cuwG7NuNbdOuKEQvIyQ82QpaAUU612hYNv7rPnZ860	testclient	testclient	f	2026-10-31 00:02:09.114891+03	2026-10-24 00:02:09.116474+03	2026-10-24 00:02:09.116477+03
105	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5NTI0LCJleHAiOjE3OTMzOTQzMjQsImp0aSI6IjliZDY2YmVjZTI1OTRmZmE4NzAzOTU5NWQ1YjY2OGQxIiwidHlwZSI6InJlZnJlc2gifQ.ouRvuD4m4CFQELOfbzHLtMmALjEs_XNe75_1TN0T6B0	testclient	testclient	f	2026-10-31 00:05:24.377051+03	2026-10-24 00:05:24.378755+03	2026-10-24 00:05:24.378758+03
106	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5NjAxLCJleHAiOjE3OTMzOTQ0MDEsImp0aSI6IjMzYWY4YWE1OGI4NjQ0YzI5YTkwMjBkZWIzY2NkYjFhIiwidHlwZSI6InJlZnJlc2gifQ.bf_okVOAD8CYIuNgKsg_7JVQt9j7lFWfQZK-aM3Vuo4	testclient	testclient	f	2026-10-31 00:06:41.538677+03	2026-10-24 00:06:41.540348+03	2026-10-24 00:06:41.54035+03
107	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5NjI1LCJleHAiOjE3OTMzOTQ0MjUsImp0aSI6IjMzODM4YmU2MjliMTQ5NDBhYzE2MjMwMjM5OTM3MzlmIiwidHlwZSI6InJlZnJlc2gifQ.1zg4haDToUr6B07-qsYEOme3rEbn_qJl5PFIbAhntLI	testclient	testclient	f	2026-10-31 00:07:05.948205+03	2026-10-24 00:07:05.949562+03	2026-10-24 00:07:05.949564+03
108	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5NjM3LCJleHAiOjE3OTMzOTQ0MzcsImp0aSI6Ijg5ZDA2Y2U4NWI2NTRlYTlhMzZkNDI5MjMyMTM4NThlIiwidHlwZSI6InJlZnJlc2gifQ.PMn80uPrdTMYqUmwdY6G4hWggwgkT_raLmwfwe_mtZI	testclient	testclient	f	2026-10-31 00:07:17.357163+03	2026-10-24 00:07:17.358654+03	2026-10-24 00:07:17.358656+03
109	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5NjM4LCJleHAiOjE3OTMzOTQ0MzgsImp0aSI6ImI3NzAwNzI3YmI1MTRlZmRhYTBhNjA5YWYwN2M0NGYxIiwidHlwZSI6InJlZnJlc2gifQ.mahBo4wMyqOM9WHhsB6zr4j15ywQg71yiJuSSuYpqhE	testclient	testclient	f	2026-10-31 00:07:18.065259+03	2026-10-24 00:07:18.065653+03	2026-10-24 00:07:18.065655+03
110	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5Njk5LCJleHAiOjE3OTMzOTQ0OTksImp0aSI6IjA1NjQ2Njk5YjEzMzQ2ZDlhMTY3ZTkxNzIwY2RhOGMxIiwidHlwZSI6InJlZnJlc2gifQ.5PcZxAn74b-eQTi1c2GmfhCfyfzTBO4y3si1xS_Lung	testclient	testclient	f	2026-10-31 00:08:19.198198+03	2026-10-24 00:08:19.199568+03	2026-10-24 00:08:19.19957+03
111	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzg5Njk5LCJleHAiOjE3OTMzOTQ0OTksImp0aSI6Ijg2YzhkNDM2Y2U0ZTQ5NTdiOWNmODMxYTA1OTJmYzJjIiwidHlwZSI6InJlZnJlc2gifQ.0wwv8HP2cSe_kzBYypBhbBZhLX-lGxXcqEr3vJUbNmk	testclient	testclient	f	2026-10-31 00:08:19.92238+03	2026-10-24 00:08:19.922962+03	2026-10-24 00:08:19.922964+03
112	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzkxMTkxLCJleHAiOjE3OTMzOTU5OTEsImp0aSI6IjMwMjE3NjVmZTk1MzQ4YmQ4YzlkNjkyMDcxZWRmYzA3IiwidHlwZSI6InJlZnJlc2gifQ.ePkiFIvcdtSbi5rtRvaeRiq18lMeW8HLG-VJGIh-i-A	testclient	testclient	f	2026-10-31 00:33:11.557549+03	2026-10-24 00:33:11.564416+03	2026-10-24 00:33:11.564423+03
113	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyNzkxMTk0LCJleHAiOjE3OTMzOTU5OTQsImp0aSI6Ijc1MzIzNTU4ZDQxMTRjM2ViMTFjZjc2OTM0YzMzNTUxIiwidHlwZSI6InJlZnJlc2gifQ.SBGDluEcfbCv6j5RQqyY3d79wjj3Es2qwes6NsmBG5A	testclient	testclient	f	2026-10-31 00:33:14.060397+03	2026-10-24 00:33:14.061927+03	2026-10-24 00:33:14.061933+03
116	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyODc3ODk3LCJleHAiOjE3OTM0ODI2OTcsImp0aSI6IjFjMTQ1NGJjZWY2NTRlMzJiNzY5YzdiMjIyNjVmZDQ5IiwidHlwZSI6InJlZnJlc2gifQ.4aYRg5doVBX1tUaujld3atxLjI-J-8HYwxTmKONpOsM	testclient	testclient	f	2026-11-01 00:38:17.479241+03	2026-10-25 00:38:17.48202+03	2026-10-25 00:38:17.482024+03
117	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyODc3OTc5LCJleHAiOjE3OTM0ODI3NzksImp0aSI6IjgzZjZkZWI1OGFmYjRhYTk4M2U0NDhmODUyNzVlZWVhIiwidHlwZSI6InJlZnJlc2gifQ.Hwy9TfXJJnBuQl6affhl2A8wNuxpJDoKWMJrOu6M8Bg	testclient	testclient	f	2026-11-01 00:39:39.966429+03	2026-10-25 00:39:39.9712+03	2026-10-25 00:39:39.971209+03
118	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyODc3OTk4LCJleHAiOjE3OTM0ODI3OTgsImp0aSI6ImQ2ZGM4NDExNmNmNDRiZWQ5OTkyNGI5MWU0ZGVlZjBiIiwidHlwZSI6InJlZnJlc2gifQ.uuM4qee-31IRZhlyhqkNixkrs_6R6o-NiVaP_LfneBw	testclient	testclient	f	2026-11-01 00:39:58.105117+03	2026-10-25 00:39:58.113109+03	2026-10-25 00:39:58.113121+03
119	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkyODc4MDU2LCJleHAiOjE3OTM0ODI4NTYsImp0aSI6ImU0YWU2YjNmNGQ5ZjQ5Y2M5NDJiNDk3YzAxY2VlOWY4IiwidHlwZSI6InJlZnJlc2gifQ.IgMJZua53sTBXapyZiarHVRXFeuOzgt-2UvLJMLwJro	testclient	testclient	f	2026-11-01 00:40:56.107734+03	2026-10-25 00:40:56.11506+03	2026-10-25 00:40:56.11507+03
120	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkzMDczNDYzLCJleHAiOjE3OTM2NzgyNjMsImp0aSI6IjMwZDcyNGJiNWJlMDRjN2U4NWE1M2FmZDExMzY5MzczIiwidHlwZSI6InJlZnJlc2gifQ.cfyzsBX5x0gkvMfNpUMy3YZpnJXoqSj_qhT4ztU2NBw	127.0.0.1	Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.9711	f	2026-11-03 06:57:43.170969+03	2026-10-27 06:57:43.174995+03	2026-10-27 06:57:43.175001+03
121	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkzMDc4NzU3LCJleHAiOjE3OTM2ODM1NTcsImp0aSI6ImVkMTVjNThkNDU2MDQxNjc5NjYwNDNiMmI1OTkxN2VmIiwidHlwZSI6InJlZnJlc2gifQ.P98c2QC548BgwMzThiNaT5Ks9lEKtTP3yhW_qqIvljo	testclient	testclient	f	2026-11-03 08:25:57.182191+03	2026-10-27 08:25:57.187171+03	2026-10-27 08:25:57.187178+03
122	364	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjQiLCJpYXQiOjE3OTMwNzg3NTgsImV4cCI6MTc5MzY4MzU1OCwianRpIjoiZmRkZjQ0YjkwNTAzNGE5Zjg2NzBiZTk3YzAxZWEwNmYiLCJ0eXBlIjoicmVmcmVzaCJ9.Ijz_k3xVoYsG8CMQN87s4ttVHDyuip2q2RTgZj_tXDU	testclient	testclient	f	2026-11-03 08:25:58.199482+03	2026-10-27 08:25:58.200846+03	2026-10-27 08:25:58.200853+03
123	399	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzOTkiLCJpYXQiOjE3OTMwNzg3NjAsImV4cCI6MTc5MzY4MzU2MCwianRpIjoiY2M5YjM4YTg0MWRjNGQzYTg4YjQ4OGI4MmJhOTNkOGEiLCJ0eXBlIjoicmVmcmVzaCJ9.EmEjK1XDBw5Qr08Qn_BQa5a34h8dxBHhQY0H0wpActM	testclient	testclient	f	2026-11-03 08:26:00.345458+03	2026-10-27 08:26:00.346954+03	2026-10-27 08:26:00.346962+03
124	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkzMDc4ODE5LCJleHAiOjE3OTM2ODM2MTksImp0aSI6ImEyYWVhNjU1OGYwMjQ5MDVhZGEwNjNhMjczZjUxNzI5IiwidHlwZSI6InJlZnJlc2gifQ.sCzCJ0kWq3-c4qFs_P23-XC54aUdJFepxMVvi-GHHP0	testclient	testclient	f	2026-11-03 08:26:59.343335+03	2026-10-27 08:26:59.349155+03	2026-10-27 08:26:59.349162+03
125	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkzMDc4OTYwLCJleHAiOjE3OTM2ODM3NjAsImp0aSI6IjI5MjI5YWNmYmIyNjRkMTQ5YTU1ZTcwODQ2ZjllYjdiIiwidHlwZSI6InJlZnJlc2gifQ.3MUBChNboqKaQLwgfhsWHADQPlrdfoc3X6nwv2173BM	testclient	testclient	f	2026-11-03 08:29:20.079971+03	2026-10-27 08:29:20.084712+03	2026-10-27 08:29:20.08472+03
126	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkzMDc5MDQ5LCJleHAiOjE3OTM2ODM4NDksImp0aSI6IjZlNGZiZWVhNzc4ZTRkYzRiODM1MTY5ZDM0YzEyODRiIiwidHlwZSI6InJlZnJlc2gifQ.8o56vnHGQcL4pAw383TAZ4Sh2dwinCs2Liy3Vcb6qq8	testclient	testclient	f	2026-11-03 08:30:49.473708+03	2026-10-27 08:30:49.479896+03	2026-10-27 08:30:49.479903+03
127	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkzMDc5MTAxLCJleHAiOjE3OTM2ODM5MDEsImp0aSI6IjhhMWNiZjA1NGE1NjRlYjI5MWU1NTQ2Y2I0NmEzMWU0IiwidHlwZSI6InJlZnJlc2gifQ.adb7eXPMOY1TgbimkhANa_Dzectxx_n9Te4mP5LL-2c	testclient	testclient	f	2026-11-03 08:31:41.001887+03	2026-10-27 08:31:41.008239+03	2026-10-27 08:31:41.008249+03
128	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkzMDc5MTQxLCJleHAiOjE3OTM2ODM5NDEsImp0aSI6ImQ1NWI1ZDVkODk5YzQ1MTNhMzdkYTZmZjBkOGY4Yjg1IiwidHlwZSI6InJlZnJlc2gifQ.i9Ep-McBx_pFoLJGdrtmRUpos56bBMDzkVVnNuezaew	testclient	testclient	f	2026-11-03 08:32:21.673522+03	2026-10-27 08:32:21.680198+03	2026-10-27 08:32:21.680208+03
129	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkzMDc5MTYwLCJleHAiOjE3OTM2ODM5NjAsImp0aSI6IjRjZGJiNzBiOWQ1ODQ0ODE5MTZlNDFlZjBhMzhiOTEzIiwidHlwZSI6InJlZnJlc2gifQ.-u9NjS88YRn5QkYq-Z6mdazXhxkOunY-VCzabhKE1Es	testclient	testclient	f	2026-11-03 08:32:40.309882+03	2026-10-27 08:32:40.316511+03	2026-10-27 08:32:40.316519+03
130	364	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjQiLCJpYXQiOjE3OTMwNzkxNjEsImV4cCI6MTc5MzY4Mzk2MSwianRpIjoiOGNiMTkwNzljNzI5NDg5MmI1N2U2Y2YxNzExMzMxMzUiLCJ0eXBlIjoicmVmcmVzaCJ9.AcHG1TFE5Nx_y6zbo0uHlqQXVESwtgGf1PsPGSuTiyI	testclient	testclient	f	2026-11-03 08:32:41.34035+03	2026-10-27 08:32:41.341545+03	2026-10-27 08:32:41.341555+03
131	400	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MDAiLCJpYXQiOjE3OTMwNzkxNjMsImV4cCI6MTc5MzY4Mzk2MywianRpIjoiZTVhMWE5NWYxNjVmNDNkNzg0M2ZkNDZiYzEzNGI2MjEiLCJ0eXBlIjoicmVmcmVzaCJ9.W3W4fEpqz0Mxyn-4vGGcTxsQ7sPBoy5waCYOo2of6wk	testclient	testclient	f	2026-11-03 08:32:43.389283+03	2026-10-27 08:32:43.390922+03	2026-10-27 08:32:43.390931+03
132	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3NjAxLCJleHAiOjE3OTQ5ODI0MDEsImp0aSI6IjFmNjVjYmVkMzRjMTQxYjZhZmQ4ODkyZTRjODQ5OGRkIiwidHlwZSI6InJlZnJlc2gifQ.-S3mJOf1laU8TRJmYv-BozVh8-3B-CrDU7z_RpsKinU	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:13:21.84517+03	2026-11-11 09:13:21.847013+03	2026-11-11 09:13:21.847015+03
133	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3NjQ2LCJleHAiOjE3OTQ5ODI0NDYsImp0aSI6IjUwYmM0NzJhN2Y1YjQ1MjA5ZDA5OTljMWZkYmU1Y2JkIiwidHlwZSI6InJlZnJlc2gifQ.UdHir-5Vw7C7zsfXBuUsp4WWgSnvNhWAErIyz6DjXSY	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:14:06.260205+03	2026-11-11 09:14:06.261078+03	2026-11-11 09:14:06.26108+03
134	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3NjQ3LCJleHAiOjE3OTQ5ODI0NDcsImp0aSI6ImU1NjM3NjBjYTQ0OTRkYThiOTEzY2QzNzdjOGZlOWU1IiwidHlwZSI6InJlZnJlc2gifQ.g3Z6h6xKwJLNcEECThl3miWJoWwejUNsv1Zbfa6NyLw	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:14:07.332292+03	2026-11-11 09:14:07.332664+03	2026-11-11 09:14:07.332666+03
135	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3NzUzLCJleHAiOjE3OTQ5ODI1NTMsImp0aSI6IjRjNjg0MDgwODMwNzRiMWNiY2JiYjNkOGVhNWJhNzNlIiwidHlwZSI6InJlZnJlc2gifQ.MgUB3kdBf484fEjoFjCEV--rU4_XzP0hpUJVHdnkgk8	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:15:53.937999+03	2026-11-11 09:15:53.939638+03	2026-11-11 09:15:53.939642+03
136	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3NzY0LCJleHAiOjE3OTQ5ODI1NjQsImp0aSI6ImNkNzkzOTQ3YzljMjRkNjM4MDllN2YzOTA5Mjc4YTM1IiwidHlwZSI6InJlZnJlc2gifQ.MR5fqb51VtM-VHiTAOOX9gWobqDt8wD_4HWgiosyAN4	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:16:04.549642+03	2026-11-11 09:16:04.550086+03	2026-11-11 09:16:04.550088+03
137	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3Nzc0LCJleHAiOjE3OTQ5ODI1NzQsImp0aSI6Ijc3NzRmYzA0NzA3YTQ1NzliZTQzYzQxMWZhNjM5MGM2IiwidHlwZSI6InJlZnJlc2gifQ.49NkiZvQdsM_lpfW6G7v8humvKvMAvbuyBdVQJt4fCo	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:16:14.736084+03	2026-11-11 09:16:14.736458+03	2026-11-11 09:16:14.736459+03
138	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3OTIwLCJleHAiOjE3OTQ5ODI3MjAsImp0aSI6ImE5NmExZWRlN2M0NTQ2NzlhN2ExMWNlNGQ1NGM2MTNhIiwidHlwZSI6InJlZnJlc2gifQ.Pzp8xN6DlqY842-Fgl5Wb-qdT9MJxXGcOxSfnPfIYA0	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:18:40.347118+03	2026-11-11 09:18:40.348448+03	2026-11-11 09:18:40.34845+03
139	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3OTU4LCJleHAiOjE3OTQ5ODI3NTgsImp0aSI6IjgzMzE2NDcyYzAyMTRhY2JhZTc5OTNlNTlkNjlhODU5IiwidHlwZSI6InJlZnJlc2gifQ.vFB96ZRNz-1WNxC1U-Z-3GiRNL-oOe6So3sGOilEsuQ	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:19:18.894561+03	2026-11-11 09:19:18.895058+03	2026-11-11 09:19:18.89506+03
140	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc3OTgzLCJleHAiOjE3OTQ5ODI3ODMsImp0aSI6IjQ1ZTJkMzNjZDFlNTQ4M2NiMzc5NjNkZmFmYTNlN2NlIiwidHlwZSI6InJlZnJlc2gifQ.ovoqOd3fdjwh9CTxtlUCZMlOxBd1hllbqIPDe5PqTlY	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:19:43.332214+03	2026-11-11 09:19:43.332735+03	2026-11-11 09:19:43.332738+03
141	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc4MDIwLCJleHAiOjE3OTQ5ODI4MjAsImp0aSI6ImVjZmY4OWVkNTNjMTRmY2M4NjFmZGExOTExMGIwNjk5IiwidHlwZSI6InJlZnJlc2gifQ.Tep7OPGHF6Bqk-E892yVercnpKek2K9Oo8Dnumto6VE	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:20:20.340582+03	2026-11-11 09:20:20.341182+03	2026-11-11 09:20:20.341185+03
142	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0Mzc4MDIxLCJleHAiOjE3OTQ5ODI4MjEsImp0aSI6IjM0NWVlZGQ2MWVmMzQ0Nzk4MDY0NGYzMzY3MzY4NDg4IiwidHlwZSI6InJlZnJlc2gifQ.sm1Y_SVv4KTiw_wcY9nAIV5Q-qLCHnrddOIDAkPl-34	127.0.0.1	python-requests/2.34.2	f	2026-11-18 09:20:21.114521+03	2026-11-11 09:20:21.115033+03	2026-11-11 09:20:21.115035+03
143	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDAyMzc1LCJleHAiOjE3OTUwMDcxNzUsImp0aSI6IjUzNjZlYzRjNTU3NzRkOWU4YmU2M2E4ZTg2NDc4MjVlIiwidHlwZSI6InJlZnJlc2gifQ.yAypKEUj7KPw8jIYDDZVv3O_mmCO0uw1eIaqwGXha7w	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-18 16:06:15.394041+03	2026-11-11 16:06:15.395368+03	2026-11-11 16:52:10.915743+03
144	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDA1MTk0LCJleHAiOjE3OTUwMDk5OTQsImp0aSI6ImY0MWU3OWUxNjMyYTRjNmFhZDhlNzYxYzIzZTAwYmU4IiwidHlwZSI6InJlZnJlc2gifQ.-NlY7oFKmgAmbXNAeA-6GOEZzgYjwWMri5IRM941Bog	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-18 16:53:14.997855+03	2026-11-11 16:53:14.999916+03	2026-11-11 16:54:48.231653+03
145	309	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDkiLCJpYXQiOjE3OTQ0NjY5MjUsImV4cCI6MTc5NTA3MTcyNSwianRpIjoiNDM5MWYzMWEwODM1NGIyMDhhYTIzMGYzNTYyNGIzYmQiLCJ0eXBlIjoicmVmcmVzaCJ9.KJeE_crqbksNi6OgJX1G35HwzbXqLLqQ9BDoh-ATlTA	testclient	testclient	f	2026-11-19 10:02:05.017687+03	2026-11-12 10:02:05.019885+03	2026-11-12 10:02:05.019891+03
146	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDY2OTI1LCJleHAiOjE3OTUwNzE3MjUsImp0aSI6ImRhYzJmODJhZDQwYzRmZWVhM2NiZGM4Yzk3ZDE1ODA1IiwidHlwZSI6InJlZnJlc2gifQ.d78OaW743Ylzo6f1Kz8VAPwWIG0ESY50ejXs8JCgjbQ	testclient	testclient	f	2026-11-19 10:02:05.3128+03	2026-11-12 10:02:05.31356+03	2026-11-12 10:02:05.313575+03
147	309	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDkiLCJpYXQiOjE3OTQ0NjcwNjcsImV4cCI6MTc5NTA3MTg2NywianRpIjoiMzZmZWYzMWIyYzY1NDA0ODk3OTQ2MGIxMzlhYWYyMzQiLCJ0eXBlIjoicmVmcmVzaCJ9.3xuVgwZw3XMp1OPYfAmZ1y88TVF54T7L12kK12C0R2o	testclient	testclient	f	2026-11-19 10:04:27.777238+03	2026-11-12 10:04:27.779131+03	2026-11-12 10:04:27.779134+03
148	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDY3MDY4LCJleHAiOjE3OTUwNzE4NjgsImp0aSI6ImZmNjBmZjQ4MmVjMzQwM2E4MmM4ODRmMTcyNTAwMDU1IiwidHlwZSI6InJlZnJlc2gifQ.OFVDsM3-EPjU-iCKHY_iCoLyldFwugzniKK2B62fxCU	testclient	testclient	f	2026-11-19 10:04:28.038917+03	2026-11-12 10:04:28.039501+03	2026-11-12 10:04:28.039504+03
149	309	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDkiLCJpYXQiOjE3OTQ0Njc2MzEsImV4cCI6MTc5NTA3MjQzMSwianRpIjoiMmE5OTg4NTJkMzFmNDE1ODlmYmU3MDk2ZTg1OWU2MTMiLCJ0eXBlIjoicmVmcmVzaCJ9.MKt9lpkQthjey5Rg4spfLX7jLoBaChIHekqTToypgCA	testclient	testclient	f	2026-11-19 10:13:51.250895+03	2026-11-12 10:13:51.252861+03	2026-11-12 10:13:51.252864+03
150	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDY3NjMxLCJleHAiOjE3OTUwNzI0MzEsImp0aSI6IjI0NmQzZGJiOGRjYTQzMTRiZDU4YjljMDQxMDkzNTBhIiwidHlwZSI6InJlZnJlc2gifQ.ybygBHXwJd53JA5aeGNY22TS7n-K8Rlwc078GlK1efY	testclient	testclient	f	2026-11-19 10:13:51.565487+03	2026-11-12 10:13:51.565983+03	2026-11-12 10:13:51.565985+03
151	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDcwNjY2LCJleHAiOjE3OTUwNzU0NjYsImp0aSI6IjA1YzRjMmQ5MmZmZjQ1NTlhYzg2Yjg4YzI5MzUzNzUxIiwidHlwZSI6InJlZnJlc2gifQ.0-KNbSXPdyz4_Id-efvBO55O6-JTYJeEK0bCbuMTqsY	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-19 11:04:26.19587+03	2026-11-12 11:04:26.199653+03	2026-11-12 11:33:54.590708+03
152	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDcyNTg0LCJleHAiOjE3OTUwNzczODQsImp0aSI6Ijk2MmMzMWY5ZDk5ZDQxZDJiNDEwMDU2MjNlYjkzYmY5IiwidHlwZSI6InJlZnJlc2gifQ.SP414b7Oc6PBcFqf7qxceb50JQMCVQFu1yd9flP635c	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	f	2026-11-19 11:36:24.039095+03	2026-11-12 11:36:24.040515+03	2026-11-12 11:36:24.040522+03
153	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDc1NjcyLCJleHAiOjE3OTUwODA0NzIsImp0aSI6IjI0MDgzMzYwOWQyMzRhNzY4MmFmZDQ2MGJiODI5MDRmIiwidHlwZSI6InJlZnJlc2gifQ.Avn4excsJbCtTucbRXUxClE4rldM61PQrDfapqs04bo	\N	\N	f	2026-11-19 12:27:52.981601+03	2026-11-12 12:27:52.98401+03	2026-11-12 12:27:52.984013+03
154	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDc1NzI1LCJleHAiOjE3OTUwODA1MjUsImp0aSI6ImZkYjMwYTU0MGUyZDQ3OGM5ZjVkYTQzNDdkZTA0MDkzIiwidHlwZSI6InJlZnJlc2gifQ.8FWGEl3B58RYsUlk8vf168Q7wL4MdwjSOzarnzexyqk	127.0.0.1	Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.9711	f	2026-11-19 12:28:45.155405+03	2026-11-12 12:28:45.157857+03	2026-11-12 12:28:45.15786+03
155	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDc2NjExLCJleHAiOjE3OTUwODE0MTEsImp0aSI6Ijc1NmIwNGJhMzU0MjQyYzk4YWI2ODM5NzkxOWJjY2Y0IiwidHlwZSI6InJlZnJlc2gifQ.iUJaWmzobjEE5UWZ1LJ2wgOGpeDQmM3HttfRZPvdzSI	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-19 12:43:31.289317+03	2026-11-12 12:43:31.29553+03	2026-11-12 12:47:24.150512+03
156	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDk3MzI3LCJleHAiOjE3OTUxMDIxMjcsImp0aSI6IjU3MGM3MzMzMThhZTQwMjhiNzlmYTkxZDc1ZjM1YzA4IiwidHlwZSI6InJlZnJlc2gifQ.6SPh6XUVj-2soZYYH25m1KPsdFbwJ1hQ1A8HBrEokGY	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-19 18:28:47.653399+03	2026-11-12 18:28:47.658521+03	2026-11-12 18:41:12.734276+03
157	377	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzciLCJpYXQiOjE3OTQ0OTg3ODYsImV4cCI6MTc5NTEwMzU4NiwianRpIjoiOWZiZWRkMjk0YzFkNGVmOTk1NzVhZWRjNjkxNTJiZjUiLCJ0eXBlIjoicmVmcmVzaCJ9.HMNHBGbAPktV4GzM43ykddkRQ9YbEZO5W42AjUwoA3E	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-19 18:53:06.068586+03	2026-11-12 18:53:06.070089+03	2026-11-12 19:10:23.178235+03
158	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NDk5ODM1LCJleHAiOjE3OTUxMDQ2MzUsImp0aSI6IjM1YmY2MDJjNTM3MTQwZDI5Njc4ZGNlZjRhYWZiY2QzIiwidHlwZSI6InJlZnJlc2gifQ.FipNhtZWGThZgd8aXAvxMI3slKNNd7-Ru8WJ6rmNN7M	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-19 19:10:35.948996+03	2026-11-12 19:10:35.950883+03	2026-11-12 19:10:49.508841+03
159	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTQ2NDgwLCJleHAiOjE3OTUxNTEyODAsImp0aSI6ImNhZmQ1NzVmMDk5YjRiMTRhM2FiZjhiNjE1OTI0YjQwIiwidHlwZSI6InJlZnJlc2gifQ.n0lSWtlmotcSpvHStveRDFSqjHjpE1OwyeLwlDr52kk	127.0.0.1	Python-urllib/3.14	f	2026-11-20 08:08:00.82861+03	2026-11-13 08:08:00.830228+03	2026-11-13 08:08:00.830231+03
160	377	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNzciLCJpYXQiOjE3OTQ1NDY1MjAsImV4cCI6MTc5NTE1MTMyMCwianRpIjoiN2Y1OGU2NTRjY2Y1NDNjY2FkZDFmNTg1MWQ5ZjRlMmYiLCJ0eXBlIjoicmVmcmVzaCJ9.NPiJkKIUbMk49hEvcDY4Q27TulC4yhGCs7FchcL7vy0	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	f	2026-11-20 08:08:40.227784+03	2026-11-13 08:08:40.228291+03	2026-11-13 08:08:40.228294+03
161	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NTMxNjcsImV4cCI6MTc5NTE1Nzk2NywianRpIjoiNzg5NDE0MWZhMWE4NDgwYTlhNzkxYzg1MzY4YzNmOTkiLCJ0eXBlIjoicmVmcmVzaCJ9.nOg_zJ-i5jyxk08XpXydUPKCW0ZmNmCKXTyKKulGFus	testclient	testclient	f	2026-11-20 09:59:27.198891+03	2026-11-13 09:59:27.204614+03	2026-11-13 09:59:27.204623+03
162	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NTQzMDYsImV4cCI6MTc5NTE1OTEwNiwianRpIjoiOTYwYWFmNTcxYWMwNGRiN2FhOTg1OWVlZWM0ZTRjNzMiLCJ0eXBlIjoicmVmcmVzaCJ9.Yku5khVayfWvFa4LZvkerRt8b6oFF5GhqmUkIb5A2TY	testclient	testclient	f	2026-11-20 10:18:26.748197+03	2026-11-13 10:18:26.751906+03	2026-11-13 10:18:26.751912+03
163	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTU1ODEzLCJleHAiOjE3OTUxNjA2MTMsImp0aSI6IjY5OGUyY2U0Nzg5MDQ3NjRiZWNjMzAxM2ViNDI4YTQzIiwidHlwZSI6InJlZnJlc2gifQ.b1XdD4nB5tRJ5OAMgDeqHnuOnzDmOTyNwFIx5wvWjK8	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-20 10:43:33.448065+03	2026-11-13 10:43:33.452678+03	2026-11-13 10:43:44.853865+03
164	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTU1ODM5LCJleHAiOjE3OTUxNjA2MzksImp0aSI6ImY2YTkyZmVhNTQ5MTQzYzc5MmI2OTQ1NGMwMjMwYmQxIiwidHlwZSI6InJlZnJlc2gifQ.49kQdnDMvTPMokgbXptIsw2I95uNiMQK7JNjABM0yNQ	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-20 10:43:59.73351+03	2026-11-13 10:43:59.735578+03	2026-11-13 10:44:05.437496+03
165	410	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MTAiLCJpYXQiOjE3OTQ1NTYxODAsImV4cCI6MTc5NTE2MDk4MCwianRpIjoiMWYzYWQyZWZhMzJlNGFhMTk5YmY5OTZhMWEyZDM2MzYiLCJ0eXBlIjoicmVmcmVzaCJ9.zHGnOXXQUouctxD-pScfzG45AEH14v5FnroVgPUWQvc	127.0.0.1	python-requests/2.34.2	f	2026-11-20 10:49:40.475415+03	2026-11-13 10:49:40.476456+03	2026-11-13 10:49:40.476461+03
166	410	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MTAiLCJpYXQiOjE3OTQ1NTYzNTgsImV4cCI6MTc5NTE2MTE1OCwianRpIjoiZDBlMmMxZjllZTRiNGRiZmE0MGY2ZTg1ZGEzYjY1ZTQiLCJ0eXBlIjoicmVmcmVzaCJ9.scRmZslRcWGZTqHje-O4m7Jbe_as9tu9hYq8PlNXX8o	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-20 10:52:38.559017+03	2026-11-13 10:52:38.561171+03	2026-11-13 10:56:58.778066+03
167	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTYxMzIwLCJleHAiOjE3OTUxNjYxMjAsImp0aSI6IjhmNGFhZTViZDFkNjRmZjI4ZWYzZWRjMzQwMTA3NzhlIiwidHlwZSI6InJlZnJlc2gifQ.J5-GNa9Z-JQkylgUkOCNX5YZFIMTHoUP4Jkp-qXRye8	testclient	testclient	f	2026-11-20 12:15:20.227536+03	2026-11-13 12:15:20.228896+03	2026-11-13 12:15:20.228898+03
168	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTYxMzM2LCJleHAiOjE3OTUxNjYxMzYsImp0aSI6IjVhZDNiMDY1YjBkZjQzMTdhY2JlNGU0MWM1MTI1MzdhIiwidHlwZSI6InJlZnJlc2gifQ.MDorn1aBPMua0PQHFbLFPpbRHdORJ9Jfo_9azvxICMM	testclient	testclient	f	2026-11-20 12:15:36.49883+03	2026-11-13 12:15:36.50043+03	2026-11-13 12:15:36.500432+03
169	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTYxMzYwLCJleHAiOjE3OTUxNjYxNjAsImp0aSI6IjlkZjMxYmNlNjMxMTQ3OThiYzkxY2Q1ODU1MmE1MDFlIiwidHlwZSI6InJlZnJlc2gifQ.Ju9P2ghS1K1srvMoeISmrBX4zQBPGeCNaxmZ9IMYZ-U	testclient	testclient	f	2026-11-20 12:16:00.075491+03	2026-11-13 12:16:00.077067+03	2026-11-13 12:16:00.07707+03
170	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTYxMzkxLCJleHAiOjE3OTUxNjYxOTEsImp0aSI6IjZjZmVhOWU3NTE4YzRmZjZiZDUxMDYyNWUzZWU1ZTk0IiwidHlwZSI6InJlZnJlc2gifQ.B3-4yX-Whr2AkpGJtR8PO0OEPI7z5dYUeFqNpx-LpH0	testclient	testclient	f	2026-11-20 12:16:31.273812+03	2026-11-13 12:16:31.275443+03	2026-11-13 12:16:31.275446+03
171	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTYxNDE0LCJleHAiOjE3OTUxNjYyMTQsImp0aSI6IjVhMmM1MjNiYmJlNzRhMWQ4Yjc0NzE1OGU1MjQ4OTJlIiwidHlwZSI6InJlZnJlc2gifQ.WTjCP0-cMbgnxUQwgXQmzOHM2GSXcwA0oqLJqQ-lPZU	testclient	testclient	f	2026-11-20 12:16:54.556877+03	2026-11-13 12:16:54.55855+03	2026-11-13 12:16:54.558552+03
172	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTYzMTg4LCJleHAiOjE3OTUxNjc5ODgsImp0aSI6IjhmOTU3YWM5MThlYzRlY2JiMWExMDgwN2JlYzM0ZDRmIiwidHlwZSI6InJlZnJlc2gifQ.G61z4UOM03NLuyHWXOfIuyy_GNxYEhJ-8W1SKL1SbPo	127.0.0.1	python-requests/2.34.2	f	2026-11-20 12:46:28.351974+03	2026-11-13 12:46:28.353232+03	2026-11-13 12:46:28.353234+03
173	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NjMyNTUsImV4cCI6MTc5NTE2ODA1NSwianRpIjoiZWRiOWQyMDFlMTQ4NDlkNDljZmJlNmFiMmE4MjIwMjgiLCJ0eXBlIjoicmVmcmVzaCJ9.z3ziMq6z_3Vii67-wVDUOoTO5kCR7JmTGZipJXdueME	testclient	testclient	f	2026-11-20 12:47:35.948368+03	2026-11-13 12:47:35.951164+03	2026-11-13 12:47:35.951166+03
174	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NjM5NDgsImV4cCI6MTc5NTE2ODc0OCwianRpIjoiYWI3ZjY3NzU1ZjZjNDk2MDk5NGNhNTBjZDBlYjkyYzQiLCJ0eXBlIjoicmVmcmVzaCJ9.3L10T1VPoiUfYumYty_k8ZU-L3wT5znE4UnTI4XAbjg	testclient	testclient	f	2026-11-20 12:59:08.23485+03	2026-11-13 12:59:08.238309+03	2026-11-13 12:59:08.238315+03
175	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NjQxNjIsImV4cCI6MTc5NTE2ODk2MiwianRpIjoiNDY5M2M4ZmZlN2VjNGEwOGI5ZTRjZjI4Mjc0ODE4NDgiLCJ0eXBlIjoicmVmcmVzaCJ9.B9k8wnnqHltvDoBmOG8EMLA5PpI0DsV54U8wIBJRGfo	testclient	testclient	f	2026-11-20 13:02:42.055136+03	2026-11-13 13:02:42.0589+03	2026-11-13 13:02:42.058908+03
176	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NjUwMTQsImV4cCI6MTc5NTE2OTgxNCwianRpIjoiZWJmNzM0OGQ1ZWI0NDZkNWJiNjg5ZTEyM2I3MjkzZWEiLCJ0eXBlIjoicmVmcmVzaCJ9.FRNodwxlo9Uik6uS4xl-E09owefQkrUzmKXIMPHfhU0	testclient	testclient	f	2026-11-20 13:16:54.773143+03	2026-11-13 13:16:54.774516+03	2026-11-13 13:16:54.774519+03
177	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NzQyOTQsImV4cCI6MTc5NTE3OTA5NCwianRpIjoiMDU1YjgxOTQxODQzNGJjN2FjZmNiYTkwMWM4N2U5NTAiLCJ0eXBlIjoicmVmcmVzaCJ9.qfTmFEJz1pkplzPPH8dLz6O6LnmMXGYA04RmR3bnaVk	testclient	testclient	f	2026-11-20 15:51:34.545115+03	2026-11-13 15:51:34.546895+03	2026-11-13 15:51:34.546897+03
178	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NzQ4MjgsImV4cCI6MTc5NTE3OTYyOCwianRpIjoiMTJiNmJlMTJmNmJhNDQzMTg5OThiMDdmZDcxN2FmNTAiLCJ0eXBlIjoicmVmcmVzaCJ9.oSZjRtR3Fz_WYAVxlOwmElZdCjunRhbNvQOyejGL1FI	testclient	testclient	f	2026-11-20 16:00:28.258322+03	2026-11-13 16:00:28.26001+03	2026-11-13 16:00:28.260013+03
179	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NzQ5MTIsImV4cCI6MTc5NTE3OTcxMiwianRpIjoiMDBhMzI5NDM2ZTVhNDZmNTlmODU0Y2Q5YzBiODBiOTUiLCJ0eXBlIjoicmVmcmVzaCJ9.2wIeOx6ghWXRYyTBAK6cx9EwLxeaoW0EEP7uav71Hdg	testclient	testclient	f	2026-11-20 16:01:52.702944+03	2026-11-13 16:01:52.70439+03	2026-11-13 16:01:52.704392+03
180	424	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQiLCJpYXQiOjE3OTQ1NzUwMDcsImV4cCI6MTc5NTE3OTgwNywianRpIjoiN2E3OWJlZTc5MzkwNDdiY2FkZGRkNzI0OTE2NDUwZmMiLCJ0eXBlIjoicmVmcmVzaCJ9.Tzs6P77MCC0pskHZtkKfwsWhefWQCtd2YRxd3L3fSSg	testclient	testclient	f	2026-11-20 16:03:27.868058+03	2026-11-13 16:03:27.869128+03	2026-11-13 16:03:27.869131+03
181	424	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQiLCJpYXQiOjE3OTQ1NzUwMjQsImV4cCI6MTc5NTE3OTgyNCwianRpIjoiYWJhMGVkYWIzZTA1NDlhMjllNjU1NmJmNTZhOGZmMjAiLCJ0eXBlIjoicmVmcmVzaCJ9.6IfX-RxfTrmXPdY4g8HHyyKhDKJlpXsL0y1KeF-NLfE	testclient	testclient	f	2026-11-20 16:03:44.93298+03	2026-11-13 16:03:44.933864+03	2026-11-13 16:03:44.933866+03
182	424	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQiLCJpYXQiOjE3OTQ1NzUwNDMsImV4cCI6MTc5NTE3OTg0MywianRpIjoiZDVhYjMwNGJlMjUxNDkwNTg1NGRhZTFjOTUwMTlhMWQiLCJ0eXBlIjoicmVmcmVzaCJ9.lwIJse8zufw2PzCbqJZ6zhIJ6w55_8aINDV0ZANPRS4	testclient	testclient	f	2026-11-20 16:04:03.878041+03	2026-11-13 16:04:03.878915+03	2026-11-13 16:04:03.878917+03
183	424	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQiLCJpYXQiOjE3OTQ1NzUwNTMsImV4cCI6MTc5NTE3OTg1MywianRpIjoiMDkxMWU5NjQ0MDBhNDAyNGJkZDA5NTEzY2I4N2RlOWQiLCJ0eXBlIjoicmVmcmVzaCJ9.DeSs6pVa5mQ6YioBDAMZjlWqdGT5VohHdp5EwGqAGo0	testclient	testclient	f	2026-11-20 16:04:13.670787+03	2026-11-13 16:04:13.671976+03	2026-11-13 16:04:13.671979+03
184	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NzUwNTUsImV4cCI6MTc5NTE3OTg1NSwianRpIjoiNjE0MzYyNThjMTNlNDE2MjgyNzZhMGE1MGExOGM2YWYiLCJ0eXBlIjoicmVmcmVzaCJ9.dwkk81OjgdSt83HspDE1VTFN5iIxLeJ9THSsn8V3Zog	testclient	testclient	f	2026-11-20 16:04:15.093931+03	2026-11-13 16:04:15.094309+03	2026-11-13 16:04:15.094311+03
185	424	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQiLCJpYXQiOjE3OTQ1NzUzNzgsImV4cCI6MTc5NTE4MDE3OCwianRpIjoiMWFlMjljMWQ1YzQ0NDBmM2FiMmE1NDU3NmFmMDhkOTgiLCJ0eXBlIjoicmVmcmVzaCJ9.Bev2UNMkxCGp68X7lDyCifm2o-bPi9hADyJVSjksa3U	testclient	testclient	f	2026-11-20 16:09:38.562137+03	2026-11-13 16:09:38.563121+03	2026-11-13 16:09:38.563123+03
186	304	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDQiLCJpYXQiOjE3OTQ1NzUzNzksImV4cCI6MTc5NTE4MDE3OSwianRpIjoiNWJhMmJmMzM3NWM1NGNhY2I0OGIwZTk2ODEwYmM1YzIiLCJ0eXBlIjoicmVmcmVzaCJ9.HzUHrzWYC7IX_NCkVl7SSem01OI00CDK5K0Tzgue4jM	testclient	testclient	f	2026-11-20 16:09:39.571835+03	2026-11-13 16:09:39.572283+03	2026-11-13 16:09:39.572285+03
187	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2MDE1LCJleHAiOjE3OTUxODA4MTUsImp0aSI6IjA1NDRlNjU2ZjBhNjQ4NGJhNDIwNDY2YWYyNTUwYzg3IiwidHlwZSI6InJlZnJlc2gifQ.y-D5Q2uYV4wESDFwSXXWyiJkqVHX5KoJItz0Gcx57So	testclient	testclient	f	2026-11-20 16:20:15.028664+03	2026-11-13 16:20:15.030506+03	2026-11-13 16:20:15.030508+03
188	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2MDI0LCJleHAiOjE3OTUxODA4MjQsImp0aSI6IjIwNTc3Zjk2YjU1OTQxZGM4YTFkZmNkYTBjMDEzNTUxIiwidHlwZSI6InJlZnJlc2gifQ.u_R6psnSxBY_AhnQ-1R-fw1CYx-HP8XD9KkiU-OY-NM	testclient	testclient	f	2026-11-20 16:20:24.85094+03	2026-11-13 16:20:24.852476+03	2026-11-13 16:20:24.852478+03
189	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2MDI1LCJleHAiOjE3OTUxODA4MjUsImp0aSI6ImQ1YjZhY2E1MTljYzRjZDQ5MDZiNzhiM2UzYzM0MDgxIiwidHlwZSI6InJlZnJlc2gifQ.Vg3ihI75mlq9hICw0u_P2_wUDWcpF39ipz5_PJPDf-o	testclient	testclient	f	2026-11-20 16:20:25.588954+03	2026-11-13 16:20:25.589317+03	2026-11-13 16:20:25.589319+03
190	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2Mjk2LCJleHAiOjE3OTUxODEwOTYsImp0aSI6IjJkYWZlYjI0ZGYzNDQ0NDk5YzI4OWFmM2I5ZTQ4YzZkIiwidHlwZSI6InJlZnJlc2gifQ.tEP_sHt-wEefo40MXnY3rgrNCzj2hytuI7C1I6hFICU	127.0.0.1	python-requests/2.34.2	f	2026-11-20 16:24:56.818672+03	2026-11-13 16:24:56.819443+03	2026-11-13 16:24:56.819445+03
191	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2MzYwLCJleHAiOjE3OTUxODExNjAsImp0aSI6Ijc3MTE4NWY4OWNhZjQ4ZDJiNTlhOTA3MDU4OGZhOTY3IiwidHlwZSI6InJlZnJlc2gifQ.pBElZFH2j2YxcgWmgDWJeomBGMJ3ouYoV7yX6EkohME	127.0.0.1	python-requests/2.34.2	f	2026-11-20 16:26:00.906068+03	2026-11-13 16:26:00.906711+03	2026-11-13 16:26:00.906714+03
192	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2NDU1LCJleHAiOjE3OTUxODEyNTUsImp0aSI6IjRmOTZhZjYwNTMzNjQxZmZhNGI2Nzc2NDI4MDg1N2EwIiwidHlwZSI6InJlZnJlc2gifQ.Cdvm8kvSybtfCvWoGOLnWPNLjxLaV2PcxR2T892yBMM	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	f	2026-11-20 16:27:35.066822+03	2026-11-13 16:27:35.067348+03	2026-11-13 16:27:35.06735+03
193	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2NDgwLCJleHAiOjE3OTUxODEyODAsImp0aSI6IjRhY2FkZWE4MmVhODQxN2VhN2JmMmYzZDVlMzdlMTI1IiwidHlwZSI6InJlZnJlc2gifQ.eJtJykioNCLZw2ahZnDxCYWPX1zzYnHEMcjOt6gSD3k	127.0.0.1	python-requests/2.34.2	f	2026-11-20 16:28:00.917066+03	2026-11-13 16:28:00.917625+03	2026-11-13 16:28:00.917628+03
194	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2NTI3LCJleHAiOjE3OTUxODEzMjcsImp0aSI6IjNhMGIzZDZlZGY5MDRjNTRiMzk1NzRjODYyYTM2ZmJiIiwidHlwZSI6InJlZnJlc2gifQ.5sDza3nPrufSAaV071xF-SKjmP9KmQClmW1ln5pmyBQ	127.0.0.1	python-requests/2.34.2	f	2026-11-20 16:28:47.238013+03	2026-11-13 16:28:47.238654+03	2026-11-13 16:28:47.238656+03
195	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2NTM2LCJleHAiOjE3OTUxODEzMzYsImp0aSI6IjRmYmZmOGU4YzBmMDQ0Mjk5YzI2YjhkNTJhMTU3Mzg2IiwidHlwZSI6InJlZnJlc2gifQ.rhDyY9tVnDC3NvepCpz9EslBHjMrO13Hz5GClI3qCl8	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	f	2026-11-20 16:28:56.581146+03	2026-11-13 16:28:56.581631+03	2026-11-13 16:28:56.581633+03
196	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2NTYzLCJleHAiOjE3OTUxODEzNjMsImp0aSI6IjdjNGY3MTk5NTE5NTQwZDFhYTljMDllMmNmNmZlNGZmIiwidHlwZSI6InJlZnJlc2gifQ.K0Yp0vvafPJGmB2kk3CAPHGHo2URYNT3sPTo8yBPeMU	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	f	2026-11-20 16:29:23.782525+03	2026-11-13 16:29:23.791196+03	2026-11-13 16:29:23.791203+03
197	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2ODUyLCJleHAiOjE3OTUxODE2NTIsImp0aSI6Ijk5ZTNlMzIzNmQ3MzRmMmI5N2EwY2I1ZmZkMDk2YmNkIiwidHlwZSI6InJlZnJlc2gifQ.LX7cBqm_OLLeVjvDGKlq1OLHWKXlVUXwa2Lfe3w27Lw	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	f	2026-11-20 16:34:12.288525+03	2026-11-13 16:34:12.289505+03	2026-11-13 16:34:12.289509+03
198	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2OTI2LCJleHAiOjE3OTUxODE3MjYsImp0aSI6ImI3MzNjMGViMDA1ODQzZWI5MTdmZmM3NjI0M2M4NThkIiwidHlwZSI6InJlZnJlc2gifQ.xGP49EiJxR16Volpj3uzpKMh6dqZPJbsDcNZobdSnt8	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	f	2026-11-20 16:35:26.570813+03	2026-11-13 16:35:26.571425+03	2026-11-13 16:35:26.571427+03
199	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc2OTYzLCJleHAiOjE3OTUxODE3NjMsImp0aSI6ImE5YzcyY2YzZjM0NzRjNjY4YmIwMjg2ZGVmMGE2ZDA0IiwidHlwZSI6InJlZnJlc2gifQ.eaU1mUZrM-lwLEt_T-5zxPRnkv2MnbdSOvZcDvY38IQ	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/157.0.0.0 Safari/537.36	f	2026-11-20 16:36:03.289353+03	2026-11-13 16:36:03.289949+03	2026-11-13 16:36:03.289952+03
200	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc3MDQzLCJleHAiOjE3OTUxODE4NDMsImp0aSI6ImEyMTkyMTdjNDc2MTRhYTJiOWUzODFmOWYyYjI3MjJjIiwidHlwZSI6InJlZnJlc2gifQ.5ogScKSB-Vj_V874Zd8VLHYJJFEULX1mmn7j-aSPTi8	testclient	testclient	f	2026-11-20 16:37:23.007349+03	2026-11-13 16:37:23.00919+03	2026-11-13 16:37:23.009192+03
201	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc3MDQ0LCJleHAiOjE3OTUxODE4NDQsImp0aSI6IjljNjExN2YzOGNhOTRlZWQ4NzRlN2MwMWYwYmY3NDVjIiwidHlwZSI6InJlZnJlc2gifQ.K5f-MhCa0cO3OFp9caymdz1Z_nKQWb_mfU3xQDte_YA	testclient	testclient	f	2026-11-20 16:37:24.138533+03	2026-11-13 16:37:24.139058+03	2026-11-13 16:37:24.139061+03
202	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTc3MDQ0LCJleHAiOjE3OTUxODE4NDQsImp0aSI6IjYzZGU0NjA1YmE0YjQ5YTViZWQxNTdjMTBkZDBhMTg5IiwidHlwZSI6InJlZnJlc2gifQ.my8H6c7VLFIrkm2U8RHlsTpdL4Z1qpSNfG5f_afyVj4	testclient	testclient	f	2026-11-20 16:37:24.936825+03	2026-11-13 16:37:24.937391+03	2026-11-13 16:37:24.937393+03
203	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTgzMjI0LCJleHAiOjE3OTUxODgwMjQsImp0aSI6ImExMzIxOGI3ZGEyOTRlNjViMWY3MGRkNzhjMTFjZDgzIiwidHlwZSI6InJlZnJlc2gifQ.N1aY3FZ7Apn1JWgbQ719a4EL6NVinTUk74z7QThsFhY	127.0.0.1	python-requests/2.34.2	f	2026-11-20 18:20:24.710912+03	2026-11-13 18:20:24.714538+03	2026-11-13 18:20:24.714543+03
204	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTgzMjY4LCJleHAiOjE3OTUxODgwNjgsImp0aSI6ImJhZWUyYzZiNTc1YjRlOTE5MWZkZTFmMzQ5Y2RhOGI3IiwidHlwZSI6InJlZnJlc2gifQ.qQNAcMs1XzixZCy7w1HmWMfIJLKciVFFinRp9GI5wi0	testclient	testclient	f	2026-11-20 18:21:08.907839+03	2026-11-13 18:21:08.909649+03	2026-11-13 18:21:08.909652+03
205	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTgzMjgwLCJleHAiOjE3OTUxODgwODAsImp0aSI6IjM2ZGJmMTVhOTc3NTQ1OGRiOGU3MjllNTNjMjQzOTJmIiwidHlwZSI6InJlZnJlc2gifQ.4_frjUHPIqE7tTfDKTpt_4AynZoSAxFpOWiv4dnA4O8	testclient	testclient	f	2026-11-20 18:21:20.121598+03	2026-11-13 18:21:20.123232+03	2026-11-13 18:21:20.123234+03
206	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NTgzMjgxLCJleHAiOjE3OTUxODgwODEsImp0aSI6IjBmMGM0ZmYyNzE5YjQ3MTVhYmYzMzFhZDNmMjdkZTNkIiwidHlwZSI6InJlZnJlc2gifQ.pFc7jjOT6d4817-uHTckKlc72_SdoWW6boOdA5VncqM	testclient	testclient	f	2026-11-20 18:21:21.09766+03	2026-11-13 18:21:21.098253+03	2026-11-13 18:21:21.098255+03
207	410	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MTAiLCJpYXQiOjE3OTQ1ODQwODgsImV4cCI6MTc5NTE4ODg4OCwianRpIjoiNzA0ZmM3ZDY4ZWFlNDYzZjlmNzcxZTk3ZjhjYTc0ZmEiLCJ0eXBlIjoicmVmcmVzaCJ9.y-OHi7bMVtCVGPGMJ7HbD-IoberlSiTZiq9DYAwYzD0	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	t	2026-11-20 18:34:48.085782+03	2026-11-13 18:34:48.08843+03	2026-11-13 18:39:08.287248+03
208	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzk0NjQ1OTM3LCJleHAiOjE3OTUyNTA3MzcsImp0aSI6IjAxYWYwNzc3MzQwMTQ4MTlhMjNjOWFhOTkwNDUyOTk4IiwidHlwZSI6InJlZnJlc2gifQ.E9bLdpHw63D8bs5dvS5SphcmlrBhIB2V1BAiWsDA8lI	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36	f	2026-11-21 11:45:37.075132+03	2026-11-14 11:45:37.080117+03	2026-11-14 11:45:37.080125+03
\.


--
-- Data for Name: student_enrollments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_enrollments (id, student_id, class_id, academic_year, roll_number, start_date, end_date, status, created_at, updated_at) FROM stdin;
1	1	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.884835+03	2026-09-20 05:36:35.884837+03
2	2	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.89261+03	2026-09-20 05:36:35.892614+03
3	3	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.896526+03	2026-09-20 05:36:35.896527+03
4	4	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.898871+03	2026-09-20 05:36:35.898872+03
5	5	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.901008+03	2026-09-20 05:36:35.901009+03
6	6	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.903071+03	2026-09-20 05:36:35.903073+03
7	7	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.908722+03	2026-09-20 05:36:35.908725+03
8	8	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.912603+03	2026-09-20 05:36:35.912605+03
9	9	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.915053+03	2026-09-20 05:36:35.915054+03
10	10	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.91717+03	2026-09-20 05:36:35.917171+03
11	11	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.919205+03	2026-09-20 05:36:35.919206+03
12	12	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.925932+03	2026-09-20 05:36:35.925941+03
13	13	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.932499+03	2026-09-20 05:36:35.932501+03
14	14	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.934817+03	2026-09-20 05:36:35.934818+03
15	15	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.939301+03	2026-09-20 05:36:35.939306+03
16	16	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.944346+03	2026-09-20 05:36:35.944349+03
17	17	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.947385+03	2026-09-20 05:36:35.947387+03
18	18	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.949777+03	2026-09-20 05:36:35.949778+03
19	19	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.951799+03	2026-09-20 05:36:35.951801+03
20	20	1	2025/2026	\N	2026-09-20	\N	ACTIVE	2026-09-20 05:36:35.95583+03	2026-09-20 05:36:35.955834+03
21	21	3	2026-2027	01	\N	\N	ACTIVE	2026-09-21 01:42:58.09909+03	2026-09-21 01:42:58.099093+03
22	22	3	2026-2027	02	\N	\N	ACTIVE	2026-09-21 01:42:58.099094+03	2026-09-21 01:42:58.099095+03
23	23	5	2026-2027	01	\N	\N	ACTIVE	2026-09-21 01:42:59.339019+03	2026-09-21 01:42:59.339021+03
24	24	5	2026-2027	02	\N	\N	ACTIVE	2026-09-21 01:42:59.348223+03	2026-09-21 01:42:59.348225+03
25	25	5	2026-2027	03	\N	\N	ACTIVE	2026-09-21 01:42:59.353739+03	2026-09-21 01:42:59.353741+03
26	26	5	2026-2027	04	\N	\N	ACTIVE	2026-09-21 01:42:59.360352+03	2026-09-21 01:42:59.360357+03
27	27	5	2026-2027	05	\N	\N	ACTIVE	2026-09-21 01:42:59.366405+03	2026-09-21 01:42:59.366408+03
28	28	5	2026-2027	06	\N	\N	ACTIVE	2026-09-21 01:42:59.371607+03	2026-09-21 01:42:59.371609+03
29	29	5	2026-2027	07	\N	\N	ACTIVE	2026-09-21 01:42:59.379301+03	2026-09-21 01:42:59.379304+03
30	30	5	2026-2027	08	\N	\N	ACTIVE	2026-09-21 01:42:59.385217+03	2026-09-21 01:42:59.385219+03
31	31	5	2026-2027	09	\N	\N	ACTIVE	2026-09-21 01:42:59.3918+03	2026-09-21 01:42:59.391804+03
32	32	5	2026-2027	10	\N	\N	ACTIVE	2026-09-21 01:42:59.399085+03	2026-09-21 01:42:59.399088+03
33	33	5	2026-2027	11	\N	\N	ACTIVE	2026-09-21 01:42:59.405537+03	2026-09-21 01:42:59.40554+03
34	34	5	2026-2027	12	\N	\N	ACTIVE	2026-09-21 01:42:59.414008+03	2026-09-21 01:42:59.414012+03
35	35	5	2026-2027	13	\N	\N	ACTIVE	2026-09-21 01:42:59.42069+03	2026-09-21 01:42:59.420692+03
36	36	5	2026-2027	14	\N	\N	ACTIVE	2026-09-21 01:42:59.429245+03	2026-09-21 01:42:59.429248+03
37	37	5	2026-2027	15	\N	\N	ACTIVE	2026-09-21 01:42:59.435993+03	2026-09-21 01:42:59.435995+03
38	38	5	2026-2027	16	\N	\N	ACTIVE	2026-09-21 01:42:59.444695+03	2026-09-21 01:42:59.4447+03
39	39	5	2026-2027	17	\N	\N	ACTIVE	2026-09-21 01:42:59.452153+03	2026-09-21 01:42:59.452156+03
40	40	5	2026-2027	18	\N	\N	ACTIVE	2026-09-21 01:42:59.461828+03	2026-09-21 01:42:59.461832+03
41	41	5	2026-2027	19	\N	\N	ACTIVE	2026-09-21 01:42:59.469337+03	2026-09-21 01:42:59.469342+03
42	42	5	2026-2027	20	\N	\N	ACTIVE	2026-09-21 01:42:59.479244+03	2026-09-21 01:42:59.479249+03
43	43	5	2026-2027	21	\N	\N	ACTIVE	2026-09-21 01:42:59.487164+03	2026-09-21 01:42:59.487168+03
44	44	5	2026-2027	22	\N	\N	ACTIVE	2026-09-21 01:42:59.496954+03	2026-09-21 01:42:59.496959+03
45	45	5	2026-2027	23	\N	\N	ACTIVE	2026-09-21 01:42:59.505876+03	2026-09-21 01:42:59.505882+03
46	46	5	2026-2027	24	\N	\N	ACTIVE	2026-09-21 01:42:59.516281+03	2026-09-21 01:42:59.516285+03
47	47	5	2026-2027	25	\N	\N	ACTIVE	2026-09-21 01:42:59.525111+03	2026-09-21 01:42:59.525117+03
48	48	5	2026-2027	26	\N	\N	ACTIVE	2026-09-21 01:42:59.534361+03	2026-09-21 01:42:59.534364+03
49	49	5	2026-2027	27	\N	\N	ACTIVE	2026-09-21 01:42:59.542833+03	2026-09-21 01:42:59.54284+03
50	50	5	2026-2027	28	\N	\N	ACTIVE	2026-09-21 01:42:59.550335+03	2026-09-21 01:42:59.550338+03
51	51	5	2026-2027	29	\N	\N	ACTIVE	2026-09-21 01:42:59.558268+03	2026-09-21 01:42:59.558273+03
52	52	5	2026-2027	30	\N	\N	ACTIVE	2026-09-21 01:42:59.56687+03	2026-09-21 01:42:59.566872+03
53	53	6	2026-2027	01	\N	\N	ACTIVE	2026-09-21 01:43:04.429276+03	2026-09-21 01:43:04.429279+03
54	54	6	2026-2027	02	\N	\N	ACTIVE	2026-09-21 01:43:04.436374+03	2026-09-21 01:43:04.43638+03
55	55	6	2026-2027	03	\N	\N	ACTIVE	2026-09-21 01:43:04.444054+03	2026-09-21 01:43:04.444059+03
56	56	6	2026-2027	04	\N	\N	ACTIVE	2026-09-21 01:43:04.450624+03	2026-09-21 01:43:04.450627+03
57	57	6	2026-2027	05	\N	\N	ACTIVE	2026-09-21 01:43:04.457626+03	2026-09-21 01:43:04.457631+03
58	58	6	2026-2027	06	\N	\N	ACTIVE	2026-09-21 01:43:04.464903+03	2026-09-21 01:43:04.464906+03
59	59	6	2026-2027	07	\N	\N	ACTIVE	2026-09-21 01:43:04.470134+03	2026-09-21 01:43:04.470136+03
60	60	6	2026-2027	08	\N	\N	ACTIVE	2026-09-21 01:43:04.477016+03	2026-09-21 01:43:04.477022+03
61	61	6	2026-2027	09	\N	\N	ACTIVE	2026-09-21 01:43:04.483419+03	2026-09-21 01:43:04.483421+03
62	62	6	2026-2027	10	\N	\N	ACTIVE	2026-09-21 01:43:04.488658+03	2026-09-21 01:43:04.488661+03
63	63	6	2026-2027	11	\N	\N	ACTIVE	2026-09-21 01:43:04.496682+03	2026-09-21 01:43:04.496685+03
64	64	6	2026-2027	12	\N	\N	ACTIVE	2026-09-21 01:43:04.503129+03	2026-09-21 01:43:04.503132+03
65	65	6	2026-2027	13	\N	\N	ACTIVE	2026-09-21 01:43:04.510283+03	2026-09-21 01:43:04.510287+03
66	66	6	2026-2027	14	\N	\N	ACTIVE	2026-09-21 01:43:04.516893+03	2026-09-21 01:43:04.516895+03
67	67	6	2026-2027	15	\N	\N	ACTIVE	2026-09-21 01:43:04.522309+03	2026-09-21 01:43:04.522311+03
68	68	6	2026-2027	16	\N	\N	ACTIVE	2026-09-21 01:43:04.528636+03	2026-09-21 01:43:04.52864+03
69	69	6	2026-2027	17	\N	\N	ACTIVE	2026-09-21 01:43:04.535091+03	2026-09-21 01:43:04.535094+03
70	70	6	2026-2027	18	\N	\N	ACTIVE	2026-09-21 01:43:04.540587+03	2026-09-21 01:43:04.54059+03
71	71	6	2026-2027	19	\N	\N	ACTIVE	2026-09-21 01:43:04.547124+03	2026-09-21 01:43:04.547126+03
72	72	6	2026-2027	20	\N	\N	ACTIVE	2026-09-21 01:43:04.553359+03	2026-09-21 01:43:04.553361+03
73	73	6	2026-2027	21	\N	\N	ACTIVE	2026-09-21 01:43:04.560063+03	2026-09-21 01:43:04.560068+03
74	74	6	2026-2027	22	\N	\N	ACTIVE	2026-09-21 01:43:04.566978+03	2026-09-21 01:43:04.56698+03
75	75	6	2026-2027	23	\N	\N	ACTIVE	2026-09-21 01:43:04.572421+03	2026-09-21 01:43:04.572424+03
76	76	6	2026-2027	24	\N	\N	ACTIVE	2026-09-21 01:43:04.580091+03	2026-09-21 01:43:04.580095+03
77	77	6	2026-2027	25	\N	\N	ACTIVE	2026-09-21 01:43:04.584736+03	2026-09-21 01:43:04.584738+03
158	134	16	2026/2027	ROLL-88CE	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.335814+03	2026-10-27 08:32:22.018047+03
159	135	48	2026/2027	ROLL-6303	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.339901+03	2026-10-27 08:32:22.018047+03
160	136	48	2026/2027	ROLL-D1D4	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.343429+03	2026-10-27 08:32:22.018047+03
161	137	48	2026/2027	ROLL-1283	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.345442+03	2026-10-27 08:32:22.018047+03
270	202	50	2027/2028	\N	2026-11-11	\N	ACTIVE	2026-11-11 09:14:06.846748+03	2026-11-11 09:14:06.84675+03
152	128	36	2026/2027	ROLL-C71E	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.302106+03	2026-10-27 08:32:24.910903+03
78	78	9	2026/2027	R-1	\N	\N	ACTIVE	2026-09-21 01:43:08.502104+03	2026-09-21 01:43:09.902214+03
280	218	87	2026/2027	\N	\N	\N	ACTIVE	2026-11-13 08:48:05.380322+03	2026-11-13 08:48:05.380327+03
292	230	94	2026/2027	\N	\N	\N	ACTIVE	2026-11-13 16:03:25.655861+03	2026-11-13 16:03:25.655868+03
155	131	42	2026/2027	ROLL-BF37	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.319143+03	2026-10-27 08:32:22.018047+03
156	132	16	2026/2027	ROLL-4162	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.323016+03	2026-10-27 08:32:22.018047+03
157	133	16	2026/2027	ROLL-1328	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.326923+03	2026-10-27 08:32:22.018047+03
90	90	13	2026/2027	R-1	\N	\N	PROMOTED	2026-09-21 01:43:08.616106+03	2026-09-21 01:43:09.257923+03
96	90	14	2027/2028	\N	2026-09-20	\N	ACTIVE	2026-09-21 01:43:09.259378+03	2026-09-21 01:43:09.259384+03
94	94	14	2026/2027	R-2	\N	\N	ACTIVE	2026-09-21 01:43:08.634722+03	2026-09-21 01:43:09.902224+03
95	95	14	2026/2027	R-3	\N	\N	ACTIVE	2026-09-21 01:43:08.642912+03	2026-09-21 01:43:09.902225+03
208	121	58	2027/2028	ROLL-1218	2026-10-27	\N	ACTIVE	2026-10-27 08:32:23.061505+03	2026-10-27 08:32:23.061515+03
116	1	3	2026/2027	\N	\N	\N	ACTIVE	2026-09-21 01:43:21.030782+03	2026-09-21 01:43:21.030785+03
117	2	3	2026/2027	\N	\N	\N	ACTIVE	2026-09-21 01:43:21.030785+03	2026-09-21 01:43:21.030786+03
118	100	1	2025-2026	\N	2026-09-01	\N	ACTIVE	2026-09-21 01:43:25.544817+03	2026-09-21 01:43:25.544821+03
209	122	58	2027/2028	ROLL-0020	2026-10-27	\N	ACTIVE	2026-10-27 08:32:23.071253+03	2026-10-27 08:32:23.071259+03
210	123	58	2027/2028	ROLL-5903	2026-10-27	\N	ACTIVE	2026-10-27 08:32:23.087768+03	2026-10-27 08:32:23.087774+03
211	124	58	2027/2028	ROLL-D420	2026-10-27	\N	ACTIVE	2026-10-27 08:32:23.098592+03	2026-10-27 08:32:23.098599+03
271	213	50	2027/2028	\N	2026-11-11	\N	ACTIVE	2026-11-11 09:20:20.756523+03	2026-11-11 09:20:20.756525+03
281	219	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.588361+03	2026-11-13 12:46:28.588363+03
282	220	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.600287+03	2026-11-13 12:46:28.600289+03
283	221	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.603674+03	2026-11-13 12:46:28.603676+03
284	222	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.606213+03	2026-11-13 12:46:28.606215+03
285	223	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.608395+03	2026-11-13 12:46:28.608399+03
286	224	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.610537+03	2026-11-13 12:46:28.610538+03
287	225	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.612845+03	2026-11-13 12:46:28.612847+03
288	226	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.614843+03	2026-11-13 12:46:28.614845+03
289	227	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.618582+03	2026-11-13 12:46:28.618584+03
290	228	29	2026/2027	\N	2026-11-13	\N	ACTIVE	2026-11-13 12:46:28.631208+03	2026-11-13 12:46:28.631211+03
145	121	35	2026/2027	ROLL-1218	2026-09-01	\N	PROMOTED	2026-10-27 08:14:23.262729+03	2026-10-27 08:32:23.058164+03
146	122	35	2026/2027	ROLL-0020	2026-09-01	\N	PROMOTED	2026-10-27 08:14:23.266887+03	2026-10-27 08:32:23.070235+03
147	123	35	2026/2027	ROLL-5903	2026-09-01	\N	PROMOTED	2026-10-27 08:14:23.2719+03	2026-10-27 08:32:23.086673+03
148	124	35	2026/2027	ROLL-D420	2026-09-01	\N	PROMOTED	2026-10-27 08:14:23.280713+03	2026-10-27 08:32:23.097482+03
225	168	84	2026/2027	R-1	\N	\N	PROMOTED	2026-10-27 08:32:42.415788+03	2026-10-27 08:32:43.677205+03
246	175	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.40985+03	2026-11-11 08:58:58.409852+03
247	176	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.420954+03	2026-11-11 08:58:58.420957+03
248	177	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.423069+03	2026-11-11 08:58:58.423071+03
122	104	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.327934+03	2026-10-27 08:32:22.018047+03
123	105	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.330913+03	2026-10-27 08:32:22.018047+03
124	106	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.333073+03	2026-10-27 08:32:22.018047+03
125	107	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.335133+03	2026-10-27 08:32:22.018047+03
126	108	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.33823+03	2026-10-27 08:32:22.018047+03
127	109	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.34185+03	2026-10-27 08:32:22.018047+03
79	79	9	2026/2027	R-2	\N	\N	ACTIVE	2026-09-21 01:43:08.524243+03	2026-09-21 01:43:09.902216+03
80	80	9	2026/2027	R-3	\N	\N	ACTIVE	2026-09-21 01:43:08.535848+03	2026-09-21 01:43:09.902217+03
81	81	10	2026/2027	R-1	\N	\N	ACTIVE	2026-09-21 01:43:08.547279+03	2026-09-21 01:43:09.902217+03
82	82	10	2026/2027	R-2	\N	\N	ACTIVE	2026-09-21 01:43:08.556497+03	2026-09-21 01:43:09.902218+03
83	83	10	2026/2027	R-3	\N	\N	ACTIVE	2026-09-21 01:43:08.56535+03	2026-09-21 01:43:09.902219+03
84	84	11	2026/2027	R-1	\N	\N	ACTIVE	2026-09-21 01:43:08.572362+03	2026-09-21 01:43:09.902219+03
85	85	11	2026/2027	R-2	\N	\N	ACTIVE	2026-09-21 01:43:08.580304+03	2026-09-21 01:43:09.90222+03
86	86	11	2026/2027	R-3	\N	\N	ACTIVE	2026-09-21 01:43:08.586982+03	2026-09-21 01:43:09.90222+03
87	87	12	2026/2027	R-1	\N	\N	ACTIVE	2026-09-21 01:43:08.595621+03	2026-09-21 01:43:09.902221+03
88	88	12	2026/2027	R-2	\N	\N	ACTIVE	2026-09-21 01:43:08.601863+03	2026-09-21 01:43:09.902222+03
89	89	12	2026/2027	R-3	\N	\N	ACTIVE	2026-09-21 01:43:08.608222+03	2026-09-21 01:43:09.902222+03
91	91	13	2026/2027	R-2	\N	\N	ACTIVE	2026-09-21 01:43:08.621055+03	2026-09-21 01:43:09.902223+03
92	92	13	2026/2027	R-3	\N	\N	ACTIVE	2026-09-21 01:43:08.627018+03	2026-09-21 01:43:09.902223+03
93	93	14	2026/2027	R-1	\N	\N	ACTIVE	2026-09-21 01:43:08.631084+03	2026-09-21 01:43:09.902224+03
111	1	3	2026-2027	\N	2026-09-21	\N	ACTIVE	2026-09-21 01:43:10.263862+03	2026-09-21 01:43:10.263866+03
128	110	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.344099+03	2026-10-27 08:32:22.018047+03
129	111	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.346168+03	2026-10-27 08:32:22.018047+03
130	112	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.34888+03	2026-10-27 08:32:22.018047+03
131	113	18	2026/2027	\N	2026-10-22	\N	ACTIVE	2026-10-22 17:34:09.350517+03	2026-10-27 08:32:22.018047+03
132	114	22	2025-2026	\N	\N	\N	ACTIVE	2026-10-22 17:35:08.397727+03	2026-10-22 17:35:08.39773+03
133	3	3	2026/2027	\N	\N	\N	ACTIVE	2026-10-23 00:35:44.10323+03	2026-10-23 00:35:44.103235+03
134	4	3	2026/2027	\N	\N	\N	ACTIVE	2026-10-23 00:35:44.103236+03	2026-10-23 00:35:44.103237+03
135	5	3	2026/2027	\N	\N	\N	ACTIVE	2026-10-23 00:37:24.623002+03	2026-10-23 00:37:24.623019+03
136	6	3	2026/2027	\N	\N	\N	ACTIVE	2026-10-23 00:38:38.701681+03	2026-10-23 00:38:38.701696+03
137	115	25	2026/2027	WF-R1	\N	\N	ACTIVE	2026-10-23 00:42:41.536322+03	2026-10-23 00:42:41.53633+03
138	116	25	2026/2027	WF-R2	\N	\N	ACTIVE	2026-10-23 00:42:41.557751+03	2026-10-23 00:42:41.557762+03
139	117	25	2026/2027	WF-R3	\N	\N	ACTIVE	2026-10-23 00:42:41.579883+03	2026-10-23 00:42:41.579888+03
140	7	3	2026/2027	\N	\N	\N	ACTIVE	2026-10-23 22:36:12.710199+03	2026-10-23 22:36:12.710212+03
141	8	3	2026/2027	\N	\N	\N	ACTIVE	2026-10-23 22:36:12.710219+03	2026-10-23 22:36:12.710222+03
142	118	31	2026/2027	ROLL-61C6	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.223886+03	2026-10-27 08:32:22.018047+03
143	119	31	2026/2027	ROLL-E255	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.247706+03	2026-10-27 08:32:22.018047+03
144	120	31	2026/2027	ROLL-8A40	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.258539+03	2026-10-27 08:32:22.018047+03
174	150	78	2026/2027	R-1	\N	\N	PROMOTED	2026-10-27 08:25:59.30579+03	2026-10-27 08:26:00.717402+03
180	150	79	2027/2028	\N	2026-10-27	\N	ACTIVE	2026-10-27 08:26:00.719464+03	2026-10-27 08:26:00.71947+03
162	138	74	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:25:59.174529+03	2026-10-27 08:26:03.314478+03
163	139	74	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:25:59.186629+03	2026-10-27 08:26:03.314484+03
164	140	74	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:25:59.197747+03	2026-10-27 08:26:03.314486+03
165	141	75	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:25:59.208118+03	2026-10-27 08:26:03.314487+03
166	142	75	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:25:59.220158+03	2026-10-27 08:26:03.314489+03
167	143	75	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:25:59.231123+03	2026-10-27 08:26:03.314491+03
249	178	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.425082+03	2026-11-11 08:58:58.425083+03
250	179	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.427047+03	2026-11-11 08:58:58.427049+03
251	180	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.429097+03	2026-11-11 08:58:58.429098+03
149	125	36	2026/2027	ROLL-9011	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.284568+03	2026-10-27 08:32:22.018047+03
150	126	36	2026/2027	ROLL-8C60	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.289738+03	2026-10-27 08:32:22.018047+03
151	127	36	2026/2027	ROLL-FC13	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.29339+03	2026-10-27 08:32:22.018047+03
153	129	42	2026/2027	ROLL-11CF	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.307134+03	2026-10-27 08:32:22.018047+03
154	130	42	2026/2027	ROLL-9DCB	2026-09-01	\N	ACTIVE	2026-10-27 08:14:23.310961+03	2026-10-27 08:32:22.018047+03
252	181	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.431076+03	2026-11-11 08:58:58.431077+03
253	182	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.43502+03	2026-11-11 08:58:58.435026+03
254	183	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.437384+03	2026-11-11 08:58:58.437386+03
255	184	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.440152+03	2026-11-11 08:58:58.440154+03
256	185	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.764693+03	2026-11-11 08:58:58.764695+03
257	186	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.767335+03	2026-11-11 08:58:58.767341+03
213	156	80	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:32:42.265723+03	2026-10-27 08:32:46.65277+03
214	157	80	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:32:42.280067+03	2026-10-27 08:32:46.652776+03
215	158	80	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:32:42.292253+03	2026-10-27 08:32:46.652778+03
216	159	81	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:32:42.304103+03	2026-10-27 08:32:46.65278+03
217	160	81	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:32:42.315266+03	2026-10-27 08:32:46.652781+03
218	161	81	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:32:42.328126+03	2026-10-27 08:32:46.652783+03
219	162	82	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:32:42.340182+03	2026-10-27 08:32:46.652785+03
220	163	82	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:32:42.352436+03	2026-10-27 08:32:46.652786+03
221	164	82	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:32:42.364802+03	2026-10-27 08:32:46.652788+03
222	165	83	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:32:42.374979+03	2026-10-27 08:32:46.652789+03
223	166	83	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:32:42.38885+03	2026-10-27 08:32:46.652791+03
224	167	83	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:32:42.401194+03	2026-10-27 08:32:46.652793+03
258	187	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.772353+03	2026-11-11 08:58:58.772358+03
259	188	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.775436+03	2026-11-11 08:58:58.775439+03
260	189	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.778446+03	2026-11-11 08:58:58.778449+03
261	190	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.781125+03	2026-11-11 08:58:58.781127+03
262	191	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.783669+03	2026-11-11 08:58:58.783671+03
231	168	85	2027/2028	\N	2026-10-27	\N	ACTIVE	2026-10-27 08:32:43.679196+03	2026-10-27 08:32:43.679201+03
168	144	76	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:25:59.241671+03	2026-10-27 08:26:03.314492+03
169	145	76	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:25:59.252108+03	2026-10-27 08:26:03.314494+03
170	146	76	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:25:59.262736+03	2026-10-27 08:26:03.314495+03
171	147	77	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:25:59.272871+03	2026-10-27 08:26:03.314497+03
172	148	77	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:25:59.284463+03	2026-10-27 08:26:03.314499+03
173	149	77	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:25:59.294487+03	2026-10-27 08:26:03.3145+03
175	151	78	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:25:59.316774+03	2026-10-27 08:26:03.314502+03
176	152	78	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:25:59.32908+03	2026-10-27 08:26:03.314504+03
177	153	79	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:25:59.339428+03	2026-10-27 08:26:03.314505+03
178	154	79	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:25:59.350914+03	2026-10-27 08:26:03.314507+03
179	155	79	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:25:59.360813+03	2026-10-27 08:26:03.314508+03
226	169	84	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:32:42.428015+03	2026-10-27 08:32:46.652794+03
227	170	84	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:32:42.440969+03	2026-10-27 08:32:46.652796+03
228	171	85	2026/2027	R-1	\N	\N	ACTIVE	2026-10-27 08:32:42.453658+03	2026-10-27 08:32:46.652797+03
229	172	85	2026/2027	R-2	\N	\N	ACTIVE	2026-10-27 08:32:42.467742+03	2026-10-27 08:32:46.652799+03
230	173	85	2026/2027	R-3	\N	\N	ACTIVE	2026-10-27 08:32:42.481359+03	2026-10-27 08:32:46.6528+03
263	192	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.789206+03	2026-11-11 08:58:58.789213+03
264	193	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.793458+03	2026-11-11 08:58:58.79346+03
265	194	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:58.794678+03	2026-11-11 08:58:58.79468+03
266	195	16	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:59.057922+03	2026-11-11 08:58:59.057925+03
267	196	16	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:59.059852+03	2026-11-11 08:58:59.059859+03
268	197	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:59.237977+03	2026-11-11 08:58:59.237982+03
269	198	32	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 08:58:59.241517+03	2026-11-11 08:58:59.241524+03
278	216	37	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 10:02:08.305315+03	2026-11-11 10:02:08.305315+03
279	217	38	2026/2027	\N	2026-11-11	\N	ACTIVE	2026-11-11 10:02:08.305315+03	2026-11-11 10:02:08.305315+03
291	229	91	2026/2027	\N	\N	\N	ACTIVE	2026-11-13 13:51:15.340448+03	2026-11-13 13:51:15.340462+03
\.


--
-- Data for Name: student_fees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_fees (id, student_id, fee_structure_id, amount_due, discount_amount, due_date, status, created_at, updated_at, invoice_number, academic_year, class_id, fee_type) FROM stdin;
1	1	2	15.00	0.00	2026-10-06	PENDING	2026-09-21 01:43:15.300519+03	2026-09-21 01:43:15.300524+03	INV-2026-000001	2026/2027	3	Exam Fee Special 260210
2	1	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.382834+03	2026-09-21 01:43:15.382839+03	INV-2026-000002	2026/2027	3	Class Fee 357665
3	2	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.388455+03	2026-09-21 01:43:15.388459+03	INV-2026-000003	2026/2027	1	Class Fee 357665
4	3	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.394329+03	2026-09-21 01:43:15.394333+03	INV-2026-000004	2026/2027	1	Class Fee 357665
5	4	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.399412+03	2026-09-21 01:43:15.399415+03	INV-2026-000005	2026/2027	1	Class Fee 357665
6	5	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.404457+03	2026-09-21 01:43:15.404461+03	INV-2026-000006	2026/2027	1	Class Fee 357665
7	6	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.412096+03	2026-09-21 01:43:15.412101+03	INV-2026-000007	2026/2027	1	Class Fee 357665
8	7	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.41771+03	2026-09-21 01:43:15.417713+03	INV-2026-000008	2026/2027	1	Class Fee 357665
9	8	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.423983+03	2026-09-21 01:43:15.423986+03	INV-2026-000009	2026/2027	1	Class Fee 357665
10	9	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.429776+03	2026-09-21 01:43:15.429781+03	INV-2026-000010	2026/2027	1	Class Fee 357665
11	10	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.434751+03	2026-09-21 01:43:15.434755+03	INV-2026-000011	2026/2027	1	Class Fee 357665
12	11	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.442222+03	2026-09-21 01:43:15.442227+03	INV-2026-000012	2026/2027	1	Class Fee 357665
13	12	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.44702+03	2026-09-21 01:43:15.447023+03	INV-2026-000013	2026/2027	1	Class Fee 357665
14	13	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.452629+03	2026-09-21 01:43:15.452633+03	INV-2026-000014	2026/2027	1	Class Fee 357665
15	14	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.457883+03	2026-09-21 01:43:15.457887+03	INV-2026-000015	2026/2027	1	Class Fee 357665
16	15	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.462443+03	2026-09-21 01:43:15.462446+03	INV-2026-000016	2026/2027	1	Class Fee 357665
17	16	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.46784+03	2026-09-21 01:43:15.467844+03	INV-2026-000017	2026/2027	1	Class Fee 357665
18	17	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.472143+03	2026-09-21 01:43:15.472147+03	INV-2026-000018	2026/2027	1	Class Fee 357665
19	18	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.478894+03	2026-09-21 01:43:15.478898+03	INV-2026-000019	2026/2027	1	Class Fee 357665
20	19	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.483954+03	2026-09-21 01:43:15.483957+03	INV-2026-000020	2026/2027	1	Class Fee 357665
21	20	3	20.00	0.00	2026-10-11	PENDING	2026-09-21 01:43:15.488776+03	2026-09-21 01:43:15.488779+03	INV-2026-000021	2026/2027	1	Class Fee 357665
25	1	4	30.00	0.00	2026-10-01	PENDING	2026-09-21 01:43:15.612335+03	2026-09-21 01:43:15.61234+03	INV-2026-000022	2026/2027	3	Dup Test Fee 587445
51	18	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.207275+03	2026-10-22 17:29:52.207278+03	INV-2026-000051	2026/2027	1	Class Fee 116329
26	1	5	50.00	0.00	2026-10-01	PAID	2026-09-21 01:43:15.662302+03	2026-09-21 01:43:15.805785+03	INV-TEST-661370	2026/2027	\N	\N
27	1	6	40.00	0.00	2026-10-01	PENDING	2026-09-21 01:43:15.850119+03	2026-09-21 01:43:15.850121+03	INV-OVERPAY-849542	2026/2027	\N	\N
28	1	7	35.00	0.00	2026-09-26	PAID	2026-09-21 01:43:15.897685+03	2026-09-21 01:43:15.922406+03	INV-RCT-896808	2026/2027	\N	\N
29	1	8	45.00	0.00	2026-09-16	OVERDUE	2026-09-21 01:43:15.98811+03	2026-09-21 01:43:15.988114+03	INV-PASTDUE-987339	2026/2027	\N	\N
52	1	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.211878+03	2026-10-22 17:29:52.21188+03	INV-2026-000052	2026/2027	3	Class Fee 116329
30	1	9	60.00	0.00	2026-10-01	PENDING	2026-09-21 01:43:16.036738+03	2026-09-21 01:43:16.109171+03	INV-VOID-35833	2026/2027	\N	\N
53	100	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.21521+03	2026-10-22 17:29:52.215212+03	INV-2026-000053	2026/2027	1	Class Fee 116329
32	3	12	15.00	0.00	2026-11-06	PENDING	2026-10-22 17:29:52.042695+03	2026-10-22 17:29:52.042699+03	INV-2026-000031	2026/2027	1	Exam Fee Special 964252
33	3	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.13897+03	2026-10-22 17:29:52.138973+03	INV-2026-000033	2026/2027	1	Class Fee 116329
34	4	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.144635+03	2026-10-22 17:29:52.144638+03	INV-2026-000034	2026/2027	1	Class Fee 116329
35	5	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.148859+03	2026-10-22 17:29:52.148861+03	INV-2026-000035	2026/2027	1	Class Fee 116329
36	6	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.152094+03	2026-10-22 17:29:52.152096+03	INV-2026-000036	2026/2027	1	Class Fee 116329
37	7	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.156152+03	2026-10-22 17:29:52.156156+03	INV-2026-000037	2026/2027	1	Class Fee 116329
38	8	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.161434+03	2026-10-22 17:29:52.161437+03	INV-2026-000038	2026/2027	1	Class Fee 116329
39	9	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.164971+03	2026-10-22 17:29:52.164973+03	INV-2026-000039	2026/2027	1	Class Fee 116329
40	10	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.168236+03	2026-10-22 17:29:52.168238+03	INV-2026-000040	2026/2027	1	Class Fee 116329
41	11	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.171399+03	2026-10-22 17:29:52.171401+03	INV-2026-000041	2026/2027	1	Class Fee 116329
42	12	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.176983+03	2026-10-22 17:29:52.176986+03	INV-2026-000042	2026/2027	1	Class Fee 116329
43	13	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.180346+03	2026-10-22 17:29:52.180348+03	INV-2026-000043	2026/2027	1	Class Fee 116329
44	14	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.183433+03	2026-10-22 17:29:52.183434+03	INV-2026-000044	2026/2027	1	Class Fee 116329
45	15	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.186436+03	2026-10-22 17:29:52.186438+03	INV-2026-000045	2026/2027	1	Class Fee 116329
46	16	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.189613+03	2026-10-22 17:29:52.189616+03	INV-2026-000046	2026/2027	1	Class Fee 116329
47	17	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.19424+03	2026-10-22 17:29:52.194242+03	INV-2026-000047	2026/2027	1	Class Fee 116329
48	19	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.197505+03	2026-10-22 17:29:52.197507+03	INV-2026-000048	2026/2027	1	Class Fee 116329
49	20	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.200591+03	2026-10-22 17:29:52.200593+03	INV-2026-000049	2026/2027	1	Class Fee 116329
50	2	13	20.00	0.00	2026-11-11	PENDING	2026-10-22 17:29:52.203727+03	2026-10-22 17:29:52.203729+03	INV-2026-000050	2026/2027	3	Class Fee 116329
57	3	14	30.00	0.00	2026-11-01	PENDING	2026-10-22 17:29:52.3326+03	2026-10-22 17:29:52.332603+03	INV-2026-000054	2026/2027	1	Dup Test Fee 314520
58	3	15	50.00	0.00	2026-11-01	PAID	2026-10-22 17:29:52.369191+03	2026-10-22 17:29:52.46955+03	INV-TEST-367988	2026/2027	\N	\N
59	3	16	40.00	0.00	2026-11-01	PENDING	2026-10-22 17:29:52.503034+03	2026-10-22 17:29:52.503036+03	INV-OVERPAY-502566	2026/2027	\N	\N
60	3	17	35.00	0.00	2026-10-27	PAID	2026-10-22 17:29:52.542843+03	2026-10-22 17:29:52.563131+03	INV-RCT-542099	2026/2027	\N	\N
61	3	18	45.00	0.00	2026-10-17	OVERDUE	2026-10-22 17:29:52.621559+03	2026-10-22 17:29:52.621562+03	INV-PASTDUE-621000	2026/2027	\N	\N
63	3	21	35.00	0.00	2026-10-27	PAID	2026-10-22 17:31:11.547733+03	2026-10-22 17:31:11.843997+03	INV-RCT-546185	2026/2027	\N	\N
62	3	19	60.00	0.00	2026-11-01	PENDING	2026-10-22 17:29:52.696079+03	2026-10-22 17:29:52.786951+03	INV-VOID-695253	2026/2027	\N	\N
64	218	\N	150.00	0.00	2026-11-08	OVERDUE	2026-11-13 08:48:05.496816+03	2026-11-13 08:48:05.496819+03	INV-FM-001	2026/2027	87	\N
65	6	21	35.00	0.00	2026-10-27	OVERDUE	2026-11-14 11:46:30.917838+03	2026-11-14 11:46:30.917847+03	INV-2026-000065	2026/2027	3	Receipt Test Fee 535369
\.


--
-- Data for Name: student_import_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_import_logs (id, admin_user_id, file_name, class_id, academic_year, total_rows, imported_count, already_enrolled_count, skipped_count, failed_count, details, created_at, updated_at) FROM stdin;
1	1	Students_20.xlsx	1	2025/2026	20	20	0	0	0	{"destination_class": "Grade 1 - A", "academic_year": "2025/2026", "enroll_existing_flag": false}	2026-09-20 05:36:35.959055+03	2026-09-20 05:36:35.959064+03
2	1	students_974A8C.xlsx	18	2026/2027	10	10	0	0	0	{"destination_class": "Grade 4 - E", "academic_year": "2026/2027", "enroll_existing_flag": false}	2026-10-22 17:34:09.351641+03	2026-10-22 17:34:09.35166+03
3	1	students_import_54AB0.xlsx	32	2026/2027	10	10	0	0	0	{"destination_class": "Grade 2 - B", "academic_year": "2026/2027", "enroll_existing_flag": false}	2026-11-11 08:58:58.441067+03	2026-11-11 08:58:58.441068+03
4	1	dup_test.xlsx	32	2026/2027	10	10	0	0	0	{"destination_class": "Grade 2 - B", "academic_year": "2026/2027", "enroll_existing_flag": false}	2026-11-11 08:58:58.795107+03	2026-11-11 08:58:58.795108+03
5	1	dup_test.xlsx	32	2026/2027	10	0	10	10	0	{"destination_class": "Grade 2 - B", "academic_year": "2026/2027", "enroll_existing_flag": false}	2026-11-11 08:58:58.858785+03	2026-11-11 08:58:58.858788+03
6	1	form1_students.xlsx	16	2026/2027	2	2	0	0	0	{"destination_class": "Form 1 - B", "academic_year": "2026/2027", "enroll_existing_flag": false}	2026-11-11 08:58:59.060451+03	2026-11-11 08:58:59.060454+03
7	1	admin_route_test.xlsx	32	2026/2027	2	2	0	0	0	{"destination_class": "Grade 2 - B", "academic_year": "2026/2027", "enroll_existing_flag": false}	2026-11-11 08:58:59.242366+03	2026-11-11 08:58:59.242368+03
8	1	students.xlsx	50	2027/2028	1	1	0	0	0	{"destination_class": "Grade 1 - A", "academic_year": "2027/2028", "enroll_existing_flag": false}	2026-11-11 09:14:06.853559+03	2026-11-11 09:14:06.853562+03
9	1	students.xlsx	50	2027/2028	1	1	0	0	0	{"destination_class": "Grade 1 - A", "academic_year": "2027/2028", "enroll_existing_flag": false}	2026-11-11 09:20:20.760831+03	2026-11-11 09:20:20.760833+03
10	1	students_8DFEC2.xlsx	29	2026/2027	10	10	0	0	0	{"destination_class": "Grade 1 - A", "academic_year": "2026/2027", "enroll_existing_flag": false}	2026-11-13 12:46:28.633966+03	2026-11-13 12:46:28.63399+03
\.


--
-- Data for Name: student_result_views; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_result_views (id, student_id, exam_name, class_id, academic_year, release_batch_id, first_viewed_at, last_viewed_at, view_count, created_at, updated_at) FROM stdin;
1	2	Mid-Term Mathematics Exam	3	2025-2026	\N	2026-09-21 01:43:21.567931+03	2026-09-21 01:43:21.600254+03	2	2026-09-21 01:43:21.582996+03	2026-09-21 01:43:21.602948+03
2	3	Mid-Term Mathematics Exam	3	2025-2026	\N	2026-10-23 00:35:45.18397+03	2026-10-23 00:35:45.252404+03	2	2026-10-23 00:35:45.23153+03	2026-10-23 00:35:45.256556+03
3	4	Mid-Term Mathematics Exam	3	2025-2026	\N	2026-10-23 00:37:30.379795+03	2026-10-23 00:37:30.659842+03	2	2026-10-23 00:37:30.62198+03	2026-10-23 00:37:30.666969+03
4	6	Mid-Term Mathematics Exam	3	2025-2026	\N	2026-10-23 00:38:42.137189+03	2026-10-23 00:38:42.530559+03	2	2026-10-23 00:38:42.49601+03	2026-10-23 00:38:42.537667+03
5	8	Mid-Term Mathematics Exam	3	2025-2026	\N	2026-10-23 22:36:18.648758+03	2026-10-23 22:36:18.754236+03	2	2026-10-23 22:36:18.717183+03	2026-10-23 22:36:18.76318+03
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (id, user_id, admission_number, first_name, middle_name, last_name, gender, date_of_birth, phone, address, guardian_name, guardian_phone, guardian_email, guardian_relationship, admission_date, status, created_at, updated_at, photo_path, photo_filename, photo_mime_type, photo_size, photo_uploaded_at, photo_updated_at) FROM stdin;
156	\N	ADM-PROM-1-1-6582	Student1_1	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.231077+03	2026-10-27 08:32:42.231084+03	\N	\N	\N	\N	\N	\N
157	\N	ADM-PROM-1-2-6582	Student1_2	A.	Surname6582	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.271256+03	2026-10-27 08:32:42.271563+03	\N	\N	\N	\N	\N	\N
9	\N	9	Ibrahim	Abdi	Warsame	Male	2013-02-19	\N	\N	Guardian Abdi Warsame	+252611234509	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.911865+03	2026-09-20 05:36:35.911868+03	\N	\N	\N	\N	\N	\N
10	\N	10	Fadumo	Ahmed	Osman	Female	2012-08-11	\N	\N	Guardian Ahmed Osman	+252611234510	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.914645+03	2026-09-20 05:36:35.914647+03	\N	\N	\N	\N	\N	\N
11	\N	11	Hamza	Mohamed	Hassan	Male	2011-05-03	\N	\N	Guardian Mohamed Hassan	+252611234511	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.91679+03	2026-09-20 05:36:35.916792+03	\N	\N	\N	\N	\N	\N
12	\N	12	Nimco	Ali	Jama	Female	2013-10-16	\N	\N	Guardian Ali Jama	+252611234512	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.91881+03	2026-09-20 05:36:35.918812+03	\N	\N	\N	\N	\N	\N
13	\N	13	Mustafa	Abdullahi	Omar	Male	2012-01-25	\N	\N	Guardian Abdullahi Omar	+252611234513	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.924107+03	2026-09-20 05:36:35.924113+03	\N	\N	\N	\N	\N	\N
14	\N	14	Asma	Hassan	Mohamed	Female	2011-03-09	\N	\N	Guardian Hassan Mohamed	+252611234514	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.931705+03	2026-09-20 05:36:35.931709+03	\N	\N	\N	\N	\N	\N
15	\N	15	Abdirahman	Yusuf	Ahmed	Male	2013-07-21	\N	\N	Guardian Yusuf Ahmed	+252611234515	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.934437+03	2026-09-20 05:36:35.934438+03	\N	\N	\N	\N	\N	\N
16	\N	16	Khadra	Mohamed	Abdi	Female	2012-09-13	\N	\N	Guardian Mohamed Abdi	+252611234516	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.938084+03	2026-09-20 05:36:35.938088+03	\N	\N	\N	\N	\N	\N
17	\N	17	Ismail	Hassan	Ali	Male	2011-11-28	\N	\N	Guardian Hassan Ali	+252611234517	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.943021+03	2026-09-20 05:36:35.943026+03	\N	\N	\N	\N	\N	\N
19	\N	19	Suleiman	Ahmed	Farah	Male	2012-02-06	\N	\N	Guardian Ahmed Farah	+252611234519	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.949372+03	2026-09-20 05:36:35.949374+03	\N	\N	\N	\N	\N	\N
20	\N	20	Rahma	Yusuf	Hassan	Female	2011-10-24	\N	\N	Guardian Yusuf Hassan	+252611234520	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.951428+03	2026-09-20 05:36:35.95143+03	\N	\N	\N	\N	\N	\N
21	306	ADM-TEST-001	Mustaf	\N	Noor	Male	\N	\N	\N	Abdi Noor	+252615551111	abdi@test.so	\N	\N	ACTIVE	2026-09-21 01:42:58.056382+03	2026-09-21 01:42:58.056388+03	\N	\N	\N	\N	\N	\N
22	307	ADM-TEST-002	Amina	\N	Ibrahim	Female	\N	\N	\N	Hassan Ibrahim	+252615552222	hassan@test.so	\N	\N	ACTIVE	2026-09-21 01:42:58.065202+03	2026-09-21 01:42:58.065205+03	\N	\N	\N	\N	\N	\N
23	309	ADM-12S-001	Student01	\N	GradeSeven	Male	\N	\N	\N	Guardian 01	+252615550001	guardian1@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.330856+03	2026-09-21 01:42:59.330858+03	\N	\N	\N	\N	\N	\N
24	310	ADM-12S-002	Student02	\N	GradeSeven	Female	\N	\N	\N	Guardian 02	+252615550002	guardian2@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.344314+03	2026-09-21 01:42:59.344318+03	\N	\N	\N	\N	\N	\N
25	311	ADM-12S-003	Student03	\N	GradeSeven	Male	\N	\N	\N	Guardian 03	+252615550003	guardian3@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.350619+03	2026-09-21 01:42:59.350621+03	\N	\N	\N	\N	\N	\N
26	312	ADM-12S-004	Student04	\N	GradeSeven	Female	\N	\N	\N	Guardian 04	+252615550004	guardian4@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.355974+03	2026-09-21 01:42:59.355976+03	\N	\N	\N	\N	\N	\N
27	313	ADM-12S-005	Student05	\N	GradeSeven	Male	\N	\N	\N	Guardian 05	+252615550005	guardian5@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.363129+03	2026-09-21 01:42:59.363131+03	\N	\N	\N	\N	\N	\N
28	314	ADM-12S-006	Student06	\N	GradeSeven	Female	\N	\N	\N	Guardian 06	+252615550006	guardian6@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.368615+03	2026-09-21 01:42:59.368617+03	\N	\N	\N	\N	\N	\N
29	315	ADM-12S-007	Student07	\N	GradeSeven	Male	\N	\N	\N	Guardian 07	+252615550007	guardian7@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.374729+03	2026-09-21 01:42:59.374736+03	\N	\N	\N	\N	\N	\N
30	316	ADM-12S-008	Student08	\N	GradeSeven	Female	\N	\N	\N	Guardian 08	+252615550008	guardian8@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.381809+03	2026-09-21 01:42:59.381812+03	\N	\N	\N	\N	\N	\N
31	317	ADM-12S-009	Student09	\N	GradeSeven	Male	\N	\N	\N	Guardian 09	+252615550009	guardian9@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.387746+03	2026-09-21 01:42:59.387749+03	\N	\N	\N	\N	\N	\N
32	318	ADM-12S-010	Student10	\N	GradeSeven	Female	\N	\N	\N	Guardian 10	+252615550010	guardian10@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.39519+03	2026-09-21 01:42:59.395194+03	\N	\N	\N	\N	\N	\N
33	319	ADM-12S-011	Student11	\N	GradeSeven	Male	\N	\N	\N	Guardian 11	+252615550011	guardian11@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.40165+03	2026-09-21 01:42:59.401653+03	\N	\N	\N	\N	\N	\N
34	320	ADM-12S-012	Student12	\N	GradeSeven	Female	\N	\N	\N	Guardian 12	+252615550012	guardian12@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.409319+03	2026-09-21 01:42:59.409324+03	\N	\N	\N	\N	\N	\N
35	321	ADM-12S-013	Student13	\N	GradeSeven	Male	\N	\N	\N	Guardian 13	+252615550013	guardian13@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.416747+03	2026-09-21 01:42:59.41675+03	\N	\N	\N	\N	\N	\N
36	322	ADM-12S-014	Student14	\N	GradeSeven	Female	\N	\N	\N	Guardian 14	+252615550014	guardian14@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.423862+03	2026-09-21 01:42:59.423866+03	\N	\N	\N	\N	\N	\N
37	323	ADM-12S-015	Student15	\N	GradeSeven	Male	\N	\N	\N	Guardian 15	+252615550015	guardian15@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.432124+03	2026-09-21 01:42:59.432126+03	\N	\N	\N	\N	\N	\N
38	324	ADM-12S-016	Student16	\N	GradeSeven	Female	\N	\N	\N	Guardian 16	+252615550016	guardian16@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.43886+03	2026-09-21 01:42:59.438862+03	\N	\N	\N	\N	\N	\N
39	325	ADM-12S-017	Student17	\N	GradeSeven	Male	\N	\N	\N	Guardian 17	+252615550017	guardian17@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.447961+03	2026-09-21 01:42:59.447964+03	\N	\N	\N	\N	\N	\N
40	326	ADM-12S-018	Student18	\N	GradeSeven	Female	\N	\N	\N	Guardian 18	+252615550018	guardian18@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.455208+03	2026-09-21 01:42:59.455211+03	\N	\N	\N	\N	\N	\N
41	327	ADM-12S-019	Student19	\N	GradeSeven	Male	\N	\N	\N	Guardian 19	+252615550019	guardian19@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.465131+03	2026-09-21 01:42:59.465133+03	\N	\N	\N	\N	\N	\N
42	328	ADM-12S-020	Student20	\N	GradeSeven	Female	\N	\N	\N	Guardian 20	+252615550020	guardian20@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.473423+03	2026-09-21 01:42:59.473426+03	\N	\N	\N	\N	\N	\N
43	329	ADM-12S-021	Student21	\N	GradeSeven	Male	\N	\N	\N	Guardian 21	+252615550021	guardian21@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.48265+03	2026-09-21 01:42:59.482654+03	\N	\N	\N	\N	\N	\N
44	330	ADM-12S-022	Student22	\N	GradeSeven	Female	\N	\N	\N	Guardian 22	+252615550022	guardian22@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.49113+03	2026-09-21 01:42:59.491137+03	\N	\N	\N	\N	\N	\N
45	331	ADM-12S-023	Student23	\N	GradeSeven	Male	\N	\N	\N	Guardian 23	+252615550023	guardian23@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.500463+03	2026-09-21 01:42:59.500466+03	\N	\N	\N	\N	\N	\N
46	332	ADM-12S-024	Student24	\N	GradeSeven	Female	\N	\N	\N	Guardian 24	+252615550024	guardian24@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.510482+03	2026-09-21 01:42:59.510489+03	\N	\N	\N	\N	\N	\N
47	333	ADM-12S-025	Student25	\N	GradeSeven	Male	\N	\N	\N	Guardian 25	+252615550025	guardian25@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.519719+03	2026-09-21 01:42:59.519723+03	\N	\N	\N	\N	\N	\N
48	334	ADM-12S-026	Student26	\N	GradeSeven	Female	\N	\N	\N	Guardian 26	+252615550026	guardian26@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.529601+03	2026-09-21 01:42:59.529607+03	\N	\N	\N	\N	\N	\N
49	335	ADM-12S-027	Student27	\N	GradeSeven	Male	\N	\N	\N	Guardian 27	+252615550027	guardian27@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.537521+03	2026-09-21 01:42:59.537524+03	\N	\N	\N	\N	\N	\N
50	336	ADM-12S-028	Student28	\N	GradeSeven	Female	\N	\N	\N	Guardian 28	+252615550028	guardian28@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.546415+03	2026-09-21 01:42:59.546417+03	\N	\N	\N	\N	\N	\N
51	337	ADM-12S-029	Student29	\N	GradeSeven	Male	\N	\N	\N	Guardian 29	+252615550029	guardian29@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.553131+03	2026-09-21 01:42:59.553134+03	\N	\N	\N	\N	\N	\N
78	\N	ADM-PROM-1-1-5369	Student1_1	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.488751+03	2026-09-21 01:43:08.488755+03	\N	\N	\N	\N	\N	\N
2	375	2	Amina	Hassan	Noor	Female	2011-07-22	\N	\N	Guardian Hassan Noor	+252611234502	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.883863+03	2026-09-21 01:43:21.556935+03	\N	\N	\N	\N	\N	\N
18	379	18	Deqa	Abdi	Mohamed	Female	2013-05-17	\N	\N	Guardian Abdi Mohamed	+252611234518	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.946894+03	2026-09-21 04:02:30.90475+03	\N	\N	\N	\N	\N	\N
3	382	3	Abdiqadir	Omar	Yusuf	Male	2013-01-10	\N	\N	Guardian Omar Yusuf	+252611234503	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.891162+03	2026-10-23 00:35:45.154976+03	\N	\N	\N	\N	\N	\N
4	383	4	Hodan	Mohamed	Ibrahim	Female	2012-11-05	\N	\N	Guardian Mohamed Ibrahim	+252611234504	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.895918+03	2026-10-23 00:37:30.333441+03	\N	\N	\N	\N	\N	\N
6	385	6	Maryan	Abdi	Farah	Female	2013-04-27	\N	\N	Guardian Abdi Farah	+252611234506	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.900636+03	2026-10-23 00:38:42.090136+03	\N	\N	\N	\N	\N	\N
7	397	7	Yasin	Mohamed	Ali	Male	2012-06-14	\N	\N	Guardian Mohamed Ali	+252611234507	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.902681+03	2026-10-23 22:36:16.9637+03	\N	\N	\N	\N	\N	\N
8	398	8	Sahra	Hassan	Aden	Female	2011-12-30	\N	\N	Guardian Hassan Aden	+252611234508	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.907324+03	2026-10-23 22:36:18.615936+03	\N	\N	\N	\N	\N	\N
52	338	ADM-12S-030	Student30	\N	GradeSeven	Female	\N	\N	\N	Guardian 30	+252615550030	guardian30@hawlwadaag.edu.so	\N	\N	ACTIVE	2026-09-21 01:42:59.56231+03	2026-09-21 01:42:59.562313+03	\N	\N	\N	\N	\N	\N
53	339	ADM-G9-001	Student01	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.424792+03	2026-09-21 01:43:04.424796+03	\N	\N	\N	\N	\N	\N
54	340	ADM-G9-002	Student02	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.431774+03	2026-09-21 01:43:04.431777+03	\N	\N	\N	\N	\N	\N
55	341	ADM-G9-003	Student03	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.439249+03	2026-09-21 01:43:04.439251+03	\N	\N	\N	\N	\N	\N
56	342	ADM-G9-004	Student04	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.447061+03	2026-09-21 01:43:04.447064+03	\N	\N	\N	\N	\N	\N
57	343	ADM-G9-005	Student05	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.453903+03	2026-09-21 01:43:04.453906+03	\N	\N	\N	\N	\N	\N
58	344	ADM-G9-006	Student06	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.461286+03	2026-09-21 01:43:04.461288+03	\N	\N	\N	\N	\N	\N
59	345	ADM-G9-007	Student07	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.467391+03	2026-09-21 01:43:04.467393+03	\N	\N	\N	\N	\N	\N
60	346	ADM-G9-008	Student08	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.472746+03	2026-09-21 01:43:04.472748+03	\N	\N	\N	\N	\N	\N
61	347	ADM-G9-009	Student09	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.479519+03	2026-09-21 01:43:04.479522+03	\N	\N	\N	\N	\N	\N
62	348	ADM-G9-010	Student10	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.485858+03	2026-09-21 01:43:04.48586+03	\N	\N	\N	\N	\N	\N
63	349	ADM-G9-011	Student11	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.492012+03	2026-09-21 01:43:04.492016+03	\N	\N	\N	\N	\N	\N
64	350	ADM-G9-012	Student12	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.49943+03	2026-09-21 01:43:04.499432+03	\N	\N	\N	\N	\N	\N
65	351	ADM-G9-013	Student13	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.505335+03	2026-09-21 01:43:04.505337+03	\N	\N	\N	\N	\N	\N
66	352	ADM-G9-014	Student14	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.513264+03	2026-09-21 01:43:04.513266+03	\N	\N	\N	\N	\N	\N
67	353	ADM-G9-015	Student15	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.519166+03	2026-09-21 01:43:04.519169+03	\N	\N	\N	\N	\N	\N
68	354	ADM-G9-016	Student16	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.525176+03	2026-09-21 01:43:04.52518+03	\N	\N	\N	\N	\N	\N
69	355	ADM-G9-017	Student17	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.531396+03	2026-09-21 01:43:04.531398+03	\N	\N	\N	\N	\N	\N
70	356	ADM-G9-018	Student18	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.537413+03	2026-09-21 01:43:04.537415+03	\N	\N	\N	\N	\N	\N
71	357	ADM-G9-019	Student19	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.543941+03	2026-09-21 01:43:04.543944+03	\N	\N	\N	\N	\N	\N
72	358	ADM-G9-020	Student20	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.549795+03	2026-09-21 01:43:04.549797+03	\N	\N	\N	\N	\N	\N
73	359	ADM-G9-021	Student21	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.555483+03	2026-09-21 01:43:04.555485+03	\N	\N	\N	\N	\N	\N
74	360	ADM-G9-022	Student22	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.56316+03	2026-09-21 01:43:04.563163+03	\N	\N	\N	\N	\N	\N
75	361	ADM-G9-023	Student23	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.569117+03	2026-09-21 01:43:04.569119+03	\N	\N	\N	\N	\N	\N
76	362	ADM-G9-024	Student24	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.575825+03	2026-09-21 01:43:04.575831+03	\N	\N	\N	\N	\N	\N
77	363	ADM-G9-025	Student25	\N	GradeNine	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:04.582545+03	2026-09-21 01:43:04.582548+03	\N	\N	\N	\N	\N	\N
158	\N	ADM-PROM-1-3-6582	Student1_3	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.283853+03	2026-10-27 08:32:42.283861+03	\N	\N	\N	\N	\N	\N
159	\N	ADM-PROM-2-1-6582	Student2_1	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.29755+03	2026-10-27 08:32:42.29756+03	\N	\N	\N	\N	\N	\N
160	\N	ADM-PROM-2-2-6582	Student2_2	A.	Surname6582	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.308586+03	2026-10-27 08:32:42.308594+03	\N	\N	\N	\N	\N	\N
161	\N	ADM-PROM-2-3-6582	Student2_3	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.319296+03	2026-10-27 08:32:42.319304+03	\N	\N	\N	\N	\N	\N
162	\N	ADM-PROM-3-1-6582	Student3_1	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.332494+03	2026-10-27 08:32:42.332502+03	\N	\N	\N	\N	\N	\N
163	\N	ADM-PROM-3-2-6582	Student3_2	A.	Surname6582	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.344957+03	2026-10-27 08:32:42.344966+03	\N	\N	\N	\N	\N	\N
164	\N	ADM-PROM-3-3-6582	Student3_3	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.356764+03	2026-10-27 08:32:42.356774+03	\N	\N	\N	\N	\N	\N
165	\N	ADM-PROM-4-1-6582	Student4_1	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.368333+03	2026-10-27 08:32:42.36834+03	\N	\N	\N	\N	\N	\N
166	\N	ADM-PROM-4-2-6582	Student4_2	A.	Surname6582	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.379942+03	2026-10-27 08:32:42.379952+03	\N	\N	\N	\N	\N	\N
167	\N	ADM-PROM-4-3-6582	Student4_3	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.39318+03	2026-10-27 08:32:42.393191+03	\N	\N	\N	\N	\N	\N
168	400	ADM-PROM-5-1-6582	Mohamed	Ali	Mire	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.40592+03	2026-10-27 08:32:42.405928+03	\N	\N	\N	\N	\N	\N
169	\N	ADM-PROM-5-2-6582	Student5_2	A.	Surname6582	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.420056+03	2026-10-27 08:32:42.420064+03	\N	\N	\N	\N	\N	\N
170	\N	ADM-PROM-5-3-6582	Student5_3	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.43253+03	2026-10-27 08:32:42.432539+03	\N	\N	\N	\N	\N	\N
216	404	STD-G5A-001	Student	\N	FiveA Somali	Male	\N	\N	\N	\N	\N	\N	\N	2026-11-11	ACTIVE	2026-11-11 09:59:08.833334+03	2026-11-11 09:59:08.833334+03	\N	\N	\N	\N	\N	\N
217	405	STD-G5B-001	Student	\N	FiveB Somali	Female	\N	\N	\N	\N	\N	\N	\N	2026-11-11	ACTIVE	2026-11-11 09:59:08.833334+03	2026-11-11 09:59:08.833334+03	\N	\N	\N	\N	\N	\N
229	\N	STD-DYN-01	Ahmed	\N	DynStudent	M	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-11-13 13:51:15.287512+03	2026-11-13 13:51:15.287527+03	\N	\N	\N	\N	\N	\N
171	\N	ADM-PROM-6-1-6582	Student6_1	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.445395+03	2026-10-27 08:32:46.650325+03	\N	\N	\N	\N	\N	\N
172	\N	ADM-PROM-6-2-6582	Student6_2	A.	Surname6582	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.458373+03	2026-10-27 08:32:46.650332+03	\N	\N	\N	\N	\N	\N
173	\N	ADM-PROM-6-3-6582	Student6_3	A.	Surname6582	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:32:42.472286+03	2026-10-27 08:32:46.650336+03	\N	\N	\N	\N	\N	\N
230	\N	STD-LOCK-01	Hassan	\N	LockStudent	M	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-11-13 16:03:25.630973+03	2026-11-13 16:03:25.630979+03	\N	\N	\N	\N	\N	\N
201	\N	ADM-P2-E55629	Nasra	\N	Warsame	Female	2012-07-14	\N	\N	Warsame Ali	+252615000002	\N	\N	\N	ACTIVE	2026-11-11 09:14:06.396663+03	2026-11-11 09:14:06.396666+03	\N	\N	\N	\N	\N	\N
200	\N	ADM-P1-43EC8C	Mustafe	\N	Farah	Male	2011-03-20	\N	\N	Farah Ahmed	+252615000001	\N	\N	\N	ACTIVE	2026-11-11 09:14:06.305702+03	2026-11-11 09:14:06.999127+03	student_photos/student_200_cb84dcdc8b90.webp	mustafe_new.webp	image/webp	114	2026-11-11 09:14:06.379328+03	2026-11-11 09:14:06.998301+03
207	\N	ADM-P1-260B99	Mustafe	\N	Farah	Male	2011-03-20	\N	\N	Farah Ahmed	+252615000001	\N	\N	\N	ACTIVE	2026-11-11 09:19:18.913857+03	2026-11-11 09:19:18.951869+03	student_photos/student_207_42d94baf219f.jpg	mustafe_avatar.jpg	image/jpeg	885	2026-11-11 09:19:18.951438+03	2026-11-11 09:19:18.951438+03
208	\N	ADM-P2-03B8F2	Nasra	\N	Warsame	Female	2012-07-14	\N	\N	Warsame Ali	+252615000002	\N	\N	\N	ACTIVE	2026-11-11 09:19:18.964312+03	2026-11-11 09:19:18.964315+03	\N	\N	\N	\N	\N	\N
212	\N	ADM-P2-CA4E71	Nasra	\N	Warsame	Female	2012-07-14	\N	\N	Warsame Ali	+252615000002	\N	\N	\N	ACTIVE	2026-11-11 09:20:20.393629+03	2026-11-11 09:20:20.393632+03	\N	\N	\N	\N	\N	\N
211	\N	ADM-P1-665539	Mustafe	\N	Farah	Male	2011-03-20	\N	\N	Farah Ahmed	+252615000001	\N	\N	\N	ACTIVE	2026-11-11 09:20:20.352402+03	2026-11-11 09:20:20.880476+03	student_photos/student_211_cac7d208eb80.webp	mustafe_new.webp	image/webp	114	2026-11-11 09:20:20.383486+03	2026-11-11 09:20:20.879533+03
79	\N	ADM-PROM-1-2-5369	Student1_2	A.	Surname5369	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.504682+03	2026-09-21 01:43:08.504687+03	\N	\N	\N	\N	\N	\N
80	\N	ADM-PROM-1-3-5369	Student1_3	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.529251+03	2026-09-21 01:43:08.52926+03	\N	\N	\N	\N	\N	\N
81	\N	ADM-PROM-2-1-5369	Student2_1	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.539062+03	2026-09-21 01:43:08.539067+03	\N	\N	\N	\N	\N	\N
82	\N	ADM-PROM-2-2-5369	Student2_2	A.	Surname5369	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.550652+03	2026-09-21 01:43:08.550657+03	\N	\N	\N	\N	\N	\N
83	\N	ADM-PROM-2-3-5369	Student2_3	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.560454+03	2026-09-21 01:43:08.560462+03	\N	\N	\N	\N	\N	\N
84	\N	ADM-PROM-3-1-5369	Student3_1	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.567841+03	2026-09-21 01:43:08.567845+03	\N	\N	\N	\N	\N	\N
85	\N	ADM-PROM-3-2-5369	Student3_2	A.	Surname5369	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.57528+03	2026-09-21 01:43:08.575287+03	\N	\N	\N	\N	\N	\N
86	\N	ADM-PROM-3-3-5369	Student3_3	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.582682+03	2026-09-21 01:43:08.582687+03	\N	\N	\N	\N	\N	\N
87	\N	ADM-PROM-4-1-5369	Student4_1	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.589152+03	2026-09-21 01:43:08.589157+03	\N	\N	\N	\N	\N	\N
88	\N	ADM-PROM-4-2-5369	Student4_2	A.	Surname5369	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.597842+03	2026-09-21 01:43:08.597846+03	\N	\N	\N	\N	\N	\N
89	\N	ADM-PROM-4-3-5369	Student4_3	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.603758+03	2026-09-21 01:43:08.603762+03	\N	\N	\N	\N	\N	\N
90	365	ADM-PROM-5-1-5369	Mohamed	Ali	Mire	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.611133+03	2026-09-21 01:43:08.611139+03	\N	\N	\N	\N	\N	\N
91	\N	ADM-PROM-5-2-5369	Student5_2	A.	Surname5369	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.617971+03	2026-09-21 01:43:08.617975+03	\N	\N	\N	\N	\N	\N
92	\N	ADM-PROM-5-3-5369	Student5_3	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.622726+03	2026-09-21 01:43:08.622729+03	\N	\N	\N	\N	\N	\N
93	\N	ADM-PROM-6-1-5369	Student6_1	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.628575+03	2026-09-21 01:43:09.900494+03	\N	\N	\N	\N	\N	\N
94	\N	ADM-PROM-6-2-5369	Student6_2	A.	Surname5369	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.632394+03	2026-09-21 01:43:09.900497+03	\N	\N	\N	\N	\N	\N
174	402	ADM-TEST-PHOTO-4ED88D	Hamza	\N	Warsame	Male	2010-05-15	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-11-11 08:58:33.838251+03	2026-11-11 08:58:34.325421+03	\N	\N	\N	\N	2026-11-11 08:58:34.031383+03	2026-11-11 08:58:34.324867+03
202	\N	ADM-IMP-4BD181	Guled	Abdi	Hassan	Male	2010-09-10	+252615000003	Wadajir, Mogadishu	Abdi Hassan	+252615000004	abdi.hassan@test.so	Father	2026-11-11	ACTIVE	2026-11-11 09:14:06.844532+03	2026-11-11 09:14:06.893403+03	student_photos/student_202_bf9806c227f7.png	guled_photo.png	image/png	344	2026-11-11 09:14:06.892612+03	2026-11-11 09:14:06.892612+03
1	374	1	Mohamed	Ali	Mire	Male	2012-03-15	\N	\N	Guardian Ahmed Ali	+252611234501	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.879262+03	2026-09-21 01:43:21.431193+03	\N	\N	\N	\N	\N	\N
100	376	ADM-633578	Khadija	Ali	Warsame	Female	2010-05-15	+252617778899	Wadajir District, Mogadishu	Ali Warsame	+252615554433	\N	Father	2026-09-01	ACTIVE	2026-09-21 01:43:25.537892+03	2026-09-21 01:43:25.615053+03	\N	\N	\N	\N	\N	\N
95	378	ADM-PROM-6-3-5369	Student6_3	A.	Surname5369	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-09-21 01:43:08.639178+03	2026-09-21 04:00:10.914563+03	\N	\N	\N	\N	\N	\N
209	\N	ADM-P1-DF97D9	Mustafe	\N	Farah	Male	2011-03-20	\N	\N	Farah Ahmed	+252615000001	\N	\N	\N	ACTIVE	2026-11-11 09:19:43.344567+03	2026-11-11 09:19:43.379472+03	student_photos/student_209_ba9d943d80dc.jpg	mustafe_avatar.jpg	image/jpeg	885	2026-11-11 09:19:43.379079+03	2026-11-11 09:19:43.379079+03
210	\N	ADM-P2-6CCF03	Nasra	\N	Warsame	Female	2012-07-14	\N	\N	Warsame Ali	+252615000002	\N	\N	\N	ACTIVE	2026-11-11 09:19:43.390138+03	2026-11-11 09:19:43.39014+03	\N	\N	\N	\N	\N	\N
213	\N	ADM-IMP-15804B	Guled	Abdi	53F4	Male	2010-09-10	\N	Wadajir, Mogadishu	Abdi Hassan	+252615000004	\N	Parent	2026-11-11	ACTIVE	2026-11-11 09:20:20.754559+03	2026-11-11 09:20:20.787705+03	student_photos/student_213_ff107e4dfbd2.png	guled_photo.png	image/png	344	2026-11-11 09:20:20.787223+03	2026-11-11 09:20:20.787223+03
218	\N	ADM-FM-001	Ahmed	\N	Ali	Male	\N	\N	\N	Ali Farah	+252615000001	\N	\N	\N	ACTIVE	2026-11-13 08:48:05.357387+03	2026-11-13 08:48:05.357392+03	\N	\N	\N	\N	\N	\N
114	381	ADM-749B3D	Amina	\N	Farah	Female	\N	\N	\N	Farah Jama	+252615999999	\N	\N	\N	ACTIVE	2026-10-22 17:35:08.390929+03	2026-10-22 17:35:08.390932+03	\N	\N	\N	\N	\N	\N
5	384	5	Abdullahi	Ahmed	Ismail	Male	2011-09-18	\N	\N	Guardian Ahmed Ismail	+252611234505	\N	Parent	2026-09-20	ACTIVE	2026-09-20 05:36:35.89849+03	2026-10-23 00:38:41.1883+03	\N	\N	\N	\N	\N	\N
115	394	ADM-WF-001	Mustaf	\N	Farah	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-23 00:42:41.504319+03	2026-10-23 00:42:41.504327+03	\N	\N	\N	\N	\N	\N
116	395	ADM-WF-002	Amina	\N	Dahir	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-23 00:42:41.551338+03	2026-10-23 00:42:41.551346+03	\N	\N	\N	\N	\N	\N
117	396	ADM-WF-003	Jama	\N	Noor	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-23 00:42:41.573829+03	2026-10-23 00:42:41.573838+03	\N	\N	\N	\N	\N	\N
138	\N	ADM-PROM-1-1-3300	Student1_1	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.141591+03	2026-10-27 08:25:59.1416+03	\N	\N	\N	\N	\N	\N
139	\N	ADM-PROM-1-2-3300	Student1_2	A.	Surname3300	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.179243+03	2026-10-27 08:25:59.17925+03	\N	\N	\N	\N	\N	\N
140	\N	ADM-PROM-1-3-3300	Student1_3	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.190242+03	2026-10-27 08:25:59.190248+03	\N	\N	\N	\N	\N	\N
141	\N	ADM-PROM-2-1-3300	Student2_1	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.201936+03	2026-10-27 08:25:59.201943+03	\N	\N	\N	\N	\N	\N
142	\N	ADM-PROM-2-2-3300	Student2_2	A.	Surname3300	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.212909+03	2026-10-27 08:25:59.212916+03	\N	\N	\N	\N	\N	\N
143	\N	ADM-PROM-2-3-3300	Student2_3	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.22414+03	2026-10-27 08:25:59.224147+03	\N	\N	\N	\N	\N	\N
144	\N	ADM-PROM-3-1-3300	Student3_1	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.234939+03	2026-10-27 08:25:59.234946+03	\N	\N	\N	\N	\N	\N
145	\N	ADM-PROM-3-2-3300	Student3_2	A.	Surname3300	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.245623+03	2026-10-27 08:25:59.245631+03	\N	\N	\N	\N	\N	\N
146	\N	ADM-PROM-3-3-3300	Student3_3	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.255598+03	2026-10-27 08:25:59.255604+03	\N	\N	\N	\N	\N	\N
147	\N	ADM-PROM-4-1-3300	Student4_1	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.2662+03	2026-10-27 08:25:59.266207+03	\N	\N	\N	\N	\N	\N
148	\N	ADM-PROM-4-2-3300	Student4_2	A.	Surname3300	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.276761+03	2026-10-27 08:25:59.276769+03	\N	\N	\N	\N	\N	\N
149	\N	ADM-PROM-4-3-3300	Student4_3	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.287883+03	2026-10-27 08:25:59.287889+03	\N	\N	\N	\N	\N	\N
150	399	ADM-PROM-5-1-3300	Mohamed	Ali	Mire	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.299075+03	2026-10-27 08:25:59.299083+03	\N	\N	\N	\N	\N	\N
151	\N	ADM-PROM-5-2-3300	Student5_2	A.	Surname3300	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.309602+03	2026-10-27 08:25:59.30961+03	\N	\N	\N	\N	\N	\N
152	\N	ADM-PROM-5-3-3300	Student5_3	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.321179+03	2026-10-27 08:25:59.321189+03	\N	\N	\N	\N	\N	\N
121	\N	ADM-2026-121805	TestGrade4A	\N	Student121	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.25721+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
122	\N	ADM-2026-002041	TestGrade4A	\N	Student002	Female	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.261332+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
123	\N	ADM-2026-590336	TestGrade4A	\N	Student590	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.265548+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
153	\N	ADM-PROM-6-1-3300	Student6_1	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.332705+03	2026-10-27 08:26:03.311588+03	\N	\N	\N	\N	\N	\N
154	\N	ADM-PROM-6-2-3300	Student6_2	A.	Surname3300	Female	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.343065+03	2026-10-27 08:26:03.311595+03	\N	\N	\N	\N	\N	\N
155	\N	ADM-PROM-6-3-3300	Student6_3	A.	Surname3300	Male	\N	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:25:59.354131+03	2026-10-27 08:26:03.311599+03	\N	\N	\N	\N	\N	\N
175	\N	ADM-2026-0175	Khadar1	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190001	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.405907+03	2026-11-11 08:58:58.40591+03	\N	\N	\N	\N	\N	\N
176	\N	ADM-2026-0176	Khadar2	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190002	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.409026+03	2026-11-11 08:58:58.409029+03	\N	\N	\N	\N	\N	\N
177	\N	ADM-2026-0177	Khadar3	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190003	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.420461+03	2026-11-11 08:58:58.420463+03	\N	\N	\N	\N	\N	\N
178	\N	ADM-2026-0178	Khadar4	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190004	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.422681+03	2026-11-11 08:58:58.422683+03	\N	\N	\N	\N	\N	\N
179	\N	ADM-2026-0179	Khadar5	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190005	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.424691+03	2026-11-11 08:58:58.424692+03	\N	\N	\N	\N	\N	\N
180	\N	ADM-2026-0180	Khadar6	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190006	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.426663+03	2026-11-11 08:58:58.426665+03	\N	\N	\N	\N	\N	\N
181	\N	ADM-2026-0181	Khadar7	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190007	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.428671+03	2026-11-11 08:58:58.428672+03	\N	\N	\N	\N	\N	\N
182	\N	ADM-2026-0182	Khadar8	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190008	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.430684+03	2026-11-11 08:58:58.430685+03	\N	\N	\N	\N	\N	\N
183	\N	ADM-2026-0183	Khadar9	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190009	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.434078+03	2026-11-11 08:58:58.434084+03	\N	\N	\N	\N	\N	\N
184	\N	ADM-2026-0184	Khadar10	Ali	Warsame54AB0	Male	\N	\N	Mogadishu	Ali Warsame	+252615190010	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.437036+03	2026-11-11 08:58:58.437039+03	\N	\N	\N	\N	\N	\N
185	\N	ADM-2026-0185	Khadar1	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200001	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.761724+03	2026-11-11 08:58:58.761727+03	\N	\N	\N	\N	\N	\N
186	\N	ADM-2026-0186	Khadar2	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200002	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.764206+03	2026-11-11 08:58:58.764208+03	\N	\N	\N	\N	\N	\N
187	\N	ADM-2026-0187	Khadar3	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200003	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.766585+03	2026-11-11 08:58:58.766588+03	\N	\N	\N	\N	\N	\N
188	\N	ADM-2026-0188	Khadar4	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200004	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.771188+03	2026-11-11 08:58:58.771194+03	\N	\N	\N	\N	\N	\N
189	\N	ADM-2026-0189	Khadar5	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200005	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.774884+03	2026-11-11 08:58:58.774886+03	\N	\N	\N	\N	\N	\N
190	\N	ADM-2026-0190	Khadar6	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200006	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.777949+03	2026-11-11 08:58:58.777951+03	\N	\N	\N	\N	\N	\N
191	\N	ADM-2026-0191	Khadar7	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200007	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.780679+03	2026-11-11 08:58:58.780681+03	\N	\N	\N	\N	\N	\N
192	\N	ADM-2026-0192	Khadar8	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200008	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.783205+03	2026-11-11 08:58:58.783207+03	\N	\N	\N	\N	\N	\N
193	\N	ADM-2026-0193	Khadar9	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200009	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.78769+03	2026-11-11 08:58:58.787696+03	\N	\N	\N	\N	\N	\N
194	\N	ADM-2026-0194	Khadar10	Ali	Warsame58F99	Male	\N	\N	Mogadishu	Ali Warsame	+252615200010	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:58.792768+03	2026-11-11 08:58:58.79277+03	\N	\N	\N	\N	\N	\N
195	\N	ADM-2026-0195	DaudA1562	Omar	Kahin	Male	\N	\N	Mogadishu	Omar Kahin	+252615999001	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:59.054726+03	2026-11-11 08:58:59.054729+03	\N	\N	\N	\N	\N	\N
196	\N	ADM-2026-0196	SagalA1562	Ali	Farah	Female	\N	\N	Mogadishu	Ali Farah	+252615999002	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:59.057265+03	2026-11-11 08:58:59.057268+03	\N	\N	\N	\N	\N	\N
197	\N	ADM-2026-0197	AdminRouteStd1	A	TestC9CA5	Male	\N	\N	Mogadishu	Parent Name	+252615440001	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:59.232636+03	2026-11-11 08:58:59.232642+03	\N	\N	\N	\N	\N	\N
198	\N	ADM-2026-0198	AdminRouteStd2	A	TestC9CA5	Male	\N	\N	Mogadishu	Parent Name	+252615440002	\N	Father	2026-11-11	ACTIVE	2026-11-11 08:58:59.236742+03	2026-11-11 08:58:59.236748+03	\N	\N	\N	\N	\N	\N
203	\N	ADM-P1-3AF07B	Mustafe	\N	Farah	Male	2011-03-20	\N	\N	Farah Ahmed	+252615000001	\N	\N	\N	ACTIVE	2026-11-11 09:15:54.069319+03	2026-11-11 09:15:54.148301+03	student_photos/student_203_609287dea749.jpg	mustafe_avatar.jpg	image/jpeg	885	2026-11-11 09:15:54.147188+03	2026-11-11 09:15:54.147188+03
204	\N	ADM-P2-9CD02F	Nasra	\N	Warsame	Female	2012-07-14	\N	\N	Warsame Ali	+252615000002	\N	\N	\N	ACTIVE	2026-11-11 09:15:54.160928+03	2026-11-11 09:15:54.16093+03	\N	\N	\N	\N	\N	\N
214	\N	ADM-TEST-PHOTO-90C2DA	Hamza	\N	Warsame	Male	2010-05-15	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-11-11 09:20:46.555569+03	2026-11-11 09:20:46.555572+03	\N	\N	\N	\N	\N	\N
219	\N	ADM-2026-0219	Khadar1	Ali	Warsame8DFEC2	Male	\N	+252615880001	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990001	guardian1@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.57553+03	2026-11-13 12:46:28.575533+03	\N	\N	\N	\N	\N	\N
124	\N	ADM-2026-D42010	TestGrade4A	\N	StudentD42	Female	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.270198+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
125	\N	ADM-2026-9011D2	TestGrade4B	\N	Student901	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.279457+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
104	\N	ADM-2026-0101	Khadar1	Ali	Warsame974A8C	Male	\N	+252615880001	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990001	guardian1@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.324374+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
105	\N	ADM-2026-0102	Khadar2	Ali	Warsame974A8C	Female	\N	+252615880002	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990002	guardian2@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.327094+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
106	\N	ADM-2026-0103	Khadar3	Ali	Warsame974A8C	Male	\N	+252615880003	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990003	guardian3@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.330419+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
107	\N	ADM-2026-0104	Khadar4	Ali	Warsame974A8C	Female	\N	+252615880004	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990004	guardian4@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.332681+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
118	\N	ADM-2026-61C651	TestGrade2A	\N	Student61C	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.194073+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
220	\N	ADM-2026-0220	Khadar2	Ali	Warsame8DFEC2	Female	\N	+252615880002	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990002	guardian2@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.587391+03	2026-11-13 12:46:28.587394+03	\N	\N	\N	\N	\N	\N
221	\N	ADM-2026-0221	Khadar3	Ali	Warsame8DFEC2	Male	\N	+252615880003	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990003	guardian3@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.599588+03	2026-11-13 12:46:28.599592+03	\N	\N	\N	\N	\N	\N
222	\N	ADM-2026-0222	Khadar4	Ali	Warsame8DFEC2	Female	\N	+252615880004	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990004	guardian4@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.60311+03	2026-11-13 12:46:28.603113+03	\N	\N	\N	\N	\N	\N
108	\N	ADM-2026-0105	Khadar5	Ali	Warsame974A8C	Male	\N	+252615880005	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990005	guardian5@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.33475+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
109	\N	ADM-2026-0106	Khadar6	Ali	Warsame974A8C	Female	\N	+252615880006	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990006	guardian6@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.33735+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
110	\N	ADM-2026-0107	Khadar7	Ali	Warsame974A8C	Male	\N	+252615880007	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990007	guardian7@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.341389+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
111	\N	ADM-2026-0108	Khadar8	Ali	Warsame974A8C	Female	\N	+252615880008	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990008	guardian8@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.343713+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
112	\N	ADM-2026-0109	Khadar9	Ali	Warsame974A8C	Male	\N	+252615880009	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990009	guardian9@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.345779+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
113	\N	ADM-2026-0110	Khadar10	Ali	Warsame974A8C	Female	\N	+252615880010	Hawlwadaag, Mogadishu	Ali Warsame 974A8C	+252615990010	guardian10@974a8c.so	Father	2026-10-22	ACTIVE	2026-10-22 17:34:09.34841+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
119	\N	ADM-2026-E25534	TestGrade2A	\N	StudentE25	Female	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.220022+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
120	\N	ADM-2026-8A406B	TestGrade2A	\N	Student8A4	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.246122+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
126	\N	ADM-2026-8C6029	TestGrade4B	\N	Student8C6	Female	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.283237+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
127	\N	ADM-2026-FC13FA	TestGrade4B	\N	StudentFC1	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.288033+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
128	\N	ADM-2026-C71E94	TestGrade4B	\N	StudentC71	Female	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.292186+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
129	\N	ADM-2026-11CF7F	TestGrade8A	\N	Student11C	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.300891+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
130	\N	ADM-2026-9DCB3C	TestGrade8A	\N	Student9DC	Female	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.305447+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
131	\N	ADM-2026-BF37D3	TestGrade8A	\N	StudentBF3	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.309695+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
132	\N	ADM-2026-41627E	TestForm1B	\N	Student416	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.317608+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
133	\N	ADM-2026-132815	TestForm1B	\N	Student132	Female	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.321739+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
134	\N	ADM-2026-88CE83	TestForm1B	\N	Student88C	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.32559+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
135	\N	ADM-2026-630314	TestForm4A	\N	Student630	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.334086+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
136	\N	ADM-2026-D1D481	TestForm4A	\N	StudentD1D	Female	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.338492+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
137	\N	ADM-2026-12831C	TestForm4A	\N	Student128	Male	2012-01-01	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-10-27 08:14:23.342228+03	2026-10-27 08:32:22.023321+03	\N	\N	\N	\N	\N	\N
199	\N	ADM-P1-87945F	Mustafe	\N	Farah	Male	2011-03-20	\N	\N	Farah Ahmed	+252615000001	\N	\N	\N	ACTIVE	2026-11-11 09:13:21.89977+03	2026-11-11 09:13:21.899775+03	\N	\N	\N	\N	\N	\N
205	\N	ADM-P1-3DE770	Mustafe	\N	Farah	Male	2011-03-20	\N	\N	Farah Ahmed	+252615000001	\N	\N	\N	ACTIVE	2026-11-11 09:18:40.398047+03	2026-11-11 09:18:40.467644+03	student_photos/student_205_302beee45b91.jpg	mustafe_avatar.jpg	image/jpeg	885	2026-11-11 09:18:40.466667+03	2026-11-11 09:18:40.466667+03
206	\N	ADM-P2-60E577	Nasra	\N	Warsame	Female	2012-07-14	\N	\N	Warsame Ali	+252615000002	\N	\N	\N	ACTIVE	2026-11-11 09:18:40.479196+03	2026-11-11 09:18:40.479198+03	\N	\N	\N	\N	\N	\N
215	403	ADM-TEST-PHOTO-EAA099	Hamza	\N	Warsame	Male	2010-05-15	\N	\N	\N	\N	\N	\N	\N	ACTIVE	2026-11-11 09:21:12.70431+03	2026-11-11 09:21:12.989932+03	\N	\N	\N	\N	2026-11-11 09:21:12.802376+03	2026-11-11 09:21:12.988724+03
223	\N	ADM-2026-0223	Khadar5	Ali	Warsame8DFEC2	Male	\N	+252615880005	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990005	guardian5@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.605759+03	2026-11-13 12:46:28.605761+03	\N	\N	\N	\N	\N	\N
224	\N	ADM-2026-0224	Khadar6	Ali	Warsame8DFEC2	Female	\N	+252615880006	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990006	guardian6@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.608008+03	2026-11-13 12:46:28.60801+03	\N	\N	\N	\N	\N	\N
225	\N	ADM-2026-0225	Khadar7	Ali	Warsame8DFEC2	Male	\N	+252615880007	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990007	guardian7@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.610132+03	2026-11-13 12:46:28.610134+03	\N	\N	\N	\N	\N	\N
226	\N	ADM-2026-0226	Khadar8	Ali	Warsame8DFEC2	Female	\N	+252615880008	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990008	guardian8@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.612424+03	2026-11-13 12:46:28.612426+03	\N	\N	\N	\N	\N	\N
227	\N	ADM-2026-0227	Khadar9	Ali	Warsame8DFEC2	Male	\N	+252615880009	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990009	guardian9@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.614461+03	2026-11-13 12:46:28.614462+03	\N	\N	\N	\N	\N	\N
228	\N	ADM-2026-0228	Khadar10	Ali	Warsame8DFEC2	Female	\N	+252615880010	Hawlwadaag, Mogadishu	Ali Warsame 8DFEC2	+252615990010	guardian10@8dfec2.so	Father	2026-11-13	ACTIVE	2026-11-13 12:46:28.618032+03	2026-11-13 12:46:28.618035+03	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: subjects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subjects (id, name, code, department, description, status, created_at, updated_at, division, applicable_levels) FROM stdin;
1	math	MAT-101	\N	\N	ACTIVE	2026-09-20 05:38:39.739979+03	2026-09-20 05:38:39.739991+03	ALL	\N
2	Mathematics-Test	MATH-TST	\N	\N	ACTIVE	2026-09-21 01:42:58.008059+03	2026-09-21 01:42:58.008093+03	ALL	\N
3	Physics-Test	PHYS-TST	\N	\N	ACTIVE	2026-09-21 01:42:58.012983+03	2026-09-21 01:42:58.012987+03	ALL	\N
4	Mathematics	MATH-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.302138+03	2026-09-21 01:42:59.302141+03	ALL	\N
5	English	ENG-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.303777+03	2026-09-21 01:42:59.303779+03	ALL	\N
6	Somali	SOM-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.304868+03	2026-09-21 01:42:59.304869+03	ALL	\N
7	Physics	PHYS-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.306139+03	2026-09-21 01:42:59.306143+03	ALL	\N
8	Chemistry	CHEM-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.308986+03	2026-09-21 01:42:59.308991+03	ALL	\N
9	Biology	BIO-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.310706+03	2026-09-21 01:42:59.31071+03	ALL	\N
10	Geography	GEO-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.312344+03	2026-09-21 01:42:59.312348+03	ALL	\N
11	History	HIST-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.31394+03	2026-09-21 01:42:59.313944+03	ALL	\N
12	Islamic Studies	ISL-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.31575+03	2026-09-21 01:42:59.315753+03	ALL	\N
13	Arabic	ARB-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.31745+03	2026-09-21 01:42:59.317454+03	ALL	\N
14	Computer	CMP-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.319238+03	2026-09-21 01:42:59.319242+03	ALL	\N
15	Physical Education	PE-12S	\N	\N	ACTIVE	2026-09-21 01:42:59.320525+03	2026-09-21 01:42:59.320527+03	ALL	\N
16	Math G9	G9-S1	\N	\N	ACTIVE	2026-09-21 01:43:04.367863+03	2026-09-21 01:43:04.367869+03	ALL	\N
17	English G9	G9-S2	\N	\N	ACTIVE	2026-09-21 01:43:04.373723+03	2026-09-21 01:43:04.37373+03	ALL	\N
18	Somali G9	G9-S3	\N	\N	ACTIVE	2026-09-21 01:43:04.380913+03	2026-09-21 01:43:04.380919+03	ALL	\N
19	Physics G9	G9-S4	\N	\N	ACTIVE	2026-09-21 01:43:04.385908+03	2026-09-21 01:43:04.385911+03	ALL	\N
20	Chemistry G9	G9-S5	\N	\N	ACTIVE	2026-09-21 01:43:04.389678+03	2026-09-21 01:43:04.38968+03	ALL	\N
21	Biology G9	G9-S6	\N	\N	ACTIVE	2026-09-21 01:43:04.395097+03	2026-09-21 01:43:04.395101+03	ALL	\N
22	Geography G9	G9-S7	\N	\N	ACTIVE	2026-09-21 01:43:04.398593+03	2026-09-21 01:43:04.398596+03	ALL	\N
23	History G9	G9-S8	\N	\N	ACTIVE	2026-09-21 01:43:04.402479+03	2026-09-21 01:43:04.402481+03	ALL	\N
24	Arabic G9	G9-S9	\N	\N	ACTIVE	2026-09-21 01:43:04.406257+03	2026-09-21 01:43:04.406259+03	ALL	\N
25	Islamic G9	G9-S10	\N	\N	ACTIVE	2026-09-21 01:43:04.411039+03	2026-09-21 01:43:04.411043+03	ALL	\N
26	Computer G9	G9-S11	\N	\N	ACTIVE	2026-09-21 01:43:04.414724+03	2026-09-21 01:43:04.414726+03	ALL	\N
27	Physical Education G9	G9-S12	\N	\N	ACTIVE	2026-09-21 01:43:04.418035+03	2026-09-21 01:43:04.418037+03	ALL	\N
28	General Science SCI-1CECA6	SCI-1CECA6	Sciences	Basic experimental science	ACTIVE	2026-09-21 01:43:22.354468+03	2026-09-21 01:43:22.354489+03	ALL	\N
29	Somali Literature 749B3D	SOM-749B3D	Languages	\N	ACTIVE	2026-10-22 17:35:07.723094+03	2026-10-22 17:35:07.723099+03	ALL	\N
34	Workflow Mathematics	WF-MATH-101	\N	\N	ACTIVE	2026-10-23 00:42:41.400112+03	2026-10-23 00:42:41.40012+03	ALL	\N
35	Workflow Biology	WF-BIO-101	\N	\N	ACTIVE	2026-10-23 00:42:41.404618+03	2026-10-23 00:42:41.404625+03	ALL	\N
36	General Science SCI-B0E14A	SCI-B0E14A	Sciences	Basic experimental science	ACTIVE	2026-10-23 23:31:17.859417+03	2026-10-23 23:31:17.85942+03	ALL	\N
37	Science 5	SCI-501	Natural Sciences	\N	ACTIVE	2026-11-11 09:59:08.833334+03	2026-11-11 09:59:08.833334+03	ALL	\N
38	FM Mathematics	FM-MATH	Science	\N	ACTIVE	2026-11-13 08:48:05.336059+03	2026-11-13 08:48:05.336063+03	ALL	\N
39	FM English	FM-ENG	Languages	\N	ACTIVE	2026-11-13 08:48:05.336065+03	2026-11-13 08:48:05.336065+03	ALL	\N
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscriptions (id, institution_id, plan_name, billing_cycle, price, setup_fee, status, start_date, end_date, auto_renew, notes, created_at, updated_at) FROM stdin;
8	8	Professional School	Annual	350.00	70.00	Active	2026-10-22 00:00:00	2027-10-22 00:00:00	t	Initial subscription created upon registration on 2026-10-22.	2026-10-22 09:18:11	2026-10-22 09:18:11
9	9	Professional School	Annual	350.00	70.00	Active	2026-11-12 00:00:00	2027-11-12 00:00:00	t	Initial subscription created upon registration on 2026-11-12.	2026-11-12 11:33:25.17901	2026-11-12 11:33:25.17901
10	16	Professional School	Annual	350.00	70.00	Active	2026-11-12 00:00:00	2027-11-12 00:00:00	t	Initial subscription created upon registration on 2026-11-12.	2026-11-12 12:47:15.627021	2026-11-12 12:47:15.627021
11	17	Starter Academy	Annual	250.00	70.00	Active	2026-11-13 00:00:00	2027-11-13 00:00:00	t	Initial subscription created upon registration on 2026-11-13.	2026-11-13 10:56:46.451992	2026-11-13 10:56:46.451992
12	18	Professional School	Annual	350.00	70.00	Active	2026-11-13 00:00:00	2027-11-13 00:00:00	t	Initial subscription created upon registration on 2026-11-13.	2026-11-13 18:38:19.490147	2026-11-13 18:38:19.490147
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_settings (id, key, value, description, is_public, created_at, updated_at) FROM stdin;
3	school_motto	Excellence in Education and Character	Official school motto	t	2026-09-16 09:03:26.832201+03	2026-09-16 09:03:26.832212+03
5	school_phone	+252 61 0000000	Official contact phone number	t	2026-09-16 09:03:26.842957+03	2026-09-16 09:03:26.842964+03
6	school_address	Hawlwadaag District, Mogadishu, Somalia	Physical campus location	t	2026-09-16 09:03:26.848889+03	2026-09-16 09:03:26.848897+03
7	primary_color	#1e3a8a	Primary school theme branding color	t	2026-09-16 09:03:26.855183+03	2026-09-16 09:03:26.855192+03
8	secondary_color	#0284c7	Secondary theme branding color	t	2026-09-16 09:03:26.860488+03	2026-09-16 09:03:26.860494+03
10	notify_attendance_absent_enabled	true	Automatic attendance absence SMS alerts	f	2026-09-17 11:47:03.941817+03	2026-09-17 11:47:03.94182+03
11	notify_result_release_enabled	true	Automatic result release SMS alerts	f	2026-09-17 11:47:03.945921+03	2026-09-17 11:47:03.945923+03
12	notification_default_channel	SMS	Default notification channel	f	2026-09-17 11:47:03.947506+03	2026-09-17 11:47:03.947508+03
9	academic_year_current	2026/2027	Current active academic year	t	2026-09-16 09:32:25.835139+03	2026-09-18 22:56:28.202836+03
4	school_email	info@ems.edu.so	Official contact email	t	2026-09-16 09:03:26.837814+03	2026-09-16 09:03:26.837821+03
1	school_name	Hawlwadaag Primary and Secondary School	Official school institution name	t	2026-09-16 09:03:26.816042+03	2026-09-16 09:03:26.816049+03
2	school_short_name	Hawlwadaag School	Abbreviated school name	t	2026-09-16 09:03:26.825909+03	2026-09-16 09:03:26.825916+03
\.


--
-- Data for Name: teacher_assignments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teacher_assignments (id, teacher_id, class_id, subject_id, academic_year, status, created_at, updated_at) FROM stdin;
1	1	1	1	2025-2026	ACTIVE	2026-09-20 05:39:17.640288+03	2026-09-20 05:39:17.640301+03
2	2	3	2	2026-2027	ACTIVE	2026-09-21 01:42:58.029451+03	2026-09-21 01:42:58.029456+03
3	3	5	4	2026-2027	ACTIVE	2026-09-21 01:42:59.58767+03	2026-09-21 01:42:59.587673+03
4	3	5	5	2026-2027	ACTIVE	2026-09-21 01:42:59.594615+03	2026-09-21 01:42:59.594618+03
5	3	5	6	2026-2027	ACTIVE	2026-09-21 01:42:59.600089+03	2026-09-21 01:42:59.600092+03
6	3	5	7	2026-2027	ACTIVE	2026-09-21 01:42:59.605509+03	2026-09-21 01:42:59.605513+03
7	3	5	8	2026-2027	ACTIVE	2026-09-21 01:42:59.613968+03	2026-09-21 01:42:59.613972+03
8	3	5	9	2026-2027	ACTIVE	2026-09-21 01:42:59.619856+03	2026-09-21 01:42:59.619859+03
9	3	5	10	2026-2027	ACTIVE	2026-09-21 01:42:59.626342+03	2026-09-21 01:42:59.626347+03
10	3	5	11	2026-2027	ACTIVE	2026-09-21 01:42:59.632367+03	2026-09-21 01:42:59.632371+03
11	3	5	12	2026-2027	ACTIVE	2026-09-21 01:42:59.637876+03	2026-09-21 01:42:59.637879+03
12	3	5	13	2026-2027	ACTIVE	2026-09-21 01:42:59.645065+03	2026-09-21 01:42:59.645069+03
13	3	5	14	2026-2027	ACTIVE	2026-09-21 01:42:59.6506+03	2026-09-21 01:42:59.650603+03
14	3	5	15	2026-2027	ACTIVE	2026-09-21 01:42:59.657692+03	2026-09-21 01:42:59.657698+03
15	2	6	16	2026-2027	ACTIVE	2026-09-21 01:43:04.374809+03	2026-09-21 01:43:04.374813+03
16	2	6	17	2026-2027	ACTIVE	2026-09-21 01:43:04.381699+03	2026-09-21 01:43:04.381702+03
17	2	6	18	2026-2027	ACTIVE	2026-09-21 01:43:04.386424+03	2026-09-21 01:43:04.386426+03
18	2	6	19	2026-2027	ACTIVE	2026-09-21 01:43:04.390428+03	2026-09-21 01:43:04.390432+03
19	2	6	20	2026-2027	ACTIVE	2026-09-21 01:43:04.395657+03	2026-09-21 01:43:04.39566+03
20	2	6	21	2026-2027	ACTIVE	2026-09-21 01:43:04.399039+03	2026-09-21 01:43:04.399041+03
21	2	6	22	2026-2027	ACTIVE	2026-09-21 01:43:04.402898+03	2026-09-21 01:43:04.4029+03
22	2	6	23	2026-2027	ACTIVE	2026-09-21 01:43:04.406784+03	2026-09-21 01:43:04.406786+03
23	2	6	24	2026-2027	ACTIVE	2026-09-21 01:43:04.411573+03	2026-09-21 01:43:04.411575+03
24	2	6	25	2026-2027	ACTIVE	2026-09-21 01:43:04.415172+03	2026-09-21 01:43:04.415174+03
25	2	6	26	2026-2027	ACTIVE	2026-09-21 01:43:04.418465+03	2026-09-21 01:43:04.418467+03
26	2	6	27	2026-2027	ACTIVE	2026-09-21 01:43:04.421197+03	2026-09-21 01:43:04.421199+03
27	5	3	4	2026/2027	ACTIVE	2026-09-21 01:43:21.025814+03	2026-09-21 01:43:21.025819+03
28	6	1	26	2026-2027	ACTIVE	2026-09-21 03:43:44.56549+03	2026-09-21 03:43:44.565498+03
29	7	22	29	2025-2026	ACTIVE	2026-10-22 17:35:08.120415+03	2026-10-22 17:35:08.120421+03
34	12	25	34	2026/2027	ACTIVE	2026-10-23 00:42:41.441057+03	2026-10-23 00:42:41.441065+03
35	13	25	35	2026/2027	ACTIVE	2026-10-23 00:42:41.441068+03	2026-10-23 00:42:41.44107+03
36	2	1	2	2025-2026	ACTIVE	2026-10-25 00:40:56.413628+03	2026-10-25 00:40:56.413641+03
37	1	31	7	2026/2027	ACTIVE	2026-11-13 08:46:45.13045+03	2026-11-13 08:46:45.130454+03
46	17	29	13	2025-2026	ACTIVE	2026-11-13 12:15:20.891947+03	2026-11-13 12:15:20.89195+03
51	19	29	13	2028-2029	ACTIVE	2026-11-13 12:16:00.745405+03	2026-11-13 12:16:00.745409+03
56	21	29	13	2054-2055	ACTIVE	2026-11-13 12:16:55.377443+03	2026-11-13 12:16:55.377447+03
61	23	1	13	2025/2026	ACTIVE	2026-11-13 13:02:11.398893+03	2026-11-13 13:02:11.398904+03
62	24	1	4	2025/2026	ACTIVE	2026-11-13 13:02:11.398907+03	2026-11-13 13:02:11.398909+03
63	25	91	13	2026/2027	ACTIVE	2026-11-13 13:51:19.630778+03	2026-11-13 13:51:19.630788+03
64	26	91	4	2026/2027	ACTIVE	2026-11-13 13:51:19.630792+03	2026-11-13 13:51:19.630794+03
65	27	92	7	2026/2027	ACTIVE	2026-11-13 13:51:19.630796+03	2026-11-13 13:51:19.630798+03
66	28	93	8	2025/2026	ACTIVE	2026-11-13 13:51:19.6308+03	2026-11-13 13:51:19.630802+03
72	30	94	13	2026/2027	ACTIVE	2026-11-13 16:03:26.195967+03	2026-11-13 16:03:26.195973+03
73	30	94	5	2026/2027	ACTIVE	2026-11-13 16:03:26.195975+03	2026-11-13 16:03:26.195977+03
\.


--
-- Data for Name: teacher_attendances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teacher_attendances (id, teacher_id, date, academic_year, status, reason, recorded_by_id, created_at, updated_at) FROM stdin;
3	13	2026-11-13	2026/2027	LATE	Automated test note LATE	1	2026-11-13 10:17:15.348231+03	2026-11-13 10:17:15.348232+03
5	16	2026-11-13	2026/2027	PRESENT	\N	1	2026-11-13 10:17:15.348234+03	2026-11-13 10:17:15.348234+03
6	12	2026-11-13	2026/2027	ABSENT	Automated test note ABSENT	1	2026-11-13 10:17:15.348234+03	2026-11-13 10:17:15.348235+03
7	7	2026-11-13	2026/2027	LATE	Automated test note LATE	1	2026-11-13 10:17:15.348235+03	2026-11-13 10:17:15.348236+03
8	6	2026-11-13	2026/2027	ON_LEAVE	Automated test note ON_LEAVE	1	2026-11-13 10:17:15.348236+03	2026-11-13 10:17:15.348237+03
9	1	2026-11-13	2026/2027	PRESENT	\N	1	2026-11-13 10:17:15.348237+03	2026-11-13 10:17:15.348238+03
1	3	2026-11-13	2026/2027	PRESENT	\N	1	2026-11-13 10:17:15.348224+03	2026-11-13 12:47:37.434445+03
2	5	2026-11-13	2026/2027	ABSENT	Automated test note ABSENT	1	2026-11-13 10:17:15.34823+03	2026-11-13 12:47:37.435259+03
4	2	2026-11-13	2026/2027	ON_LEAVE	Automated test note ON_LEAVE	1	2026-11-13 10:17:15.348233+03	2026-11-13 12:47:37.435821+03
10	14	2026-11-13	2026/2027	LATE	Automated test note LATE	1	2026-11-13 10:17:15.348238+03	2026-11-13 12:47:37.435823+03
11	15	2026-11-13	2026/2027	ON_LEAVE	Automated test note ON_LEAVE	1	2026-11-13 10:17:15.348239+03	2026-11-13 12:47:37.435823+03
17	23	2026-11-13	2026/2027	PRESENT	\N	1	2026-11-13 13:02:44.503243+03	2026-11-13 13:02:44.503253+03
12	21	2026-11-13	2026/2027	ABSENT	Automated test note ABSENT	1	2026-11-13 12:47:37.437318+03	2026-11-13 13:54:35.43622+03
13	19	2026-11-13	2026/2027	ON_LEAVE	Automated test note ON_LEAVE	1	2026-11-13 12:47:37.437321+03	2026-11-13 13:54:35.436236+03
14	20	2026-11-13	2026/2027	PRESENT	\N	1	2026-11-13 12:47:37.437322+03	2026-11-13 13:54:35.43624+03
15	17	2026-11-13	2026/2027	ABSENT	Automated test note ABSENT	1	2026-11-13 12:47:37.437323+03	2026-11-13 13:54:35.436247+03
16	18	2026-11-13	2026/2027	LATE	Automated test note LATE	1	2026-11-13 12:47:37.437324+03	2026-11-13 13:54:35.43625+03
18	24	2026-11-13	2026/2027	LATE	Automated test note LATE	1	2026-11-13 13:02:44.503257+03	2026-11-13 13:54:35.436257+03
19	25	2026-11-13	2026/2027	ABSENT	Automated test note ABSENT	1	2026-11-13 13:54:35.445813+03	2026-11-13 13:54:35.445826+03
20	28	2026-11-13	2026/2027	ON_LEAVE	Automated test note ON_LEAVE	1	2026-11-13 13:54:35.445834+03	2026-11-13 13:54:35.445839+03
21	26	2026-11-13	2026/2027	PRESENT	\N	1	2026-11-13 13:54:35.445843+03	2026-11-13 13:54:35.445847+03
22	27	2026-11-13	2026/2027	ABSENT	Automated test note ABSENT	1	2026-11-13 13:54:35.445851+03	2026-11-13 13:54:35.445854+03
\.


--
-- Data for Name: teacher_availabilities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teacher_availabilities (id, teacher_id, academic_year, day_of_week, start_time, end_time, is_available, max_periods_per_day, max_periods_per_week, notes, created_at, updated_at) FROM stdin;
1	1	2025-2026	Saturday	07:30:00	13:30:00	t	5	25	Full day availability	2026-10-24 00:05:24.662012+03	2026-10-24 00:05:24.662015+03
2	1	2025-2026	Sunday	07:30:00	13:30:00	t	5	25	\N	2026-10-24 00:05:24.662016+03	2026-10-24 00:05:24.662016+03
3	1	2025-2026	Friday	\N	\N	f	5	25	Weekend	2026-10-24 00:05:24.662017+03	2026-10-24 00:05:24.662017+03
\.


--
-- Data for Name: teachers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teachers (id, user_id, teacher_number, first_name, middle_name, last_name, gender, date_of_birth, phone, email, address, qualification, hire_date, status, created_at, updated_at) FROM stdin;
1	304	TCH-4305	Mohammed	xuseen	Mukhtar	Male	\N	7878787877	skycast45@gmail.com	\N	B.Sc. Education	2026-09-20	ACTIVE	2026-09-20 05:38:12.600513+03	2026-09-20 05:38:12.600516+03
2	305	TCH-ALI-01	Ali	\N	Warsame	Male	\N	\N	ali.teacher@hawlwadaag.edu.so	\N	\N	\N	ACTIVE	2026-09-21 01:42:57.975702+03	2026-09-21 01:42:57.975707+03
3	308	TCH-AHMED-12S	Ahmed	\N	Ali	Male	\N	\N	ahmed.12s@hawlwadaag.edu.so	\N	\N	\N	ACTIVE	2026-09-21 01:42:59.324834+03	2026-09-21 01:42:59.324838+03
5	373	TCH-TEST-001	Ahmed	\N	Warsame	Male	\N	\N	ahmed.test@hawlwadaag.edu.so	\N	\N	\N	ACTIVE	2026-09-21 01:43:21.019861+03	2026-09-21 01:43:21.019865+03
6	377	TCH-5022	MOHAMED	nuur	sulayma	Male	\N	+447538511769	alimire8x14@gmail.com	2020 Bentworth Dr	B.Sc. Education	2026-09-21	ACTIVE	2026-09-21 03:35:43.662572+03	2026-09-21 03:35:43.662579+03
7	380	TCH-749B3D	Khadar	\N	Warsame	Male	\N	\N	khadar.749b3d@hawlwadaagschool.edu.so	\N	B.Ed Somali Language	\N	ACTIVE	2026-10-22 17:35:08.079074+03	2026-10-22 17:35:08.079077+03
12	392	TCH-WF-MATH	Hassan	\N	Math	Male	\N	\N	math.wf@somroyal.edu.so	\N	\N	\N	ACTIVE	2026-10-23 00:42:41.354549+03	2026-10-23 00:42:41.354557+03
13	393	TCH-WF-BIO	Ali	\N	Biology	Male	\N	\N	bio.wf@somroyal.edu.so	\N	\N	\N	ACTIVE	2026-10-23 00:42:41.369517+03	2026-10-23 00:42:41.369524+03
14	407	TCH-FM-001	Ordinary	\N	Teacher	Male	\N	\N	t_ordinary@test.com	\N	\N	\N	ACTIVE	2026-11-13 08:47:44.475189+03	2026-11-13 08:47:44.475195+03
15	408	TCH-FM-002	SingleClass	\N	Master	Female	\N	\N	t_fmsingle@test.com	\N	\N	\N	ACTIVE	2026-11-13 08:47:44.48276+03	2026-11-13 08:47:44.482765+03
16	409	TCH-FM-003	DoubleClass	\N	Master	Male	\N	\N	t_fmdouble@test.com	\N	\N	\N	ACTIVE	2026-11-13 08:47:44.486382+03	2026-11-13 08:47:44.486387+03
17	411	TCH-959610	Mustaf	Hassan	Farah	Male	1992-04-10	+25261959610	mustaf_959610@hawlwadaag.edu.so	Hawlwadaag District, Mogadishu	M.Sc. Mathematics Education	2026-09-01	ACTIVE	2026-11-13 12:15:20.758767+03	2026-11-13 12:15:20.75877+03
18	412	TCH-239150	Mustaf	Hassan	Farah	Male	1992-04-10	+25261239150	mustaf_239150@hawlwadaag.edu.so	Hawlwadaag District, Mogadishu	M.Sc. Mathematics Education	2026-09-01	ACTIVE	2026-11-13 12:15:37.114251+03	2026-11-13 12:15:37.114253+03
19	413	TCH-206739	Mustaf	Hassan	Farah	Male	1992-04-10	+25261206739	mustaf_206739@hawlwadaag.edu.so	Hawlwadaag District, Mogadishu	M.Sc. Mathematics Education	2026-09-01	ACTIVE	2026-11-13 12:16:00.69544+03	2026-11-13 12:16:00.695443+03
20	414	TCH-899666	Mustaf	Hassan	Farah	Male	1992-04-10	+25261899666	mustaf_899666@hawlwadaag.edu.so	Hawlwadaag District, Mogadishu	M.Sc. Mathematics Education	2026-09-01	ACTIVE	2026-11-13 12:16:31.957854+03	2026-11-13 12:16:31.957858+03
26	420	T-DYN-B	Teacher	\N	Math	M	\N	\N	dyn_teacher_b@hawlwadaagschool.edu.so	\N	\N	\N	ACTIVE	2026-11-13 13:51:17.56563+03	2026-11-13 16:28:37.824783+03
21	415	TCH-398544	Mustaf	Hassan	Farah	Male	1992-04-10	+25261398544	mustaf_398544@hawlwadaag.edu.so	Hawlwadaag District, Mogadishu	M.Sc. Mathematics Education	2026-09-01	ACTIVE	2026-11-13 12:16:55.328353+03	2026-11-13 12:16:55.455995+03
23	417	T-ARB-01	Teacher	\N	A Arabic	M	\N	\N	teacher_arabic@hawlwadaagschool.edu.so	\N	\N	\N	ACTIVE	2026-11-13 13:02:10.533082+03	2026-11-13 16:28:37.824778+03
24	418	T-MTH-02	Teacher	\N	B Math	M	\N	\N	teacher_math@hawlwadaagschool.edu.so	\N	\N	\N	ACTIVE	2026-11-13 13:02:11.359044+03	2026-11-13 16:28:37.824782+03
25	419	T-DYN-A	Teacher	\N	Arabic	M	\N	\N	dyn_teacher_a@hawlwadaagschool.edu.so	\N	\N	\N	ACTIVE	2026-11-13 13:51:16.551451+03	2026-11-13 16:28:37.824782+03
27	421	T-DYN-C	Teacher	\N	Physics	M	\N	\N	dyn_teacher_c@hawlwadaagschool.edu.so	\N	\N	\N	ACTIVE	2026-11-13 13:51:18.573677+03	2026-11-13 16:28:37.824784+03
28	422	T-DYN-D	Teacher	\N	Chem	M	\N	\N	dyn_teacher_d@hawlwadaagschool.edu.so	\N	\N	\N	ACTIVE	2026-11-13 13:51:19.575742+03	2026-11-13 16:28:37.824784+03
30	424	T-LOCK-01	Teacher	\N	Lock Tester	M	\N	\N	teacher_lock_test@hawlwadaagschool.edu.so	\N	\N	\N	ACTIVE	2026-11-13 16:03:26.176055+03	2026-11-13 16:28:37.824785+03
\.


--
-- Data for Name: timetable_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.timetable_settings (id, academic_year, division, school_days, start_time, end_time, period_duration_minutes, break_duration_minutes, break_after_period, lunch_duration_minutes, lunch_after_period, periods_per_day, is_active, created_at, updated_at) FROM stdin;
1	2026/2027	ALL	Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday	07:30:00	13:00:00	45	20	3	30	5	6	t	2026-10-23 23:34:30.008801+03	2026-11-13 18:10:59.760746+03
\.


--
-- Data for Name: timetables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.timetables (id, class_id, subject_id, teacher_id, academic_year, day_of_week, start_time, end_time, room, status, created_at, updated_at, period_number, is_break, published_at, published_by_id) FROM stdin;
1	21	13	\N	2025-2026	Friday	06:00:00	07:00:00	Room-5adc	ACTIVE	2026-09-21 01:43:22.840602+03	2026-09-21 01:43:22.840609+03	\N	f	\N	\N
54	50	13	\N	2027/2028	Sunday	08:00:00	08:45:00	Room-Test	ACTIVE	2026-11-13 16:24:57.026903+03	2026-11-13 16:24:57.026907+03	1	f	\N	\N
55	50	13	\N	2027/2028	Saturday	08:00:00	09:00:00	Room 101	ACTIVE	2026-11-13 16:29:02.003068+03	2026-11-13 16:29:02.003074+03	\N	f	\N	\N
3	27	13	\N	2025-2026	Friday	06:00:00	07:00:00	Room-88fa	ACTIVE	2026-10-23 23:31:18.397252+03	2026-10-23 23:31:18.397256+03	\N	f	\N	\N
4	28	13	\N	2025-2026	Friday	06:00:00	07:00:00	Room-7262	ACTIVE	2026-10-23 23:31:46.603863+03	2026-10-23 23:31:46.603866+03	\N	f	\N	\N
57	30	24	\N	2026/2027	Tuesday	07:30:00	08:15:00	Room-3056	ACTIVE	2026-11-13 16:36:08.603005+03	2026-11-13 16:36:08.603011+03	\N	f	\N	\N
58	29	13	17	2026/2027	t	07:30:00	08:15:00	Room G1-A-2026-2027	GENERATED	2026-11-13 16:36:13.773054+03	2026-11-13 16:36:13.773057+03	1	f	\N	\N
59	29	13	17	2026/2027	u	07:30:00	08:15:00	Room G1-A-2026-2027	GENERATED	2026-11-13 16:36:13.773058+03	2026-11-13 16:36:13.773059+03	1	f	\N	\N
60	29	13	17	2026/2027	r	07:30:00	08:15:00	Room G1-A-2026-2027	GENERATED	2026-11-13 16:36:13.77306+03	2026-11-13 16:36:13.77306+03	1	f	\N	\N
61	29	13	17	2026/2027	S	07:30:00	08:15:00	Room G1-A-2026-2027	GENERATED	2026-11-13 16:36:13.773061+03	2026-11-13 16:36:13.773062+03	1	f	\N	\N
62	29	13	17	2026/2027	a	07:30:00	08:15:00	Room G1-A-2026-2027	GENERATED	2026-11-13 16:36:13.773062+03	2026-11-13 16:36:13.773063+03	1	f	\N	\N
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles (id, user_id, role_id, assigned_at, assigned_by) FROM stdin;
1	1	1	2026-09-16 09:03:27.793071+03	\N
245	304	2	2026-09-20 05:38:12.58164+03	1
246	305	2	2026-09-21 01:42:57.947265+03	\N
247	306	3	2026-09-21 01:42:58.060075+03	\N
248	307	3	2026-09-21 01:42:58.065771+03	\N
249	308	2	2026-09-21 01:42:59.325894+03	\N
250	309	3	2026-09-21 01:42:59.331651+03	\N
251	310	3	2026-09-21 01:42:59.345002+03	\N
252	311	3	2026-09-21 01:42:59.351112+03	\N
253	312	3	2026-09-21 01:42:59.356427+03	\N
254	313	3	2026-09-21 01:42:59.363683+03	\N
255	314	3	2026-09-21 01:42:59.369051+03	\N
256	315	3	2026-09-21 01:42:59.375485+03	\N
257	316	3	2026-09-21 01:42:59.382266+03	\N
258	317	3	2026-09-21 01:42:59.388253+03	\N
259	318	3	2026-09-21 01:42:59.395771+03	\N
260	319	3	2026-09-21 01:42:59.402144+03	\N
261	320	3	2026-09-21 01:42:59.410043+03	\N
262	321	3	2026-09-21 01:42:59.417269+03	\N
263	322	3	2026-09-21 01:42:59.424677+03	\N
264	323	3	2026-09-21 01:42:59.432641+03	\N
265	324	3	2026-09-21 01:42:59.439432+03	\N
266	325	3	2026-09-21 01:42:59.448567+03	\N
267	326	3	2026-09-21 01:42:59.456056+03	\N
268	327	3	2026-09-21 01:42:59.465727+03	\N
269	328	3	2026-09-21 01:42:59.47418+03	\N
270	329	3	2026-09-21 01:42:59.483238+03	\N
271	330	3	2026-09-21 01:42:59.492055+03	\N
272	331	3	2026-09-21 01:42:59.501123+03	\N
273	332	3	2026-09-21 01:42:59.511425+03	\N
274	333	3	2026-09-21 01:42:59.520409+03	\N
275	334	3	2026-09-21 01:42:59.530303+03	\N
276	335	3	2026-09-21 01:42:59.538036+03	\N
277	336	3	2026-09-21 01:42:59.546962+03	\N
278	337	3	2026-09-21 01:42:59.553669+03	\N
279	338	3	2026-09-21 01:42:59.564254+03	\N
280	364	2	2026-09-21 01:43:07.569654+03	\N
281	365	3	2026-09-21 01:43:08.487179+03	\N
282	373	2	2026-09-21 01:43:21.017341+03	\N
283	374	3	2026-09-21 01:43:21.430235+03	\N
284	375	3	2026-09-21 01:43:21.555927+03	\N
285	376	3	2026-09-21 01:43:25.534463+03	1
286	377	2	2026-09-21 03:35:43.647038+03	1
287	378	3	2026-09-21 04:00:10.903661+03	1
288	379	3	2026-09-21 04:02:30.898656+03	1
289	366	2	2026-09-26 09:13:05.043305+03	\N
290	380	2	2026-10-22 17:35:08.060262+03	1
291	381	3	2026-10-22 17:35:08.388011+03	1
292	382	3	2026-10-23 00:35:45.143136+03	\N
293	383	3	2026-10-23 00:37:30.32904+03	\N
294	384	3	2026-10-23 00:38:41.185056+03	\N
295	385	3	2026-10-23 00:38:42.088672+03	\N
302	392	2	2026-10-23 00:42:41.337933+03	\N
303	393	2	2026-10-23 00:42:41.364504+03	\N
304	394	3	2026-10-23 00:42:41.454995+03	\N
305	395	3	2026-10-23 00:42:41.545936+03	\N
306	396	3	2026-10-23 00:42:41.567612+03	\N
307	397	3	2026-10-23 22:36:16.932997+03	\N
308	398	3	2026-10-23 22:36:18.614053+03	\N
309	399	3	2026-10-27 08:25:59.116472+03	\N
310	400	3	2026-10-27 08:32:42.222+03	\N
311	401	1	2026-11-11 08:58:08.861545+03	\N
312	402	3	2026-11-11 08:58:33.620698+03	\N
313	403	3	2026-11-11 09:21:12.533989+03	\N
315	404	3	2026-11-11 10:02:08.305315+03	\N
316	405	3	2026-11-11 10:02:08.305315+03	\N
317	406	1	2026-11-13 08:47:43.504836+03	\N
318	407	2	2026-11-13 08:47:43.847776+03	\N
319	408	2	2026-11-13 08:47:44.148393+03	\N
320	409	2	2026-11-13 08:47:44.463803+03	\N
321	410	6	2026-11-13 10:49:26.604298+03	\N
322	411	2	2026-11-13 12:15:20.755346+03	1
323	412	2	2026-11-13 12:15:37.110975+03	1
324	413	2	2026-11-13 12:16:00.691844+03	1
325	414	2	2026-11-13 12:16:31.953941+03	1
326	415	2	2026-11-13 12:16:55.324134+03	1
328	417	2	2026-11-13 13:02:10.516078+03	\N
329	418	2	2026-11-13 13:02:11.35328+03	\N
330	419	2	2026-11-13 13:51:16.519667+03	\N
331	420	2	2026-11-13 13:51:17.559159+03	\N
332	421	2	2026-11-13 13:51:18.567411+03	\N
333	422	2	2026-11-13 13:51:19.570365+03	\N
335	424	2	2026-11-13 16:03:26.166158+03	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, username, hashed_password, full_name, phone_number, is_active, is_superuser, last_login_at, created_at, updated_at) FROM stdin;
412	mustaf_239150@hawlwadaag.edu.so	mustaf_239150	$2b$12$Ed64UZCTPBgEJ14Lkyf.j.rdaZMsiTXNvq7NFShh2il4hA9GN4FlO	Mustaf Farah	+25261239150	t	f	\N	2026-11-13 12:15:37.099097+03	2026-11-13 12:15:37.099101+03
415	mustaf_398544@hawlwadaag.edu.so	mustaf_398544	$2b$12$jCq7LqZ8WbqlKazRYvYGXeE19mhFUHid9vntLtvq8ai/UOaj/vrr6	Mustaf Farah	+25261398544	t	f	\N	2026-11-13 12:16:55.313706+03	2026-11-13 12:16:55.459074+03
304	skycast45@gmail.com	teacher_4305	$2b$12$vfA3ZMORyoskl2G1MnMZ9etJGVERNv55v8pVwFO8rzAlZmZICKeGa	Mohammed Mukhtar	7878787877	t	f	2026-11-13 16:09:39.570177+03	2026-09-20 05:38:12.559755+03	2026-11-13 16:09:39.570599+03
419	dyn_teacher_a@hawlwadaagschool.edu.so	dyn_teacher_a	$2b$12$7oc3vUeQnluKr1Fb92wMbO7nq3a1DavUDBrp/lZngibG/ze9a.lda	Teacher A Arabic	\N	t	f	\N	2026-11-13 13:51:16.513072+03	2026-11-13 16:28:37.821355+03
420	dyn_teacher_b@hawlwadaagschool.edu.so	dyn_teacher_b	$2b$12$H74AgqSjo4YrqbYR0GTYaOk.9a2tSESiOtYBJrgP5korIMCjfrwx.	Teacher B Math	\N	t	f	\N	2026-11-13 13:51:17.555398+03	2026-11-13 16:28:37.821356+03
421	dyn_teacher_c@hawlwadaagschool.edu.so	dyn_teacher_c	$2b$12$MKXD/OwqeAG2sDIhNapPrOf3cvZfS1VEONv1yHBSjx.bbOc5Q/qWC	Teacher C Physics	\N	t	f	\N	2026-11-13 13:51:18.564134+03	2026-11-13 16:28:37.821357+03
422	dyn_teacher_d@hawlwadaagschool.edu.so	dyn_teacher_d	$2b$12$NMoCgojR0HxiUsR3khVcyOi8zOCMFjhDYlYm0KoCPqTStbQlcF1TC	Teacher D Chem	\N	t	f	\N	2026-11-13 13:51:19.568059+03	2026-11-13 16:28:37.821357+03
305	ali.teacher@hawlwadaag.edu.so	teacher.ali	$2b$12$Napj38tTAUK8IyCM/UecYeF6.jfSRyr9uyHhR1QIakeo9UVB2r1eK	Ali Mohamed Warsame	\N	t	f	2026-09-26 09:18:32.061284+03	2026-09-21 01:42:57.925017+03	2026-09-26 09:18:32.061626+03
380	khadar.749b3d@hawlwadaagschool.edu.so	teacher_749b3d	$2b$12$LtHJQ3YHfGyamIILSRtd7.ehtKsjx3iUqOrAimf8ju.SA80PwJsUy	Khadar Warsame	\N	t	f	2026-10-22 17:35:08.657224+03	2026-10-22 17:35:08.018822+03	2026-10-22 17:35:08.657611+03
381	student_749B3D@student.hawlwadaagschool.edu.so	student_749b3d	$2b$12$l3SwfFZbBYHxlzqoxSm40eKHnGcPrpvX00gMgV0k6bZ3Lns7GF9cq	Amina Farah	\N	t	f	2026-10-22 17:35:09.101786+03	2026-10-22 17:35:08.376651+03	2026-10-22 17:35:09.102211+03
382	std_track_3@test.so	std_track_3	pass	Abdiqadir Omar Yusuf	\N	t	f	\N	2026-10-23 00:35:45.115747+03	2026-10-23 00:35:45.115754+03
397	std_7@hawlwadaag.edu.so	test_student_7	pass	Yasin Mohamed Ali	\N	t	f	\N	2026-10-23 22:36:16.881839+03	2026-10-23 22:36:16.881851+03
398	std_track_8@test.so	std_track_8	pass	Sahra Hassan Aden	\N	t	f	\N	2026-10-23 22:36:18.610277+03	2026-10-23 22:36:18.610289+03
399	mohamed_3300@student.hawlwadaagschool.edu.so	mohamed_mire_3300	$2b$12$HuyVRuKoeJaPQAVinLu7w.VwgHmAGDitflxnDAqAWuDIImwBwr6pG	Mohamed Ali Mire	\N	t	f	2026-10-27 08:26:00.341271+03	2026-10-27 08:25:59.058143+03	2026-10-27 08:26:00.342761+03
401	photo_admin@test.com	test_photo_admin	$2b$12$4JQByPqVnsZcWCa9ySpjmuS1RNLMvH23yWiAhB1n0i7aaibROjRw.	Photo Test Admin	\N	t	t	\N	2026-11-11 08:58:08.817922+03	2026-11-11 08:58:08.817927+03
404	student_5a@school.edu.so	student_5a	$2b$12$RN1rpFR.6llB5F/UlunW9ebvww6VEz3CW/kol9soC7eBAbP9NMKrm	Student FiveA Somali	\N	t	f	\N	2026-11-11 09:59:08.833334+03	2026-11-11 09:59:08.833334+03
405	student_5b@school.edu.so	student_5b	$2b$12$gQd3Wn./CDT5CcMQoJ//lO.21gm5BBHe3K0dPCtuko5c5kl03O4Au	Student FiveB Somali	\N	t	f	\N	2026-11-11 09:59:08.833334+03	2026-11-11 09:59:08.833334+03
377	alimire8x14@gmail.com	teacher_5022	$2b$12$MR4tXEujT7XY/wnMCCksG.Gfv.NVo.EgOeCE.XjrWpKW84q.H6VTu	MOHAMED sulayma	+447538511769	t	f	2026-11-13 08:08:40.221127+03	2026-09-21 03:35:43.583457+03	2026-11-13 08:08:40.221488+03
406	admin_fm@test.com	admin_fm_test	$2b$12$NTG6Ctudwilx/urYukUJ9eWow4XMhBLwQeJUR4TO8AP1hSJVYrOoe	Test Admin_fm_test	\N	t	t	\N	2026-11-13 08:47:43.447382+03	2026-11-13 08:47:43.447389+03
407	t_ordinary@test.com	teacher_ordinary	$2b$12$wEErD2lGoycmSCAHFPTLUuE1IkN.v9Y7949cwiHthNGoD84nzV3vi	Test Teacher_ordinary	\N	t	f	\N	2026-11-13 08:47:43.839283+03	2026-11-13 08:47:43.83929+03
408	t_fmsingle@test.com	teacher_fm_single	$2b$12$/1iLJppViEePcV68EEIj.Om7ZkzAHlU9o4eDhRNCr2zSGGpbI.H1a	Test Teacher_fm_single	\N	t	f	\N	2026-11-13 08:47:44.144972+03	2026-11-13 08:47:44.144977+03
409	t_fmdouble@test.com	teacher_fm_double	$2b$12$UOUPUt8rcJ2khNOkiWVWCOGki0P6giczopn9QDB.fU4eY1EguOw4y	Test Teacher_fm_double	\N	t	f	\N	2026-11-13 08:47:44.460369+03	2026-11-13 08:47:44.460373+03
365	mohamed_5369@student.hawlwadaagschool.edu.so	mohamed_mire_5369	$2b$12$q4o5d/fPglB5kgYGh9JByOQvYAXotP50WvOQ3uqFUiNIpENUXlt9G	Mohamed Ali Mire	\N	t	f	2026-09-21 01:43:09.146014+03	2026-09-21 01:43:08.476503+03	2026-09-21 01:43:09.146922+03
376	khadija_633578@student.hawlwadaagschool.edu.so	khadija_633578	$2b$12$upcX8pCwy.743F7aOANnVecxdwIbMaTb2.dEvwGRMmi2IOthLHVmO	Khadija Warsame	+252617778899	t	f	\N	2026-09-21 01:43:25.524593+03	2026-09-21 01:43:25.524598+03
402	photo_student@test.com	test_photo_student	$2b$12$B3G8weLerSQVyQCNL2l64.t6XMNTPfTzoI5pCamKnVpp2Ds16bAnG	Photo Test Student	\N	t	f	\N	2026-11-11 08:58:33.607738+03	2026-11-11 08:58:33.607742+03
368	teacher_fee@hawlwadaag.edu.so	teacher_fee_test	$2b$12$kCgkROvbJkUeJflbVtGt7e5lQmMwV6wwQVxlRGam4LXALilW5ndb2	Teacher Fee Tester	\N	t	f	\N	2026-09-21 01:43:15.000604+03	2026-09-21 03:31:34.373189+03
370	admin_hormuud@school.edu.so	admin_test_hormuud	$2b$12$I/.kNQoUT40gjWL19eDaiOIM7flPhDMgWEgCrKSWrxvBc8feqZwbq	Admin Hormuud Tester	\N	t	t	\N	2026-09-21 01:43:18.935368+03	2026-09-21 03:31:34.373192+03
372	student_hormuud@school.edu.so	student_test_hormuud	$2b$12$/6ZSWGQB65V/TPzHU5ioJeNGWbSfOx7j/ZVPEN.n0OS82/KgWLOTG	Student Hormuud Tester	\N	t	f	\N	2026-09-21 01:43:18.947125+03	2026-09-21 03:31:34.373195+03
373	ahmed.test@hawlwadaag.edu.so	test_teacher_ahmed	$2b$12$Cqq6j7EMINlWYNBjX26cJ.vZg38EMtO/o6JK2WT6x9OE0L/jTpPp2	Ahmed Hassan Warsame	\N	t	f	\N	2026-09-21 01:43:21.015615+03	2026-09-21 03:31:34.373197+03
378	student63prom635369@student.hawlwadaagschool.edu.so	student63prom635369	$2b$12$x1NKrjkf1oACVhREAEp67O5heclTj4Ip3SXq6NAwFHLuYpMVZFZzW	Student6_3 A. Surname5369	\N	t	f	2026-09-21 04:00:46.417793+03	2026-09-21 04:00:10.867372+03	2026-09-21 04:00:46.418847+03
374	std_1@hawlwadaag.edu.so	test_student_1	$2b$12$8Lb4HMEw9slSpuZ6p/4pVONaeatLw.rf8MX4nmCVYcZEbkFLh46gG	Mohamed Ali Mire	\N	t	f	2026-09-21 04:10:04.838301+03	2026-09-21 01:43:21.429131+03	2026-09-21 04:10:04.838746+03
413	mustaf_206739@hawlwadaag.edu.so	mustaf_206739	$2b$12$vivLDAdKInhrewKw32NYKOO69AHZ6z9W9dUYV9DhMUl3Fn1V7K5p2	Mustaf Farah	+25261206739	t	f	\N	2026-11-13 12:16:00.683392+03	2026-11-13 12:16:00.683396+03
379	deqa18@student.hawlwadaagschool.edu.so	deqa18	$2b$12$kYlV.bbE8kfNzq0J2nvzX.plLHE0mhxX9WoZ0NMj3Gc7H5.V/L5wS	Deqa Abdi Mohamed	\N	t	f	2026-09-26 09:06:52.787084+03	2026-09-21 04:02:30.883573+03	2026-09-26 09:06:52.787593+03
424	teacher_lock_test@hawlwadaagschool.edu.so	teacher_lock_tester	$2b$12$hfFfCedoFRZmpX6Iz7kWY.NAmUlvZCSmFHZrmnH78TIJKZgPQpRzO	Teacher Lock Tester	\N	t	f	2026-11-13 16:09:38.559725+03	2026-11-13 16:03:26.164228+03	2026-11-13 16:09:38.560813+03
410	superadmin@somroyal.com	superadmin	$2b$12$6Naw0rbe6eXNzpwAB/GJyO5/wHS4RGnFd04RCWJmR8erpIBxYKjrO	Somroyal Super Administrator	+252612508505	t	t	2026-11-13 18:34:48.076986+03	2026-11-13 10:49:26.53826+03	2026-11-13 18:34:48.080891+03
383	std_track_4@test.so	std_track_4	pass	Hodan Mohamed Ibrahim	\N	t	f	\N	2026-10-23 00:37:30.323851+03	2026-10-23 00:37:30.323859+03
392	math.wf@somroyal.edu.so	test_teacher_math_wf	hash	Ustad Hassan Math	\N	t	f	\N	2026-10-23 00:42:41.331908+03	2026-10-23 00:42:41.331921+03
393	bio.wf@somroyal.edu.so	test_teacher_bio_wf	hash	Ustad Ali Biology	\N	t	f	\N	2026-10-23 00:42:41.362177+03	2026-10-23 00:42:41.362185+03
394	std_wf_1@somroyal.edu.so	std_wf_1	hash	Mustaf Farah WF	\N	t	f	\N	2026-10-23 00:42:41.452616+03	2026-10-23 00:42:41.452627+03
395	std_wf_2@somroyal.edu.so	std_wf_2	hash	Amina Dahir WF	\N	t	f	\N	2026-10-23 00:42:41.54409+03	2026-10-23 00:42:41.544096+03
396	std_wf_3@somroyal.edu.so	std_wf_3	hash	Jama Noor WF	\N	t	f	\N	2026-10-23 00:42:41.565209+03	2026-10-23 00:42:41.565218+03
366	ahmed.ali@hawlwadaagschool.edu.so	teacher.ahmed	$2b$12$7XQVSE0jlbJYBHdmYIae0.BmjlHAdh/EqO0PUT8J/OVJWpOG3LAma	Ahmed Hassan Ali	\N	t	f	2026-10-23 23:31:19.165869+03	2026-09-21 01:43:10.610605+03	2026-10-23 23:31:19.166274+03
364	teacher_prom@hawlwadaagschool.edu.so	teacher_test_prom	$2b$12$wa8sZ1.nXCfbZkKt7pJkI.yf8MP4gtU1UYAhPCN7KPpVJFeBNTAuq	Teacher Promotion Test	\N	t	f	2026-10-27 08:32:41.332168+03	2026-09-21 01:43:07.555838+03	2026-10-27 08:32:41.33339+03
400	mohamed_6582@student.hawlwadaagschool.edu.so	mohamed_mire_6582	$2b$12$f4pq0KVcBimrLUFNO1OzO.XfemLLvqVpvzxwoeWdDzNpV1U/qjMT2	Mohamed Ali Mire	\N	t	f	2026-10-27 08:32:43.38075+03	2026-10-27 08:32:42.198214+03	2026-10-27 08:32:43.3818+03
309	std1.12s@hawlwadaag.edu.so	std_12s_001	$2b$12$wSdn1sj9C6ZGq.GElNpdA.Z3HcSetwfoct2oM7XwRFCb8ZqyWYNYa	Student 01 GradeSeven	\N	t	f	2026-11-12 10:13:51.246562+03	2026-09-21 01:42:59.328658+03	2026-11-12 10:13:51.248178+03
308	ahmed.12s@hawlwadaag.edu.so	teacher.ahmed.12s	$2b$12$MwWvpDvtIDDmkkoodnqfKumR2ylB2wrhqsWAvprELMvugAkpqoHom	Ahmed Hassan Ali	\N	t	f	2026-09-26 09:12:47.523676+03	2026-09-21 01:42:59.32213+03	2026-09-26 09:12:47.524023+03
330	std22.12s@hawlwadaag.edu.so	std_12s_022	$2b$12$Dj3FwkoA2D4VlrQFReqKw..L7no7h2GaHp8BI.DoRBvEMGXCff5.6	Student 22 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.487845+03	2026-09-21 03:31:34.373135+03
331	std23.12s@hawlwadaag.edu.so	std_12s_023	$2b$12$.UDED55tLc7b14qRWvyJc.p0n8u5KvtulvxDGXSTqtN1rBAYYmRXy	Student 23 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.497665+03	2026-09-21 03:31:34.373137+03
332	std24.12s@hawlwadaag.edu.so	std_12s_024	$2b$12$rCCLE4euUmPGpRkmh8RXqujF/YgKx87M9AzfwQAW3YkBb.5UInzRa	Student 24 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.506872+03	2026-09-21 03:31:34.373138+03
333	std25.12s@hawlwadaag.edu.so	std_12s_025	$2b$12$kU58Eh8AO8hiLwinMvrS/eRg8owSxqR/P75cTjT7eTEibrC4bI3qq	Student 25 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.516986+03	2026-09-21 03:31:34.37314+03
334	std26.12s@hawlwadaag.edu.so	std_12s_026	$2b$12$qLFS4gJEPds4Zwv8Mprg9.Wbzk.3ou0hpI530H1wGqDsTgzFpbuPa	Student 26 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.525955+03	2026-09-21 03:31:34.373141+03
335	std27.12s@hawlwadaag.edu.so	std_12s_027	$2b$12$.oL6lDl9Uvc2X17HrSzJIeD5B6ipebAIguiGCAV7bsMZU4i8/Pyny	Student 27 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.534924+03	2026-09-21 03:31:34.373143+03
336	std28.12s@hawlwadaag.edu.so	std_12s_028	$2b$12$Kri0py9L3D3BFtUi9gf9i.lbdcgqMtgvpWJN.qcHoZeF00LVTafNy	Student 28 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.54361+03	2026-09-21 03:31:34.373144+03
337	std29.12s@hawlwadaag.edu.so	std_12s_029	$2b$12$57MwaXWBSUsVUiJoOfyuceUzRKuPy2yuoFPRrbZq6WU6uPb36uCyG	Student 29 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.550853+03	2026-09-21 03:31:34.373146+03
338	std30.12s@hawlwadaag.edu.so	std_12s_030	$2b$12$AfMaQhttrliNTrU0EHa02.3WhEeFATsSdIvQRwNr8oSsefNcKQmWm	Student 30 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.559205+03	2026-09-21 03:31:34.373147+03
339	std1.g9@hawlwadaag.edu.so	std_g9_001	$2b$12$gtaeoInbG/nQEtjRCUtyx.mZkQAxfOJiSoAoefqz6yY5irSXzqpbO	Student 01 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.421648+03	2026-09-21 03:31:34.373149+03
340	std2.g9@hawlwadaag.edu.so	std_g9_002	$2b$12$Wu0P9qj5nynhT4EcyUXyxeDJeaeVPO8i2QyBYakKQ0uXMiE7Y.iXS	Student 02 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.429842+03	2026-09-21 03:31:34.37315+03
306	mustaf.t@hawlwadaag.edu.so	std_mustaf_test	$2b$12$iSExYYsOXJZegJCj8JxIKOUiKSTj2vm6vaj5fB.Os4NvjpvUq5Kzm	Mustaf Abdi Noor	\N	t	f	\N	2026-09-21 01:42:58.034026+03	2026-09-21 03:31:34.373093+03
307	amina.t@hawlwadaag.edu.so	std_amina_test	$2b$12$DAmPAbzn1iTlG9UcBHWNveZJDfdPopWt90LjL9DX7HNaJ/WiIqA1W	Amina Hassan Ibrahim	\N	t	f	\N	2026-09-21 01:42:58.062821+03	2026-09-21 03:31:34.373097+03
310	std2.12s@hawlwadaag.edu.so	std_12s_002	$2b$12$WIXm3vG7bHCA72DnBePV4eTxnP5gOSUBWKSIuMSdaExfkZ4.bQHBm	Student 02 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.340394+03	2026-09-21 03:31:34.373103+03
311	std3.12s@hawlwadaag.edu.so	std_12s_003	$2b$12$VzItLT3azemATcOWs6VWsukPMzHTsopucdRt7s8YGmiVD7meSuCiy	Student 03 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.348781+03	2026-09-21 03:31:34.373105+03
312	std4.12s@hawlwadaag.edu.so	std_12s_004	$2b$12$vam8W0fab/FmLGdqwK4eVOpjZAzmecIMNiUpvdauM8mBgGzcMnWwm	Student 04 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.354209+03	2026-09-21 03:31:34.373106+03
313	std5.12s@hawlwadaag.edu.so	std_12s_005	$2b$12$1YLkHtO8Om3bgIH2RxtxBO/qN8FyrMfzGXKKR/m4i6wOEbRDHhgNa	Student 05 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.361063+03	2026-09-21 03:31:34.373108+03
314	std6.12s@hawlwadaag.edu.so	std_12s_006	$2b$12$AlT3K06w.VLIF/Yc6TdJuOq9E4MNIxsyaRR2tyrdOwEq9J3jl13ZO	Student 06 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.366898+03	2026-09-21 03:31:34.373109+03
315	std7.12s@hawlwadaag.edu.so	std_12s_007	$2b$12$8YpuwNsLiy2NdlsDJtFabOt5fknHtznUNlWGuRwyni5CptvXb6VLa	Student 07 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.372113+03	2026-09-21 03:31:34.373111+03
316	std8.12s@hawlwadaag.edu.so	std_12s_008	$2b$12$ZS3q7Wq60.9vpnKAoDp8Mu7NBlpaYefE0DHuIoaxMS2.4yByGMO2q	Student 08 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.379788+03	2026-09-21 03:31:34.373113+03
317	std9.12s@hawlwadaag.edu.so	std_12s_009	$2b$12$CQK3ghM6fY4C2gNmsEHXAOPQxTIXOIq9SH0PzFUeF9eFokbhNuocC	Student 09 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.385668+03	2026-09-21 03:31:34.373114+03
318	std10.12s@hawlwadaag.edu.so	std_12s_010	$2b$12$6OaqX439YMIVEI04zNatnuKr0t/ISQmORGpaXPZm92q/3pysiP6K2	Student 10 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.392404+03	2026-09-21 03:31:34.373116+03
319	std11.12s@hawlwadaag.edu.so	std_12s_011	$2b$12$nryMgKLA7eddPi7Noq.zaelSi/LlO3sE.EvILWlQhW9bRS0yxbYBO	Student 11 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.399558+03	2026-09-21 03:31:34.373117+03
320	std12.12s@hawlwadaag.edu.so	std_12s_012	$2b$12$ecnz8jmOstultLYlTUzEbughvgR8UbkGQ8W6vxub9zWeI1xnyBMGG	Student 12 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.406033+03	2026-09-21 03:31:34.373119+03
321	std13.12s@hawlwadaag.edu.so	std_12s_013	$2b$12$gXdFOLXYdcJGIinfQvzrE..HtIadqJqiuU07svjmOec9vL34WR9PW	Student 13 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.414528+03	2026-09-21 03:31:34.373121+03
322	std14.12s@hawlwadaag.edu.so	std_12s_014	$2b$12$5T7PUFYFpZHAUgx1qZa/2uz1XUlC68jJJ37A0iXUDGL/uKkZ8Ally	Student 14 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.421203+03	2026-09-21 03:31:34.373122+03
323	std15.12s@hawlwadaag.edu.so	std_12s_015	$2b$12$1zP9QB17kpom1Vorgrjmaee9O3u.4Ba7AJdrrk1dcNQckR33SY.uO	Student 15 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.429801+03	2026-09-21 03:31:34.373124+03
324	std16.12s@hawlwadaag.edu.so	std_12s_016	$2b$12$L4/muRpOZEA2Q1.QEGZJiez4sLPax2idxbc2nZl3xq2IJdGaSZ5iO	Student 16 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.436492+03	2026-09-21 03:31:34.373125+03
325	std17.12s@hawlwadaag.edu.so	std_12s_017	$2b$12$b1sE/prGcg6Fc05yPMU9ruMWzybdnUY9cSwk2CNFM.qx3JPJnGe6e	Student 17 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.445336+03	2026-09-21 03:31:34.373127+03
326	std18.12s@hawlwadaag.edu.so	std_12s_018	$2b$12$I1.9cxNCd7iUMUaTFzGxTeXYgG4kGm98ok.QbP7o7FfwW9Qea0pUq	Student 18 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.45267+03	2026-09-21 03:31:34.373129+03
327	std19.12s@hawlwadaag.edu.so	std_12s_019	$2b$12$J/arReXE1/q69ylbjFyWe.QZkk86oZottDCFZfoZCFR9c78iZY6py	Student 19 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.462532+03	2026-09-21 03:31:34.37313+03
328	std20.12s@hawlwadaag.edu.so	std_12s_020	$2b$12$suAnR99Wka0V7TvS4OpPl.Pfki0Gh5JyISztiWHuO0U79agfBN7lW	Student 20 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.470225+03	2026-09-21 03:31:34.373132+03
329	std21.12s@hawlwadaag.edu.so	std_12s_021	$2b$12$i/KuVJZ6tnkluieigwqld.dS/mhNZGCViWS.00GsL7kPulsYdvcSC	Student 21 GradeSeven	\N	t	f	\N	2026-09-21 01:42:59.479947+03	2026-09-21 03:31:34.373133+03
341	std3.g9@hawlwadaag.edu.so	std_g9_003	$2b$12$aGX56Hltd0AufoZ6gBN.dejhOpzBEyXs5QR4sr3uIaurdC93RKzAu	Student 03 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.437113+03	2026-09-21 03:31:34.373152+03
342	std4.g9@hawlwadaag.edu.so	std_g9_004	$2b$12$O27wCdvdssCyLgo.x4h.OejY32DplBhQxGDz.qkS1Vmt13Vzo/vze	Student 04 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.444685+03	2026-09-21 03:31:34.373153+03
343	std5.g9@hawlwadaag.edu.so	std_g9_005	$2b$12$34JeIr6KjbEMHyzauDwj.ewnRe0.P28q2DGC74dY/jeEMX.vW7fFO	Student 05 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.451087+03	2026-09-21 03:31:34.373155+03
344	std6.g9@hawlwadaag.edu.so	std_g9_006	$2b$12$9WcwIljsZh2roONIgrAQsOy4RfF89rIUxA7PJ1n/.ik9u14G.sYT6	Student 06 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.458401+03	2026-09-21 03:31:34.373156+03
345	std7.g9@hawlwadaag.edu.so	std_g9_007	$2b$12$MYIgVbp23Bb6nvvl4rB64.wyBk9A6BT9Dqu57aIpZAs83kV3TR4TK	Student 07 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.465394+03	2026-09-21 03:31:34.373158+03
346	std8.g9@hawlwadaag.edu.so	std_g9_008	$2b$12$AkBrK4BYkgj63RCngHcd2.vZK93eNWLKj4ABUREwPe/Q4fOJv6OKi	Student 08 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.470948+03	2026-09-21 03:31:34.37316+03
384	std_5@hawlwadaag.edu.so	test_student_5	pass	Abdullahi Ahmed Ismail	\N	t	f	\N	2026-10-23 00:38:41.179526+03	2026-10-23 00:38:41.179536+03
385	std_track_6@test.so	std_track_6	pass	Maryan Abdi Farah	\N	t	f	\N	2026-10-23 00:38:42.08528+03	2026-10-23 00:38:42.08529+03
347	std9.g9@hawlwadaag.edu.so	std_g9_009	$2b$12$Zuv5Jscy/OLOnmwGuqaVxe6c4ni8V8qsvsjrWqLToiIvARv0mkiWq	Student 09 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.477588+03	2026-09-21 03:31:34.373161+03
348	std10.g9@hawlwadaag.edu.so	std_g9_010	$2b$12$5LJuGqOCgxRbQ4vzV2IHe.NIvhQnENAXWmpb.QdiC6DYQcxLqfCuO	Student 10 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.483896+03	2026-09-21 03:31:34.373163+03
349	std11.g9@hawlwadaag.edu.so	std_g9_011	$2b$12$BjzrgT/nIe7Kte4e3lNy9.IzpMnEjcB3kAZCtQGZYy9vYFHNL1QCe	Student 11 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.489569+03	2026-09-21 03:31:34.373164+03
350	std12.g9@hawlwadaag.edu.so	std_g9_012	$2b$12$W7eCKZ9AdiAbL7pmL6Br0u0vA46JKwJpMw6IKJ5//NcGNIVePfCiG	Student 12 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.497585+03	2026-09-21 03:31:34.373165+03
351	std13.g9@hawlwadaag.edu.so	std_g9_013	$2b$12$Jk0J9uqPMMOEivN31pAPhuNwwkaWjw9iBVUdI952ovHp2DWIKba5.	Student 13 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.503604+03	2026-09-21 03:31:34.373167+03
352	std14.g9@hawlwadaag.edu.so	std_g9_014	$2b$12$lX8NmnPiPbcx58f8W9YONuzLdSApyzZfzFhHLBPHutuEkZ/liipOq	Student 14 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.511262+03	2026-09-21 03:31:34.373168+03
353	std15.g9@hawlwadaag.edu.so	std_g9_015	$2b$12$jnqqJ7ucQN41Qw2dDrLmPO3.pFnh2R7NCBgcl.cqHW4cjXF/aolY6	Student 15 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.517369+03	2026-09-21 03:31:34.37317+03
354	std16.g9@hawlwadaag.edu.so	std_g9_016	$2b$12$3Q6XAvePFmZRtLFTDzGfCOwon1bNrPU1zo3Z8lRpvC2rRy4SmftrK	Student 16 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.522745+03	2026-09-21 03:31:34.373172+03
355	std17.g9@hawlwadaag.edu.so	std_g9_017	$2b$12$gX9roOM4oUUZ7W0Z1u8TsOLvRNQO7.sXLDtWzOQh9s8LMGrBEuJbO	Student 17 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.529559+03	2026-09-21 03:31:34.373173+03
356	std18.g9@hawlwadaag.edu.so	std_g9_018	$2b$12$AHS9XoPZi2CiCtoJSWBLQujj.0QfnW9szNJRgCYtQ/Rk2BgovR0jS	Student 18 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.535685+03	2026-09-21 03:31:34.373175+03
357	std19.g9@hawlwadaag.edu.so	std_g9_019	$2b$12$6H/JhMDxNfNHDH0xfx0dr.MuUu6NY2uPecTT0vv58xdO0Wf7JZfLy	Student 19 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.541336+03	2026-09-21 03:31:34.373176+03
358	std20.g9@hawlwadaag.edu.so	std_g9_020	$2b$12$D0O5hh2sD3A5sKGkCtvNcuK/v3JIkVvP4S29kdjzvmlpjqZsozvJe	Student 20 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.547966+03	2026-09-21 03:31:34.373178+03
359	std21.g9@hawlwadaag.edu.so	std_g9_021	$2b$12$M1qQNx5JK.lYXQrz0QDUN.IYl2n1tLexvPOke7LqiqDmK8PxjeYiK	Student 21 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.553829+03	2026-09-21 03:31:34.373179+03
360	std22.g9@hawlwadaag.edu.so	std_g9_022	$2b$12$bf7CQW9ubZAukq7eTNkMJevkJMoIAX2eSbrA81/TPrJqtb2xYb02S	Student 22 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.561177+03	2026-09-21 03:31:34.373181+03
361	std23.g9@hawlwadaag.edu.so	std_g9_023	$2b$12$DGKQ57qdLWAMswxW5BC3a.Cf4gINf/60APZZ.lRMjIcbpZF/n19SK	Student 23 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.567436+03	2026-09-21 03:31:34.373182+03
362	std24.g9@hawlwadaag.edu.so	std_g9_024	$2b$12$lcp4s296J5CcrM2d2AS38uk2gY.7WiNrskfVciDAhDwgC1QXGQeEi	Student 24 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.572881+03	2026-09-21 03:31:34.373184+03
363	std25.g9@hawlwadaag.edu.so	std_g9_025	$2b$12$C.QpCvQVcc7LGVUajlv79.37OhrSfyevu5d4xgHIOw1QmyvxAVTlm	Student 25 GradeNine	\N	t	f	\N	2026-09-21 01:43:04.58062+03	2026-09-21 03:31:34.373186+03
367	admin_fee@hawlwadaag.edu.so	admin_fee_test	$2b$12$rSA3m5ByzaLfdd4Gv3rjbOHBbVVjeSG3HTRF/QWoVESWUCrd4R2UW	Finance Administrator	\N	t	t	\N	2026-09-21 01:43:14.989063+03	2026-09-21 03:31:34.373187+03
369	student_fee@hawlwadaag.edu.so	student_fee_test	$2b$12$JQaXzbF/NEuhUCMHquYzHuExR0SFUoLqDYOgMKQzJo6e07G.T7VwW	Student Fee Tester	\N	t	f	\N	2026-09-21 01:43:15.005579+03	2026-09-21 03:31:34.37319+03
371	teacher_hormuud@school.edu.so	teacher_test_hormuud	$2b$12$I1H3Du13B0QDKEQeH0IlPusGvkY8fCK6uL.zQbSauD2qCAyry7olO	Teacher Hormuud Tester	\N	t	f	\N	2026-09-21 01:43:18.941812+03	2026-09-21 03:31:34.373194+03
375	std_track_2@test.so	std_track_2	$2b$12$gR5VXwKOvFE8J27N2boU5eNChvOl.SIxYNQBsB0xNAQEjJgdByGum	Amina Hassan Noor	\N	t	f	\N	2026-09-21 01:43:21.554826+03	2026-09-21 03:31:34.3732+03
417	teacher_arabic@hawlwadaagschool.edu.so	teacher_arabic_test	$2b$12$uVDz8hMAK.Qsovb0Tz1vXOaqXC2U8J8bTTqQPESDbUHYWUDtafuPK	Teacher A Arabic	\N	t	f	\N	2026-11-13 13:02:10.510618+03	2026-11-13 16:28:37.821349+03
411	mustaf_959610@hawlwadaag.edu.so	mustaf_959610	$2b$12$4PxfQh8B0keR/BanGT81XuYl957lNTM/PQdfFKuJXFkrq8F6XA7Ve	Mustaf Farah	+25261959610	t	f	\N	2026-11-13 12:15:20.742342+03	2026-11-13 12:15:20.742345+03
403	std_photo_5e4d76@test.com	std_photo_5e4d76	$2b$12$XfdED0jxwuOwkhoMXbz9oOyLldn3MQhoCDnOYpFNYYGVoSpoaHFdy	Photo Test Student	\N	t	f	\N	2026-11-11 09:21:12.526212+03	2026-11-11 09:21:12.526216+03
418	teacher_math@hawlwadaagschool.edu.so	teacher_math_test	$2b$12$6HTXqFVx5N5q/YWSaxWxaOG0PTxfxAozkcyV2X7eBZnbbGS2E0.uq	Teacher B Mathematics	\N	t	f	\N	2026-11-13 13:02:11.350608+03	2026-11-13 16:28:37.821354+03
414	mustaf_899666@hawlwadaag.edu.so	mustaf_899666	$2b$12$y8BfGSz1p8mdTbLXFzIAe.QQLmCCm5YdietvyyejyrAwRm8E/R9Ye	Mustaf Farah	+25261899666	t	f	\N	2026-11-13 12:16:31.944985+03	2026-11-13 12:16:31.944989+03
1	admin@hawlwadaagschool.edu.so	admin	$2b$12$8XuSj7OGSgnX1mXhvqxH8ei0RHqnM4J1tLh3pJ3ZWzu70blhN/KJS	Hawlwadaag System Admin	+252 61 9999999	t	t	2026-11-14 11:45:37.057161+03	2026-09-16 09:03:27.764955+03	2026-11-14 11:45:37.061262+03
\.


--
-- Name: attendance_submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_submissions_id_seq', 54, true);


--
-- Name: attendances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendances_id_seq', 173, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 786, true);


--
-- Name: class_promotion_batches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.class_promotion_batches_id_seq', 107, true);


--
-- Name: class_promotion_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.class_promotion_records_id_seq', 72, true);


--
-- Name: classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.classes_id_seq', 94, true);


--
-- Name: exam_deadline_extensions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exam_deadline_extensions_id_seq', 4, true);


--
-- Name: exam_results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exam_results_id_seq', 475, true);


--
-- Name: exams_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_id_seq', 33, true);


--
-- Name: fee_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fee_payments_id_seq', 11, true);


--
-- Name: fee_structures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fee_structures_id_seq', 21, true);


--
-- Name: form_master_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_master_assignments_id_seq', 11, true);


--
-- Name: inquiries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inquiries_id_seq', 5, true);


--
-- Name: institution_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institution_payments_id_seq', 12, true);


--
-- Name: institutions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institutions_id_seq', 18, true);


--
-- Name: notification_deliveries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_deliveries_id_seq', 129, true);


--
-- Name: notification_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_templates_id_seq', 16, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 240, true);


--
-- Name: result_release_batches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.result_release_batches_id_seq', 12, true);


--
-- Name: result_submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.result_submissions_id_seq', 46, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 6, true);


--
-- Name: sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sessions_id_seq', 208, true);


--
-- Name: student_enrollments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_enrollments_id_seq', 292, true);


--
-- Name: student_fees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_fees_id_seq', 65, true);


--
-- Name: student_import_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_import_logs_id_seq', 10, true);


--
-- Name: student_result_views_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_result_views_id_seq', 5, true);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_id_seq', 230, true);


--
-- Name: subjects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subjects_id_seq', 39, true);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 12, true);


--
-- Name: system_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_settings_id_seq', 12, true);


--
-- Name: teacher_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teacher_assignments_id_seq', 73, true);


--
-- Name: teacher_attendances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teacher_attendances_id_seq', 22, true);


--
-- Name: teacher_availabilities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teacher_availabilities_id_seq', 3, true);


--
-- Name: teachers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teachers_id_seq', 30, true);


--
-- Name: timetable_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.timetable_settings_id_seq', 1, true);


--
-- Name: timetables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.timetables_id_seq', 163, true);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 335, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 424, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attendance_submissions attendance_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_submissions
    ADD CONSTRAINT attendance_submissions_pkey PRIMARY KEY (id);


--
-- Name: attendances attendances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: class_promotion_batches class_promotion_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_batches
    ADD CONSTRAINT class_promotion_batches_pkey PRIMARY KEY (id);


--
-- Name: class_promotion_records class_promotion_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_records
    ADD CONSTRAINT class_promotion_records_pkey PRIMARY KEY (id);


--
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- Name: exam_deadline_extensions exam_deadline_extensions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_deadline_extensions
    ADD CONSTRAINT exam_deadline_extensions_pkey PRIMARY KEY (id);


--
-- Name: exam_results exam_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT exam_results_pkey PRIMARY KEY (id);


--
-- Name: exams exams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_pkey PRIMARY KEY (id);


--
-- Name: fee_payments fee_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_payments
    ADD CONSTRAINT fee_payments_pkey PRIMARY KEY (id);


--
-- Name: fee_structures fee_structures_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_structures
    ADD CONSTRAINT fee_structures_pkey PRIMARY KEY (id);


--
-- Name: form_master_assignments form_master_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_master_assignments
    ADD CONSTRAINT form_master_assignments_pkey PRIMARY KEY (id);


--
-- Name: inquiries inquiries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inquiries
    ADD CONSTRAINT inquiries_pkey PRIMARY KEY (id);


--
-- Name: institution_payments institution_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institution_payments
    ADD CONSTRAINT institution_payments_pkey PRIMARY KEY (id);


--
-- Name: institutions institutions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_pkey PRIMARY KEY (id);


--
-- Name: notification_deliveries notification_deliveries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_deliveries
    ADD CONSTRAINT notification_deliveries_pkey PRIMARY KEY (id);


--
-- Name: notification_templates notification_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_templates
    ADD CONSTRAINT notification_templates_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: result_release_batches result_release_batches_batch_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_release_batches
    ADD CONSTRAINT result_release_batches_batch_code_key UNIQUE (batch_code);


--
-- Name: result_release_batches result_release_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_release_batches
    ADD CONSTRAINT result_release_batches_pkey PRIMARY KEY (id);


--
-- Name: result_submissions result_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT result_submissions_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: student_enrollments student_enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_enrollments
    ADD CONSTRAINT student_enrollments_pkey PRIMARY KEY (id);


--
-- Name: student_fees student_fees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT student_fees_pkey PRIMARY KEY (id);


--
-- Name: student_import_logs student_import_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_import_logs
    ADD CONSTRAINT student_import_logs_pkey PRIMARY KEY (id);


--
-- Name: student_result_views student_result_views_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_result_views
    ADD CONSTRAINT student_result_views_pkey PRIMARY KEY (id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: subjects subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (id);


--
-- Name: teacher_assignments teacher_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_assignments
    ADD CONSTRAINT teacher_assignments_pkey PRIMARY KEY (id);


--
-- Name: teacher_attendances teacher_attendances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_attendances
    ADD CONSTRAINT teacher_attendances_pkey PRIMARY KEY (id);


--
-- Name: teacher_availabilities teacher_availabilities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_availabilities
    ADD CONSTRAINT teacher_availabilities_pkey PRIMARY KEY (id);


--
-- Name: teachers teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (id);


--
-- Name: timetable_settings timetable_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetable_settings
    ADD CONSTRAINT timetable_settings_pkey PRIMARY KEY (id);


--
-- Name: timetables timetables_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetables
    ADD CONSTRAINT timetables_pkey PRIMARY KEY (id);


--
-- Name: attendance_submissions uq_attendance_submission_session; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_submissions
    ADD CONSTRAINT uq_attendance_submission_session UNIQUE NULLS NOT DISTINCT (class_id, subject_id, date, period);


--
-- Name: classes uq_class_academic_year_div_level_sec; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT uq_class_academic_year_div_level_sec UNIQUE (academic_year, division, level, section);


--
-- Name: class_promotion_batches uq_class_promotion_batch_code; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_batches
    ADD CONSTRAINT uq_class_promotion_batch_code UNIQUE (batch_code);


--
-- Name: teacher_assignments uq_class_subject_academic_year; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_assignments
    ADD CONSTRAINT uq_class_subject_academic_year UNIQUE (class_id, subject_id, academic_year);


--
-- Name: exams uq_exam_academic_year_class_subj_type; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT uq_exam_academic_year_class_subj_type UNIQUE (academic_year, class_id, subject_id, exam_type);


--
-- Name: exam_results uq_exam_student_subject; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT uq_exam_student_subject UNIQUE (exam_id, student_id, subject_id);


--
-- Name: notification_templates uq_notification_template_code; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_templates
    ADD CONSTRAINT uq_notification_template_code UNIQUE (code);


--
-- Name: notifications uq_notifications_idempotency_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT uq_notifications_idempotency_key UNIQUE (idempotency_key);


--
-- Name: result_submissions uq_result_sub_exam_class_subj_tch; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT uq_result_sub_exam_class_subj_tch UNIQUE (exam_id, class_id, subject_id, teacher_id);


--
-- Name: student_enrollments uq_student_academic_year; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_enrollments
    ADD CONSTRAINT uq_student_academic_year UNIQUE (student_id, academic_year);


--
-- Name: attendances uq_student_date_subject_period; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT uq_student_date_subject_period UNIQUE NULLS NOT DISTINCT (student_id, date, subject_id, period);


--
-- Name: student_result_views uq_student_exam_class_year_view; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_result_views
    ADD CONSTRAINT uq_student_exam_class_year_view UNIQUE (student_id, exam_name, class_id, academic_year);


--
-- Name: student_fees uq_student_fee_structure; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT uq_student_fee_structure UNIQUE (student_id, fee_structure_id);


--
-- Name: teacher_attendances uq_teacher_date_attendance; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_attendances
    ADD CONSTRAINT uq_teacher_date_attendance UNIQUE (teacher_id, date);


--
-- Name: teacher_availabilities uq_teacher_year_day_availability; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_availabilities
    ADD CONSTRAINT uq_teacher_year_day_availability UNIQUE (teacher_id, academic_year, day_of_week);


--
-- Name: user_roles uq_user_role; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT uq_user_role UNIQUE (user_id, role_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_attendance_submissions_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_submissions_academic_year ON public.attendance_submissions USING btree (academic_year);


--
-- Name: ix_attendance_submissions_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_submissions_class_id ON public.attendance_submissions USING btree (class_id);


--
-- Name: ix_attendance_submissions_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_submissions_date ON public.attendance_submissions USING btree (date);


--
-- Name: ix_attendance_submissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_submissions_id ON public.attendance_submissions USING btree (id);


--
-- Name: ix_attendance_submissions_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_submissions_subject_id ON public.attendance_submissions USING btree (subject_id);


--
-- Name: ix_attendance_submissions_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_submissions_teacher_id ON public.attendance_submissions USING btree (teacher_id);


--
-- Name: ix_attendances_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_academic_year ON public.attendances USING btree (academic_year);


--
-- Name: ix_attendances_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_class_id ON public.attendances USING btree (class_id);


--
-- Name: ix_attendances_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_date ON public.attendances USING btree (date);


--
-- Name: ix_attendances_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_id ON public.attendances USING btree (id);


--
-- Name: ix_attendances_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_status ON public.attendances USING btree (status);


--
-- Name: ix_attendances_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_student_id ON public.attendances USING btree (student_id);


--
-- Name: ix_attendances_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_subject_id ON public.attendances USING btree (subject_id);


--
-- Name: ix_attendances_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendances_teacher_id ON public.attendances USING btree (teacher_id);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: ix_class_promotion_batches_batch_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_class_promotion_batches_batch_code ON public.class_promotion_batches USING btree (batch_code);


--
-- Name: ix_class_promotion_batches_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_batches_created_at ON public.class_promotion_batches USING btree (created_at);


--
-- Name: ix_class_promotion_batches_created_by_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_batches_created_by_id ON public.class_promotion_batches USING btree (created_by_id);


--
-- Name: ix_class_promotion_batches_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_batches_id ON public.class_promotion_batches USING btree (id);


--
-- Name: ix_class_promotion_batches_source_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_batches_source_academic_year ON public.class_promotion_batches USING btree (source_academic_year);


--
-- Name: ix_class_promotion_batches_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_batches_status ON public.class_promotion_batches USING btree (status);


--
-- Name: ix_class_promotion_batches_target_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_batches_target_academic_year ON public.class_promotion_batches USING btree (target_academic_year);


--
-- Name: ix_class_promotion_records_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_records_batch_id ON public.class_promotion_records USING btree (batch_id);


--
-- Name: ix_class_promotion_records_from_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_records_from_class_id ON public.class_promotion_records USING btree (from_class_id);


--
-- Name: ix_class_promotion_records_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_records_id ON public.class_promotion_records USING btree (id);


--
-- Name: ix_class_promotion_records_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_records_student_id ON public.class_promotion_records USING btree (student_id);


--
-- Name: ix_class_promotion_records_to_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_promotion_records_to_class_id ON public.class_promotion_records USING btree (to_class_id);


--
-- Name: ix_classes_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_classes_academic_year ON public.classes USING btree (academic_year);


--
-- Name: ix_classes_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_classes_code ON public.classes USING btree (code);


--
-- Name: ix_classes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_classes_id ON public.classes USING btree (id);


--
-- Name: ix_classes_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_classes_name ON public.classes USING btree (name);


--
-- Name: ix_exam_results_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exam_results_class_id ON public.exam_results USING btree (class_id);


--
-- Name: ix_exam_results_exam_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exam_results_exam_id ON public.exam_results USING btree (exam_id);


--
-- Name: ix_exam_results_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exam_results_id ON public.exam_results USING btree (id);


--
-- Name: ix_exam_results_release_batch_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exam_results_release_batch_id ON public.exam_results USING btree (release_batch_id);


--
-- Name: ix_exam_results_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exam_results_status ON public.exam_results USING btree (status);


--
-- Name: ix_exam_results_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exam_results_student_id ON public.exam_results USING btree (student_id);


--
-- Name: ix_exam_results_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exam_results_subject_id ON public.exam_results USING btree (subject_id);


--
-- Name: ix_exam_results_submission_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exam_results_submission_id ON public.exam_results USING btree (submission_id);


--
-- Name: ix_exams_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exams_academic_year ON public.exams USING btree (academic_year);


--
-- Name: ix_exams_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exams_class_id ON public.exams USING btree (class_id);


--
-- Name: ix_exams_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exams_id ON public.exams USING btree (id);


--
-- Name: ix_exams_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exams_name ON public.exams USING btree (name);


--
-- Name: ix_exams_published_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exams_published_at ON public.exams USING btree (published_at);


--
-- Name: ix_exams_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exams_subject_id ON public.exams USING btree (subject_id);


--
-- Name: ix_fee_payments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_payments_id ON public.fee_payments USING btree (id);


--
-- Name: ix_fee_payments_receipt_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_fee_payments_receipt_number ON public.fee_payments USING btree (receipt_number);


--
-- Name: ix_fee_payments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_payments_status ON public.fee_payments USING btree (status);


--
-- Name: ix_fee_payments_student_fee_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_payments_student_fee_id ON public.fee_payments USING btree (student_fee_id);


--
-- Name: ix_fee_payments_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_payments_student_id ON public.fee_payments USING btree (student_id);


--
-- Name: ix_fee_structures_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_structures_academic_year ON public.fee_structures USING btree (academic_year);


--
-- Name: ix_fee_structures_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_structures_class_id ON public.fee_structures USING btree (class_id);


--
-- Name: ix_fee_structures_created_by_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_structures_created_by_id ON public.fee_structures USING btree (created_by_id);


--
-- Name: ix_fee_structures_education_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_structures_education_level ON public.fee_structures USING btree (education_level);


--
-- Name: ix_fee_structures_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_structures_id ON public.fee_structures USING btree (id);


--
-- Name: ix_fee_structures_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fee_structures_name ON public.fee_structures USING btree (name);


--
-- Name: ix_form_master_assignments_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_master_assignments_academic_year ON public.form_master_assignments USING btree (academic_year);


--
-- Name: ix_form_master_assignments_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_master_assignments_class_id ON public.form_master_assignments USING btree (class_id);


--
-- Name: ix_form_master_assignments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_master_assignments_id ON public.form_master_assignments USING btree (id);


--
-- Name: ix_form_master_assignments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_master_assignments_status ON public.form_master_assignments USING btree (status);


--
-- Name: ix_form_master_assignments_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_master_assignments_teacher_id ON public.form_master_assignments USING btree (teacher_id);


--
-- Name: ix_form_master_class_year_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_master_class_year_status ON public.form_master_assignments USING btree (class_id, academic_year, status);


--
-- Name: ix_form_master_teacher_year_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_master_teacher_year_status ON public.form_master_assignments USING btree (teacher_id, academic_year, status);


--
-- Name: ix_inquiries_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inquiries_email ON public.inquiries USING btree (email);


--
-- Name: ix_inquiries_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inquiries_id ON public.inquiries USING btree (id);


--
-- Name: ix_inquiries_school_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inquiries_school_name ON public.inquiries USING btree (school_name);


--
-- Name: ix_inquiries_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inquiries_status ON public.inquiries USING btree (status);


--
-- Name: ix_institution_payments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institution_payments_id ON public.institution_payments USING btree (id);


--
-- Name: ix_institution_payments_institution_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institution_payments_institution_id ON public.institution_payments USING btree (institution_id);


--
-- Name: ix_institution_payments_reference; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_institution_payments_reference ON public.institution_payments USING btree (reference);


--
-- Name: ix_institution_payments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institution_payments_status ON public.institution_payments USING btree (status);


--
-- Name: ix_institution_payments_subscription_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institution_payments_subscription_id ON public.institution_payments USING btree (subscription_id);


--
-- Name: ix_institutions_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_institutions_code ON public.institutions USING btree (code);


--
-- Name: ix_institutions_database_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_database_name ON public.institutions USING btree (database_name);


--
-- Name: ix_institutions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_id ON public.institutions USING btree (id);


--
-- Name: ix_institutions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_name ON public.institutions USING btree (name);


--
-- Name: ix_institutions_provisioning_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_provisioning_status ON public.institutions USING btree (provisioning_status);


--
-- Name: ix_institutions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_status ON public.institutions USING btree (status);


--
-- Name: ix_institutions_subscription_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_subscription_status ON public.institutions USING btree (subscription_status);


--
-- Name: ix_institutions_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_type ON public.institutions USING btree (type);


--
-- Name: ix_notification_deliveries_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_deliveries_id ON public.notification_deliveries USING btree (id);


--
-- Name: ix_notification_deliveries_notification_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_deliveries_notification_id ON public.notification_deliveries USING btree (notification_id);


--
-- Name: ix_notification_deliveries_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_deliveries_status ON public.notification_deliveries USING btree (status);


--
-- Name: ix_notification_templates_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_notification_templates_code ON public.notification_templates USING btree (code);


--
-- Name: ix_notification_templates_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_templates_id ON public.notification_templates USING btree (id);


--
-- Name: ix_notifications_channel; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_channel ON public.notifications USING btree (channel);


--
-- Name: ix_notifications_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_class_id ON public.notifications USING btree (class_id);


--
-- Name: ix_notifications_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_created_at ON public.notifications USING btree (created_at);


--
-- Name: ix_notifications_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_id ON public.notifications USING btree (id);


--
-- Name: ix_notifications_idempotency_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_notifications_idempotency_key ON public.notifications USING btree (idempotency_key);


--
-- Name: ix_notifications_notification_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_notification_type ON public.notifications USING btree (notification_type);


--
-- Name: ix_notifications_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_status ON public.notifications USING btree (status);


--
-- Name: ix_notifications_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_student_id ON public.notifications USING btree (student_id);


--
-- Name: ix_result_release_batches_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_release_batches_academic_year ON public.result_release_batches USING btree (academic_year);


--
-- Name: ix_result_release_batches_batch_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_result_release_batches_batch_code ON public.result_release_batches USING btree (batch_code);


--
-- Name: ix_result_release_batches_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_release_batches_class_id ON public.result_release_batches USING btree (class_id);


--
-- Name: ix_result_release_batches_exam_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_release_batches_exam_name ON public.result_release_batches USING btree (exam_name);


--
-- Name: ix_result_release_batches_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_release_batches_id ON public.result_release_batches USING btree (id);


--
-- Name: ix_result_release_batches_released_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_release_batches_released_at ON public.result_release_batches USING btree (released_at);


--
-- Name: ix_result_submissions_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_academic_year ON public.result_submissions USING btree (academic_year);


--
-- Name: ix_result_submissions_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_class_id ON public.result_submissions USING btree (class_id);


--
-- Name: ix_result_submissions_exam_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_exam_id ON public.result_submissions USING btree (exam_id);


--
-- Name: ix_result_submissions_exam_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_exam_name ON public.result_submissions USING btree (exam_name);


--
-- Name: ix_result_submissions_exam_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_exam_type ON public.result_submissions USING btree (exam_type);


--
-- Name: ix_result_submissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_id ON public.result_submissions USING btree (id);


--
-- Name: ix_result_submissions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_status ON public.result_submissions USING btree (status);


--
-- Name: ix_result_submissions_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_subject_id ON public.result_submissions USING btree (subject_id);


--
-- Name: ix_result_submissions_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_result_submissions_teacher_id ON public.result_submissions USING btree (teacher_id);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_sessions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sessions_id ON public.sessions USING btree (id);


--
-- Name: ix_sessions_refresh_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sessions_refresh_token ON public.sessions USING btree (refresh_token);


--
-- Name: ix_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sessions_user_id ON public.sessions USING btree (user_id);


--
-- Name: ix_student_enrollments_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_enrollments_academic_year ON public.student_enrollments USING btree (academic_year);


--
-- Name: ix_student_enrollments_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_enrollments_class_id ON public.student_enrollments USING btree (class_id);


--
-- Name: ix_student_enrollments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_enrollments_id ON public.student_enrollments USING btree (id);


--
-- Name: ix_student_enrollments_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_enrollments_student_id ON public.student_enrollments USING btree (student_id);


--
-- Name: ix_student_fees_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_fees_academic_year ON public.student_fees USING btree (academic_year);


--
-- Name: ix_student_fees_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_fees_class_id ON public.student_fees USING btree (class_id);


--
-- Name: ix_student_fees_fee_structure_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_fees_fee_structure_id ON public.student_fees USING btree (fee_structure_id);


--
-- Name: ix_student_fees_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_fees_id ON public.student_fees USING btree (id);


--
-- Name: ix_student_fees_invoice_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_student_fees_invoice_number ON public.student_fees USING btree (invoice_number);


--
-- Name: ix_student_fees_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_fees_student_id ON public.student_fees USING btree (student_id);


--
-- Name: ix_student_import_logs_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_import_logs_academic_year ON public.student_import_logs USING btree (academic_year);


--
-- Name: ix_student_import_logs_admin_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_import_logs_admin_user_id ON public.student_import_logs USING btree (admin_user_id);


--
-- Name: ix_student_import_logs_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_import_logs_class_id ON public.student_import_logs USING btree (class_id);


--
-- Name: ix_student_import_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_import_logs_id ON public.student_import_logs USING btree (id);


--
-- Name: ix_student_result_views_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_result_views_academic_year ON public.student_result_views USING btree (academic_year);


--
-- Name: ix_student_result_views_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_result_views_class_id ON public.student_result_views USING btree (class_id);


--
-- Name: ix_student_result_views_exam_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_result_views_exam_name ON public.student_result_views USING btree (exam_name);


--
-- Name: ix_student_result_views_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_result_views_id ON public.student_result_views USING btree (id);


--
-- Name: ix_student_result_views_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_student_result_views_student_id ON public.student_result_views USING btree (student_id);


--
-- Name: ix_students_admission_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_students_admission_number ON public.students USING btree (admission_number);


--
-- Name: ix_students_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_students_id ON public.students USING btree (id);


--
-- Name: ix_students_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_students_user_id ON public.students USING btree (user_id);


--
-- Name: ix_subjects_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_subjects_code ON public.subjects USING btree (code);


--
-- Name: ix_subjects_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subjects_id ON public.subjects USING btree (id);


--
-- Name: ix_subjects_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subjects_name ON public.subjects USING btree (name);


--
-- Name: ix_subscriptions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subscriptions_id ON public.subscriptions USING btree (id);


--
-- Name: ix_subscriptions_institution_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subscriptions_institution_id ON public.subscriptions USING btree (institution_id);


--
-- Name: ix_subscriptions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subscriptions_status ON public.subscriptions USING btree (status);


--
-- Name: ix_system_settings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_settings_id ON public.system_settings USING btree (id);


--
-- Name: ix_system_settings_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_system_settings_key ON public.system_settings USING btree (key);


--
-- Name: ix_teacher_assignments_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_assignments_academic_year ON public.teacher_assignments USING btree (academic_year);


--
-- Name: ix_teacher_assignments_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_assignments_class_id ON public.teacher_assignments USING btree (class_id);


--
-- Name: ix_teacher_assignments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_assignments_id ON public.teacher_assignments USING btree (id);


--
-- Name: ix_teacher_assignments_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_assignments_subject_id ON public.teacher_assignments USING btree (subject_id);


--
-- Name: ix_teacher_assignments_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_assignments_teacher_id ON public.teacher_assignments USING btree (teacher_id);


--
-- Name: ix_teacher_attendances_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_attendances_academic_year ON public.teacher_attendances USING btree (academic_year);


--
-- Name: ix_teacher_attendances_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_attendances_date ON public.teacher_attendances USING btree (date);


--
-- Name: ix_teacher_attendances_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_attendances_id ON public.teacher_attendances USING btree (id);


--
-- Name: ix_teacher_attendances_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_attendances_status ON public.teacher_attendances USING btree (status);


--
-- Name: ix_teacher_attendances_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_attendances_teacher_id ON public.teacher_attendances USING btree (teacher_id);


--
-- Name: ix_teacher_availabilities_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_availabilities_academic_year ON public.teacher_availabilities USING btree (academic_year);


--
-- Name: ix_teacher_availabilities_day_of_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_availabilities_day_of_week ON public.teacher_availabilities USING btree (day_of_week);


--
-- Name: ix_teacher_availabilities_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_availabilities_id ON public.teacher_availabilities USING btree (id);


--
-- Name: ix_teacher_availabilities_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_availabilities_teacher_id ON public.teacher_availabilities USING btree (teacher_id);


--
-- Name: ix_teachers_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_teachers_email ON public.teachers USING btree (email);


--
-- Name: ix_teachers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teachers_id ON public.teachers USING btree (id);


--
-- Name: ix_teachers_teacher_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_teachers_teacher_number ON public.teachers USING btree (teacher_number);


--
-- Name: ix_teachers_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_teachers_user_id ON public.teachers USING btree (user_id);


--
-- Name: ix_timetable_settings_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetable_settings_academic_year ON public.timetable_settings USING btree (academic_year);


--
-- Name: ix_timetable_settings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetable_settings_id ON public.timetable_settings USING btree (id);


--
-- Name: ix_timetables_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetables_academic_year ON public.timetables USING btree (academic_year);


--
-- Name: ix_timetables_class_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetables_class_id ON public.timetables USING btree (class_id);


--
-- Name: ix_timetables_day_of_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetables_day_of_week ON public.timetables USING btree (day_of_week);


--
-- Name: ix_timetables_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetables_id ON public.timetables USING btree (id);


--
-- Name: ix_timetables_period_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetables_period_number ON public.timetables USING btree (period_number);


--
-- Name: ix_timetables_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetables_subject_id ON public.timetables USING btree (subject_id);


--
-- Name: ix_timetables_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_timetables_teacher_id ON public.timetables USING btree (teacher_id);


--
-- Name: ix_user_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_roles_id ON public.user_roles USING btree (id);


--
-- Name: ix_user_roles_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_roles_role_id ON public.user_roles USING btree (role_id);


--
-- Name: ix_user_roles_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_roles_user_id ON public.user_roles USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: attendance_submissions attendance_submissions_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_submissions
    ADD CONSTRAINT attendance_submissions_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: attendance_submissions attendance_submissions_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_submissions
    ADD CONSTRAINT attendance_submissions_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: attendance_submissions attendance_submissions_submitted_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_submissions
    ADD CONSTRAINT attendance_submissions_submitted_by_id_fkey FOREIGN KEY (submitted_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: attendance_submissions attendance_submissions_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_submissions
    ADD CONSTRAINT attendance_submissions_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE SET NULL;


--
-- Name: attendances attendances_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: attendances attendances_recorded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_recorded_by_id_fkey FOREIGN KEY (recorded_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: attendances attendances_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: attendances attendances_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: attendances attendances_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE SET NULL;


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: class_promotion_batches class_promotion_batches_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_batches
    ADD CONSTRAINT class_promotion_batches_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: class_promotion_records class_promotion_records_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_records
    ADD CONSTRAINT class_promotion_records_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.class_promotion_batches(id) ON DELETE CASCADE;


--
-- Name: class_promotion_records class_promotion_records_from_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_records
    ADD CONSTRAINT class_promotion_records_from_class_id_fkey FOREIGN KEY (from_class_id) REFERENCES public.classes(id) ON DELETE SET NULL;


--
-- Name: class_promotion_records class_promotion_records_from_enrollment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_records
    ADD CONSTRAINT class_promotion_records_from_enrollment_id_fkey FOREIGN KEY (from_enrollment_id) REFERENCES public.student_enrollments(id) ON DELETE SET NULL;


--
-- Name: class_promotion_records class_promotion_records_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_records
    ADD CONSTRAINT class_promotion_records_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: class_promotion_records class_promotion_records_to_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_records
    ADD CONSTRAINT class_promotion_records_to_class_id_fkey FOREIGN KEY (to_class_id) REFERENCES public.classes(id) ON DELETE SET NULL;


--
-- Name: class_promotion_records class_promotion_records_to_enrollment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_promotion_records
    ADD CONSTRAINT class_promotion_records_to_enrollment_id_fkey FOREIGN KEY (to_enrollment_id) REFERENCES public.student_enrollments(id) ON DELETE SET NULL;


--
-- Name: exam_deadline_extensions exam_deadline_extensions_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_deadline_extensions
    ADD CONSTRAINT exam_deadline_extensions_exam_id_fkey FOREIGN KEY (exam_id) REFERENCES public.exams(id) ON DELETE CASCADE;


--
-- Name: exam_deadline_extensions exam_deadline_extensions_extended_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_deadline_extensions
    ADD CONSTRAINT exam_deadline_extensions_extended_by_id_fkey FOREIGN KEY (extended_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: exam_results exam_results_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT exam_results_exam_id_fkey FOREIGN KEY (exam_id) REFERENCES public.exams(id) ON DELETE CASCADE;


--
-- Name: exam_results exam_results_recorded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT exam_results_recorded_by_id_fkey FOREIGN KEY (recorded_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: exam_results exam_results_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT exam_results_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: exam_results exam_results_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT exam_results_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: exams exams_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: exams exams_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: exams exams_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE SET NULL;


--
-- Name: fee_payments fee_payments_recorded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_payments
    ADD CONSTRAINT fee_payments_recorded_by_id_fkey FOREIGN KEY (recorded_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: fee_payments fee_payments_student_fee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_payments
    ADD CONSTRAINT fee_payments_student_fee_id_fkey FOREIGN KEY (student_fee_id) REFERENCES public.student_fees(id) ON DELETE RESTRICT;


--
-- Name: fee_payments fee_payments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_payments
    ADD CONSTRAINT fee_payments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: fee_structures fee_structures_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_structures
    ADD CONSTRAINT fee_structures_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE SET NULL;


--
-- Name: exam_results fk_exam_results_class_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT fk_exam_results_class_id FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: exam_results fk_exam_results_release_batch_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT fk_exam_results_release_batch_id FOREIGN KEY (release_batch_id) REFERENCES public.result_release_batches(id) ON DELETE SET NULL;


--
-- Name: exam_results fk_exam_results_submission_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_results
    ADD CONSTRAINT fk_exam_results_submission_id FOREIGN KEY (submission_id) REFERENCES public.result_submissions(id) ON DELETE SET NULL;


--
-- Name: exams fk_exams_published_by_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT fk_exams_published_by_id FOREIGN KEY (published_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: fee_structures fk_fee_structures_created_by_id_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_structures
    ADD CONSTRAINT fk_fee_structures_created_by_id_users FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: student_fees fk_student_fees_class_id_classes; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT fk_student_fees_class_id_classes FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE SET NULL;


--
-- Name: timetables fk_timetables_published_by_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetables
    ADD CONSTRAINT fk_timetables_published_by_id FOREIGN KEY (published_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: form_master_assignments form_master_assignments_appointed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_master_assignments
    ADD CONSTRAINT form_master_assignments_appointed_by_id_fkey FOREIGN KEY (appointed_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: form_master_assignments form_master_assignments_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_master_assignments
    ADD CONSTRAINT form_master_assignments_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: form_master_assignments form_master_assignments_revoked_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_master_assignments
    ADD CONSTRAINT form_master_assignments_revoked_by_id_fkey FOREIGN KEY (revoked_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: form_master_assignments form_master_assignments_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_master_assignments
    ADD CONSTRAINT form_master_assignments_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE CASCADE;


--
-- Name: inquiries inquiries_converted_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inquiries
    ADD CONSTRAINT inquiries_converted_institution_id_fkey FOREIGN KEY (converted_institution_id) REFERENCES public.institutions(id) ON DELETE SET NULL;


--
-- Name: institution_payments institution_payments_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institution_payments
    ADD CONSTRAINT institution_payments_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: institution_payments institution_payments_subscription_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institution_payments
    ADD CONSTRAINT institution_payments_subscription_id_fkey FOREIGN KEY (subscription_id) REFERENCES public.subscriptions(id) ON DELETE SET NULL;


--
-- Name: institutions institutions_admin_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_admin_user_id_fkey FOREIGN KEY (admin_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: notification_deliveries notification_deliveries_notification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_deliveries
    ADD CONSTRAINT notification_deliveries_notification_id_fkey FOREIGN KEY (notification_id) REFERENCES public.notifications(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_related_attendance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_related_attendance_id_fkey FOREIGN KEY (related_attendance_id) REFERENCES public.attendances(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_related_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_related_exam_id_fkey FOREIGN KEY (related_exam_id) REFERENCES public.exams(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_related_release_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_related_release_batch_id_fkey FOREIGN KEY (related_release_batch_id) REFERENCES public.result_release_batches(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_related_result_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_related_result_id_fkey FOREIGN KEY (related_result_id) REFERENCES public.exam_results(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE SET NULL;


--
-- Name: result_release_batches result_release_batches_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_release_batches
    ADD CONSTRAINT result_release_batches_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: result_release_batches result_release_batches_released_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_release_batches
    ADD CONSTRAINT result_release_batches_released_by_id_fkey FOREIGN KEY (released_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: result_submissions result_submissions_approved_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT result_submissions_approved_by_id_fkey FOREIGN KEY (approved_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: result_submissions result_submissions_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT result_submissions_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: result_submissions result_submissions_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT result_submissions_exam_id_fkey FOREIGN KEY (exam_id) REFERENCES public.exams(id) ON DELETE CASCADE;


--
-- Name: result_submissions result_submissions_reviewed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT result_submissions_reviewed_by_id_fkey FOREIGN KEY (reviewed_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: result_submissions result_submissions_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT result_submissions_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: result_submissions result_submissions_submitted_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT result_submissions_submitted_by_id_fkey FOREIGN KEY (submitted_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: result_submissions result_submissions_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.result_submissions
    ADD CONSTRAINT result_submissions_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: student_enrollments student_enrollments_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_enrollments
    ADD CONSTRAINT student_enrollments_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE RESTRICT;


--
-- Name: student_enrollments student_enrollments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_enrollments
    ADD CONSTRAINT student_enrollments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: student_fees student_fees_fee_structure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT student_fees_fee_structure_id_fkey FOREIGN KEY (fee_structure_id) REFERENCES public.fee_structures(id) ON DELETE SET NULL;


--
-- Name: student_fees student_fees_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT student_fees_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: student_import_logs student_import_logs_admin_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_import_logs
    ADD CONSTRAINT student_import_logs_admin_user_id_fkey FOREIGN KEY (admin_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: student_import_logs student_import_logs_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_import_logs
    ADD CONSTRAINT student_import_logs_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE SET NULL;


--
-- Name: student_result_views student_result_views_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_result_views
    ADD CONSTRAINT student_result_views_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: student_result_views student_result_views_release_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_result_views
    ADD CONSTRAINT student_result_views_release_batch_id_fkey FOREIGN KEY (release_batch_id) REFERENCES public.result_release_batches(id) ON DELETE SET NULL;


--
-- Name: student_result_views student_result_views_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_result_views
    ADD CONSTRAINT student_result_views_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: students students_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: subscriptions subscriptions_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: teacher_assignments teacher_assignments_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_assignments
    ADD CONSTRAINT teacher_assignments_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: teacher_assignments teacher_assignments_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_assignments
    ADD CONSTRAINT teacher_assignments_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: teacher_assignments teacher_assignments_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_assignments
    ADD CONSTRAINT teacher_assignments_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE CASCADE;


--
-- Name: teacher_attendances teacher_attendances_recorded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_attendances
    ADD CONSTRAINT teacher_attendances_recorded_by_id_fkey FOREIGN KEY (recorded_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: teacher_attendances teacher_attendances_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_attendances
    ADD CONSTRAINT teacher_attendances_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE CASCADE;


--
-- Name: teacher_availabilities teacher_availabilities_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_availabilities
    ADD CONSTRAINT teacher_availabilities_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE CASCADE;


--
-- Name: teachers teachers_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: timetables timetables_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetables
    ADD CONSTRAINT timetables_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: timetables timetables_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetables
    ADD CONSTRAINT timetables_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: timetables timetables_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetables
    ADD CONSTRAINT timetables_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE SET NULL;


--
-- Name: user_roles user_roles_assigned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict JtfRwSkqdmZ5KGgT3qwdqdOgVXgo39Of1FW8lm21c0C88C1pc94wvTHwKNsk790

