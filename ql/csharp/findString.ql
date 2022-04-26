/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id csharp/example/empty-block
 */

import csharp

from Variable var, string text, string name, string location, string line
where
var.getType() instanceof  StringType and
text = var.getInitializer().toString() and
text.length() >= 6 and
name = var.getName().toString() and
line = var.getInitializer().getLocation().getStartLine().toString() and
location = var.getInitializer().getLocation().toString()

select name, text, line, location