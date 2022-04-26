/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id java/example/empty-block
 */

import java

from Variable var, string text, string name, string location, string line
where
var.getType() instanceof  TypeString and
text = var.getInitializer().toString() and
text.length() >= 6 and
name = var.getName().toString() and
line = var.getInitializer().getLocation().getStartLine().toString() and
location = var.getInitializer().getLocation().toString()

select name, text, line, location