# Change Log

## v2.0.0

> (Breaking Changes)
> Completely refactored the new version, features are not compatible with the old version.
> Result's `err` attribute changed to `error` attribute.
> Separated AsMysql class logic, added Engine class to handle mysql connections and execute statements, Engine can be used separately.
>
> (New Features)
> Execution result Result supports MysqlError's error code `error_no` and error message `error_msg` attributes.
> Mysql initialization connection supports url parameter: mysql://user:password@host:port/?charset=utf8mb4.
> Supports getting mysql connection status using status attribute (Engine.status).
> execute method supports stream parameter, returns uncached data stream.
> Result supports context and iterator patterns.
> Result supports uncached data stream acquisition mode.
> Supports Result returning custom type data.
> Added pytest tests.
>
> (Update) Using uv as package management tool.
> 
> (Features)
> 1. asmysql is an easy-to-use library that encapsulates aiomysql.
> 2. Supports automatic management of mysql connection pool and reconnection mechanism.
> 3. Globally automatically captures and handles MysqlError errors.
> 4. Separates statement execution and data retrieval.
> 5. Supports Python type hints for IDE programming.
> 6. Directly integrate AsMysql class for logical development.
