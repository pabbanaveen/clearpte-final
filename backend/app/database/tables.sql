-- LEGACY DRAFT ONLY — DO NOT EXECUTE.
-- The canonical active schema is defined by app/database/models.py and the
-- versioned Alembic migrations under migrations/versions. This historical SQL
-- sketch includes unimplemented tables and differs from the active ORM schema.
-- Apply changes with Alembic; review/extend the models and migration chain first.

-- speaking module tables
CREATE TABLE read_aloud_question (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),                      
    text TEXT NOT NULL,                     
    preparation_time INT DEFAULT 30,         
    recording_time INT DEFAULT 40,           
    difficulty VARCHAR(50),                 
    category VARCHAR(100),                  
    tags TEXT[],                            
    expected_answer TEXT,                   
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE repeat_sentence_question (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,                 
    sentence TEXT NOT NULL,                 
    recording_time INT DEFAULT 15,           
    difficulty VARCHAR(50),                  
    category VARCHAR(100),                   
    tags TEXT[],                             
    title VARCHAR(255),                  
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE describe_image_question (
    id SERIAL PRIMARY KEY,
    image_url TEXT NOT NULL,                 
    image_type VARCHAR(100),                
    preparation_time INT DEFAULT 25,        
    speaking_time INT DEFAULT 40,            
    difficulty VARCHAR(50),                 
    category VARCHAR(100),                   
    key_points TEXT[],                      
    sample_answer TEXT,                     
    title VARCHAR(255),                     
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    description VARCHAR(500)             -- Optional description of the image
);

CREATE TABLE retell_lecture_question (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,                 
    transcript TEXT NOT NULL,              
    duration INT,                            
    key_points TEXT[],                       
    subject VARCHAR(100),                    
    preparation_time INT DEFAULT 10,        
    speaking_time INT DEFAULT 40,            
    difficulty VARCHAR(50),                  
    category VARCHAR(100),                   
    title VARCHAR(255),                     
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE answer_short_question (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,                 
    question TEXT NOT NULL,                  
    correct_answer TEXT NOT NULL,           
    acceptable_answers TEXT[],               
    difficulty VARCHAR(50),                 
    category VARCHAR(100),                  
    tags TEXT[],                            
    title VARCHAR(255),                    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

--writing module tables

CREATE TABLE summarize_text_question (
    id SERIAL PRIMARY KEY,
    passage TEXT NOT NULL,
    word_limit INT DEFAULT 75,
    time_limit INT DEFAULT 600,
    sample_summary TEXT,
    key_ideas TEXT[],
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE write_email_template (
    id SERIAL PRIMARY KEY,
    scenario TEXT NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    purpose TEXT NOT NULL,
    key_points TEXT[],
    word_limit INT DEFAULT 200,
    time_limit INT DEFAULT 600,  -- 10 minutes in seconds
    tone VARCHAR(100),
    sample_email TEXT,
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE write_essay_question (
    id SERIAL PRIMARY KEY,
    prompt TEXT NOT NULL,
    essay_type VARCHAR(100),
    word_limit INT DEFAULT 200,
    time_limit INT DEFAULT 1200,  -- 20 minutes in seconds
    rubric_content TEXT,          -- Scoring criteria for content
    rubric_form TEXT,             -- Scoring criteria for form/structure
    rubric_grammar TEXT,          -- Scoring criteria for grammar
    rubric_vocabulary TEXT,       -- Scoring criteria for vocabulary
    sample_essay TEXT,
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reading_fill_blanks_template (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    text TEXT NOT NULL,
    blank1_answer VARCHAR(100),
    blank1_options TEXT[],
    blank2_answer VARCHAR(100),
    blank2_options TEXT[],
    blank3_answer VARCHAR(100),
    blank3_options TEXT[],
    blank4_answer VARCHAR(100),
    blank4_options TEXT[],
    blank5_answer VARCHAR(100),
    blank5_options TEXT[],
    difficulty VARCHAR(50),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reading_fill_blanks_rw_template (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    passage TEXT NOT NULL,
    time_limit INT DEFAULT 600,  -- 10 minutes in seconds
    blank1_answer VARCHAR(100),
    blank1_options TEXT[],
    blank2_answer VARCHAR(100),
    blank2_options TEXT[],
    blank3_answer VARCHAR(100),
    blank3_options TEXT[],
    difficulty VARCHAR(50),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE multiple_choice_multiple_template (
    id SERIAL PRIMARY KEY,
    passage TEXT NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    option_e TEXT,
    correct_answers TEXT[] NOT NULL,
    time_limit INT DEFAULT 600,  -- 10 minutes in seconds
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE multiple_choice_single_template (
    id SERIAL PRIMARY KEY,
    passage TEXT NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer VARCHAR(1) NOT NULL,     -- Stores A, B, C, or D
    time_limit INT DEFAULT 600,             -- 10 minutes in seconds
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reorder_paragraphs_template (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    paragraph1 TEXT NOT NULL,
    paragraph2 TEXT NOT NULL,
    paragraph3 TEXT NOT NULL,
    paragraph4 TEXT NOT NULL,
    paragraph5 TEXT,
    correct_order INT[] NOT NULL,
    time_limit INT DEFAULT 600,  -- 10 minutes in seconds
    difficulty VARCHAR(50),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE summarize_spoken_text_template (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,
    transcript TEXT NOT NULL,
    duration INT,                         -- Duration in seconds
    word_limit INT DEFAULT 70,           -- Typically 50-70 words
    time_limit INT DEFAULT 600,          -- 10 minutes in seconds
    key_points TEXT[],                   -- Array of key points
    sample_summary TEXT,
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE listening_multiple_choice_multiple_template (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    option_e TEXT,
    correct_answers TEXT[] NOT NULL,
    transcript TEXT NOT NULL,
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE listening_multiple_choice_single_template (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer VARCHAR(1) NOT NULL,     -- Stores A, B, C, or D
    transcript TEXT NOT NULL,
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);



CREATE TABLE listening_fill_blanks_template (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    audio_url TEXT NOT NULL,
    transcript TEXT NOT NULL,
    duration INT,                     -- Duration in seconds
    blank1_answer VARCHAR(100),
    blank1_word VARCHAR(100),
    blank2_answer VARCHAR(100),
    blank2_word VARCHAR(100),
    blank3_answer VARCHAR(100),
    blank3_word VARCHAR(100),
    extra_words TEXT[],              -- Array of extra words
    difficulty VARCHAR(50),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE highlight_correct_summary_template (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,
    summary_a TEXT NOT NULL,
    summary_b TEXT NOT NULL,
    summary_c TEXT NOT NULL,
    correct_summary VARCHAR(1) NOT NULL,    -- Stores A, B, or C
    transcript TEXT NOT NULL,
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE select_missing_word_template (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,
    transcript TEXT NOT NULL,
    missing_word_position INT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer VARCHAR(1) NOT NULL,     -- Stores A, B, C, or D
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE highlight_incorrect_words_template (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,
    transcript TEXT NOT NULL,                -- Transcript with incorrect words
    incorrect_words TEXT[] NOT NULL,         -- Array of incorrect words
    correct_transcript TEXT NOT NULL,        -- Original correct transcript
    difficulty VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE write_from_dictation_template (
    id SERIAL PRIMARY KEY,
    audio_url TEXT NOT NULL,
    sentence TEXT NOT NULL,
    play_count INT DEFAULT 2,
    difficulty VARCHAR(50),
    category VARCHAR(100),
    key_words TEXT[],
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'student',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

create table user_profile(
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    target_score INT,
    test_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
-- User Sessions / Tokens (JWT, refresh tokens, etc.)
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Test Categories (Speaking, Writing, Reading, Listening)
CREATE TABLE test_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Test Definitions (PTE Test / Practice Test / Mock Test)
CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INT REFERENCES test_categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Test Sections (optional - if you break a test into sections like speaking/writing)
CREATE TABLE test_sections (
    id SERIAL PRIMARY KEY,
    test_id INT REFERENCES tests(id) ON DELETE CASCADE,
    section_name VARCHAR(100) NOT NULL,
    order_no INT NOT NULL
);

-- Test Questions (Audio, Text, Image, etc.)
CREATE TABLE test_questions (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES test_sections(id) ON DELETE CASCADE,
    question_type VARCHAR(100) NOT NULL, -- e.g. speaking, writing, mcq
    content TEXT NOT NULL,               -- Question text / transcription
    media_url TEXT,                      -- Audio/Video/Image file
    correct_answer TEXT,                 -- For auto-checkable questions (optional)
    max_score INT DEFAULT 90,
    order_no INT NOT NULL
);

-- Choices for MCQ Questions
CREATE TABLE test_choices (
    id SERIAL PRIMARY KEY,
    question_id INT REFERENCES test_questions(id) ON DELETE CASCADE,
    choice_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE
);

-- User attempts a test
CREATE TABLE user_test_attempts (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    test_id INT REFERENCES tests(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'in_progress'
)

-- User answers for each question
CREATE TABLE user_answers (
    id SERIAL PRIMARY KEY,
    attempt_id INT REFERENCES user_test_attempts(id) ON DELETE CASCADE,
    question_id INT REFERENCES test_questions(id) ON DELETE CASCADE,
    answer_text TEXT,
    answer_file_url TEXT,   -- audio/video file upload
    submitted_at TIMESTAMP DEFAULT NOW()
);


-- Detailed score per answer
CREATE TABLE user_answer_scores (
    id SERIAL PRIMARY KEY,
    answer_id INT REFERENCES user_answers(id) ON DELETE CASCADE,
    content_score INT,
    fluency_score INT,
    pronunciation_score INT,
    total_score INT GENERATED ALWAYS AS (COALESCE(content_score,0) 
                                       + COALESCE(fluency_score,0) 
                                       + COALESCE(pronunciation_score,0)) STORED
);

-- Overall score per test attempt
CREATE TABLE user_test_scores (
    id SERIAL PRIMARY KEY,
    attempt_id INT REFERENCES user_test_attempts(id) ON DELETE CASCADE,
    listening_score INT,
    reading_score INT,
    speaking_score INT,
    writing_score INT,
    overall_score INT GENERATED ALWAYS AS (
        COALESCE(listening_score,0) +
        COALESCE(reading_score,0) +
        COALESCE(speaking_score,0) +
        COALESCE(writing_score,0)
    ) STORED
);


-- For tagging tests (e.g., "Mock Test", "Practice Set 1")
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE test_tags (
    test_id INT REFERENCES tests(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (test_id, tag_id)
);

-- Payments (if you plan subscription)
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    plan_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active'
);


ALTER TABLE users
ADD COLUMN is_active BOOLEAN DEFAULT TRUE,   -- Admin can deactivate a user
ADD COLUMN last_login TIMESTAMP;

-- Admin logs (for audit trail)
CREATE TABLE admin_logs (
    id SERIAL PRIMARY KEY,
    admin_id INT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Subscription Plans (Admin-defined)
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    duration_days INT NOT NULL,  -- 30, 90, 365 etc.
    features JSONB,              -- {"max_tests": 20, "ai_scoring": true}
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payments (linked to subscriptions)
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    plan_id INT REFERENCES subscription_plans(id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending | success | failed
    payment_method VARCHAR(50),           -- stripe, razorpay, paypal, etc.
    transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
