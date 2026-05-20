-- =============================================================
-- BKMS1 Term Project: DB Doctor
-- Schema Creation & Seed Data
-- =============================================================
-- Usage: psql -U postgres -d dbdoctor -f init_db.sql
-- =============================================================

-- Drop existing tables
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- =============================================================
-- 1. Schema
-- =============================================================

CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(200) NOT NULL,
    phone        VARCHAR(20),
    address      TEXT,
    city         VARCHAR(50),
    created_at   TIMESTAMP DEFAULT now()
);

CREATE TABLE books (
    book_id        SERIAL PRIMARY KEY,
    title          VARCHAR(300) NOT NULL,
    author         VARCHAR(200) NOT NULL,
    publisher      VARCHAR(200),
    category       VARCHAR(50),
    price          NUMERIC(10,2),
    stock_quantity INTEGER DEFAULT 0,
    rating         NUMERIC(3,2),
    description    TEXT,
    isbn           VARCHAR(13),
    published_date DATE,
    page_count     INTEGER,
    language       VARCHAR(20) DEFAULT 'Korean',
    created_at     TIMESTAMP DEFAULT now()
);

CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INTEGER REFERENCES customers(customer_id),
    book_id      INTEGER REFERENCES books(book_id),
    quantity     INTEGER NOT NULL,
    total_price  NUMERIC(10,2) NOT NULL,
    status       VARCHAR(20) DEFAULT 'pending',
    order_date   TIMESTAMP DEFAULT now(),
    updated_at   TIMESTAMP DEFAULT now()
);

-- Index on FK columns (simulating normal production state)
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_book_id ON orders(book_id);

-- =============================================================
-- 2. Seed Data
-- =============================================================

-- -------------------------------------------------------------
-- 2-1. customers (5,000 rows)
-- -------------------------------------------------------------
INSERT INTO customers (name, email, phone, city)
SELECT
    'customer_' || i,
    'user' || i || '@example.com',
    '010-' || lpad((random() * 9999)::int::text, 4, '0') || '-' || lpad((random() * 9999)::int::text, 4, '0'),
    (ARRAY['Seoul','Busan','Daegu','Incheon','Gwangju','Daejeon','Ulsan','Sejong','Suwon','Seongnam','Goyang','Yongin','Changwon','Jeju'])[floor(random() * 14 + 1)::int]
FROM generate_series(1, 5000) AS i;

-- -------------------------------------------------------------
-- 2-2. books (10,000 rows)
-- -------------------------------------------------------------
-- Categories: 12 types
-- description: 200-500 chars of random text (ensures meaningful seq scan time)

INSERT INTO books (title, author, publisher, category, price, stock_quantity, rating, description, isbn, published_date, page_count, language)
SELECT
    -- Title: category + number
    (ARRAY['Fiction','Science','History','Economics','Philosophy','Art','Technology','Cooking','Travel','Health','Education','Comics'])[floor(random() * 12 + 1)::int]
        || ' Story ' || i,
    -- Author: random from 50 authors (limited cardinality)
    'Author_' || floor(random() * 50 + 1)::int,
    -- Publisher: random from 20 publishers
    'Publisher_' || floor(random() * 20 + 1)::int,
    -- Category
    (ARRAY['Fiction','Science','History','Economics','Philosophy','Art','Technology','Cooking','Travel','Health','Education','Comics'])[floor(random() * 12 + 1)::int],
    -- Price: 8000 ~ 35000
    round((random() * 27000 + 8000)::numeric, -2),
    -- Stock: 0 ~ 500
    floor(random() * 500)::int,
    -- Rating: 1.0 ~ 5.0
    round((random() * 4 + 1)::numeric, 2),
    -- Description: long text (repeat to reach 200+ chars)
    'This is book number ' || i || ', featuring '
        || (ARRAY['exciting','moving','insightful','challenging','creative','practical'])[floor(random() * 6 + 1)::int]
        || ' content. '
        || repeat(
            (ARRAY[
                'It explores the subject from diverse perspectives and offers readers a fresh viewpoint. ',
                'The author draws on years of research and experience for an in-depth narrative. ',
                'It balances theory and practice, making it valuable for beginners and experts alike. ',
                'Rich case studies and analysis clearly convey the core concepts to the reader. ',
                'Reflecting the latest research findings, it provides timely and relevant information. '
            ])[floor(random() * 5 + 1)::int],
            floor(random() * 4 + 3)::int  -- repeat 3-6 times -> 200-500 chars
        ),
    -- ISBN: 13-digit number
    lpad(floor(random() * 10000000000000)::bigint::text, 13, '0'),
    -- Published date: 2015-01-01 ~ 2025-12-31
    '2015-01-01'::date + floor(random() * 4017)::int,
    -- Page count: 100 ~ 800
    floor(random() * 700 + 100)::int,
    -- Language
    (ARRAY['Korean','Korean','Korean','Korean','English','Japanese'])[floor(random() * 6 + 1)::int]
FROM generate_series(1, 10000) AS i;

-- -------------------------------------------------------------
-- 2-3. orders (50,000 rows)
-- -------------------------------------------------------------
-- Status distribution: delivered 70%, shipped 10%, confirmed 10%, pending 10%

INSERT INTO orders (customer_id, book_id, quantity, total_price, status, order_date, updated_at)
SELECT
    floor(random() * 5000 + 1)::int,
    floor(random() * 10000 + 1)::int,
    floor(random() * 5 + 1)::int,
    round((random() * 100000 + 5000)::numeric, -2),
    (ARRAY[
        'delivered','delivered','delivered','delivered','delivered','delivered','delivered',  -- 70%
        'shipped',                                                                          -- 10%
        'confirmed',                                                                        -- 10%
        'pending'                                                                           -- 10%
    ])[floor(random() * 10 + 1)::int],
    now() - (random() * interval '365 days'),
    now() - (random() * interval '30 days')
FROM generate_series(1, 50000) AS i;

-- =============================================================
-- 3. Reset pg_stat_statements
-- =============================================================
SELECT pg_stat_statements_reset();

-- =============================================================
-- Verification
-- =============================================================
SELECT 'customers' AS table_name, count(*) AS row_count FROM customers
UNION ALL
SELECT 'books', count(*) FROM books
UNION ALL
SELECT 'orders', count(*) FROM orders;
