/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id csharp/example/empty-block
 */

import csharp

from MethodCall call,StringLiteral str_var
where
str_var = call.getAnArgument()
select str_var.toString(), str_var.toString(), 
str_var.getLocation().getStartLine().toString(),
str_var.getLocation().toString()