from __future__ import annotations

import enum
import textwrap
from dataclasses import dataclass, replace

from sqlalchemy_declarative_extensions.function import base


@enum.unique
class FunctionSecurity(enum.Enum):
    invoker = "INVOKER"
    definer = "DEFINER"


@dataclass
class Function(base.Function):
    """Describes a PostgreSQL function.

    Many function attributes are not currently supported. Support is **currently**
    minimal due to being a means to an end for defining triggers, but can certainly
    be evaluated/added on request.
    """

    security: FunctionSecurity = FunctionSecurity.invoker

    @classmethod
    def from_unknown_function(cls, f: base.Function | Function) -> Function:
        if not isinstance(f, Function):
            return Function(
                name=f.name,
                definition=f.definition,
                returns=f.returns,
                language=f.language,
                schema=f.schema,
            )

        return f

    def to_sql_create(self, replace=False):
        components = ["CREATE"]

        if replace:
            components.append("OR REPLACE")

        components.append("FUNCTION")
        components.append(self.qualified_name + "()")

        if self.returns:
            components.append(f"RETURNS {self.returns}")

        if self.security == FunctionSecurity.definer:
            components.append("SECURITY DEFINER")

        components.append(f"LANGUAGE {self.language}")
        components.append(f"AS $${self.definition}$$")

        return " ".join(components) + ";"

    def normalize(self) -> Function:
        returns = self.returns.lower()
        definition = textwrap.dedent(self.definition)
        return replace(
            self, returns=type_map.get(returns, returns), definition=definition
        )

    def with_security(self, security: FunctionSecurity):
        return replace(self, security=security)

    def with_security_definer(self):
        return replace(self, security=FunctionSecurity.definer)


type_map = {
    "bigint": "int8",
    "bigserial": "serial8",
    "boolean": "bool",
    "character varying": "varchar",
    "character": "char",
    "double precision": "float8",
    "integer": "int4",
    "numeric": "decimal",
    "real": "float4",
    "smallint": "int2",
    "serial": "serial4",
    "time with time zone": "timetz",
    "timestamp with time zone": "timestamptz",
}
