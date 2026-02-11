create table if not exists vuzi (
    id serial primary key,
    name text UNIQUE,
	city text,
	link_po text
);


create table if not exists directions (
    id serial primary key,
    num_dir text,
    name_dir text,
    link_dir text,
    vuz_id integer,
    foreign key (vuz_id) references vuzi(id) on delete cascade
);


create table if not exists programs (
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




