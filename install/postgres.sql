-- Скрипт создания БД и пользователя
-- Для Windows
CREATE DATABASE "guga" WITH TEMPLATE 'template0' OWNER "postgres" ENCODING 'UTF8';
-- Для Linux
CREATE DATABASE "guga" WITH TEMPLATE 'template0' OWNER "postgres" ENCODING 'UTF8' LC_COLLATE = 'ru_RU.UTF-8' LC_CTYPE = 'ru_RU.UTF-8';
-- Создать пользователя БД и дать ему права на БД
CREATE ROLE guga WITH LOGIN PASSWORD 'guga';
CREATE ROLE root WITH LOGIN SUPERUSER PASSWORD '++++';
ALTER DATABASE "guga" OWNER TO guga;

GRANT CONNECT ON DATABASE guga TO guga;
GRANT ALL PRIVILEGES ON DATABASE guga to guga;
GRANT ALL PRIVILEGES ON SCHEMA public TO guga;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO guga;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO guga;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO guga;

-- DROP TABLE IF EXISTS "user";
CREATE TABLE "user"
(
	id BIGINT NOT NULL CONSTRAINT user_pk PRIMARY KEY,
	username VARCHAR,
	first_name VARCHAR,
	last_name VARCHAR,
	phone VARCHAR,
    language_code VARCHAR,
	created TIMESTAMP(0) WITH TIME ZONE DEFAULT now(),
	last_message_received TIMESTAMP(0) WITH TIME ZONE,
	last_message_sent     TIMESTAMP(0) WITH TIME ZONE,
    passcode VARCHAR,
    bot_blocked TIMESTAMP(0) WITH TIME ZONE,
    user_blocked TIMESTAMP(0) WITH TIME ZONE
);
COMMENT ON TABLE "user" IS 'Пользователи Telegram';
COMMENT ON COLUMN "user".language_code IS 'Язык пользователя';
COMMENT ON COLUMN "user".passcode IS 'Код доступа для первичной регистрации пользователя';
COMMENT ON COLUMN "user".bot_blocked IS 'Дата и время, когда пользователь заблокировал бота';
COMMENT ON COLUMN "user".user_blocked IS 'Дата и время, когда пользователь был заблокирован';

-- DROP table "chat";
-- CREATE TABLE "chat"
-- (
--     id BIGINT NOT NULL CONSTRAINT chat_pk PRIMARY KEY,
--     title                 VARCHAR,
--     username              VARCHAR,
--     type                  VARCHAR,
--     created               TIMESTAMP(0) WITH TIME ZONE DEFAULT now(),
--     blocked               BOOLEAN DEFAULT FALSE,
--     last_message_sent     TIMESTAMP(0) WITH TIME ZONE,
--     last_message_received TIMESTAMP(0) WITH TIME ZONE,
--     last_error            VARCHAR,
--     migrated_to           BIGINT,
--     can_delete_messages   BOOLEAN DEFAULT FALSE
-- );
-- COMMENT ON TABLE chat IS 'Чаты';

-- DROP TABLE IF EXISTS public."property";
CREATE TABLE public."property" (
	"name" varchar CONSTRAINT property_pk PRIMARY KEY,
	"value" varchar NULL,
	"comment" varchar NULL,
	"check_regexp" varchar NULL
);
COMMENT ON TABLE property IS 'Свойства системы';
COMMENT ON COLUMN public."property"."name" IS 'Название свойства';
COMMENT ON COLUMN public."property"."value" IS 'Значение свойства';
COMMENT ON COLUMN public."property"."comment" IS 'Комментарий';
COMMENT ON COLUMN public."property"."check_regexp" IS 'Регулярное выражение для проверки значения';


DROP TABLE IF EXISTS public."context";
CREATE TABLE public."context" (
    user_id BIGINT NOT NULL PRIMARY KEY,
	context JSONB,
	updated TIMESTAMP(0) WITH TIME ZONE default now()
);
COMMENT ON TABLE public."context" IS 'Контекст работы с пользователем';
COMMENT ON COLUMN public."context"."user_id" IS 'Идентификатор пользователя';
COMMENT ON COLUMN public."context"."context" IS 'Данные контекста';
COMMENT ON COLUMN public."context"."updated" IS 'Время последнего изменения';


INSERT INTO context (user_id, context) VALUES (47254369, '{
    "current_form": "gender",
    "prev_form": "profile",
    "last_bot_message_id": 12345,
    "last_user_message_id": 9785,
    "params": {
        "gender": "23"
    }
}') ON CONFLICT (user_id) DO UPDATE SET context = '{
    "current_form": "gender",
    "prev_form": "profile",
    "last_bot_message_id": 12345,
    "last_user_message_id": 9785,
    "params": {
        "gender": "23"
    }
}';

DROP TABLE public."parameter";
CREATE TABLE public."parameter"
(
    id BIGSERIAL CONSTRAINT parameter_pk PRIMARY KEY,
    "order" INT,
    "name" VARCHAR NOT NULL,
    "type" VARCHAR NOT NULL,
    "prompt" VARCHAR,
    "json" VARCHAR NOT NULL,
	"comment" varchar,
	"check_regexp" varchar,
    "values" varchar
);
COMMENT ON TABLE property IS 'Свойства пользователя';
COMMENT ON COLUMN public."parameter"."name" IS 'Название свойства, например "Фамилия"';
COMMENT ON COLUMN public."parameter"."order" IS 'Порядок заполнения';
COMMENT ON COLUMN public."parameter"."type" IS 'Тип свойства (STRING, INTEGER, BOOLEAN, ENUM и т.п.)';
COMMENT ON COLUMN public."parameter"."prompt" IS 'Приглашение к вводу параметра, например "Введите Вашу фамилию"';
COMMENT ON COLUMN public."parameter"."json" IS 'JSON телеграм-сообщения для приглашения к вводу параметра';
COMMENT ON COLUMN public."parameter"."comment" IS 'Комментарий';
COMMENT ON COLUMN public."parameter"."check_regexp" IS 'Регулярное выражение для проверки значения';
COMMENT ON COLUMN public."parameter"."json" IS 'JSON-представление формы';
COMMENT ON COLUMN public."parameter"."type" IS 'Тип параметра (строка, выбор из нескольких вариантов)';

-- ALTER TABLE public."parameter" DROP COLUMN "values";
ALTER TABLE public."parameter" ADD COLUMN "order" INT;


DROP TABLE public."user_parameter";
CREATE TABLE public."user_parameter"
(
	user_id BIGINT NOT NULL,
	parameter_id BIGINT NOT NULL,
	"value" VARCHAR NOT NULL,
	created TIMESTAMP(0) WITH TIME ZONE DEFAULT now(),
	updated TIMESTAMP(0) WITH TIME ZONE,
	CONSTRAINT user_parameter_pk PRIMARY KEY (user_id, parameter_id)
);
CREATE INDEX user_parameter_user_id_idx ON public.user_parameter USING btree (user_id);
ALTER TABLE public.user_parameter ADD CONSTRAINT user_parameter_user_id_fk FOREIGN KEY (user_id) REFERENCES public."user"(id);
ALTER TABLE public.user_parameter ADD CONSTRAINT user_parameter_parameter_id_fk FOREIGN KEY (parameter_id) REFERENCES public."parameter"(id);

COMMENT ON TABLE public."user_parameter" IS 'Параметры пользователя';
COMMENT ON COLUMN public."user_parameter"."user_id" IS 'Идентификатор пользователя';
COMMENT ON COLUMN public."user_parameter"."parameter_id" IS 'Идентификатор параметра';
COMMENT ON COLUMN public."user_parameter"."value" IS 'Значение параметра';
COMMENT ON COLUMN public."user_parameter"."created" IS 'Дата создания параметра';
COMMENT ON COLUMN public."user_parameter"."parameter_id" IS 'Дата изменения параметра';














