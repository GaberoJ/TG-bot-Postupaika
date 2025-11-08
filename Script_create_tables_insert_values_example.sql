create table variants_of_entrance (
	id serial primary key,
	name text
);

create table subjects (
	id serial primary key,
	name text
);


create table vuzi (
    id serial primary key,
    name text UNIQUE,
	city text,
	link_po text
);


create table directions (
    id serial primary key,
    num_dir text,
    name_dir text,
    link_po text,
    vuz_id integer,
    foreign key (vuz_id) references vuzi(id) on delete cascade
);


create table programs (
    id serial primary key,
    direction_id integer,
	name text,
	education_lvl text,
	education_form text,
	has_budget boolean,
	has_contract boolean,
	count_budget integer,
	count_contract integer,
	education_cost_from integer default null,
    link_po text,
    foreign key (direction_id) references directions(id) on delete cascade
);


create table entrance (
	id serial primary key,
	program_id integer,
	variants_of_passing integer,
	average_passing_grade_from integer,
	count_places integer,
	cost_of_education_for_year integer default null,
	link_po text,
	foreign key (program_id) references programs(id) on delete cascade,
	foreign key (variants_of_passing) references variants_of_entrance(id) on delete cascade
);


create table exams (
	id serial primary key,
	entrance_id integer,
	subject integer,
	priority integer,
	points integer,
	foreign key (entrance_id) references entrance(id),	
	foreign key (subject) references subjects(id)
);





insert into variants_of_entrance (name) values
('Платно, очный вариант, 4 года обучения'),
('Бюджет, очный вариант, 4 года обучения');


insert into subjects (name) values
('Русский язык'),
('Математтика'),
('Информатика');

insert into vuzi (name, city, link_po) values 
('Национальный исследовательский университет ИТМО',
'Санкт-Петербург',
'https://spb.postupi.online/vuz/universitet-itmo/');

insert into directions (num_dir, name_dir, link_po, vuz_id) values
('09.03.02', 'Информационные системы и технологии',	'https://spb.postupi.online/vuz/universitet-itmo/specialnost/09.03.02/',	1);

insert into programs values
(default,
1,
'Разработка программного обеспечения / Software Engineering',
'Бакалавриат',
'Очно',
'true',
'true',
'151',
'500',
'459000',
'https://spb.postupi.online/vuz/universitet-itmo/programma/13129/');


insert into entrance values
(default, 1, 2, 103, 151, null, 'https://spb.postupi.online/vuz/fakultet-informacionnyh-tehnologiy-i-programmirovaniya-universitet-itmo/variant-programmi/60631/#free'),
(default, 1, 1, 62, 500, 459000, 'https://spb.postupi.online/vuz/fakultet-informacionnyh-tehnologiy-i-programmirovaniya-universitet-itmo/variant-programmi/60631/#pay');


insert into exams values
(default, 1,	1,	2,	60),
(default, 1,	2,	3,	60),
(default, 1,	3,	1,	60),
(default, 2,	1,	2,	60),
(default, 2,	2,	3,	60),
(default, 2,	3,	1,	60);




--drop table variants_of_entrance cascade;
--drop table subjects cascade;
--drop table vuzi cascade;
--drop table directions cascade;
--drop table programs cascade;
--drop table entrance cascade;
--drop table exams cascade;



