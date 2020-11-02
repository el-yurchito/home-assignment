# Website availability monitoring

### What is it
It is simple website availability monitor system. It is not intended for production use,
it's more like a coding example.

### Overview
There are 2 subsystems: **checker** and **writer**.

**Checker** looks if website (or several websites) are available and sends 
some data as checking result to kafka. Check result data contain website url, 
checking start timestamp, total checking duration and http status 
(if case website did return anything). 

It's also possible to specify regex pattern. Checker reports if it was found
in the website response in that case.

**Writer** consumes checking results from kafka and writes them to PG table.
Table is to have structure like following:
```sql
create table t_check_result (
    id serial primary key,

    -- website url
    url varchar(256) not null,

    -- how long it took to get response, in seconds
    duration numeric not null,

    -- timestamp (fractional) when check started
    started_at numeric not null,  

    -- string representation of an error if it took place during getting response from site
    error varchar(256),  

    -- if regex pattern was found
    pattern_found bool,

    -- http status
    status_code integer
);
```

And that's it.

### Configuration
There are examples for configuring both [checker](./src/checker/config.example.json) 
and [writer](./src/writer/config.example.json). 
It's also necessary to configure [kafka](./src/configs.local/kafka/config.example.json)
and [PG](./src/configs.local/pg/config.example.json).

There are some important configuration parameters to mention.

**Concurrency**
Both checker and writer can work in single-thread or thread-pool mode. 
Specify `checks=1` for single-thread mode or `checks=n` for using 
thread pool `n` thread large.

If thread-pool mode is chosen, it's mandatory to specify `timeout` settings,
which is total thread pool timeout for a single iteration.

**Repeated execution**
It's possible to run only single iteration of checking or writing 
(for checker and writer components respectively).

But it's also possible to run an infinite loop of iterations, repeated periodically 
with some interval.

So specify `interval=null` for single check mode or `interval=x` for periodical checking
with interval of `x` seconds.

### Execution
Components are intended to be executed by cron, so the commands to execute are simple.

Specify `CHECKER_CONFIG` or `WRITER_CONFIG` environment variable. It is to contain 
the path to configuration file.
Then run `python -m checker` or `python -m writer` (assuming you are in `src` directory).
